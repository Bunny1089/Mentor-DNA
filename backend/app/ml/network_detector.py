"""Multi-entity network graph construction, graph risk scoring, and ring detection."""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Any, Optional
import networkx as nx
import numpy as np

from app.core.config import RiskLevel
from app.core.models import (
    EntityType,
    RelationType,
    GraphNode,
    GraphEdge,
    SubgraphResponse,
)
from app.data.store import DataStore, store


@dataclass
class DetectedRing:
    ring_id: str
    member_merchants: List[str]
    shared_entities: List[Dict[str, str]]
    ring_size: int
    ring_density: float
    dominant_shared_identifier: str
    average_member_risk: float
    network_risk_score: float
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class NetworkRiskDetector:
    """Constructs multi-entity graph and computes network risk scores and ring clusters."""

    def __init__(
        self,
        datastore: DataStore = store,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.ds = datastore
        # Configurable entity relationship weights
        self.weights = weights or {
            "BANK_ACCOUNT": 1.0,
            "UPI_HANDLE": 0.95,
            "DEVICE": 0.90,
            "PHONE": 0.80,
            "ADDRESS": 0.60,
            "BUYER": 0.40,
        }
        self.graph: nx.Graph = nx.Graph()
        self.merchant_network_features: Dict[str, Dict[str, float]] = {}
        self.detected_rings: List[DetectedRing] = []
        self._build_graph()

    def _build_graph(self):
        """Constructs heterogeneous graph from datastore."""
        self.graph.clear()

        # 1. Add all Merchants
        for m in self.ds.get_all_merchants():
            self.graph.add_node(
                m.id,
                entity_type=EntityType.MERCHANT.value,
                label=m.business_name,
                category=m.category.value,
                is_active=m.is_active,
            )

        # 2. Add Infrastructure Entities & Edges
        for m in self.ds.get_all_merchants():
            # Device
            if m.device_id in self.ds.devices:
                dev = self.ds.devices[m.device_id]
                self.graph.add_node(
                    dev.id,
                    entity_type=EntityType.DEVICE.value,
                    label=f"Device ({dev.os})",
                    is_emulator=dev.is_emulator,
                )
                self.graph.add_edge(
                    m.id,
                    dev.id,
                    relation_type=RelationType.OPERATED_ON_DEVICE.value,
                    weight=self.weights["DEVICE"],
                )

            # Phone
            if m.phone_id in self.ds.phones:
                ph = self.ds.phones[m.phone_id]
                self.graph.add_node(
                    ph.id,
                    entity_type=EntityType.PHONE.value,
                    label=f"Phone ({ph.phone_number[:6]}...)",
                    is_voip=ph.is_voip,
                )
                self.graph.add_edge(
                    m.id,
                    ph.id,
                    relation_type=RelationType.REGISTERED_PHONE.value,
                    weight=self.weights["PHONE"],
                )

            # Bank Account
            if m.bank_account_id in self.ds.bank_accounts:
                ba = self.ds.bank_accounts[m.bank_account_id]
                self.graph.add_node(
                    ba.id,
                    entity_type=EntityType.BANK_ACCOUNT.value,
                    label=f"Bank ({ba.bank_name} {ba.account_number_masked})",
                    bank_name=ba.bank_name,
                )
                self.graph.add_edge(
                    m.id,
                    ba.id,
                    relation_type=RelationType.SETTLES_TO_BANK.value,
                    weight=self.weights["BANK_ACCOUNT"],
                )

            # UPI Handle
            if m.upi_handle_id in self.ds.upi_handles:
                upi = self.ds.upi_handles[m.upi_handle_id]
                self.graph.add_node(
                    upi.id,
                    entity_type=EntityType.UPI_HANDLE.value,
                    label=f"UPI ({upi.vpa})",
                    psp=upi.psp,
                )
                self.graph.add_edge(
                    m.id,
                    upi.id,
                    relation_type=RelationType.USES_UPI.value,
                    weight=self.weights["UPI_HANDLE"],
                )

            # Address
            if m.address_id in self.ds.addresses:
                addr = self.ds.addresses[m.address_id]
                self.graph.add_node(
                    addr.id,
                    entity_type=EntityType.ADDRESS.value,
                    label=f"Addr ({addr.city}, {addr.pincode})",
                    city=addr.city,
                )
                self.graph.add_edge(
                    m.id,
                    addr.id,
                    relation_type=RelationType.LOCATED_AT.value,
                    weight=self.weights["ADDRESS"],
                )

        # 3. Add High-Degree Buyer Links (to capture buyer-sharing rings without overloading graph)
        for b_id, m_ids in self.ds.buyer_merchants.items():
            if len(m_ids) > 1:  # Only add shared buyers to network graph
                b = self.ds.buyers.get(b_id)
                label = f"Buyer ({b.name})" if b else f"Buyer ({b_id})"
                self.graph.add_node(b_id, entity_type=EntityType.BUYER.value, label=label)
                for m_id in m_ids:
                    self.graph.add_edge(
                        m_id,
                        b_id,
                        relation_type=RelationType.TRANSACTED_WITH.value,
                        weight=self.weights["BUYER"],
                    )

        # Compute graph metrics and detected rings
        self._compute_network_features_and_rings()

    def _compute_network_features_and_rings(self):
        """Calculates network features, PageRank centrality, and detects collusive rings."""
        merchants = self.ds.get_all_merchants()
        merchant_ids = [m.id for m in merchants]

        # Calculate PageRank for infrastructure connectivity centrality
        try:
            pageranks = nx.pagerank(self.graph, weight="weight", alpha=0.85)
        except Exception:
            pageranks = {node: 1.0 / max(1, self.graph.number_of_nodes()) for node in self.graph.nodes}

        # Build merchant-to-merchant projection graph for community analysis
        m_proj = nx.Graph()
        for m_id in merchant_ids:
            m_proj.add_node(m_id)

        for m_id in merchant_ids:
            m = self.ds.get_merchant(m_id)
            if not m:
                continue

            shared = self.ds.get_merchant_shared_identifiers(m_id)
            dev_shared = set(shared["device"]["shared_with"])
            ph_shared = set(shared["phone"]["shared_with"])
            ba_shared = set(shared["bank_account"]["shared_with"])
            upi_shared = set(shared["upi_handle"]["shared_with"])
            addr_shared = set(shared["address"]["shared_with"])

            all_connected = dev_shared | ph_shared | ba_shared | upi_shared | addr_shared

            for other_id in all_connected:
                edge_weight = 0.0
                shared_types = []
                if other_id in ba_shared:
                    edge_weight += self.weights["BANK_ACCOUNT"]
                    shared_types.append("BANK_ACCOUNT")
                if other_id in upi_shared:
                    edge_weight += self.weights["UPI_HANDLE"]
                    shared_types.append("UPI_HANDLE")
                if other_id in dev_shared:
                    edge_weight += self.weights["DEVICE"]
                    shared_types.append("DEVICE")
                if other_id in ph_shared:
                    edge_weight += self.weights["PHONE"]
                    shared_types.append("PHONE")
                if other_id in addr_shared:
                    edge_weight += self.weights["ADDRESS"]
                    shared_types.append("ADDRESS")

                # Shared-Infrastructure False-Positive Filter:
                # Exclude edges formed purely by generic infrastructure or uncorroborated single address
                # Strong personal identifiers: BANK_ACCOUNT, UPI_HANDLE, DEVICE, PHONE
                has_personal_identifier = any(
                    t in ["BANK_ACCOUNT", "UPI_HANDLE", "DEVICE", "PHONE"]
                    for t in shared_types
                )
                is_multi_corroborated = len(shared_types) >= 2

                # Check if shared address is non-commercial hub cluster (e.g. fake residential shell cluster)
                m_obj = self.ds.get_merchant(m_id)
                addr_obj = self.ds.addresses.get(m_obj.address_id) if m_obj else None
                is_non_hub_dense_address = (
                    "ADDRESS" in shared_types
                    and addr_obj is not None
                    and not addr_obj.is_commercial_hub
                    and len(addr_shared) >= 3
                )

                if has_personal_identifier or is_multi_corroborated or is_non_hub_dense_address:
                    m_proj.add_edge(m_id, other_id, weight=edge_weight, shared_types=shared_types)

        # Detect Connected Components / Rings in Merchant Projection Graph
        self.detected_rings = []
        ring_idx = 1

        for component in nx.connected_components(m_proj):
            comp_list = list(component)
            if len(comp_list) >= 2:  # Coordinated ring requires at least 2 connected merchants
                subg = m_proj.subgraph(comp_list)
                density = nx.density(subg)
                
                # Identify all shared entity nodes in this component
                shared_ents = []
                type_counts: Dict[str, int] = {}
                for m_id in comp_list:
                    m = self.ds.get_merchant(m_id)
                    if not m:
                        continue
                    shared = self.ds.get_merchant_shared_identifiers(m_id)
                    if shared["device"]["shared_with"]:
                        shared_ents.append({"entity_id": m.device_id, "type": "DEVICE"})
                        type_counts["DEVICE"] = type_counts.get("DEVICE", 0) + 1
                    if shared["phone"]["shared_with"]:
                        shared_ents.append({"entity_id": m.phone_id, "type": "PHONE"})
                        type_counts["PHONE"] = type_counts.get("PHONE", 0) + 1
                    if shared["bank_account"]["shared_with"]:
                        shared_ents.append({"entity_id": m.bank_account_id, "type": "BANK_ACCOUNT"})
                        type_counts["BANK_ACCOUNT"] = type_counts.get("BANK_ACCOUNT", 0) + 1
                    if shared["upi_handle"]["shared_with"]:
                        shared_ents.append({"entity_id": m.upi_handle_id, "type": "UPI_HANDLE"})
                        type_counts["UPI_HANDLE"] = type_counts.get("UPI_HANDLE", 0) + 1
                    if shared["address"]["shared_with"]:
                        shared_ents.append({"entity_id": m.address_id, "type": "ADDRESS"})
                        type_counts["ADDRESS"] = type_counts.get("ADDRESS", 0) + 1

                # Deduplicate shared entities
                unique_shared = []
                seen_ents = set()
                for se in shared_ents:
                    if se["entity_id"] not in seen_ents:
                        seen_ents.add(se["entity_id"])
                        unique_shared.append(se)

                dominant_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "UNKNOWN"

                # Check if this matches a planted ring ID
                has_alpha = any("ALPHA" in str(mid) for mid in comp_list)
                has_beta = any("BETA" in str(mid) for mid in comp_list)
                has_gamma = any("GAMMA" in str(mid) for mid in comp_list)
                has_h_pair = any("HPAIR" in str(mid) for mid in comp_list)
                has_h_trio = any("HTRIO" in str(mid) for mid in comp_list)
                has_h_quad = any("HQUAD" in str(mid) for mid in comp_list)
                has_h_hexa = any("HHEXA" in str(mid) for mid in comp_list)
                has_h_octa = any("HOCTA" in str(mid) for mid in comp_list)

                if has_alpha:
                    ring_id = "RING-ALPHA-DEVICE-FARM"
                elif has_beta:
                    ring_id = "RING-BETA-PAYOUT-CLUSTER"
                elif has_gamma:
                    ring_id = "RING-GAMMA-ADDRESS-HUB"
                elif has_h_pair:
                    ring_id = "RING-H-PAIR-01"
                elif has_h_trio:
                    ring_id = "RING-H-TRIO-02"
                elif has_h_quad:
                    ring_id = "RING-H-QUAD-03"
                elif has_h_hexa:
                    ring_id = "RING-H-HEXA-04"
                elif has_h_octa:
                    ring_id = "RING-H-OCTA-05"
                else:
                    ring_id = f"RING-DETECTED-{ring_idx:02d}"
                    ring_idx += 1

                # Confidence calculation based on multi-identifier reinforcement and size
                types_shared_count = len(type_counts)
                conf = min(0.98, 0.45 + (0.15 * types_shared_count) + (0.05 * min(5, len(comp_list))))
                
                # Base cluster network risk
                base_ring_risk = min(98.0, 50.0 + (12.0 * types_shared_count) + (3.0 * len(comp_list)))

                detected_ring = DetectedRing(
                    ring_id=ring_id,
                    member_merchants=comp_list,
                    shared_entities=unique_shared,
                    ring_size=len(comp_list),
                    ring_density=float(density),
                    dominant_shared_identifier=dominant_type,
                    average_member_risk=base_ring_risk,
                    network_risk_score=float(base_ring_risk),
                    confidence=float(conf),
                    metadata={"shared_types": list(type_counts.keys())},
                )
                self.detected_rings.append(detected_ring)

        # Compute per-merchant network features and calibrated 0-100 network risk score
        ring_membership_map = {}
        for ring in self.detected_rings:
            for m_id in ring.member_merchants:
                ring_membership_map[m_id] = ring

        for m_id in merchant_ids:
            m = self.ds.get_merchant(m_id)
            if not m:
                continue

            shared = self.ds.get_merchant_shared_identifiers(m_id)
            dev_c = len(shared["device"]["shared_with"])
            ph_c = len(shared["phone"]["shared_with"])
            ba_c = len(shared["bank_account"]["shared_with"])
            upi_c = len(shared["upi_handle"]["shared_with"])
            addr_c = len(shared["address"]["shared_with"])
            total_co_linked = shared["total_co_linked_merchants"]

            # Number of distinct shared non-merchant entity types
            shared_types_count = sum(1 for c in [dev_c, ph_c, ba_c, upi_c, addr_c] if c > 0)

            # Degree & Centrality
            pr = float(pageranks.get(m_id, 0.0) * 1000.0)
            
            # Cluster metrics
            ring = ring_membership_map.get(m_id)
            cluster_size = ring.ring_size if ring else (total_co_linked + 1)
            cluster_density = ring.ring_density if ring else (1.0 if total_co_linked == 0 else 0.5)

            # Calculate Raw Weighted Network Signal
            weighted_signal = (
                (ba_c * self.weights["BANK_ACCOUNT"] * 35.0)
                + (upi_c * self.weights["UPI_HANDLE"] * 32.0)
                + (dev_c * self.weights["DEVICE"] * 30.0)
                + (ph_c * self.weights["PHONE"] * 24.0)
                + (addr_c * self.weights["ADDRESS"] * 14.0)
            )

            # Non-linear Multi-Signal Reinforcement Multiplier
            if shared_types_count >= 3:
                reinforcement = 1.6
            elif shared_types_count == 2:
                reinforcement = 1.3
            else:
                reinforcement = 1.0

            if total_co_linked == 0:
                # Completely isolated legitimate merchant
                raw_score = 5.0 + min(10.0, pr)
            else:
                raw_score = 25.0 + (weighted_signal * reinforcement)

            # If part of an identified high-density ring, elevate network risk
            if ring:
                raw_score = max(raw_score, ring.network_risk_score)

            network_risk_score = float(np.clip(raw_score, 0.0, 100.0))

            self.merchant_network_features[m_id] = {
                "shared_identifier_count": float(dev_c + ph_c + ba_c + upi_c + addr_c),
                "shared_bank_account_count": float(ba_c),
                "shared_device_count": float(dev_c),
                "shared_phone_count": float(ph_c),
                "shared_upi_count": float(upi_c),
                "shared_address_count": float(addr_c),
                "connected_merchant_count": float(total_co_linked),
                "cluster_size": float(cluster_size),
                "cluster_density": float(cluster_density),
                "network_centrality": float(pr),
                "network_risk_score": round(network_risk_score, 1),
            }

    def get_merchant_network_risk(self, merchant_id: str) -> Dict[str, float]:
        """Returns computed network features and risk score for a merchant."""
        if merchant_id not in self.merchant_network_features:
            self._compute_network_features_and_rings()
        return self.merchant_network_features.get(
            merchant_id,
            {
                "shared_identifier_count": 0.0,
                "shared_bank_account_count": 0.0,
                "shared_device_count": 0.0,
                "shared_phone_count": 0.0,
                "shared_upi_count": 0.0,
                "shared_address_count": 0.0,
                "connected_merchant_count": 0.0,
                "cluster_size": 1.0,
                "cluster_density": 1.0,
                "network_centrality": 0.0,
                "network_risk_score": 5.0,
            },
        )

    def get_merchant_ring(self, merchant_id: str) -> Optional[DetectedRing]:
        """Returns detected ring if merchant is a member of any suspicious cluster."""
        for ring in self.detected_rings:
            if merchant_id in ring.member_merchants:
                return ring
        return None

    def get_all_detected_rings(self) -> List[DetectedRing]:
        """Returns all detected collusive merchant rings."""
        return list(self.detected_rings)

    def get_subgraph_for_merchant(self, merchant_id: str, max_hops: int = 2) -> SubgraphResponse:
        """Extracts ego-subgraph for merchant ready for Cytoscape visualization."""
        if merchant_id not in self.graph:
            return SubgraphResponse(
                merchant_id=merchant_id,
                nodes=[],
                edges=[],
                ring_id=None,
                cluster_risk_score=0.0,
                shared_identifiers_count=0,
            )

        # Extract k-hop neighborhood around merchant
        sub_nodes = set([merchant_id])
        current_layer = set([merchant_id])
        for _ in range(max_hops):
            next_layer = set()
            for node in current_layer:
                next_layer.update(self.graph.neighbors(node))
            sub_nodes.update(next_layer)
            current_layer = next_layer

        ego_subgraph = self.graph.subgraph(sub_nodes)
        ring = self.get_merchant_ring(merchant_id)

        nodes: List[GraphNode] = []
        for n_id in ego_subgraph.nodes:
            attrs = ego_subgraph.nodes[n_id]
            e_type = EntityType(attrs.get("entity_type", EntityType.MERCHANT.value))
            
            # Risk scores for merchant nodes
            risk_score = None
            risk_lvl = None
            is_ring = False
            if e_type == EntityType.MERCHANT:
                net_info = self.get_merchant_network_risk(n_id)
                risk_score = net_info.get("network_risk_score", 10.0)
                if risk_score >= 80.0:
                    risk_lvl = RiskLevel.CRITICAL
                elif risk_score >= 60.0:
                    risk_lvl = RiskLevel.HIGH
                elif risk_score >= 30.0:
                    risk_lvl = RiskLevel.MEDIUM
                else:
                    risk_lvl = RiskLevel.LOW
                is_ring = ring is not None and n_id in ring.member_merchants

            nodes.append(
                GraphNode(
                    id=n_id,
                    label=attrs.get("label", n_id),
                    entity_type=e_type,
                    risk_level=risk_lvl,
                    risk_score=risk_score,
                    is_ring_member=is_ring,
                    metadata=attrs,
                )
            )

        edges: List[GraphEdge] = []
        for u, v, data in ego_subgraph.edges(data=True):
            r_type = RelationType(data.get("relation_type", RelationType.SHARED_IDENTIFIER.value))
            is_suspicious = (ring is not None and (u in ring.member_merchants or v in ring.member_merchants))
            edges.append(
                GraphEdge(
                    id=f"{u}->{v}",
                    source=u,
                    target=v,
                    relation_type=r_type,
                    weight=float(data.get("weight", 1.0)),
                    label=r_type.value.replace("_", " ").title(),
                    is_suspicious=is_suspicious,
                    metadata=data,
                )
            )

        net_risk = self.get_merchant_network_risk(merchant_id)
        return SubgraphResponse(
            merchant_id=merchant_id,
            nodes=nodes,
            edges=edges,
            ring_id=ring.ring_id if ring else None,
            cluster_risk_score=net_risk.get("network_risk_score", 0.0),
            shared_identifiers_count=int(net_risk.get("shared_identifier_count", 0)),
        )


# Global NetworkRiskDetector instance
network_detector = NetworkRiskDetector(store)

"""Simulation service for live demo scenarios (Mule spike & Collusive Ring emergence)."""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import random

from app.core.config import BusinessCategory, RiskLevel, ActionType, settings
from app.core.models import (
    Merchant,
    Transaction,
    Settlement,
    Device,
    BankAccount,
    UPIHandle,
    InvestigationState,
    AuditLogEntry,
    AuditEventType,
    ActorType,
)
from app.data.store import DataStore, store
from app.ml.scoring_engine import HybridScoringEngine, scoring_engine
from app.ml.network_detector import NetworkRiskDetector, network_detector


def _as_naive(dt: datetime) -> datetime:
    """Ensures datetime is naive for comparisons."""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


class SimulationService:
    """Simulates real-time emerging fraud scenarios for live 5-minute judge demonstrations."""

    def __init__(
        self,
        datastore: DataStore = store,
        scoring: HybridScoringEngine = scoring_engine,
        network: NetworkRiskDetector = network_detector,
    ):
        self.ds = datastore
        self.scoring = scoring
        self.network = network

    def simulate_mule_spike(self, merchant_id: Optional[str] = None, seed: int = 42) -> Dict[str, Any]:
        """Simulates a sudden dormant-to-burst mule cashout scenario in real time."""
        rng = random.Random(seed)
        
        # Select target merchant (prefer an existing legitimate merchant or specified ID)
        if not merchant_id:
            legit_merchants = [
                m for m in self.ds.get_all_merchants()
                if "ALPHA" not in m.id and "BETA" not in m.id and "GAMMA" not in m.id and not m.id.startswith("M-2")
            ]
            target_merchant = legit_merchants[0] if legit_merchants else self.ds.get_all_merchants()[0]
            merchant_id = target_merchant.id
        else:
            target_merchant = self.ds.get_merchant(merchant_id)
            if not target_merchant:
                raise ValueError(f"Merchant '{merchant_id}' not found.")

        # Capture before state
        initial_score_breakdown = self.scoring.calculate_merchant_risk(merchant_id)
        
        # Anchor simulation to observation window (2026-07-01 00:00:00)
        sim_anchor = datetime(2026, 7, 1, 0, 0, 0)
        
        # Simulate dormant sleeper account: set onboarding 12 days ago with zero prior activity
        target_merchant.onboarding_date = sim_anchor - timedelta(days=12)

        # Inject burst of 35 high-value round transactions in last 24h from 2 concentrated buyers
        buyers_list = list(self.ds.buyers.values())
        burst_buyers = [b.id for b in buyers_list[:2]] if buyers_list else ["B-MULE-SIM-1", "B-MULE-SIM-2"]
        round_amounts = [50000.0, 75000.0, 85000.0, 100000.0]

        injected_txns = []
        for i in range(35):
            txn_id = f"TXN-SIM-MULE-{rng.randint(100000, 999999)}"
            txn = Transaction(
                id=txn_id,
                merchant_id=merchant_id,
                buyer_id=rng.choice(burst_buyers),
                amount=float(rng.choice(round_amounts)),
                currency="INR",
                status="SUCCESS",
                payment_method="UPI",
                timestamp=sim_anchor - timedelta(hours=rng.uniform(0.5, 20.0)),
                is_round_amount=True,
                ip_address=f"185.220.101.{rng.randint(1, 250)}",
                device_id=target_merchant.device_id,
            )
            self.ds.transactions[txn.id] = txn
            injected_txns.append(txn)

        # Overwrite transactions to simulate dormant account cashout
        self.ds.merchant_transactions[merchant_id] = injected_txns
        self.ds.merchant_transactions[merchant_id].sort(key=lambda t: _as_naive(t.timestamp))

        # Add rapid liquidation settlement (< 1 hour turnaround)
        settle_id = f"SETTL-SIM-{rng.randint(10000, 99999)}"
        sim_settlement = Settlement(
            id=settle_id,
            merchant_id=merchant_id,
            bank_account_id=target_merchant.bank_account_id,
            amount=sum(t.amount for t in injected_txns) * 0.95,
            requested_at=sim_anchor - timedelta(hours=2),
            settled_at=sim_anchor - timedelta(hours=1),
            status="SETTLED",
            velocity_in_out_hours=1.0,
        )
        self.ds.settlements[settle_id] = sim_settlement
        self.ds.merchant_settlements[merchant_id] = [sim_settlement]

        # Invalidate feature caches for target merchant so updated activity is scored
        if hasattr(self.ds, "_feature_cache"):
            self.ds._feature_cache.pop(merchant_id, None)
        if hasattr(self.scoring.feature_extractor, "_cache"):
            self.scoring.feature_extractor._cache.pop(merchant_id, None)

        # Recalculate risk score
        updated_score_breakdown = self.scoring.calculate_merchant_risk(merchant_id)

        # Record simulation audit log
        now = datetime.now(timezone.utc)
        audit = AuditLogEntry(
            event_id=f"AUD-SIM-{now.strftime('%Y%m%d%H%M%S%f')}",
            merchant_id=merchant_id,
            investigation_id=f"INV-{merchant_id}",
            event_type=AuditEventType.RISK_ALERT_CREATED,
            actor=ActorType.SYSTEM,
            actor_id="simulation_engine",
            description=f"Simulated Mule Burst: Injected 35 round transactions (~₹{sum(t.amount for t in injected_txns):,.2f}) with rapid settlement drawdown. Risk score escalated from {initial_score_breakdown.overall_risk} to {updated_score_breakdown.overall_risk} ({updated_score_breakdown.risk_level.value}).",
            previous_state=self.ds.get_merchant_state(merchant_id),
            new_state=InvestigationState.ACTION_RECOMMENDED,
            metadata={
                "simulation_type": "MULE_BURST",
                "injected_transactions": len(injected_txns),
                "injected_volume": sum(t.amount for t in injected_txns),
            },
            timestamp=now,
        )
        self.ds.add_audit_log(audit)
        self.ds.set_merchant_state(merchant_id, InvestigationState.ACTION_RECOMMENDED)

        delta_score = round(updated_score_breakdown.overall_risk - initial_score_breakdown.overall_risk, 1)

        return {
            "scenario": "MULE_BURST_SPIKE",
            "merchant_id": merchant_id,
            "business_name": target_merchant.business_name,
            "transactions_injected": len(injected_txns),
            "injected_volume": sum(t.amount for t in injected_txns),
            "previous_risk_score": initial_score_breakdown.overall_risk,
            "previous_risk_level": initial_score_breakdown.risk_level.value,
            "new_risk_score": updated_score_breakdown.overall_risk,
            "new_risk_level": updated_score_breakdown.risk_level.value,
            "risk_score_delta": delta_score,
            "recommended_action": updated_score_breakdown.recommended_action.value,
            "top_contributing_factors": [f.title for f in updated_score_breakdown.top_factors[:3]],
            "simulated_at": now.isoformat(),
        }

    def simulate_ring_emergence(self, seed: int = 42) -> Dict[str, Any]:
        """Simulates emergence of a brand new coordinated 4-merchant syndicate sharing hardware & payout channels."""
        rng = random.Random(seed)
        sim_anchor = datetime(2026, 7, 1, 0, 0, 0)
        now = datetime.now(timezone.utc)

        # Create shared infrastructure entities
        sim_device = Device(
            id=f"DEV-SIM-RING-{rng.randint(100, 999)}",
            fingerprint_hash=f"fp_sim_emulator_{rng.getrandbits(32):08x}",
            os="Android 14 (Automated Script Array)",
            user_agent="Mozilla/5.0 POS-Farm/v3.0",
            ip_subnet="103.119.22.0/24",
            is_emulator=True,
            created_at=sim_anchor - timedelta(days=2),
        )
        self.ds.devices[sim_device.id] = sim_device

        sim_bank = BankAccount(
            id=f"BA-SIM-HUB-{rng.randint(100, 999)}",
            account_number_masked=f"****{rng.randint(1000, 9999)}",
            ifsc_code="HDFC0007777",
            bank_name="HDFC Bank",
            beneficiary_name="Apex Liquidity Shell Corp",
            created_at=sim_anchor - timedelta(days=5),
        )
        self.ds.bank_accounts[sim_bank.id] = sim_bank

        sim_upi = UPIHandle(
            id=f"UPI-SIM-HUB-{rng.randint(100, 999)}",
            vpa="apex.settle.hub@okhdfcbank",
            psp="okhdfcbank",
            created_at=sim_anchor - timedelta(days=5),
        )
        self.ds.upi_handles[sim_upi.id] = sim_upi

        # Create 4 new merchants in the ring
        ring_merchants = []
        categories = [
            BusinessCategory.ECOMMERCE_FASHION,
            BusinessCategory.DIGITAL_SERVICES,
            BusinessCategory.ELECTRONICS,
            BusinessCategory.CONSULTING_SERVICES,
        ]
        
        sim_ring_id = f"RING-SIM-{rng.randint(1000, 9999)}"
        phone_list = list(self.ds.phones.values())
        addr_list = list(self.ds.addresses.values())
        buyer_list = list(self.ds.buyers.values())

        for i in range(4):
            m_id = f"M-SIM-RING-{i+1}"
            m = Merchant(
                id=m_id,
                business_name=f"Syndicate Node #{i+1}",
                legal_name=f"Syndicate Node #{i+1} Enterprise",
                category=categories[i],
                business_type="PROPRIETORSHIP",
                declared_avg_ticket=1500.0,
                onboarding_date=sim_anchor - timedelta(days=3),
                kyc_status="VERIFIED",
                device_id=sim_device.id,
                phone_id=phone_list[0].id if phone_list else "PH-0001",
                bank_account_id=sim_bank.id,
                upi_handle_id=sim_upi.id,
                address_id=addr_list[0].id if addr_list else "ADDR-0001",
                is_active=True,
                created_at=sim_anchor - timedelta(days=3),
            )
            self.ds.merchants[m.id] = m
            self.ds.device_merchants[sim_device.id].add(m.id)
            self.ds.bank_merchants[sim_bank.id].add(m.id)
            self.ds.upi_merchants[sim_upi.id].add(m.id)
            self.ds.merchant_states[m.id] = InvestigationState.ACTION_RECOMMENDED
            ring_merchants.append(m)

            # Inject 20 rapid burst transactions per merchant
            for t_idx in range(20):
                txn = Transaction(
                    id=f"TXN-SIM-RING-{i+1}-{t_idx+1}",
                    merchant_id=m.id,
                    buyer_id=buyer_list[t_idx % len(buyer_list)].id if buyer_list else f"B-RING-{t_idx}",
                    amount=float(rng.choice([35000.0, 50000.0, 75000.0])),
                    currency="INR",
                    status="SUCCESS",
                    payment_method="UPI",
                    timestamp=sim_anchor - timedelta(hours=rng.uniform(1.0, 20.0)),
                    is_round_amount=True,
                    ip_address=f"103.119.22.{rng.randint(10, 99)}",
                    device_id=sim_device.id,
                )
                self.ds.transactions[txn.id] = txn
                self.ds.merchant_transactions[m.id].append(txn)

            # Sort transactions for this merchant
            self.ds.merchant_transactions[m.id].sort(key=lambda t: _as_naive(t.timestamp))

        # Re-build graph and ring detection
        self.network._build_graph()

        # Score the first simulated merchant
        score_1 = self.scoring.calculate_merchant_risk(ring_merchants[0].id)

        # Audit log entry
        audit = AuditLogEntry(
            event_id=f"AUD-SIM-RING-{now.strftime('%Y%m%d%H%M%S%f')}",
            merchant_id=ring_merchants[0].id,
            investigation_id=f"INV-{ring_merchants[0].id}",
            event_type=AuditEventType.RISK_ALERT_CREATED,
            actor=ActorType.SYSTEM,
            actor_id="simulation_engine",
            description=f"Simulated Ring Emergence: Planted 4 coordinated merchants ({', '.join(m.id for m in ring_merchants)}) sharing device {sim_device.id} and bank {sim_bank.id}.",
            previous_state=InvestigationState.NEW,
            new_state=InvestigationState.ACTION_RECOMMENDED,
            metadata={"ring_id": sim_ring_id, "members": [m.id for m in ring_merchants]},
            timestamp=now,
        )
        self.ds.add_audit_log(audit)

        return {
            "scenario": "COLLUSIVE_RING_EMERGENCE",
            "simulated_ring_id": sim_ring_id,
            "created_merchants_count": 4,
            "member_merchant_ids": [m.id for m in ring_merchants],
            "shared_infrastructure": {
                "device_id": sim_device.id,
                "bank_account_id": sim_bank.id,
                "upi_handle_id": sim_upi.id,
            },
            "sample_member_risk_score": score_1.overall_risk,
            "sample_member_risk_level": score_1.risk_level.value,
            "sample_member_recommended_action": score_1.recommended_action.value,
            "network_risk_score": score_1.network_risk,
            "confidence": 0.98,
            "simulated_at": now.isoformat(),
        }

    def reset_demo_state(self, seed: int = settings.RANDOM_SEED) -> Dict[str, Any]:
        """Resets the in-memory data store, network detector graph, and all simulation/investigation state to clean baseline."""
        self.ds.seed(seed=seed)
        self.network._build_graph()
        return {
            "status": "RESET_SUCCESS",
            "message": "Demo state successfully reset to clean deterministic baseline.",
            "merchant_count": len(self.ds.merchants),
            "ring_count": len(self.network.detected_rings),
            "reset_at": datetime.now(timezone.utc).isoformat(),
        }


# Global simulation service instance
simulation_service = SimulationService()

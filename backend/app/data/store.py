"""In-Memory Indexed Data Store & Graph Index for Merchant DNA."""

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Any
from app.core.config import settings
from app.core.models import (
    Merchant,
    Buyer,
    Device,
    Phone,
    BankAccount,
    UPIHandle,
    Address,
    Transaction,
    Settlement,
    Refund,
    GroundTruth,
    AnalystDecision,
    AuditLogEntry,
    AnalystFeedback,
    InvestigationState,
    EntityType,
    AppealRecord,
)
from app.data.generator import SyntheticDataGenerator


class DataStore:
    """Indexed store holding all entities, transactions, investigations, audit logs, and isolated ground truth."""

    def __init__(self, auto_seed: bool = True):
        # Entity Stores
        self.merchants: Dict[str, Merchant] = {}
        self.buyers: Dict[str, Buyer] = {}
        self.devices: Dict[str, Device] = {}
        self.phones: Dict[str, Phone] = {}
        self.bank_accounts: Dict[str, BankAccount] = {}
        self.upi_handles: Dict[str, UPIHandle] = {}
        self.addresses: Dict[str, Address] = {}

        # Activity Collections
        self.transactions: Dict[str, Transaction] = {}
        self.settlements: Dict[str, Settlement] = {}
        self.refunds: Dict[str, Refund] = {}

        # Reverse Indexes for Graph & Ring Operations
        self.merchant_transactions: Dict[str, List[Transaction]] = defaultdict(list)
        self.merchant_settlements: Dict[str, List[Settlement]] = defaultdict(list)
        self.merchant_refunds: Dict[str, List[Refund]] = defaultdict(list)
        
        # Entity to Merchants indexes
        self.device_merchants: Dict[str, Set[str]] = defaultdict(set)
        self.phone_merchants: Dict[str, Set[str]] = defaultdict(set)
        self.bank_merchants: Dict[str, Set[str]] = defaultdict(set)
        self.upi_merchants: Dict[str, Set[str]] = defaultdict(set)
        self.address_merchants: Dict[str, Set[str]] = defaultdict(set)
        self.buyer_merchants: Dict[str, Set[str]] = defaultdict(set)

        # Isolated Ground Truth Store
        self.ground_truths: Dict[str, GroundTruth] = {}

        # Investigation State & Lifecycle Store
        self.merchant_states: Dict[str, InvestigationState] = {}
        self.investigation_records: Dict[str, Any] = {}

        # Analyst Decisions & Persistent Audit Trail Store
        self.decisions: List[AnalystDecision] = []
        self.audit_log: List[AuditLogEntry] = []
        self.feedbacks: List[AnalystFeedback] = []
        self.appeals: List[AppealRecord] = []

        if auto_seed:
            self.seed(seed=settings.RANDOM_SEED)

    def seed(self, seed: int = settings.RANDOM_SEED):
        """Re-generates and indexes the synthetic dataset."""
        self.clear()
        generator = SyntheticDataGenerator(seed=seed)
        data = generator.generate_all()

        # Load Entities
        for d in data["devices"]:
            self.devices[d.id] = d
        for p in data["phones"]:
            self.phones[p.id] = p
        for ba in data["bank_accounts"]:
            self.bank_accounts[ba.id] = ba
        for u in data["upi_handles"]:
            self.upi_handles[u.id] = u
        for a in data["addresses"]:
            self.addresses[a.id] = a
        for b in data["buyers"]:
            self.buyers[b.id] = b

        # Load Merchants & Build Entity Reverse Indexes
        for m in data["merchants"]:
            self.merchants[m.id] = m
            self.merchant_states[m.id] = InvestigationState.NEW
            self.device_merchants[m.device_id].add(m.id)
            self.phone_merchants[m.phone_id].add(m.id)
            self.bank_merchants[m.bank_account_id].add(m.id)
            self.upi_merchants[m.upi_handle_id].add(m.id)
            self.address_merchants[m.address_id].add(m.id)

        # Load Activity & Build Activity Indexes
        for t in data["transactions"]:
            self.transactions[t.id] = t
            self.merchant_transactions[t.merchant_id].append(t)
            self.buyer_merchants[t.buyer_id].add(t.merchant_id)

        # Sort transactions per merchant by timestamp
        for m_id in self.merchant_transactions:
            self.merchant_transactions[m_id].sort(key=lambda tx: tx.timestamp)

        for s in data["settlements"]:
            self.settlements[s.id] = s
            self.merchant_settlements[s.merchant_id].append(s)

        for r in data["refunds"]:
            self.refunds[r.id] = r
            self.merchant_refunds[r.merchant_id].append(r)

        # Load Isolated Ground Truth
        for m_id, gt in data["ground_truths"].items():
            self.ground_truths[m_id] = gt

        # Seed Initial Realistic Appeal Recovery History
        now = datetime.now(timezone.utc)
        self.appeals = [
            AppealRecord(
                appeal_id="APL-REC-1024",
                investigation_id="INV-M-1024",
                merchant_id="M-1024",
                business_name="Sterling Jewels & Co",
                reason="High velocity spike was driven by seasonal wedding promotional campaign; verified with GST invoice.",
                contact_email="disputes@sterlingjewels.in",
                status="APPROVED_RELEASED",
                appeal_submitted_at=now,
                appeal_resolved_at=now,
                recovered_amount=1850000.0,
                resolution_time_hours=3.8,
            ),
            AppealRecord(
                appeal_id="APL-REC-1049",
                investigation_id="INV-M-1049",
                merchant_id="M-1049",
                business_name="Nova Wholesale Distributors",
                reason="B2B wholesale buyer concentration explained by single corporate procurement PO; vendor contracts attached.",
                contact_email="compliance@novawholesale.com",
                status="APPROVED_RELEASED",
                appeal_submitted_at=now,
                appeal_resolved_at=now,
                recovered_amount=990000.0,
                resolution_time_hours=4.6,
            ),
            AppealRecord(
                appeal_id="APL-REC-ALPHA-03",
                investigation_id="INV-M-ALPHA-03",
                merchant_id="M-ALPHA-03",
                business_name="Apex Luxury Timepieces",
                reason="Customer ticket size exceeds typical threshold due to vintage watch sale. Requesting urgent settlement release.",
                contact_email="accounts@apextimepieces.com",
                status="PENDING_REVIEW",
                appeal_submitted_at=now,
                appeal_resolved_at=None,
                recovered_amount=None,
                resolution_time_hours=None,
            ),
        ]

    def clear(self):
        """Clears all stored records and indexes."""
        self.merchants.clear()
        self.buyers.clear()
        self.devices.clear()
        self.phones.clear()
        self.bank_accounts.clear()
        self.upi_handles.clear()
        self.addresses.clear()
        self.transactions.clear()
        self.settlements.clear()
        self.refunds.clear()
        self.merchant_transactions.clear()
        self.merchant_settlements.clear()
        self.merchant_refunds.clear()
        self.device_merchants.clear()
        self.phone_merchants.clear()
        self.bank_merchants.clear()
        self.upi_merchants.clear()
        self.address_merchants.clear()
        self.buyer_merchants.clear()
        self.ground_truths.clear()
        self.merchant_states.clear()
        self.investigation_records.clear()
        self.decisions.clear()
        self.audit_log.clear()
        self.feedbacks.clear()
        self.appeals.clear()

    # =========================================================================
    # Merchant Query Methods
    # =========================================================================

    def get_merchant(self, merchant_id: str) -> Optional[Merchant]:
        return self.merchants.get(merchant_id)

    def get_all_merchants(self) -> List[Merchant]:
        return list(self.merchants.values())

    def get_merchant_transactions(self, merchant_id: str) -> List[Transaction]:
        return self.merchant_transactions.get(merchant_id, [])

    def get_merchant_settlements(self, merchant_id: str) -> List[Settlement]:
        return self.merchant_settlements.get(merchant_id, [])

    def get_merchant_refunds(self, merchant_id: str) -> List[Refund]:
        return self.merchant_refunds.get(merchant_id, [])

    # =========================================================================
    # Investigation Lifecycle State Methods
    # =========================================================================

    def get_merchant_state(self, merchant_id: str) -> InvestigationState:
        return self.merchant_states.get(merchant_id, InvestigationState.NEW)

    def set_merchant_state(self, merchant_id: str, state: InvestigationState):
        self.merchant_states[merchant_id] = state

    # =========================================================================
    # Entity Resolution & Cross-Merchant Relationships
    # =========================================================================

    def get_shared_merchants_by_entity(self, entity_type: EntityType, entity_id: str) -> Set[str]:
        if entity_type == EntityType.DEVICE:
            return self.device_merchants.get(entity_id, set())
        elif entity_type == EntityType.PHONE:
            return self.phone_merchants.get(entity_id, set())
        elif entity_type == EntityType.BANK_ACCOUNT:
            return self.bank_merchants.get(entity_id, set())
        elif entity_type == EntityType.UPI_HANDLE:
            return self.upi_merchants.get(entity_id, set())
        elif entity_type == EntityType.ADDRESS:
            return self.address_merchants.get(entity_id, set())
        elif entity_type == EntityType.BUYER:
            return self.buyer_merchants.get(entity_id, set())
        return set()

    def get_merchant_shared_identifiers(self, merchant_id: str) -> Dict[str, Any]:
        m = self.get_merchant(merchant_id)
        if not m:
            return {}

        connected_by_dev = self.device_merchants.get(m.device_id, set()) - {merchant_id}
        connected_by_phone = self.phone_merchants.get(m.phone_id, set()) - {merchant_id}
        connected_by_bank = self.bank_merchants.get(m.bank_account_id, set()) - {merchant_id}
        connected_by_upi = self.upi_merchants.get(m.upi_handle_id, set()) - {merchant_id}
        connected_by_addr = self.address_merchants.get(m.address_id, set()) - {merchant_id}

        all_co_linked = connected_by_dev | connected_by_phone | connected_by_bank | connected_by_upi | connected_by_addr

        return {
            "merchant_id": merchant_id,
            "device": {"id": m.device_id, "shared_with": list(connected_by_dev)},
            "phone": {"id": m.phone_id, "shared_with": list(connected_by_phone)},
            "bank_account": {"id": m.bank_account_id, "shared_with": list(connected_by_bank)},
            "upi_handle": {"id": m.upi_handle_id, "shared_with": list(connected_by_upi)},
            "address": {"id": m.address_id, "shared_with": list(connected_by_addr)},
            "total_co_linked_merchants": len(all_co_linked),
            "co_linked_merchant_ids": list(all_co_linked),
        }

    # =========================================================================
    # Isolated Ground Truth Methods
    # =========================================================================

    def get_ground_truth(self, merchant_id: str) -> Optional[GroundTruth]:
        return self.ground_truths.get(merchant_id)

    def get_all_ground_truths(self) -> Dict[str, GroundTruth]:
        return dict(self.ground_truths)

    # =========================================================================
    # Decision, Audit Trail & Feedback Methods
    # =========================================================================

    def record_decision(self, decision: AnalystDecision):
        self.decisions.append(decision)

    def get_merchant_decisions(self, merchant_id: str) -> List[AnalystDecision]:
        return [d for d in self.decisions if d.merchant_id == merchant_id]

    def get_all_decisions(self) -> List[AnalystDecision]:
        return list(self.decisions)

    def add_audit_log(self, entry: AuditLogEntry):
        self.audit_log.append(entry)

    def get_audit_log(self, merchant_id: Optional[str] = None, investigation_id: Optional[str] = None) -> List[AuditLogEntry]:
        if investigation_id:
            return [e for e in self.audit_log if e.investigation_id == investigation_id]
        if merchant_id:
            return [e for e in self.audit_log if e.merchant_id == merchant_id]
        return list(self.audit_log)

    def add_feedback(self, feedback: AnalystFeedback):
        self.feedbacks.append(feedback)

    def get_all_feedback(self) -> List[AnalystFeedback]:
        return list(self.feedbacks)

    def get_merchant_feedback(self, merchant_id: str) -> List[AnalystFeedback]:
        return [f for f in self.feedbacks if f.merchant_id == merchant_id]

    # =========================================================================
    # Appeal & False-Positive Recovery Methods
    # =========================================================================

    def add_appeal(self, appeal: AppealRecord):
        self.appeals.append(appeal)

    def get_all_appeals(self) -> List[AppealRecord]:
        return list(self.appeals)

    def get_merchant_appeals(self, merchant_id: str) -> List[AppealRecord]:
        return [a for a in self.appeals if a.merchant_id == merchant_id]

    def get_appeal(self, appeal_id: str) -> Optional[AppealRecord]:
        return next((a for a in self.appeals if a.appeal_id == appeal_id), None)


# Global Store Singleton instance
store = DataStore(auto_seed=True)


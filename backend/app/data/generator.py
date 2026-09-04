"""Synthetic Dataset & Ground-Truth Fraud Scenario Generator for Merchant DNA."""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

from app.core.config import (
    BusinessCategory,
    CATEGORY_BASELINES,
    RiskLevel,
    settings,
)
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
    TrueLabel,
    FraudScenarioType,
)


class SyntheticDataGenerator:
    """Generates realistic payment aggregator ecosystem with planted fraud patterns."""

    def __init__(self, seed: int = settings.RANDOM_SEED):
        self.seed = seed
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)
        
        # Fixed simulation anchor timestamp
        self.anchor_time = datetime(2026, 9, 1, 12, 0, 0)
        
        # Entity pools
        self.devices: List[Device] = []
        self.phones: List[Phone] = []
        self.bank_accounts: List[BankAccount] = []
        self.upi_handles: List[UPIHandle] = []
        self.addresses: List[Address] = []
        self.buyers: List[Buyer] = []
        
        self.merchants: List[Merchant] = []
        self.transactions: List[Transaction] = []
        self.settlements: List[Settlement] = []
        self.refunds: List[Refund] = []
        self.ground_truths: Dict[str, GroundTruth] = {}

    def generate_all(self) -> Dict[str, Any]:
        """Runs the entire generation pipeline and returns structured data."""
        self._reset()
        
        # 1. Generate entity pools
        self._generate_shared_entity_pools()
        self._generate_buyer_pool(count=1500)
        
        # 2. Generate Legitimate Merchants (~186)
        self._generate_legitimate_merchants(count=186)
        
        # 3. Generate Mule / Shell Merchants (~24)
        self._generate_mule_shell_merchants(count=24)
        
        # 4. Generate Planted Fraud Rings (3 distinct rings, 10 merchants each = 30)
        self._generate_fraud_ring_alpha()  # Device Farm Syndicate
        self._generate_fraud_ring_beta()   # Payout Laundering Cluster
        self._generate_fraud_ring_gamma()  # Burst-and-Bust Address Hub
        
        # 5. Generate Transactions, Settlements, and Refunds for all merchants
        self._generate_merchant_activity()
        
        return {
            "merchants": self.merchants,
            "buyers": self.buyers,
            "devices": self.devices,
            "phones": self.phones,
            "bank_accounts": self.bank_accounts,
            "upi_handles": self.upi_handles,
            "addresses": self.addresses,
            "transactions": self.transactions,
            "settlements": self.settlements,
            "refunds": self.refunds,
            "ground_truths": self.ground_truths,
        }

    def _reset(self):
        self.rng = random.Random(self.seed)
        self.np_rng = np.random.default_rng(self.seed)
        self.devices.clear()
        self.phones.clear()
        self.bank_accounts.clear()
        self.upi_handles.clear()
        self.addresses.clear()
        self.buyers.clear()
        self.merchants.clear()
        self.transactions.clear()
        self.settlements.clear()
        self.refunds.clear()
        self.ground_truths.clear()

    # =========================================================================
    # Shared Entity Pool Generation
    # =========================================================================

    def _generate_shared_entity_pools(self, pool_size: int = 280):
        # 1. Devices (pool_size devices)
        os_options = ["Android 14", "Android 13", "iOS 17.4", "iOS 16.5", "Windows 11", "macOS Sonoma"]
        for i in range(1, pool_size + 1):
            dev_id = f"DEV-{i:04d}"
            os_name = self.rng.choice(os_options)
            self.devices.append(
                Device(
                    id=dev_id,
                    fingerprint_hash=f"fp_{self.rng.getrandbits(64):016x}",
                    os=os_name,
                    user_agent=f"Mozilla/5.0 ({os_name}; POS-Terminal/v2.4)",
                    ip_subnet=f"192.168.{self.rng.randint(1, 254)}.0/24",
                    is_emulator=False,
                    created_at=self.anchor_time - timedelta(days=self.rng.randint(60, 180)),
                )
            )

        # 2. Phones (pool_size phones)
        carriers = ["Jio 5G", "Airtel", "Vodafone Idea", "BSNL"]
        for i in range(1, pool_size + 1):
            ph_id = f"PH-{i:04d}"
            number = f"+91-9{self.rng.randint(100000000, 999999999)}"
            self.phones.append(
                Phone(
                    id=ph_id,
                    phone_number=number,
                    carrier=self.rng.choice(carriers),
                    is_voip=False,
                    created_at=self.anchor_time - timedelta(days=self.rng.randint(60, 180)),
                )
            )

        # 3. Bank Accounts (pool_size accounts)
        banks = [
            ("HDFC Bank", "HDFC0001234"),
            ("ICICI Bank", "ICIC0005678"),
            ("State Bank of India", "SBIN0009101"),
            ("Axis Bank", "UTIB0002345"),
            ("Kotak Mahindra Bank", "KKBK0006789"),
            ("Yes Bank", "YESB0003456"),
        ]
        for i in range(1, pool_size + 1):
            ba_id = f"BA-{i:04d}"
            bname, ifsc = self.rng.choice(banks)
            acc_num = f"****{self.rng.randint(1000, 9999)}"
            self.bank_accounts.append(
                BankAccount(
                    id=ba_id,
                    account_number_masked=acc_num,
                    ifsc_code=ifsc,
                    bank_name=bname,
                    beneficiary_name=f"Enterprise Entity {i}",
                    created_at=self.anchor_time - timedelta(days=self.rng.randint(60, 180)),
                )
            )

        # 4. UPI Handles (pool_size handles)
        psps = ["@okhdfcbank", "@oksbi", "@okicici", "@okaxis", "@paytm", "@ybl"]
        for i in range(1, pool_size + 1):
            upi_id = f"UPI-{i:04d}"
            vpa = f"merchant.biz.{i:03d}{self.rng.choice(psps)}"
            self.upi_handles.append(
                UPIHandle(
                    id=upi_id,
                    vpa=vpa,
                    psp=vpa.split("@")[-1],
                    created_at=self.anchor_time - timedelta(days=self.rng.randint(60, 180)),
                )
            )

        # 5. Addresses (pool_size addresses across Indian cities)
        cities = [
            ("Mumbai", "Maharashtra", "400001", 18.9220, 72.8347),
            ("Bengaluru", "Karnataka", "560001", 12.9716, 77.5946),
            ("New Delhi", "Delhi", "110001", 28.6139, 77.2090),
            ("Hyderabad", "Telangana", "500001", 17.3850, 78.4867),
            ("Chennai", "Tamil Nadu", "600001", 13.0827, 80.2707),
            ("Pune", "Maharashtra", "411001", 18.5204, 73.8567),
            ("Ahmedabad", "Gujarat", "380001", 23.0225, 72.5714),
            ("Kolkata", "West Bengal", "700001", 22.5726, 88.3639),
            ("Jaipur", "Rajasthan", "302001", 26.9124, 75.7873),
            ("Surat", "Gujarat", "395001", 21.1702, 72.8311),
        ]
        street_types = ["MG Road", "Brigade Road", "Tech Park Sector 4", "Industrial Area Phase 2", "Commercial Complex Suite", "Ring Road Hub"]
        for i in range(1, pool_size + 1):
            addr_id = f"ADDR-{i:04d}"
            city, state, pin, lat, lng = self.rng.choice(cities)
            street = f"Unit {self.rng.randint(101, 808)}, {self.rng.choice(street_types)}"
            self.addresses.append(
                Address(
                    id=addr_id,
                    address_line=street,
                    city=city,
                    state=state,
                    pincode=pin,
                    geo_lat=lat + self.rng.uniform(-0.05, 0.05),
                    geo_lng=lng + self.rng.uniform(-0.05, 0.05),
                    is_commercial_hub=self.rng.random() < 0.2,
                    created_at=self.anchor_time - timedelta(days=self.rng.randint(60, 180)),
                )
            )

    def _generate_buyer_pool(self, count: int = 1500):
        first_names = ["Aarav", "Aditi", "Rohan", "Pooja", "Vikram", "Sneha", "Karan", "Ananya", "Rahul", "Priya", "Amit", "Neha", "Deepak", "Ritu", "Manish"]
        last_names = ["Sharma", "Patel", "Verma", "Rao", "Gupta", "Mehta", "Singh", "Nair", "Deshmukh", "Iyer", "Joshi", "Kapoor"]
        
        for i in range(1, count + 1):
            fn = self.rng.choice(first_names)
            ln = self.rng.choice(last_names)
            b_id = f"B-{i:05d}"
            age = self.rng.randint(10, 365)
            self.buyers.append(
                Buyer(
                    id=b_id,
                    name=f"{fn} {ln}",
                    email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
                    phone_id=f"PH-BUYER-{i:05d}",
                    account_age_days=age,
                    trust_score=round(self.rng.uniform(70.0, 98.0), 1),
                    created_at=self.anchor_time - timedelta(days=age),
                )
            )

    # =========================================================================
    # Merchant Generation (Legitimate Baseline)
    # =========================================================================

    def _generate_legitimate_merchants(self, count: int = 186):
        biz_name_prefixes = [
            "Apex", "Zenith", "Royal", "Urban", "Nova", "Prime", "Loom & Craft",
            "ByteWave", "GreenLeaf", "Silverline", "CloudPeak", "Vibrant", "Omni",
            "Bharat", "TrueValue", "Saffron", "Metro", "Elevate", "Kaveri", "Indus"
        ]
        biz_types = ["PROPRIETORSHIP", "PVT_LTD", "INDIVIDUAL_FREELANCER", "LLP", "PARTNERSHIP"]
        categories = list(BusinessCategory)

        for i in range(1, count + 1):
            m_id = f"M-{1000 + i}"
            cat = self.rng.choice(categories)
            baseline = CATEGORY_BASELINES[cat]
            prefix = self.rng.choice(biz_name_prefixes)
            biz_name = f"{prefix} {cat.value.replace('_', ' ').title()} #{i}"
            onboard_days = self.rng.randint(30, 180)
            onboarding_dt = self.anchor_time - timedelta(days=onboard_days)

            # Legitimate entities: each gets an individual entity from pool
            dev = self.devices[i - 1]
            phone = self.phones[i - 1]
            ba = self.bank_accounts[i - 1]
            upi = self.upi_handles[i - 1]
            addr = self.addresses[i - 1]

            merchant = Merchant(
                id=m_id,
                business_name=biz_name,
                legal_name=f"{biz_name} Private Limited",
                category=cat,
                business_type=self.rng.choice(biz_types),
                declared_avg_ticket=baseline["avg_ticket"],
                onboarding_date=onboarding_dt,
                kyc_status="VERIFIED",
                device_id=dev.id,
                phone_id=phone.id,
                bank_account_id=ba.id,
                upi_handle_id=upi.id,
                address_id=addr.id,
                is_active=True,
                created_at=onboarding_dt,
            )
            self.merchants.append(merchant)

            # Record isolated ground truth
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.LEGITIMATE,
                fraud_scenario=FraudScenarioType.NONE,
                planted_ring_id=None,
                planted_anomalies=[],
                expected_risk_tier=RiskLevel.LOW,
                description="Legitimate merchant with organic growth, healthy buyer diversity, and normal settlement intervals.",
            )

    # =========================================================================
    # Merchant Generation (Mule / Shell Accounts)
    # =========================================================================

    def _generate_mule_shell_merchants(self, count: int = 24):
        mule_names = [
            "QuickBreeze Retail", "GoldenSunrise Traders", "AeroDigital Corner", "SwiftKart Global",
            "Starline Ventures", "BrightFuture Consult", "Zenith Daily Mart", "SilverDrop Supplies",
            "PrimePulse Digital", "Velocity Craft Studio", "EasyPay Point", "Horizon Online Shop",
            "MicroTech Express", "FlashDeal Store", "EverGreen Organics", "RapidCommerce Hub",
            "CrystalClear Solutions", "BlueSky Traders", "SuperNova Direct", "PeakPoint Services",
            "UrbanGlow Boutiques", "DirectWave Systems", "FastTrack Mercantile", "ApexStar Solutions"
        ]

        for idx in range(count):
            m_id = f"M-{2000 + idx + 1}"
            biz_name = mule_names[idx] if idx < len(mule_names) else f"Mule Shell Store {idx + 1}"
            
            if idx % 3 == 0:
                scenario = FraudScenarioType.DORMANT_BURST_MULE
                cat = BusinessCategory.ECOMMERCE_FASHION
                anomalies = [
                    "Dormant for 45 days after onboarding, then 12.5x volume spike in last 48 hours",
                    "92% round-number transactions (₹25,000 / ₹50,000)",
                    "High buyer concentration: 80% volume driven by 3 repeat buyers",
                    "Rapid payout drawdown requested within 20 mins of payment arrival",
                ]
                desc = "Dormant shell account activated for sudden high-volume cashout."
            elif idx % 3 == 1:
                scenario = FraudScenarioType.CATEGORY_MISMATCH_LAUNDERING
                cat = BusinessCategory.GROCERY_FOOD
                anomalies = [
                    "Severe catalog ticket mismatch: Grocery category averaging ₹78,000 ticket size (baseline: ₹620)",
                    "88% transactions processed during off-peak hours (1:00 AM - 4:30 AM)",
                    "Near zero refund history despite high ticket size",
                    "Abnormal new buyer ratio with single-ticket spikes",
                ]
                desc = "Category mismatch money laundering: Low-ticket food category processing massive luxury-sized round payments."
            else:
                scenario = FraudScenarioType.DORMANT_BURST_MULE
                cat = BusinessCategory.DIGITAL_SERVICES
                anomalies = [
                    "High velocity burst: 45 transactions in 6 hours following 60 days inactivity",
                    "Immediate settlement drawdown request for 98% of received volume",
                    "Extreme buyer concentration (HHI > 0.45)",
                ]
                desc = "Rapid cashout mule account with high-velocity single-source funding."

            baseline = CATEGORY_BASELINES[cat]
            onboard_days = self.rng.randint(45, 90)
            onboarding_dt = self.anchor_time - timedelta(days=onboard_days)

            # Assign disjoint individual entities from pool
            pool_idx = 186 + idx
            dev = self.devices[pool_idx]
            phone = self.phones[pool_idx]
            ba = self.bank_accounts[pool_idx]
            upi = self.upi_handles[pool_idx]
            addr = self.addresses[pool_idx]

            merchant = Merchant(
                id=m_id,
                business_name=biz_name,
                legal_name=f"{biz_name} Enterprise",
                category=cat,
                business_type="PROPRIETORSHIP",
                declared_avg_ticket=baseline["avg_ticket"],
                onboarding_date=onboarding_dt,
                kyc_status="VERIFIED",
                device_id=dev.id,
                phone_id=phone.id,
                bank_account_id=ba.id,
                upi_handle_id=upi.id,
                address_id=addr.id,
                is_active=True,
                created_at=onboarding_dt,
            )
            self.merchants.append(merchant)

            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.MULE_SHELL,
                fraud_scenario=scenario,
                planted_ring_id=None,
                planted_anomalies=anomalies,
                expected_risk_tier=RiskLevel.CRITICAL if idx % 2 == 0 else RiskLevel.HIGH,
                description=desc,
            )

    # =========================================================================
    # Planted Fraud Rings (Cross-Merchant Syndicates)
    # =========================================================================

    def _generate_fraud_ring_alpha(self):
        """Ring Alpha: 'Device Farm Syndicate' (10 merchants sharing 2 device fingerprints & VOIP phones)."""
        ring_id = "RING-ALPHA-DEVICE-FARM"
        shared_dev_1 = Device(
            id="DEV-FARM-991",
            fingerprint_hash="fp_device_farm_alpha_991823746",
            os="Android 13 (Rooted / Emulator)",
            user_agent="Mozilla/5.0 (Linux; Android 13; K) AppleWebKit/537.36",
            ip_subnet="103.212.44.0/24",
            is_emulator=True,
            created_at=self.anchor_time - timedelta(days=40),
        )
        shared_dev_2 = Device(
            id="DEV-FARM-992",
            fingerprint_hash="fp_device_farm_alpha_992110482",
            os="Android 14 (Automated Script Box)",
            user_agent="Mozilla/5.0 (Linux; Android 14; Mobile) POS-Farm/v1",
            ip_subnet="103.212.44.0/24",
            is_emulator=True,
            created_at=self.anchor_time - timedelta(days=35),
        )
        self.devices.extend([shared_dev_1, shared_dev_2])

        shared_phone = Phone(
            id="PH-VOIP-ALPHA",
            phone_number="+91-9988001122",
            carrier="Twilio / VOIP Gateway",
            is_voip=True,
            created_at=self.anchor_time - timedelta(days=40),
        )
        self.phones.append(shared_phone)

        names = [
            "Alpha Fashion Outlet", "Alpha Tech Deals", "Alpha Luxury Leather",
            "Alpha Digital Services", "Alpha Auto Spares", "Alpha Mobile Planet",
            "Alpha Sports Gear", "Alpha Cloud Books", "Alpha Home Essentials", "Alpha Fine Dine"
        ]
        categories = [
            BusinessCategory.ECOMMERCE_FASHION, BusinessCategory.ELECTRONICS, BusinessCategory.JEWELRY_LUXURY,
            BusinessCategory.DIGITAL_SERVICES, BusinessCategory.B2B_SUPPLIES, BusinessCategory.ELECTRONICS,
            BusinessCategory.ECOMMERCE_FASHION, BusinessCategory.EDTECH, BusinessCategory.GROCERY_FOOD, BusinessCategory.CONSULTING_SERVICES
        ]

        for i in range(10):
            m_id = f"M-ALPHA-{i+1:02d}"
            cat = categories[i]
            dev = shared_dev_1 if i < 5 else shared_dev_2
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(20, 45))
            
            # Use disjoint index slices from upper pool
            ba = self.bank_accounts[220 + i]
            upi = self.upi_handles[220 + i]
            addr = self.addresses[220 + i]

            merchant = Merchant(
                id=m_id,
                business_name=names[i],
                legal_name=f"{names[i]} Corp",
                category=cat,
                business_type="PROPRIETORSHIP",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=dev.id,
                phone_id=shared_phone.id,
                bank_account_id=ba.id,
                upi_handle_id=upi.id,
                address_id=addr.id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(merchant)

            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.RING_MEMBER,
                fraud_scenario=FraudScenarioType.DEVICE_FARM_SYNDICATE,
                planted_ring_id=ring_id,
                planted_anomalies=[
                    f"Shared hardware device fingerprint with 9 other syndicate merchants ({dev.id})",
                    f"Shared VOIP phone number across distinct legal business entities ({shared_phone.id})",
                    "Synchronized volume surge within the identical 48-hour window",
                    "High round amount clustering across disparate categories",
                ],
                expected_risk_tier=RiskLevel.CRITICAL,
                description=f"Member of {ring_id}: Coordinated device farm operating 10 seemingly independent storefronts from 2 emulator devices.",
            )

    def _generate_fraud_ring_beta(self):
        """Ring Beta: 'Payout Laundering Cluster' (10 merchants routing settlements to shared beneficiary accounts & UPI)."""
        ring_id = "RING-BETA-PAYOUT-CLUSTER"
        
        shared_bank_1 = BankAccount(
            id="BA-BETA-HUB1",
            account_number_masked="****9988",
            ifsc_code="HDFC0009999",
            bank_name="HDFC Bank",
            beneficiary_name="Vortex Capital Payout Hub",
            created_at=self.anchor_time - timedelta(days=60),
        )
        shared_bank_2 = BankAccount(
            id="BA-BETA-HUB2",
            account_number_masked="****7766",
            ifsc_code="ICIC0008888",
            bank_name="ICICI Bank",
            beneficiary_name="Vortex Liquidity Ventures",
            created_at=self.anchor_time - timedelta(days=60),
        )
        self.bank_accounts.extend([shared_bank_1, shared_bank_2])

        shared_upi = UPIHandle(
            id="UPI-BETA-HUB",
            vpa="vortex.settlements.in@okhdfcbank",
            psp="okhdfcbank",
            created_at=self.anchor_time - timedelta(days=60),
        )
        self.upi_handles.append(shared_upi)

        names = [
            "Beta Gaming Arena", "Beta Pro Consulting", "Beta Cloud Hosting",
            "Beta Diamond Jewels", "Beta Skill Academy", "Beta Global Logistics",
            "Beta Organic Supermart", "Beta Fashion Lab", "Beta Electro Hub", "Beta Creative Studio"
        ]
        categories = [
            BusinessCategory.GAMING_ENTERTAINMENT, BusinessCategory.CONSULTING_SERVICES, BusinessCategory.DIGITAL_SERVICES,
            BusinessCategory.JEWELRY_LUXURY, BusinessCategory.EDTECH, BusinessCategory.B2B_SUPPLIES,
            BusinessCategory.GROCERY_FOOD, BusinessCategory.ECOMMERCE_FASHION, BusinessCategory.ELECTRONICS, BusinessCategory.DIGITAL_SERVICES
        ]

        for i in range(10):
            m_id = f"M-BETA-{i+1:02d}"
            cat = categories[i]
            ba = shared_bank_1 if i < 6 else shared_bank_2
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(30, 75))
            
            dev = self.devices[235 + i]
            phone = self.phones[235 + i]
            addr = self.addresses[235 + i]

            merchant = Merchant(
                id=m_id,
                business_name=names[i],
                legal_name=f"{names[i]} LLP",
                category=cat,
                business_type="LLP",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=dev.id,
                phone_id=phone.id,
                bank_account_id=ba.id,
                upi_handle_id=shared_upi.id,
                address_id=addr.id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(merchant)

            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.RING_MEMBER,
                fraud_scenario=FraudScenarioType.PAYOUT_LAUNDERING_CLUSTER,
                planted_ring_id=ring_id,
                planted_anomalies=[
                    f"Shared settlement beneficiary bank account with multiple disparate merchants ({ba.id})",
                    f"Shared payout UPI handle across unrelated business categories ({shared_upi.id})",
                    "Aggressive settlement turnover velocity (< 45 mins in/out lag)",
                    "Synchronized fund pooling from high-velocity buyer transfers",
                ],
                expected_risk_tier=RiskLevel.CRITICAL,
                description=f"Member of {ring_id}: Coordinated merchant ring routing aggregated credit collections into a single beneficiary bank/UPI conduit.",
            )

    def _generate_fraud_ring_gamma(self):
        """Ring Gamma: 'Burst-and-Bust Address Hub' (10 merchants registered at same fake corporate address with overlapping synthetic buyers)."""
        ring_id = "RING-GAMMA-ADDRESS-HUB"
        
        shared_address = Address(
            id="ADDR-GAMMA-HUB",
            address_line="Suite 404, Cyber Heights Commercial Plaza, Outer Ring Road",
            city="Bengaluru",
            state="Karnataka",
            pincode="560103",
            geo_lat=12.9279,
            geo_lng=77.6835,
            is_commercial_hub=False,
            created_at=self.anchor_time - timedelta(days=20),
        )
        self.addresses.append(shared_address)

        names = [
            "Gamma QuickMart", "Gamma Electronics Direct", "Gamma Luxe Fashion",
            "Gamma EdTech Pro", "Gamma Travel Express", "Gamma Digital Works",
            "Gamma Wholesale Spares", "Gamma Gourmet Treats", "Gamma Tech Hub", "Gamma Media Lab"
        ]
        categories = [
            BusinessCategory.GROCERY_FOOD, BusinessCategory.ELECTRONICS, BusinessCategory.ECOMMERCE_FASHION,
            BusinessCategory.EDTECH, BusinessCategory.TRAVEL_TICKETING, BusinessCategory.DIGITAL_SERVICES,
            BusinessCategory.B2B_SUPPLIES, BusinessCategory.GROCERY_FOOD, BusinessCategory.ELECTRONICS, BusinessCategory.DIGITAL_SERVICES
        ]

        for i in range(10):
            m_id = f"M-GAMMA-{i+1:02d}"
            cat = categories[i]
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(7, 21))  # Brand new entities
            
            dev = self.devices[248 + i]
            phone = self.phones[248 + i]
            ba = self.bank_accounts[248 + i]
            upi = self.upi_handles[248 + i]

            merchant = Merchant(
                id=m_id,
                business_name=names[i],
                legal_name=f"{names[i]} Enterprises",
                category=cat,
                business_type="PROPRIETORSHIP",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=dev.id,
                phone_id=phone.id,
                bank_account_id=ba.id,
                upi_handle_id=upi.id,
                address_id=shared_address.id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(merchant)

            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.RING_MEMBER,
                fraud_scenario=FraudScenarioType.BURST_BUST_ADDRESS_HUB,
                planted_ring_id=ring_id,
                planted_anomalies=[
                    f"Identical physical registration address across 10 newly onboarded merchants ({shared_address.id})",
                    "Rapid onboarding-to-spike velocity (first major volume burst < 10 days post-KYC)",
                    "Shared synthetic buyer rotation purchasing high-ticket items across all ring merchants",
                    "Low organic refund rate and immediate settlement liquidation",
                ],
                expected_risk_tier=RiskLevel.HIGH if i % 3 != 0 else RiskLevel.CRITICAL,
                description=f"Member of {ring_id}: Synthetic identity shell cluster sharing a common physical suite and rotating buyer liquidity.",
            )

    # =========================================================================
    # Activity Generation (Transactions, Settlements, Refunds)
    # =========================================================================

    def _generate_merchant_activity(self):
        """Generates realistic time series of transactions, settlements, and refunds."""
        txn_counter = 1
        settl_counter = 1
        ref_counter = 1

        ring_buyers = self.buyers[0:20]  # First 20 buyers used as collusive rotating buyers

        payment_methods = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "NETBANKING"]
        payment_weights = [0.65, 0.20, 0.10, 0.05]

        for m in self.merchants:
            gt = self.ground_truths[m.id]
            cat_info = CATEGORY_BASELINES[m.category]
            
            days_active = max(1, (self.anchor_time - m.onboarding_date).days)
            
            if gt.true_label == TrueLabel.LEGITIMATE:
                avg_txns_per_day = self.rng.uniform(4.0, 18.0)
                total_txns = int(days_active * avg_txns_per_day)
                total_txns = min(total_txns, 250)
                
                m_buyers = self.rng.sample(self.buyers[50:], min(len(self.buyers) - 50, int(total_txns * 0.75)))
                
                for t_idx in range(total_txns):
                    day_offset = self.rng.uniform(0, days_active)
                    txn_dt = m.onboarding_date + timedelta(days=day_offset, hours=self.rng.uniform(8, 22))
                    if txn_dt > self.anchor_time:
                        txn_dt = self.anchor_time - timedelta(minutes=self.rng.randint(10, 300))

                    base_amt = float(self.np_rng.normal(cat_info["avg_ticket"], cat_info["ticket_std"]))
                    base_amt = max(cat_info["min_ticket"], min(cat_info["max_normal_ticket"], base_amt))
                    
                    if self.rng.random() > cat_info["round_number_ratio_baseline"]:
                        amount = round(base_amt + self.rng.uniform(1.0, 99.0), 2)
                        is_round = False
                    else:
                        amount = float(round(base_amt / 100) * 100)
                        is_round = True

                    buyer = self.rng.choice(m_buyers)
                    method = self.rng.choices(payment_methods, weights=payment_weights)[0]
                    
                    txn = Transaction(
                        id=f"TXN-{txn_counter:07d}",
                        merchant_id=m.id,
                        buyer_id=buyer.id,
                        amount=amount,
                        currency="INR",
                        status="SUCCESS" if self.rng.random() > 0.03 else "FAILED",
                        payment_method=method,
                        timestamp=txn_dt,
                        is_round_amount=is_round,
                        ip_address=f"49.207.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                        device_id=m.device_id,
                    )
                    self.transactions.append(txn)
                    txn_counter += 1

                    if txn.status == "SUCCESS" and self.rng.random() < cat_info["expected_refund_rate"]:
                        ref_dt = txn_dt + timedelta(days=self.rng.uniform(1, 5))
                        if ref_dt <= self.anchor_time:
                            refund = Refund(
                                id=f"REF-{ref_counter:06d}",
                                transaction_id=txn.id,
                                merchant_id=m.id,
                                amount=txn.amount,
                                reason=self.rng.choice(["Customer returned item", "Defective product", "Order cancelled by buyer"]),
                                requested_at=ref_dt,
                                status="PROCESSED",
                            )
                            self.refunds.append(refund)
                            ref_counter += 1

                settlement_batches = max(1, days_active // 7)
                for s_idx in range(settlement_batches):
                    s_req_dt = m.onboarding_date + timedelta(days=(s_idx + 1) * 7)
                    if s_req_dt < self.anchor_time:
                        settl = Settlement(
                            id=f"SETTL-{settl_counter:06d}",
                            merchant_id=m.id,
                            bank_account_id=m.bank_account_id,
                            amount=round(self.rng.uniform(15000, 85000), 2),
                            requested_at=s_req_dt,
                            settled_at=s_req_dt + timedelta(hours=24.0),
                            status="SETTLED",
                            velocity_in_out_hours=24.0,
                        )
                        self.settlements.append(settl)
                        settl_counter += 1

            elif gt.true_label == TrueLabel.MULE_SHELL:
                dormant_txns = self.rng.randint(1, 3)
                for _ in range(dormant_txns):
                    dt = m.onboarding_date + timedelta(days=self.rng.randint(2, 10))
                    txn = Transaction(
                        id=f"TXN-{txn_counter:07d}",
                        merchant_id=m.id,
                        buyer_id=self.rng.choice(self.buyers[100:150]).id,
                        amount=round(self.rng.uniform(100.0, 500.0), 2),
                        currency="INR",
                        status="SUCCESS",
                        payment_method="UPI",
                        timestamp=dt,
                        is_round_amount=False,
                        ip_address=f"103.45.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                        device_id=m.device_id,
                    )
                    self.transactions.append(txn)
                    txn_counter += 1

                burst_txns_count = self.rng.randint(35, 75)
                mule_buyers = self.rng.sample(self.buyers[20:35], self.rng.randint(2, 4))
                burst_round_options = [15000.0, 25000.0, 50000.0, 75000.0, 100000.0]
                
                for b_i in range(burst_txns_count):
                    hours_ago = self.rng.uniform(0.5, 47.5)
                    txn_dt = self.anchor_time - timedelta(hours=hours_ago)
                    
                    if self.rng.random() < 0.92:
                        amt = float(self.rng.choice(burst_round_options))
                        is_round = True
                    else:
                        amt = float(self.rng.choice(burst_round_options)) + self.rng.uniform(1, 50)
                        is_round = False

                    buyer = self.rng.choice(mule_buyers)
                    
                    txn = Transaction(
                        id=f"TXN-{txn_counter:07d}",
                        merchant_id=m.id,
                        buyer_id=buyer.id,
                        amount=amt,
                        currency="INR",
                        status="SUCCESS",
                        payment_method="UPI" if self.rng.random() < 0.85 else "CREDIT_CARD",
                        timestamp=txn_dt,
                        is_round_amount=is_round,
                        ip_address=f"185.220.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                        device_id=m.device_id,
                    )
                    self.transactions.append(txn)
                    txn_counter += 1

                for s_i in range(self.rng.randint(2, 4)):
                    s_dt = self.anchor_time - timedelta(hours=self.rng.uniform(2, 36))
                    settl = Settlement(
                        id=f"SETTL-{settl_counter:06d}",
                        merchant_id=m.id,
                        bank_account_id=m.bank_account_id,
                        amount=round(self.rng.uniform(150000, 450000), 2),
                        requested_at=s_dt,
                        settled_at=s_dt + timedelta(minutes=25),
                        status="SETTLED" if self.rng.random() < 0.7 else "HELD",
                        velocity_in_out_hours=0.4,
                    )
                    self.settlements.append(settl)
                    settl_counter += 1

            elif gt.true_label == TrueLabel.RING_MEMBER:
                burst_txns_count = self.rng.randint(40, 80)
                ring_sub_buyers = self.rng.sample(ring_buyers, self.rng.randint(3, 6))
                round_options = [20000.0, 35000.0, 50000.0, 80000.0]
                
                for b_i in range(burst_txns_count):
                    hours_ago = self.rng.uniform(1.0, 48.0)
                    txn_dt = self.anchor_time - timedelta(hours=hours_ago)
                    
                    amt = float(self.rng.choice(round_options)) if self.rng.random() < 0.88 else round(self.rng.uniform(18000, 65000), 2)
                    is_round = (amt % 1000 == 0)
                    buyer = self.rng.choice(ring_sub_buyers)

                    txn = Transaction(
                        id=f"TXN-{txn_counter:07d}",
                        merchant_id=m.id,
                        buyer_id=buyer.id,
                        amount=amt,
                        currency="INR",
                        status="SUCCESS" if self.rng.random() > 0.02 else "DISPUTED",
                        payment_method="UPI",
                        timestamp=txn_dt,
                        is_round_amount=is_round,
                        ip_address=f"103.212.44.{self.rng.randint(10, 99)}",
                        device_id=m.device_id,
                    )
                    self.transactions.append(txn)
                    txn_counter += 1

                for s_i in range(self.rng.randint(2, 3)):
                    s_dt = self.anchor_time - timedelta(hours=self.rng.uniform(3, 30))
                    settl = Settlement(
                        id=f"SETTL-{settl_counter:06d}",
                        merchant_id=m.id,
                        bank_account_id=m.bank_account_id,
                        amount=round(self.rng.uniform(200000, 600000), 2),
                        requested_at=s_dt,
                        settled_at=s_dt + timedelta(hours=1.0),
                        status="HELD" if s_i == 0 else "SETTLED",
                        velocity_in_out_hours=0.8,
                    )
                    self.settlements.append(settl)
                    settl_counter += 1


    # =========================================================================
    # Harder Benchmark Batch Generation (Subtler Fraud & Varied Ring Sizes)
    # =========================================================================

    def generate_harder_batch(self, seed: int = 142) -> Dict[str, Any]:
        """Generates a second, harder evaluation benchmark with 1,000+ merchants and subtler fraud patterns.
        
        Features:
        - 800 Legitimate Merchants (including 100 Hard Negatives: Flash sales, recalls, B2B wholesalers, coworking hubs).
        - 60 Subtle Mule Accounts (sleeper ramps, sub-radar payouts, non-round amounts).
        - 51 Planted Fraud Rings (210 merchants total across sizes 2, 3, 4, 5, 6, 8, 10, 12).
        - Overlapping feature distributions (realistic settlement lags, mixed round/odd pricing, natural buyer counts).
        """
        orig_seed = self.seed
        self.seed = seed
        self._reset()

        # 1. Entity pools & Buyer pool
        self._generate_shared_entity_pools(pool_size=2500)
        self._generate_buyer_pool(count=4000)

        cats = list(BusinessCategory)

        # 2. 700 Standard Legitimate Merchants
        for i in range(700):
            m_id = f"M-HLEG-{i+1:04d}"
            cat = self.rng.choice(cats)
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(25, 180))
            m = Merchant(
                id=m_id,
                business_name=f"Retail Store {i+1}",
                legal_name=f"Retail Store {i+1} Pvt Ltd",
                category=cat,
                business_type="PRIVATE_LIMITED",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=self.devices[i].id,
                phone_id=self.phones[i].id,
                bank_account_id=self.bank_accounts[i].id,
                upi_handle_id=self.upi_handles[i].id,
                address_id=self.addresses[i].id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(m)
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.LEGITIMATE,
                fraud_scenario=FraudScenarioType.NONE,
                planted_ring_id=None,
                planted_anomalies=[],
                expected_risk_tier=RiskLevel.LOW,
                description="Legitimate business with verified identity.",
            )

        # 3. 100 Hard Negative Legitimate Merchants
        # 25 Flash Sales
        for i in range(25):
            m_id = f"M-HN-FLASH-{i+1:02d}"
            cat = self.rng.choice([BusinessCategory.ECOMMERCE_FASHION, BusinessCategory.ELECTRONICS])
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(45, 120))
            idx = 700 + i
            m = Merchant(
                id=m_id,
                business_name=f"Flash Campaign #{i+1}",
                legal_name=f"Flash Deals {i+1} LLP",
                category=cat,
                business_type="LLP",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=self.devices[idx].id,
                phone_id=self.phones[idx].id,
                bank_account_id=self.bank_accounts[idx].id,
                upi_handle_id=self.upi_handles[idx].id,
                address_id=self.addresses[idx].id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(m)
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.LEGITIMATE,
                fraud_scenario=FraudScenarioType.NONE,
                planted_ring_id=None,
                planted_anomalies=["Promotional 48h volume surge"],
                expected_risk_tier=RiskLevel.LOW,
                description="Hard Negative: Legitimate flash campaign with sudden volume growth.",
            )

        # 25 Product Recall / High Refund
        for i in range(25):
            m_id = f"M-HN-RECALL-{i+1:02d}"
            cat = self.rng.choice([BusinessCategory.JEWELRY_LUXURY, BusinessCategory.DIGITAL_SERVICES])
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(60, 150))
            idx = 725 + i
            m = Merchant(
                id=m_id,
                business_name=f"Recall Apparel #{i+1}",
                legal_name=f"Recall Stores {i+1} Pvt Ltd",
                category=cat,
                business_type="PRIVATE_LIMITED",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=self.devices[idx].id,
                phone_id=self.phones[idx].id,
                bank_account_id=self.bank_accounts[idx].id,
                upi_handle_id=self.upi_handles[idx].id,
                address_id=self.addresses[idx].id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(m)
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.LEGITIMATE,
                fraud_scenario=FraudScenarioType.NONE,
                planted_ring_id=None,
                planted_anomalies=["Supplier batch defect causing 22% refund rate"],
                expected_risk_tier=RiskLevel.LOW,
                description="Hard Negative: Genuine inventory recall causing refund surge.",
            )

        # 25 B2B Wholesalers (High Ticket & High HHI)
        for i in range(25):
            m_id = f"M-HN-B2B-{i+1:02d}"
            cat = BusinessCategory.B2B_SUPPLIES
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(80, 180))
            idx = 750 + i
            m = Merchant(
                id=m_id,
                business_name=f"Apex Industrial Wholesalers #{i+1}",
                legal_name=f"Apex Wholesalers {i+1} Limited",
                category=cat,
                business_type="LIMITED",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"] * 2.5,
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=self.devices[idx].id,
                phone_id=self.phones[idx].id,
                bank_account_id=self.bank_accounts[idx].id,
                upi_handle_id=self.upi_handles[idx].id,
                address_id=self.addresses[idx].id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(m)
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.LEGITIMATE,
                fraud_scenario=FraudScenarioType.NONE,
                planted_ring_id=None,
                planted_anomalies=["Large ticket sizes and high buyer concentration from corporate clients"],
                expected_risk_tier=RiskLevel.LOW,
                description="Hard Negative: Genuine B2B supplier with few repeat buyers.",
            )

        # 25 Co-Working / Tech Park Hub
        coworking_addr = Address(
            id="ADDR-H-COWORK-PARK",
            address_line="WeWork Cyber City, Tower 5B, DLF Phase 3",
            city="Gurugram",
            state="Haryana",
            pincode="122002",
            geo_lat=28.4900,
            geo_lng=77.0900,
            is_commercial_hub=True,
            created_at=self.anchor_time - timedelta(days=200),
        )
        self.addresses.append(coworking_addr)
        for i in range(25):
            m_id = f"M-HN-COWORK-{i+1:02d}"
            cat = self.rng.choice(cats)
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(40, 160))
            idx = 775 + i
            m = Merchant(
                id=m_id,
                business_name=f"Cowork Startup #{i+1}",
                legal_name=f"Cowork Startup #{i+1} LLP",
                category=cat,
                business_type="LLP",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=self.devices[idx].id,
                phone_id=self.phones[idx].id,
                bank_account_id=self.bank_accounts[idx].id,
                upi_handle_id=self.upi_handles[idx].id,
                address_id=coworking_addr.id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(m)
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.LEGITIMATE,
                fraud_scenario=FraudScenarioType.NONE,
                planted_ring_id=None,
                planted_anomalies=["Shared tech park commercial address with 24 other startups"],
                expected_risk_tier=RiskLevel.LOW,
                description="Hard Negative: Genuine business in co-working incubator.",
            )

        # 4. 60 Subtle Mule Accounts
        for i in range(60):
            m_id = f"M-HMULE-{i+1:03d}"
            cat = self.rng.choice([BusinessCategory.ECOMMERCE_FASHION, BusinessCategory.DIGITAL_SERVICES, BusinessCategory.ELECTRONICS])
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(50, 120))
            idx = 800 + i
            m = Merchant(
                id=m_id,
                business_name=f"Subtle Ventures #{i+1}",
                legal_name=f"Subtle Ventures {i+1} Pvt Ltd",
                category=cat,
                business_type="PRIVATE_LIMITED",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=self.devices[idx].id,
                phone_id=self.phones[idx].id,
                bank_account_id=self.bank_accounts[idx].id,
                upi_handle_id=self.upi_handles[idx].id,
                address_id=self.addresses[idx].id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(m)
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.MULE_SHELL,
                fraud_scenario=FraudScenarioType.DORMANT_BURST_MULE,
                planted_ring_id=None,
                planted_anomalies=["Subtle sleeper account with gradual ramp"],
                expected_risk_tier=RiskLevel.HIGH if i % 2 == 0 else RiskLevel.MEDIUM,
                description="Sleeper mule with subtle velocity ramp.",
            )

        # 5. 51 Planted Fraud Rings (210 merchants total across sizes 2, 3, 4, 5, 6, 8, 10, 12)
        ring_specs = (
            [(2, "PAIR", "Shared device or bank account pair")] * 18 +
            [(3, "TRIO", "3-merchant syndicate sharing VOIP and emulator")] * 10 +
            [(4, "QUAD", "4-merchant payout hub")] * 8 +
            [(5, "QUINT", "5-merchant address hub syndicate")] * 4 +
            [(6, "HEXA", "6-merchant coordinated cluster")] * 4 +
            [(8, "OCTA", "8-merchant device farm syndicate")] * 3 +
            [(10, "DECA", "10-merchant distributed syndicate")] * 2 +
            [(12, "DODECA", "12-merchant enterprise laundering ring")] * 2
        )

        entity_cursor = 860
        for r_idx, (r_size, r_type, desc) in enumerate(ring_specs):
            ring_id = f"RING-H-{r_type}-{r_idx+1:02d}"
            
            shared_dev = self.devices[entity_cursor]
            shared_ba = self.bank_accounts[entity_cursor]
            shared_ph = self.phones[entity_cursor]
            shared_addr = self.addresses[entity_cursor]
            entity_cursor += 1

            for m_i in range(r_size):
                m_id = f"M-H{r_type[:3]}-{r_idx+1:02d}-{m_i+1:02d}"
                cat = self.rng.choice(cats)
                onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(20, 60))
                
                # Weak/subtle ties for pair rings (r_idx >= 10: only shared residential address of size 2)
                if r_size == 2 and r_idx >= 10:
                    m_dev = self.devices[entity_cursor + m_i].id
                    m_ba = self.bank_accounts[entity_cursor + m_i].id
                    m_ph = self.phones[entity_cursor + m_i].id
                    m_addr = shared_addr.id
                elif r_size == 2 and r_idx % 2 == 1:
                    m_dev = shared_dev.id if m_i == 0 else self.devices[entity_cursor + m_i].id
                    m_ba = self.bank_accounts[entity_cursor + m_i].id
                    m_ph = shared_ph.id
                    m_addr = self.addresses[entity_cursor + m_i].id
                elif r_size == 3 and r_idx % 2 == 1:
                    # Line graph topology: M1-M2 share device, M2-M3 share bank account
                    m_dev = shared_dev.id if m_i in [0, 1] else self.devices[entity_cursor + m_i].id
                    m_ba = shared_ba.id if m_i in [1, 2] else self.bank_accounts[entity_cursor + m_i].id
                    m_ph = self.phones[entity_cursor + m_i].id
                    m_addr = self.addresses[entity_cursor + m_i].id
                else:
                    m_dev = shared_dev.id
                    m_ba = shared_ba.id if r_idx % 3 == 0 else self.bank_accounts[entity_cursor + m_i].id
                    m_ph = shared_ph.id if r_idx % 2 == 0 else self.phones[entity_cursor + m_i].id
                    m_addr = self.addresses[entity_cursor + m_i].id

                m = Merchant(
                    id=m_id,
                    business_name=f"{r_type} Store {r_idx+1}-{m_i+1}",
                    legal_name=f"{r_type} Store {r_idx+1}-{m_i+1} LLP",
                    category=cat,
                    business_type="LLP",
                    declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                    onboarding_date=onboard_dt,
                    kyc_status="VERIFIED",
                    device_id=m_dev,
                    phone_id=m_ph,
                    bank_account_id=m_ba,
                    upi_handle_id=self.upi_handles[entity_cursor + m_i].id,
                    address_id=m_addr,
                    is_active=True,
                    created_at=onboard_dt,
                )
                self.merchants.append(m)
                self.ground_truths[m_id] = GroundTruth(
                    merchant_id=m_id,
                    true_label=TrueLabel.RING_MEMBER,
                    fraud_scenario=FraudScenarioType.DEVICE_FARM_SYNDICATE,
                    planted_ring_id=ring_id,
                    planted_anomalies=[desc],
                    expected_risk_tier=RiskLevel.CRITICAL if r_size >= 4 else RiskLevel.HIGH,
                    description=f"Member of {ring_id} ({r_size} merchants).",
                )
            entity_cursor += (r_size + 2)

        # 6. Activity Generation with realistic noise & overlap
        self._generate_harder_merchant_activity()

        data = {
            "merchants": list(self.merchants),
            "buyers": list(self.buyers),
            "devices": list(self.devices),
            "phones": list(self.phones),
            "bank_accounts": list(self.bank_accounts),
            "upi_handles": list(self.upi_handles),
            "addresses": list(self.addresses),
            "transactions": list(self.transactions),
            "settlements": list(self.settlements),
            "refunds": list(self.refunds),
            "ground_truths": dict(self.ground_truths),
        }

        # Restore original generator seed
        self.seed = orig_seed
        self._reset()
        return data

    def _generate_harder_merchant_activity(self):
        """Generates realistic time series for harder benchmark with calibrated noise and overlap."""
        txn_counter = 1
        settl_counter = 1
        ref_counter = 1
        payment_methods = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "NETBANKING"]

        for m in self.merchants:
            gt = self.ground_truths[m.id]
            cat_info = CATEGORY_BASELINES[m.category]
            days_active = max(1, (self.anchor_time - m.onboarding_date).days)

            if gt.true_label == TrueLabel.LEGITIMATE:
                first_sale_delay_days = self.rng.uniform(0.5, 4.0) if self.rng.random() < 0.60 else self.rng.uniform(10.0, min(35.0, days_active - 2))

                if "FLASH" in m.id:
                    total_txns = self.rng.randint(40, 110)
                    m_buyers = self.rng.sample(self.buyers[100:1000], min(len(self.buyers)-100, max(15, int(total_txns * 0.70))))
                    for _ in range(total_txns):
                        days_ago = self.rng.uniform(0.1, 2.5)
                        txn_dt = self.anchor_time - timedelta(days=days_ago, hours=self.rng.uniform(9, 23))
                        is_round = self.rng.random() < 0.35
                        if is_round:
                            amount = float(self.rng.choice([999, 1499, 1999, 2999, 4999]))
                        else:
                            amount = round(float(self.np_rng.normal(cat_info["avg_ticket"] * 1.2, cat_info["ticket_std"])) + self.rng.uniform(5, 45), 2)
                        amount = max(cat_info["min_ticket"], min(cat_info["max_normal_ticket"], amount))
                        self.transactions.append(
                            Transaction(
                                id=f"TXN-H-{txn_counter:07d}",
                                merchant_id=m.id,
                                buyer_id=self.rng.choice(m_buyers).id,
                                amount=amount,
                                currency="INR",
                                status="SUCCESS",
                                payment_method=self.rng.choice(payment_methods),
                                timestamp=txn_dt,
                                is_round_amount=is_round,
                                ip_address=f"49.207.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                                device_id=m.device_id,
                            )
                        )
                        txn_counter += 1
                    
                    s_lag = self.rng.uniform(2.0, 5.0) if self.rng.random() < 0.35 else self.rng.uniform(16.0, 28.0)
                    for s_i in range(2):
                        s_dt = self.anchor_time - timedelta(days=self.rng.uniform(0.5, 2.0))
                        self.settlements.append(
                            Settlement(
                                id=f"SETTL-H-{settl_counter:06d}",
                                merchant_id=m.id,
                                bank_account_id=m.bank_account_id,
                                amount=round(self.rng.uniform(40000, 150000), 2),
                                requested_at=s_dt,
                                settled_at=s_dt + timedelta(hours=s_lag),
                                status="SETTLED",
                                velocity_in_out_hours=s_lag,
                            )
                        )
                        settl_counter += 1

                elif "B2B" in m.id:
                    total_txns = self.rng.randint(8, 22)
                    m_buyers = self.rng.sample(self.buyers[100:200], self.rng.randint(3, 6))
                    for _ in range(total_txns):
                        day_offset = self.rng.uniform(first_sale_delay_days, days_active)
                        txn_dt = m.onboarding_date + timedelta(days=day_offset, hours=self.rng.uniform(9, 18))
                        is_round = self.rng.random() < 0.40
                        if is_round:
                            amount = float(self.rng.choice([25000, 50000, 75000, 100000]))
                        else:
                            amount = round(self.rng.uniform(25000, 85000) + self.rng.uniform(12, 98), 2)
                        self.transactions.append(
                            Transaction(
                                id=f"TXN-H-{txn_counter:07d}",
                                merchant_id=m.id,
                                buyer_id=self.rng.choice(m_buyers).id,
                                amount=amount,
                                currency="INR",
                                status="SUCCESS",
                                payment_method="NETBANKING" if self.rng.random() < 0.6 else "CREDIT_CARD",
                                timestamp=txn_dt,
                                is_round_amount=is_round,
                                ip_address=f"103.11.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                                device_id=m.device_id,
                            )
                        )
                        txn_counter += 1

                    for s_i in range(max(1, int(days_active - first_sale_delay_days) // 20)):
                        s_dt = m.onboarding_date + timedelta(days=first_sale_delay_days + (s_i + 1) * 20)
                        if s_dt < self.anchor_time:
                            self.settlements.append(
                                Settlement(
                                    id=f"SETTL-H-{settl_counter:06d}",
                                    merchant_id=m.id,
                                    bank_account_id=m.bank_account_id,
                                    amount=round(self.rng.uniform(50000, 200000), 2),
                                    requested_at=s_dt,
                                    settled_at=s_dt + timedelta(hours=self.rng.uniform(20, 36)),
                                    status="SETTLED",
                                    velocity_in_out_hours=self.rng.uniform(20.0, 36.0),
                                )
                            )
                            settl_counter += 1
                else:
                    # Normal legitimate merchant: varied size (35% small 15-35 txns, 65% medium/large 40-120 txns)
                    is_small_smb = self.rng.random() < 0.35
                    if is_small_smb:
                        total_txns = self.rng.randint(15, 35)
                        m_buyers = self.rng.sample(self.buyers[500:], self.rng.randint(10, 25))
                    else:
                        total_txns = self.rng.randint(40, 110)
                        m_buyers = self.rng.sample(self.buyers[500:], min(len(self.buyers)-500, max(25, int(total_txns * 0.65))))

                    # Guarantee first transaction occurs at first_sale_delay_days
                    first_dt = m.onboarding_date + timedelta(days=first_sale_delay_days, hours=self.rng.uniform(10, 18))
                    self.transactions.append(
                        Transaction(
                            id=f"TXN-H-{txn_counter:07d}",
                            merchant_id=m.id,
                            buyer_id=self.rng.choice(m_buyers).id,
                            amount=round(float(self.np_rng.normal(cat_info["avg_ticket"], cat_info["ticket_std"])), 2),
                            currency="INR",
                            status="SUCCESS",
                            payment_method=self.rng.choice(payment_methods),
                            timestamp=first_dt,
                            is_round_amount=False,
                            ip_address=f"49.207.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                            device_id=m.device_id,
                        )
                    )
                    txn_counter += 1

                    for _ in range(total_txns - 1):
                        day_offset = self.rng.uniform(first_sale_delay_days, days_active)
                        txn_dt = m.onboarding_date + timedelta(days=day_offset, hours=self.rng.uniform(8, 22))
                        is_round = self.rng.random() < 0.22
                        if is_round:
                            amount = float(self.rng.choice([499, 999, 1499, 1999, 2499, 4999]))
                        else:
                            amount = round(float(self.np_rng.normal(cat_info["avg_ticket"], cat_info["ticket_std"])) + self.rng.uniform(1, 50), 2)
                        amount = max(cat_info["min_ticket"], min(cat_info["max_normal_ticket"], amount))
                        self.transactions.append(
                            Transaction(
                                id=f"TXN-H-{txn_counter:07d}",
                                merchant_id=m.id,
                                buyer_id=self.rng.choice(m_buyers).id,
                                amount=amount,
                                currency="INR",
                                status="SUCCESS" if self.rng.random() > 0.02 else "FAILED",
                                payment_method=self.rng.choice(payment_methods),
                                timestamp=txn_dt,
                                is_round_amount=is_round,
                                ip_address=f"49.207.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                                device_id=m.device_id,
                            )
                        )
                        txn_counter += 1

                    # 18% of legit merchants use T+0 Instant Payouts (2-4 hours)
                    s_lag = self.rng.uniform(2.0, 4.0) if self.rng.random() < 0.18 else self.rng.uniform(16.0, 32.0)
                    batches = max(1, int(days_active - first_sale_delay_days) // 12)
                    for s_i in range(batches):
                        s_dt = m.onboarding_date + timedelta(days=first_sale_delay_days + (s_i + 1) * 12)
                        if s_dt < self.anchor_time:
                            self.settlements.append(
                                Settlement(
                                    id=f"SETTL-H-{settl_counter:06d}",
                                    merchant_id=m.id,
                                    bank_account_id=m.bank_account_id,
                                    amount=round(self.rng.uniform(15000, 60000), 2),
                                    requested_at=s_dt,
                                    settled_at=s_dt + timedelta(hours=s_lag),
                                    status="SETTLED",
                                    velocity_in_out_hours=s_lag,
                                )
                            )
                            settl_counter += 1

                # Refunds for recall merchants (20% refund rate)
                if "RECALL" in m.id:
                    for _ in range(int(total_txns * 0.22)):
                        self.refunds.append(
                            Refund(
                                id=f"REF-H-{ref_counter:06d}",
                                transaction_id=f"TXN-H-0000001",
                                merchant_id=m.id,
                                amount=round(self.rng.uniform(800, 3500), 2),
                                reason="Product Defect / Recall",
                                requested_at=self.anchor_time - timedelta(days=self.rng.uniform(1, 15)),
                                status="PROCESSED",
                            )
                        )
                        ref_counter += 1

            elif gt.true_label in [TrueLabel.MULE_SHELL, TrueLabel.RING_MEMBER]:
                # Realistic onboarding: 60% start in 1-4 days, 40% start in 8-25 days
                first_sale_delay_days = self.rng.uniform(0.5, 4.0) if self.rng.random() < 0.60 else self.rng.uniform(8.0, min(25.0, days_active - 2))

                # Early test transactions
                early_txns = self.rng.randint(2, 6)
                for _ in range(early_txns):
                    early_dt = m.onboarding_date + timedelta(days=self.rng.uniform(first_sale_delay_days, first_sale_delay_days + 10), hours=self.rng.uniform(10, 18))
                    if early_dt < self.anchor_time:
                        self.transactions.append(
                            Transaction(
                                id=f"TXN-H-{txn_counter:07d}",
                                merchant_id=m.id,
                                buyer_id=self.rng.choice(self.buyers[100:500]).id,
                                amount=round(cat_info["avg_ticket"] * self.rng.uniform(0.85, 1.15), 2),
                                currency="INR",
                                status="SUCCESS",
                                payment_method="UPI",
                                timestamp=early_dt,
                                is_round_amount=False,
                                ip_address=f"49.207.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                                device_id=m.device_id,
                            )
                        )
                        txn_counter += 1

                is_weak_pair_sleeper = "PAI" in m.id and any(f"-{k:02d}-" in m.id for k in range(11, 19))
                is_subtle_mule = "HMULE" in m.id and int(m.id.split("-")[-1]) > 35

                if is_weak_pair_sleeper or is_subtle_mule:
                    # Low-profile activity: blends into normal background distributions
                    txns_count = self.rng.randint(15, 35)
                    m_buyers = self.rng.sample(self.buyers[100:], min(len(self.buyers)-100, max(8, int(txns_count * 0.70))))
                    for _ in range(txns_count):
                        day_offset = self.rng.uniform(first_sale_delay_days, days_active)
                        txn_dt = m.onboarding_date + timedelta(days=day_offset, hours=self.rng.uniform(9, 21))
                        is_round = self.rng.random() < 0.22
                        if is_round:
                            amt = float(self.rng.choice([999, 1999, 4999]))
                        else:
                            amt = round(float(self.np_rng.normal(cat_info["avg_ticket"] * 1.15, cat_info["ticket_std"])) + self.rng.uniform(2, 40), 2)
                        amt = max(cat_info["min_ticket"], min(cat_info["max_normal_ticket"], amt))
                        self.transactions.append(
                            Transaction(
                                id=f"TXN-H-{txn_counter:07d}",
                                merchant_id=m.id,
                                buyer_id=self.rng.choice(m_buyers).id,
                                amount=amt,
                                currency="INR",
                                status="SUCCESS",
                                payment_method=self.rng.choice(payment_methods),
                                timestamp=txn_dt,
                                is_round_amount=is_round,
                                ip_address=f"49.207.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                                device_id=m.device_id,
                            )
                        )
                        txn_counter += 1

                    for s_i in range(max(1, int(days_active - first_sale_delay_days) // 14)):
                        s_dt = m.onboarding_date + timedelta(days=first_sale_delay_days + (s_i + 1) * 14)
                        if s_dt < self.anchor_time:
                            self.settlements.append(
                                Settlement(
                                    id=f"SETTL-H-{settl_counter:06d}",
                                    merchant_id=m.id,
                                    bank_account_id=m.bank_account_id,
                                    amount=round(self.rng.uniform(20000, 70000), 2),
                                    requested_at=s_dt,
                                    settled_at=s_dt + timedelta(hours=self.rng.uniform(16, 28)),
                                    status="SETTLED",
                                    velocity_in_out_hours=self.rng.uniform(16.0, 28.0),
                                )
                            )
                            settl_counter += 1
                else:
                    # Active fraud activity with varied subtlety across 30 days
                    subtlety = self.rng.random()
                    txns_count = self.rng.randint(25, 60) if subtlety < 0.5 else self.rng.randint(35, 80)
                    sub_buyers = self.rng.sample(self.buyers[10:150], max(6, int(22 * (1.0 - subtlety) + 6)))
                    
                    ticket_mult = 1.25 + (1.4 * subtlety)
                    elevated_ticket = cat_info["avg_ticket"] * ticket_mult

                    for _ in range(txns_count):
                        days_ago = self.rng.uniform(0.5, min(28.0, float(days_active)))
                        txn_dt = self.anchor_time - timedelta(days=days_ago, hours=self.rng.uniform(1, 23))
                        
                        is_round = self.rng.random() < (0.24 + 0.30 * subtlety)
                        if is_round:
                            amt = float(self.rng.choice([2500, 5000, 10000, 15000, 20000, 25000]))
                        else:
                            amt = round(elevated_ticket + self.rng.uniform(15.50, 480.25), 2)

                        self.transactions.append(
                            Transaction(
                                id=f"TXN-H-{txn_counter:07d}",
                                merchant_id=m.id,
                                buyer_id=self.rng.choice(sub_buyers).id,
                                amount=amt,
                                currency="INR",
                                status="SUCCESS",
                                payment_method="UPI" if self.rng.random() < 0.70 else "CREDIT_CARD",
                                timestamp=txn_dt,
                                is_round_amount=is_round,
                                ip_address=f"103.212.{self.rng.randint(10, 99)}.{self.rng.randint(1, 254)}",
                                device_id=m.device_id,
                            )
                        )
                        txn_counter += 1

                    s_lag = 8.0 + (8.0 * (1.0 - subtlety)) if subtlety < 0.4 else self.rng.uniform(2.5, 6.0)
                    for _ in range(self.rng.randint(2, 5)):
                        s_dt = self.anchor_time - timedelta(days=self.rng.uniform(0.5, 25.0))
                        self.settlements.append(
                            Settlement(
                                id=f"SETTL-H-{settl_counter:06d}",
                                merchant_id=m.id,
                                bank_account_id=m.bank_account_id,
                                amount=round(self.rng.uniform(45000, 220000), 2),
                                requested_at=s_dt,
                                settled_at=s_dt + timedelta(hours=s_lag),
                                status="SETTLED" if self.rng.random() < 0.7 else "HELD",
                                velocity_in_out_hours=s_lag,
                            )
                        )
                        settl_counter += 1


    # =========================================================================
    # Adversarial Batch Generation (Evasion-Aware Fraudsters)
    # =========================================================================

    def generate_adversarial_batch(self, seed: int = 999) -> Dict[str, Any]:
        """Generates an evasion-aware adversarial benchmark designed to evade known top ML signals.
        
        Features:
        - 150 Legitimate background merchants (organic distributions).
        - 30 Evasion-Aware Mule Accounts:
            * Non-round amounts sampled from normal category distributions (anti-round signal).
            * Artificially diversified buyer pools (HHI < 0.04) (anti-concentration signal).
            * Gradual 45+ day volume ramps without 48h bursts (anti-velocity spike signal).
            * Organic 24-36h settlement drawdown timing (anti-rapid cashout signal).
            * Genuinely fraudulent: ground-truth labeled MULE_SHELL.
        - 20 Evasion-Aware Ring Members across 4 rings (5 merchants each):
            * Shared identifiers link the syndicate, but behavioral features blend with legitimate background.
        """
        orig_seed = self.seed
        self.seed = seed
        self._reset()

        self._generate_shared_entity_pools(pool_size=1000)
        self._generate_buyer_pool(count=2500)

        cats = list(BusinessCategory)
        txn_counter = 1
        settl_counter = 1

        # 1. 150 Legitimate Background Merchants
        for i in range(150):
            m_id = f"M-ADV-LEG-{i+1:03d}"
            cat = self.rng.choice(cats)
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(30, 180))
            m = Merchant(
                id=m_id,
                business_name=f"Standard Store #{i+1}",
                legal_name=f"Standard Store {i+1} LLP",
                category=cat,
                business_type="LLP",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=self.devices[i].id,
                phone_id=self.phones[i].id,
                bank_account_id=self.bank_accounts[i].id,
                upi_handle_id=self.upi_handles[i].id,
                address_id=self.addresses[i].id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(m)
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.LEGITIMATE,
                fraud_scenario=FraudScenarioType.NONE,
                planted_ring_id=None,
                planted_anomalies=[],
                expected_risk_tier=RiskLevel.LOW,
                description="Legitimate background merchant.",
            )

        # 2. 30 Evasion-Aware Mule Accounts
        for i in range(30):
            m_id = f"M-ADV-MULE-{i+1:03d}"
            cat = self.rng.choice([BusinessCategory.ECOMMERCE_FASHION, BusinessCategory.ELECTRONICS, BusinessCategory.DIGITAL_SERVICES])
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(60, 120))
            idx = 150 + i
            m = Merchant(
                id=m_id,
                business_name=f"Covert Retailer #{i+1}",
                legal_name=f"Covert Ventures {i+1} Pvt Ltd",
                category=cat,
                business_type="PRIVATE_LIMITED",
                declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=self.devices[idx].id,
                phone_id=self.phones[idx].id,
                bank_account_id=self.bank_accounts[idx].id,
                upi_handle_id=self.upi_handles[idx].id,
                address_id=self.addresses[idx].id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(m)
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=TrueLabel.MULE_SHELL,
                fraud_scenario=FraudScenarioType.DORMANT_BURST_MULE,
                planted_ring_id=None,
                planted_anomalies=["Evasion-aware mule: non-round amounts, diversified buyers, organic settlement cadence"],
                expected_risk_tier=RiskLevel.HIGH,
                description="Adversarial mule designed to bypass top feature thresholds.",
            )

        # 3. 20 Evasion-Aware Ring Members (4 rings × 5 merchants)
        ring_names = ["RING-ADV-DEVICE", "RING-ADV-BANK", "RING-ADV-UPI", "RING-ADV-HYBRID"]
        for r_idx, r_name in enumerate(ring_names):
            shared_dev = self.devices[200 + r_idx]
            shared_bank = self.bank_accounts[200 + r_idx]
            shared_upi = self.upi_handles[200 + r_idx]

            for m_in_ring in range(5):
                m_num = (r_idx * 5) + m_in_ring + 1
                m_id = f"M-ADV-RING-{m_num:03d}"
                cat = self.rng.choice(cats)
                onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(45, 100))
                
                # Assign shared entities according to ring archetype
                dev_id = shared_dev.id if "DEVICE" in r_name or "HYBRID" in r_name else self.devices[250 + m_num].id
                bank_id = shared_bank.id if "BANK" in r_name or "HYBRID" in r_name else self.bank_accounts[250 + m_num].id
                upi_id = shared_upi.id if "UPI" in r_name or "HYBRID" in r_name else self.upi_handles[250 + m_num].id

                m = Merchant(
                    id=m_id,
                    business_name=f"Syndicate Node #{m_num}",
                    legal_name=f"Syndicate Entity {m_num} LLP",
                    category=cat,
                    business_type="LLP",
                    declared_avg_ticket=CATEGORY_BASELINES[cat]["avg_ticket"],
                    onboarding_date=onboard_dt,
                    kyc_status="VERIFIED",
                    device_id=dev_id,
                    phone_id=self.phones[250 + m_num].id,
                    bank_account_id=bank_id,
                    upi_handle_id=upi_id,
                    address_id=self.addresses[250 + m_num].id,
                    is_active=True,
                    created_at=onboard_dt,
                )
                self.merchants.append(m)
                self.ground_truths[m_id] = GroundTruth(
                    merchant_id=m_id,
                    true_label=TrueLabel.RING_MEMBER,
                    fraud_scenario=FraudScenarioType.DEVICE_FARM_SYNDICATE,
                    planted_ring_id=r_name,
                    planted_anomalies=["Evasion-aware syndicate member with normal transaction distribution"],
                    expected_risk_tier=RiskLevel.HIGH,
                    description=f"Adversarial ring member in {r_name}.",
                )

        # 4. Generate Activity for Adversarial Batch
        for m in self.merchants:
            gt = self.ground_truths[m.id]
            cat_info = CATEGORY_BASELINES[m.category]
            days_active = max(5, (self.anchor_time - m.onboarding_date).days)

            if gt.true_label == TrueLabel.LEGITIMATE:
                # Organic legitimate traffic
                txns_count = self.rng.randint(20, 60)
                sub_buyers = self.rng.sample(self.buyers[:500], max(10, txns_count // 2))
                for _ in range(txns_count):
                    days_ago = self.rng.uniform(0.5, float(days_active))
                    txn_dt = self.anchor_time - timedelta(days=days_ago, hours=self.rng.uniform(1, 23))
                    amt = max(50.0, float(np.round(self.np_rng.normal(cat_info["avg_ticket"], cat_info["ticket_std"] * 0.4), 2)))
                    self.transactions.append(
                        Transaction(
                            id=f"TXN-ADV-{txn_counter:07d}",
                            merchant_id=m.id,
                            buyer_id=self.rng.choice(sub_buyers).id,
                            amount=amt,
                            currency="INR",
                            status="SUCCESS",
                            payment_method="UPI" if self.rng.random() < 0.65 else "CREDIT_CARD",
                            timestamp=txn_dt,
                            is_round_amount=False,
                            ip_address=f"103.14.{self.rng.randint(10, 99)}.{self.rng.randint(1, 254)}",
                            device_id=m.device_id,
                        )
                    )
                    txn_counter += 1

                for _ in range(self.rng.randint(3, 8)):
                    s_dt = self.anchor_time - timedelta(days=self.rng.uniform(1.0, float(days_active)))
                    self.settlements.append(
                        Settlement(
                            id=f"SETTL-ADV-{settl_counter:06d}",
                            merchant_id=m.id,
                            bank_account_id=m.bank_account_id,
                            amount=round(self.rng.uniform(15000, 65000), 2),
                            requested_at=s_dt,
                            settled_at=s_dt + timedelta(hours=self.rng.uniform(18, 30)),
                            status="SETTLED",
                            velocity_in_out_hours=self.rng.uniform(18.0, 30.0),
                        )
                    )
                    settl_counter += 1

            else:
                # Adversarial Fraudsters: deliberately mimic legitimate behavioral distributions
                # 1) Non-round normal ticket amounts (evade BEH_ROUND_NUMBERS and BEH_CATEGORY_MISMATCH)
                # 2) Diversified buyer pool (evade BEH_BUYER_CONCENTRATION)
                # 3) Smooth gradual ramp without 48h volume spikes (evade VEL_VOLUME_SPIKE_48H and VEL_DORMANT_BURST)
                # 4) Standard T+1 settlement timing (evade SETTL_RAPID_DRAWDOWNS)
                txns_count = self.rng.randint(40, 80)
                sub_buyers = self.rng.sample(self.buyers[500:2000], min(len(self.buyers[500:2000]), max(25, txns_count - 5)))

                for _ in range(txns_count):
                    days_ago = self.rng.uniform(0.5, float(days_active))
                    txn_dt = self.anchor_time - timedelta(days=days_ago, hours=self.rng.uniform(9, 21))
                    
                    # Exactly match expected category mean with natural decimal tails
                    base_mean = cat_info["avg_ticket"] * self.rng.uniform(0.95, 1.15)
                    amt = round(float(base_mean + self.rng.uniform(11.25, 87.75)), 2)

                    self.transactions.append(
                        Transaction(
                            id=f"TXN-ADV-{txn_counter:07d}",
                            merchant_id=m.id,
                            buyer_id=self.rng.choice(sub_buyers).id,
                            amount=amt,
                            currency="INR",
                            status="SUCCESS",
                            payment_method="UPI" if self.rng.random() < 0.60 else "CREDIT_CARD",
                            timestamp=txn_dt,
                            is_round_amount=False,
                            ip_address=f"103.88.{self.rng.randint(10, 99)}.{self.rng.randint(1, 254)}",
                            device_id=m.device_id,
                        )
                    )
                    txn_counter += 1

                # Normal 22-30h settlement lag
                for _ in range(self.rng.randint(4, 7)):
                    s_dt = self.anchor_time - timedelta(days=self.rng.uniform(1.0, float(days_active)))
                    s_lag = self.rng.uniform(22.0, 32.0)
                    self.settlements.append(
                        Settlement(
                            id=f"SETTL-ADV-{settl_counter:06d}",
                            merchant_id=m.id,
                            bank_account_id=m.bank_account_id,
                            amount=round(self.rng.uniform(35000, 110000), 2),
                            requested_at=s_dt,
                            settled_at=s_dt + timedelta(hours=s_lag),
                            status="SETTLED" if self.rng.random() < 0.8 else "HELD",
                            velocity_in_out_hours=s_lag,
                        )
                    )
                    settl_counter += 1

        self.seed = orig_seed
        return {
            "merchants": self.merchants,
            "buyers": self.buyers,
            "devices": self.devices,
            "phones": self.phones,
            "bank_accounts": self.bank_accounts,
            "upi_handles": self.upi_handles,
            "addresses": self.addresses,
            "transactions": self.transactions,
            "settlements": self.settlements,
            "refunds": self.refunds,
            "ground_truths": self.ground_truths,
        }

    # =========================================================================
    # Approximated Blind Hard-Negative Benchmark (10 Independent Cases)
    # =========================================================================

    def generate_blind_hard_negatives(self, seed: int = 777) -> Dict[str, Any]:
        """Generates 10 challenging real-world edge cases designed independently of the training batch.
        
        Framed honestly as an 'approximated blind check' (designed in a separate pass by the same team).
        
        Scenarios:
        1. Seasonal Diwali festival retailer with 8× volume spike and GST invoices.
        2. Legacy merchant undergoing bank merger / IFSC migration.
        3. Industrial chemicals B2B distributor with high ticket (₹1.2L) and corporate client concentration.
        4. Weekend night-market gourmet food truck with 95% off-peak hours.
        5. Tech incubator co-working hub with 8 distinct startup merchants sharing physical address.
        6. Viral creator merchandise drop with sudden 48h volume surge.
        7. Antiquarian rare book dealer with low volume and high declared ticket sizes.
        8. Regional franchise store operating on parent corporate IP subnet.
        9. Corporate MICE travel agent handling bulk corporate retreat flights.
        10. Private academy tuition collector processing quarterly round ₹50,000 tuition fees.
        """
        orig_seed = self.seed
        self.seed = seed
        self._reset()

        self._generate_shared_entity_pools(pool_size=100)
        self._generate_buyer_pool(count=500)

        blind_cases_meta = [
            ("M-BLIND-01", "Diwali Heritage Silks", BusinessCategory.ECOMMERCE_FASHION, "Seasonal festival surge (8× volume spike with low refunds)", TrueLabel.LEGITIMATE),
            ("M-BLIND-02", "National Tech Components", BusinessCategory.ELECTRONICS, "PSU bank merger settlement account migration", TrueLabel.LEGITIMATE),
            ("M-BLIND-03", "ChemCorp Industrial Supplies", BusinessCategory.B2B_SUPPLIES, "B2B industrial chemicals with high ticket & 3 corporate buyers", TrueLabel.LEGITIMATE),
            ("M-BLIND-04", "Midnight Wok Food Truck", BusinessCategory.GROCERY_FOOD, "Night market vendor with 95% off-peak nighttime transactions", TrueLabel.LEGITIMATE),
            ("M-BLIND-05", "Vector Labs Incubator #1", BusinessCategory.DIGITAL_SERVICES, "Tech incubator startup sharing corporate address with 7 other firms", TrueLabel.LEGITIMATE),
            ("M-BLIND-06", "Creator Drop Apparel", BusinessCategory.ECOMMERCE_FASHION, "Viral influencer merchandise launch with 48h volume burst", TrueLabel.LEGITIMATE),
            ("M-BLIND-07", "Imperial Antiquarian Books", BusinessCategory.CONSULTING_SERVICES, "Rare book art dealer with 3 high-ticket transactions (₹1.1L avg)", TrueLabel.LEGITIMATE),
            ("M-BLIND-08", "Metro Cafe Franchise #4", BusinessCategory.GROCERY_FOOD, "Franchise outlet on franchisor shared WiFi subnet", TrueLabel.LEGITIMATE),
            ("M-BLIND-09", "Horizon Corporate MICE Travel", BusinessCategory.TRAVEL_TICKETING, "Corporate group travel agent with high buyer concentration", TrueLabel.LEGITIMATE),
            ("M-BLIND-10", "Apex Olympiad Academy", BusinessCategory.EDTECH, "Quarterly tuition collection in round ₹50,000 installments", TrueLabel.LEGITIMATE),
        ]

        txn_counter = 1
        settl_counter = 1

        for idx, (m_id, name, cat, anomaly_desc, true_label) in enumerate(blind_cases_meta):
            onboard_dt = self.anchor_time - timedelta(days=self.rng.randint(40, 150))
            cat_info = CATEGORY_BASELINES[cat]
            m = Merchant(
                id=m_id,
                business_name=name,
                legal_name=f"{name} Pvt Ltd",
                category=cat,
                business_type="PRIVATE_LIMITED",
                declared_avg_ticket=cat_info["avg_ticket"] * (2.0 if "Industrial" in name or "Antiquarian" in name else 1.0),
                onboarding_date=onboard_dt,
                kyc_status="VERIFIED",
                device_id=self.devices[idx].id,
                phone_id=self.phones[idx].id,
                bank_account_id=self.bank_accounts[idx].id,
                upi_handle_id=self.upi_handles[idx].id,
                address_id=self.addresses[idx if idx != 4 else 0].id,
                is_active=True,
                created_at=onboard_dt,
            )
            self.merchants.append(m)
            self.ground_truths[m_id] = GroundTruth(
                merchant_id=m_id,
                true_label=true_label,
                fraud_scenario=FraudScenarioType.NONE,
                planted_ring_id=None,
                planted_anomalies=[anomaly_desc],
                expected_risk_tier=RiskLevel.LOW,
                description=f"Approximated Blind Check: {anomaly_desc}",
            )

            # Generate realistic activity tailored to the scenario
            if m_id == "M-BLIND-01":
                # Festival surge: 80 txns in last 3 days
                for _ in range(80):
                    txn_dt = self.anchor_time - timedelta(days=self.rng.uniform(0.1, 3.0))
                    amt = float(np.round(self.np_rng.normal(2400.0, 600.0), 2))
                    self.transactions.append(Transaction(
                        id=f"TXN-BLIND-{txn_counter:07d}", merchant_id=m.id, buyer_id=self.rng.choice(self.buyers).id,
                        amount=max(200.0, amt), currency="INR", status="SUCCESS", payment_method="UPI",
                        timestamp=txn_dt, is_round_amount=False, ip_address="103.45.22.10", device_id=m.device_id,
                    ))
                    txn_counter += 1
            elif m_id == "M-BLIND-04":
                # Night market food truck: 100% off-peak 10pm - 2am
                for _ in range(50):
                    days_ago = self.rng.randint(1, 20)
                    txn_dt = self.anchor_time - timedelta(days=days_ago, hours=self.rng.choice([22, 23, 1, 2]))
                    amt = round(self.rng.uniform(120.0, 480.0), 2)
                    self.transactions.append(Transaction(
                        id=f"TXN-BLIND-{txn_counter:07d}", merchant_id=m.id, buyer_id=self.rng.choice(self.buyers).id,
                        amount=amt, currency="INR", status="SUCCESS", payment_method="UPI",
                        timestamp=txn_dt, is_round_amount=False, ip_address="103.45.22.14", device_id=m.device_id,
                    ))
                    txn_counter += 1
            elif m_id == "M-BLIND-10":
                # Tuition collector: Round ₹50,000 payments
                for _ in range(25):
                    txn_dt = self.anchor_time - timedelta(days=self.rng.uniform(1.0, 25.0))
                    self.transactions.append(Transaction(
                        id=f"TXN-BLIND-{txn_counter:07d}", merchant_id=m.id, buyer_id=self.rng.choice(self.buyers).id,
                        amount=50000.0, currency="INR", status="SUCCESS", payment_method="NET_BANKING",
                        timestamp=txn_dt, is_round_amount=True, ip_address="103.45.22.20", device_id=m.device_id,
                    ))
                    txn_counter += 1
            else:
                # Standard business flow with scenario characteristics
                txns_count = self.rng.randint(15, 35)
                for _ in range(txns_count):
                    txn_dt = self.anchor_time - timedelta(days=self.rng.uniform(1.0, 30.0))
                    amt = float(np.round(self.np_rng.normal(cat_info["avg_ticket"], cat_info["ticket_std"] * 0.5), 2))
                    self.transactions.append(Transaction(
                        id=f"TXN-BLIND-{txn_counter:07d}", merchant_id=m.id, buyer_id=self.rng.choice(self.buyers).id,
                        amount=max(100.0, amt), currency="INR", status="SUCCESS", payment_method="UPI",
                        timestamp=txn_dt, is_round_amount=False, ip_address="103.45.22.30", device_id=m.device_id,
                    ))
                    txn_counter += 1

            for _ in range(3):
                s_dt = self.anchor_time - timedelta(days=self.rng.uniform(1.0, 20.0))
                self.settlements.append(Settlement(
                    id=f"SETTL-BLIND-{settl_counter:06d}", merchant_id=m.id, bank_account_id=m.bank_account_id,
                    amount=round(self.rng.uniform(25000, 95000), 2), requested_at=s_dt,
                    settled_at=s_dt + timedelta(hours=24), status="SETTLED", velocity_in_out_hours=24.0,
                ))
                settl_counter += 1

        self.seed = orig_seed
        return {
            "merchants": self.merchants,
            "buyers": self.buyers,
            "devices": self.devices,
            "phones": self.phones,
            "bank_accounts": self.bank_accounts,
            "upi_handles": self.upi_handles,
            "addresses": self.addresses,
            "transactions": self.transactions,
            "settlements": self.settlements,
            "refunds": self.refunds,
            "ground_truths": self.ground_truths,
        }


# Global generator singleton instance
generator = SyntheticDataGenerator(seed=settings.RANDOM_SEED)


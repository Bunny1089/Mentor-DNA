"""Core Configuration and Constants for Merchant DNA Platform."""

from enum import Enum
from typing import Dict, Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionType(str, Enum):
    CONTINUE_MONITORING = "CONTINUE_MONITORING"
    ENHANCED_MONITORING = "ENHANCED_MONITORING"
    SETTLEMENT_REVIEW = "SETTLEMENT_REVIEW"
    URGENT_SETTLEMENT_FREEZE = "URGENT_SETTLEMENT_FREEZE"


class DecisionFeedback(str, Enum):
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    NEEDS_INVESTIGATION = "NEEDS_INVESTIGATION"
    CLEARED = "CLEARED"


class BusinessCategory(str, Enum):
    ECOMMERCE_FASHION = "ECOMMERCE_FASHION"
    ELECTRONICS = "ELECTRONICS"
    GROCERY_FOOD = "GROCERY_FOOD"
    DIGITAL_SERVICES = "DIGITAL_SERVICES"
    EDTECH = "EDTECH"
    TRAVEL_TICKETING = "TRAVEL_TICKETING"
    JEWELRY_LUXURY = "JEWELRY_LUXURY"
    GAMING_ENTERTAINMENT = "GAMING_ENTERTAINMENT"
    B2B_SUPPLIES = "B2B_SUPPLIES"
    CONSULTING_SERVICES = "CONSULTING_SERVICES"


# Category baseline parameters for realistic distribution & mismatch anomaly detection
CATEGORY_BASELINES: Dict[BusinessCategory, Dict[str, Any]] = {
    BusinessCategory.ECOMMERCE_FASHION: {
        "avg_ticket": 1850.0,
        "ticket_std": 800.0,
        "min_ticket": 299.0,
        "max_normal_ticket": 8500.0,
        "expected_refund_rate": 0.045,  # 4.5%
        "round_number_ratio_baseline": 0.08,
    },
    BusinessCategory.ELECTRONICS: {
        "avg_ticket": 14500.0,
        "ticket_std": 9200.0,
        "min_ticket": 499.0,
        "max_normal_ticket": 65000.0,
        "expected_refund_rate": 0.025,
        "round_number_ratio_baseline": 0.12,
    },
    BusinessCategory.GROCERY_FOOD: {
        "avg_ticket": 620.0,
        "ticket_std": 350.0,
        "min_ticket": 50.0,
        "max_normal_ticket": 3500.0,
        "expected_refund_rate": 0.015,
        "round_number_ratio_baseline": 0.05,
    },
    BusinessCategory.DIGITAL_SERVICES: {
        "avg_ticket": 2200.0,
        "ticket_std": 1400.0,
        "min_ticket": 199.0,
        "max_normal_ticket": 12000.0,
        "expected_refund_rate": 0.010,
        "round_number_ratio_baseline": 0.15,
    },
    BusinessCategory.EDTECH: {
        "avg_ticket": 8500.0,
        "ticket_std": 5000.0,
        "min_ticket": 999.0,
        "max_normal_ticket": 40000.0,
        "expected_refund_rate": 0.030,
        "round_number_ratio_baseline": 0.20,
    },
    BusinessCategory.TRAVEL_TICKETING: {
        "avg_ticket": 6800.0,
        "ticket_std": 4200.0,
        "min_ticket": 500.0,
        "max_normal_ticket": 35000.0,
        "expected_refund_rate": 0.060,
        "round_number_ratio_baseline": 0.10,
    },
    BusinessCategory.JEWELRY_LUXURY: {
        "avg_ticket": 32000.0,
        "ticket_std": 18000.0,
        "min_ticket": 2500.0,
        "max_normal_ticket": 150000.0,
        "expected_refund_rate": 0.018,
        "round_number_ratio_baseline": 0.14,
    },
    BusinessCategory.GAMING_ENTERTAINMENT: {
        "avg_ticket": 450.0,
        "ticket_std": 380.0,
        "min_ticket": 20.0,
        "max_normal_ticket": 2500.0,
        "expected_refund_rate": 0.008,
        "round_number_ratio_baseline": 0.22,
    },
    BusinessCategory.B2B_SUPPLIES: {
        "avg_ticket": 45000.0,
        "ticket_std": 28000.0,
        "min_ticket": 5000.0,
        "max_normal_ticket": 250000.0,
        "expected_refund_rate": 0.012,
        "round_number_ratio_baseline": 0.18,
    },
    BusinessCategory.CONSULTING_SERVICES: {
        "avg_ticket": 18000.0,
        "ticket_std": 12000.0,
        "min_ticket": 1500.0,
        "max_normal_ticket": 85000.0,
        "expected_refund_rate": 0.005,
        "round_number_ratio_baseline": 0.25,
    },
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    PROJECT_NAME: str = "Merchant DNA - Risk Intelligence Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    RANDOM_SEED: int = 42
    
    # Dataset Generation Parameters
    TOTAL_MERCHANTS: int = 240
    LEGITIMATE_MERCHANTS_RATIO: float = 0.78
    MULE_MERCHANTS_RATIO: float = 0.10
    FRAUD_RING_RATIO: float = 0.12  # Planted rings
    
    # Simulation Window (days)
    TIME_HORIZON_DAYS: int = 60
    BURST_WINDOW_HOURS: int = 48
    
    # Risk Score Ranges
    SCORE_LOW_MAX: int = 29
    SCORE_MEDIUM_MAX: int = 59
    SCORE_HIGH_MAX: int = 79
    SCORE_CRITICAL_MAX: int = 100

    # Loss Cost Model (in INR)
    AVG_FRAUD_TRANSACTION_RECOVERY_RATE: float = 0.15  # Only 15% recovered once settled out (85% unrecovered loss exposure)
    FALSE_POSITIVE_DELAY_COST_RATE: float = 0.020      # 2.0% estimated capital friction / inquiry handling cost per delayed settlement volume

    # Settlement Hold Caps & Governance (Aligned with RBI T+1 Settlement Guidelines)
    MAX_HOLD_DURATION_HOURS: int = 48                  # Maximum hold duration before mandatory release or formal escalation
    HOLD_ESCALATION_HOURS: int = 24                    # Auto-escalation trigger to senior risk lead for secondary review


settings = Settings()

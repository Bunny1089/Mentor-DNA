"""Evaluation summary runner script.

Executes:
1. Multi-seed evaluation (mean & std)
2. Adversarial stress test metrics
3. Score stability analysis (non-borderline vs borderline)
4. Blind hard-negative check (accuracy & misclassified cases)
5. Recovery-rate sensitivity table
"""

import os
import sys
from typing import Any

# Ensure UTF-8 output encoding if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend root is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app.ml.evaluator import evaluator


def safe_get(obj: Any, key_or_attr: str, default: Any = "N/A") -> Any:
    """Safely retrieves a value whether obj is a dict, Pydantic model, or custom class."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        val = obj.get(key_or_attr, default)
        return default if val is None else val
    if hasattr(obj, "model_dump"):
        try:
            d = obj.model_dump()
            return d.get(key_or_attr, default)
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return getattr(obj, key_or_attr, default)
    return getattr(obj, key_or_attr, default)


def format_pct_mean_std(mean_val: Any, std_val: Any) -> str:
    try:
        m = float(mean_val) * 100.0
        s = float(std_val) * 100.0
        return f"{m:.2f}% +/- {s:.2f}%"
    except Exception:
        return f"{mean_val} +/- {std_val}"


def format_num_mean_std(mean_val: Any, std_val: Any) -> str:
    try:
        m = float(mean_val)
        s = float(std_val)
        return f"{m:.4f} +/- {s:.4f}"
    except Exception:
        return f"{mean_val} +/- {std_val}"


def sanitize_str(s: Any) -> str:
    """Replaces Unicode characters that might break legacy terminal charmaps."""
    if not isinstance(s, str):
        s = str(s)
    return s.replace("\u20b9", "INR ").replace("±", "+/-")


def main():
    print("=" * 80)
    print("RUNNING RISK ENGINE COMPREHENSIVE EVALUATION")
    print("=" * 80)

    results = evaluator.evaluate_model_performance()

    # -------------------------------------------------------------------------
    # 1. Multi-seed evaluation
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("1. MULTI-SEED EVALUATION (5 Random Seeds: 42, 101, 202, 303, 404)")
    print("=" * 80)
    multi_seed = safe_get(results, "multi_seed_evaluation", {})
    mean_m = safe_get(multi_seed, "mean_metrics", {})
    std_m = safe_get(multi_seed, "std_metrics", {})

    prec_mean = safe_get(mean_m, "precision", 0.0)
    prec_std = safe_get(std_m, "precision", 0.0)
    rec_mean = safe_get(mean_m, "recall", 0.0)
    rec_std = safe_get(std_m, "recall", 0.0)
    f1_mean = safe_get(mean_m, "f1_score", 0.0)
    f1_std = safe_get(std_m, "f1_score", 0.0)
    roc_mean = safe_get(mean_m, "roc_auc", 0.0)
    roc_std = safe_get(std_m, "roc_auc", 0.0)
    ring_mean = safe_get(mean_m, "planted_ring_detection_rate", safe_get(mean_m, "ring_detection_rate", 0.0))
    ring_std = safe_get(std_m, "planted_ring_detection_rate", safe_get(std_m, "ring_detection_rate", 0.0))
    mule_mean = safe_get(mean_m, "mule_shell_detection_rate", safe_get(mean_m, "mule_detection_rate", 0.0))
    mule_std = safe_get(std_m, "mule_shell_detection_rate", safe_get(std_m, "mule_detection_rate", 0.0))

    print(f"  * Precision (PPV)            : {format_pct_mean_std(prec_mean, prec_std)} (raw: {prec_mean:.4f} +/- {prec_std:.4f})")
    print(f"  * Recall (Sensitivity)       : {format_pct_mean_std(rec_mean, rec_std)} (raw: {rec_mean:.4f} +/- {rec_std:.4f})")
    print(f"  * F1-Score                   : {format_num_mean_std(f1_mean, f1_std)}")
    print(f"  * ROC-AUC                    : {format_num_mean_std(roc_mean, roc_std)}")
    print(f"  * Ring Detection Rate        : {format_pct_mean_std(ring_mean, ring_std)} (raw: {ring_mean:.4f} +/- {ring_std:.4f})")
    print(f"  * Mule / Shell Detection Rate: {format_pct_mean_std(mule_mean, mule_std)} (raw: {mule_mean:.4f} +/- {mule_std:.4f})")

    # -------------------------------------------------------------------------
    # 2. Adversarial stress test
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("2. ADVERSARIAL STRESS TEST (Evasion-Aware Generator Batch)")
    print("=" * 80)
    adv = safe_get(results, "adversarial_stress_test", {})
    adv_m = safe_get(adv, "metrics", {})
    adv_det = safe_get(adv, "detection_rates", {})

    adv_prec = safe_get(adv_m, "precision", 0.0)
    adv_rec = safe_get(adv_m, "recall", 0.0)
    adv_f1 = safe_get(adv_m, "f1_score", 0.0)
    adv_roc = safe_get(adv_m, "roc_auc", 0.0)
    adv_ring = safe_get(adv_det, "planted_ring_detection_rate", 0.0)
    adv_ring_caught = safe_get(adv_det, "ring_merchants_detected", "N/A")
    adv_ring_total = safe_get(adv_det, "ring_merchants_total", "N/A")
    adv_mule = safe_get(adv_det, "mule_shell_detection_rate", 0.0)

    print(f"  * Precision (PPV)            : {float(adv_prec) * 100:.2f}% (raw: {adv_prec})")
    print(f"  * Recall (Sensitivity)       : {float(adv_rec) * 100:.2f}% (raw: {adv_rec})")
    print(f"  * F1-Score                   : {adv_f1}")
    print(f"  * ROC-AUC                    : {adv_roc}")
    print(f"  * Ring Detection Rate        : {float(adv_ring) * 100:.2f}% ({adv_ring_caught}/{adv_ring_total} merchants caught)")
    print(f"  * Mule / Shell Detection Rate: {float(adv_mule) * 100:.2f}%")

    # -------------------------------------------------------------------------
    # 3. Score stability
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("3. SCORE STABILITY (+/-5% Behavioral Feature Perturbation Test)")
    print("=" * 80)
    stability = safe_get(results, "score_stability_analysis", {})
    nb_cohort = safe_get(stability, "non_borderline_cohort", {})
    b_cohort = safe_get(stability, "borderline_cohort", {})

    nb_flip_rate = safe_get(nb_cohort, "flip_rate", 0.0)
    nb_flips = safe_get(nb_cohort, "flips_observed", 0)
    nb_size = safe_get(nb_cohort, "sample_size", 0)
    nb_desc = sanitize_str(safe_get(nb_cohort, "description", "Score <45 or >75"))

    b_flip_rate = safe_get(b_cohort, "flip_rate", 0.0)
    b_flips = safe_get(b_cohort, "flips_observed", 0)
    b_size = safe_get(b_cohort, "sample_size", 0)
    b_desc = sanitize_str(safe_get(b_cohort, "description", "Score 50-70"))

    print(f"  * Non-Borderline Merchants ({nb_desc}):")
    print(f"      - Flip Rate       : {float(nb_flip_rate) * 100:.2f}% ({nb_flips}/{nb_size} merchants changed tier)")
    print(f"  * Borderline Merchants ({b_desc}):")
    print(f"      - Flip Rate       : {float(b_flip_rate) * 100:.2f}% ({b_flips}/{b_size} merchants changed tier)")

    # -------------------------------------------------------------------------
    # 4. Blind hard-negative check
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("4. BLIND HARD-NEGATIVE CHECK (10 Edge Cases)")
    print("=" * 80)
    blind = safe_get(results, "blind_hard_negative_check", {})
    accuracy = safe_get(blind, "accuracy", 0.0)
    correct_count = safe_get(blind, "correct_classifications", 0)
    total_cases = safe_get(blind, "total_blind_cases", 0)
    cases = safe_get(blind, "cases", [])

    print(f"  * Overall Accuracy: {float(accuracy) * 100:.1f}% ({correct_count}/{total_cases} correctly classified)\n")

    misclassified = [c for c in cases if not safe_get(c, "is_correctly_classified", True)]
    correct_cases = [c for c in cases if safe_get(c, "is_correctly_classified", True)]

    print(f"  * Misclassified Cases ({len(misclassified)} total):")
    if misclassified:
        for idx, mc in enumerate(misclassified, 1):
            m_id = sanitize_str(safe_get(mc, "merchant_id", "N/A"))
            b_name = sanitize_str(safe_get(mc, "business_name", "N/A"))
            cat = sanitize_str(safe_get(mc, "category", "N/A"))
            scenario = sanitize_str(safe_get(mc, "scenario_tested", "N/A"))
            score = safe_get(mc, "overall_risk_score", "N/A")
            tier = sanitize_str(safe_get(mc, "risk_tier", "N/A"))
            action = sanitize_str(safe_get(mc, "recommended_action", "N/A"))
            top_f = sanitize_str(safe_get(mc, "top_factor", "N/A"))
            print(f"    [{idx}] Merchant ID: {m_id} | Name: {b_name} ({cat})")
            print(f"        - Scenario Tested   : {scenario}")
            print(f"        - Risk Score & Tier : {score} ({tier})")
            print(f"        - Recommended Action: {action}")
            print(f"        - Top Risk Factor   : {top_f}")
    else:
        print("    (None - 100% accuracy)")

    print(f"\n  * Correctly Classified Cases ({len(correct_cases)} total):")
    for idx, cc in enumerate(correct_cases, 1):
        m_id = sanitize_str(safe_get(cc, "merchant_id", "N/A"))
        b_name = sanitize_str(safe_get(cc, "business_name", "N/A"))
        score = safe_get(cc, "overall_risk_score", "N/A")
        tier = sanitize_str(safe_get(cc, "risk_tier", "N/A"))
        scenario = sanitize_str(safe_get(cc, "scenario_tested", "N/A"))
        print(f"    [{idx}] {m_id} - {b_name} (Score: {score}, Tier: {tier}) -> {scenario}")

    # -------------------------------------------------------------------------
    # 5. Recovery-rate sensitivity table
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("5. RECOVERY-RATE SENSITIVITY TABLE (5% / 15% / 30%)")
    print("=" * 80)
    rec_sens = safe_get(results, "recovery_sensitivity_analysis", {})
    matrix = safe_get(rec_sens, "sensitivity_matrix", [])

    header = f"{'Scenario':<16} | {'Recovery %':<10} | {'Loss Exposure %':<15} | {'Loss Prevented (INR)':<22} | {'FP Friction Cost (INR)':<24} | {'FN Exposure (INR)':<20} | {'Net Savings (INR)':<20}"
    print(header)
    print("-" * len(header))
    for row in matrix:
        sc = sanitize_str(safe_get(row, "scenario", ""))
        rec_pct = sanitize_str(safe_get(row, "recovery_rate_pct", ""))
        loss_pct = sanitize_str(safe_get(row, "loss_exposure_pct", ""))
        prevented = float(safe_get(row, "fraud_loss_prevented_inr", 0.0))
        fp_cost = float(safe_get(row, "false_positive_friction_cost_inr", 0.0))
        fn_cost = float(safe_get(row, "false_negative_exposure_inr", 0.0))
        net_savings = float(safe_get(row, "net_fraud_savings_inr", 0.0))

        print(
            f"{sc:<16} | {rec_pct:<10} | {loss_pct:<15} | "
            f"INR {prevented:>15,.2f} | INR {fp_cost:>17,.2f} | INR {fn_cost:>13,.2f} | INR {net_savings:>13,.2f}"
        )

    print("\n" + "=" * 80)
    print("EVALUATION RUN COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

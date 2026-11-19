"""Controlled comparisons B-E001 through B-E005, no product dependencies."""

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.special import betaln, betainc, logsumexp
from scipy.stats import beta, binom, norm

Z = float(norm.ppf(0.975))


def binomial_intervals(n):
    successes = np.arange(n + 1)
    rate = successes / n
    se = np.sqrt(rate * (1 - rate) / n)
    center = (rate + Z**2 / (2 * n)) / (1 + Z**2 / n)
    half = Z * np.sqrt(se**2 + Z**2 / (4 * n**2)) / (1 + Z**2 / n)
    exact_low = beta.ppf(.025, np.maximum(successes, 1), n - successes + 1)
    exact_high = beta.ppf(.975, successes + 1, np.maximum(n - successes, 1))
    exact_low[0], exact_high[-1] = 0, 1
    return {
        "jeffreys": beta.ppf(np.array([[.025], [.975]]), successes + .5, n - successes + .5),
        "uniform": beta.ppf(np.array([[.025], [.975]]), successes + 1, n - successes + 1),
        "wilson": np.clip([center - half, center + half], 0, 1),
        "clopper_pearson": (exact_low, exact_high),
        "wald_clipped": np.clip([rate - Z * se, rate + Z * se], 0, 1),
    }


def exact_binomial():
    rows = []
    for n in (5, 20, 100):
        intervals = binomial_intervals(n)
        for p in (0, .0001, .001, .01, .05, .2, .5, .99, 1):
            weights = binom.pmf(np.arange(n + 1), n, p)
            assert np.isclose(weights.sum(), 1)
            for method, (lo, hi) in intervals.items():
                rows.append({
                    "n": n, "p": p, "method": method,
                    "coverage": float(weights @ ((lo <= p) & (p <= hi))),
                    "expected_width": float(weights @ (hi - lo)),
                    "v1_gate_probability": (
                        float(weights @ (hi - lo <= .25)) if n >= 20 else 0.
                    ) if method == "jeffreys" else None,
                })
    return rows


def posterior(n, e, components):
    prior_w, a, b = np.array(components, dtype=float).T
    logw = np.log(prior_w) + betaln(a + e, b + n - e) - betaln(a, b)
    w = np.exp(logw - logsumexp(logw))
    a, b = a + e, b + n - e
    if len(w) == 1:
        lo, hi = beta.ppf([.025, .975], a[0], b[0])
    else:
        def cdf(x):
            return float(w @ betainc(a, b, x))

        lo, hi = [brentq(lambda x: cdf(x) - q, 0, 1) for q in (.025, .975)]
    return float(w @ (a / (a + b))), float(lo), float(hi), w


def borrowing():
    rows = []
    for history in ((18,), (18, 90, 162)):
        count, events = 180 * len(history), sum(history)
        for n in (0, 4, 20, 100):
            methods = {
                "none": [(1, .5, .5)],
                "pool": [(1, events + .5, count - events + .5)],
                "power_0.1": [(1, .1 * events + .5, .1 * (count - events) + .5)],
            }
            for weak_weight in (.2, .5):
                center = (events + .5) / (count + 1)
                methods[f"mix_weak_{weak_weight}"] = [
                    (1 - weak_weight, center * 20, (1 - center) * 20),
                    (weak_weight, .5, .5),
                ]
            for name, prior in methods.items():
                estimates = [posterior(n, e, prior) for e in range(n + 1)]
                mean, lo, hi = np.array([x[:3] for x in estimates]).T
                abstain = ((lo <= .25) & (hi >= .25)) | ((n == 0) & (name == "none"))
                for p in (.1, .3, .5):
                    mass = binom.pmf(np.arange(n + 1), n, p)
                    regret = abs(p - .25) * ((mean > .25) != (p > .25))
                    rows.append({
                        "source_events_by_group": history, "source_n_per_group": 180,
                        "n": n, "p": p, "method": name,
                        "bias": float(mass @ (mean - p)),
                        "rmse": float(np.sqrt(mass @ (mean - p)**2)),
                        "coverage": float(mass @ ((lo <= p) & (p <= hi))),
                        "abstain_rate": float(mass @ abstain),
                        "point_regret": None if n == 0 and name == "none" else float(mass @ regret),
                        "loss_with_abstention": {
                            str(cost): float(mass @ np.where(abstain, cost, regret))
                            for cost in (.01, .08)
                        },
                        "weak_prior_weight_if_zero_target": (
                            float(estimates[0][3][-1]) if n == 0 and len(prior) > 1 else None
                        ),
                        "output_is_prior_only": n == 0,
                    })
    return rows


def summary(values):
    return {"mean": float(np.mean(values)), "mc_se": float(np.std(values, ddof=1) / np.sqrt(len(values)))}


def standardization():
    r, size = 20000, 100
    rng = np.random.default_rng(57031)
    truth, p, w = .13, np.array([.05, .45]), .2
    y = rng.random((r, 2, size)) < p[None, :, None]
    layer = y.mean(axis=2)
    q_fixed = (1 - w) * layer[:, 0] + w * layer[:, 1]
    aux = y & (rng.random(y.shape) < .8)
    w_joint = aux.mean(axis=(1, 2))
    w_ind = rng.binomial(2 * size, w, r) / (2 * size)

    def compute(weights):
        return (1 - weights) * layer[:, 0] + weights * layer[:, 1]

    # First-order influence of each observed unit under stratified sampling.
    influence_risk = (y - layer[:, :, None]) * np.stack(
        [1 - w_joint, w_joint], axis=1
    )[:, :, None]
    influence_weight = (aux - aux.mean(axis=2, keepdims=True)) * (
        (layer[:, 1] - layer[:, 0]) / 2
    )[:, None, None]
    independent_var = (
        np.var(influence_risk, axis=2, ddof=1) + np.var(influence_weight, axis=2, ddof=1)
    ).sum(axis=1) / size
    joint_var = np.var(influence_risk + influence_weight, axis=2, ddof=1).sum(axis=1) / size
    covered_ind = (np.abs(compute(w_joint) - truth) <= Z * np.sqrt(independent_var)).astype(float)
    covered_joint = (np.abs(compute(w_joint) - truth) <= Z * np.sqrt(joint_var)).astype(float)

    # Shared Bernoulli component with probability rho per cluster.
    rho, clusters, per_cluster = .4, 30, 8
    shared = rng.random((r, clusters, 1)) < .2
    use_shared = rng.random((r, clusters, 1)) < rho
    independent = rng.random((r, clusters, per_cluster)) < .2
    data = np.where(use_shared, shared, independent)
    cluster_means = data.mean(axis=2)
    means = cluster_means.mean(axis=1)
    iid_var = means * (1 - means) / (clusters * per_cluster)
    cluster_var = np.var(cluster_means, axis=1, ddof=1) / clusters
    iid_covered = (np.abs(means - .2) <= Z * np.sqrt(iid_var)).astype(float)
    cluster_covered = (np.abs(means - .2) <= Z * np.sqrt(cluster_var)).astype(float)
    return {
        "seed": 57031, "replicates": r, "truth": truth, "sample_size_per_stratum": size,
        "fixed_weight_mse": summary((q_fixed - truth)**2),
        "independent_weight_mse": summary((compute(w_ind) - truth)**2),
        "shared_weight_mse": summary((compute(w_joint) - truth)**2),
        "naive_balanced_pooled_bias": summary(layer.mean(axis=1) - truth),
        "joint_variance": summary(joint_var),
        "variance_omitting_covariance": summary(independent_var),
        "joint_coverage": summary(covered_joint),
        "omit_covariance_coverage": summary(covered_ind),
        "paired_coverage_difference": summary(covered_joint - covered_ind),
        "cluster_count": clusters, "cluster_size": per_cluster, "cluster_icc": rho,
        "cluster_expected_variance": .2 * .8 * (1 + (per_cluster - 1) * rho) / (clusters * per_cluster),
        "cluster_empirical_mse": summary((means - .2)**2),
        "cluster_iid_coverage": summary(iid_covered),
        "cluster_robust_coverage": summary(cluster_covered),
        "cluster_paired_coverage_difference": summary(cluster_covered - iid_covered),
        "missing_high_stratum_identified_set": [.04, .24],
    }


def competing_risks():
    rng = np.random.default_rng(57032)
    r, n = 8000, 200
    first = rng.choice(3, size=(r, n), p=[.7, .1, .2])
    second = rng.choice(3, size=(r, n), p=[.7, .2, .1])
    missing_rank = rng.random((r, n))
    truth = .1 + .7 * .2
    rows = {}
    for informative in (False, True):
        risk = missing_rank >= (np.where(first == 1, .8, .2) if informative else .2)
        available = risk.sum(axis=1)
        h11 = (risk & (first == 1)).sum(axis=1) / available
        h12 = (risk & (first == 2)).sum(axis=1) / available
        later_risk = risk & (first == 0)
        h21 = (later_risk & (second == 1)).sum(axis=1) / later_risk.sum(axis=1)
        aj = h11 + (1 - h11 - h12) * h21
        km = 1 - (1 - h11) * (1 - h21)
        # All retained units resolve their status: AJ then equals this ratio.
        complete = ((risk & (first == 1)) | (later_risk & (second == 1))).sum(axis=1) / available
        assert np.max(np.abs(complete - aj)) < 1e-14
        all_baseline_units = complete * available / n
        rows["informative" if informative else "independent"] = {
            "aj": summary(aj), "km_competitor_as_censor": summary(km),
            "complete_cases": summary(complete), "missing_as_none": summary(all_baseline_units),
            "paired_km_minus_aj": summary(km - aj),
            "aj_rmse": float(np.sqrt(np.mean((aj - truth)**2))),
        }
    return {"seed": 57032, "replicates": r, "n": n, "true_cumulative_incidence": truth, "results": rows}


def monitor(mode):
    distribution = np.array([1.])
    crossing = 0.
    for t in range(1, 201):
        distribution = (np.r_[distribution, 0] + np.r_[0, distribution]) / 2
        if t < 20 or (mode == "fixed" and t != 200):
            continue
        cutoff = Z * math.sqrt(t)
        if mode == "union":
            cutoff = math.sqrt(2 * t * math.log(2 * 181 / .05))
        hit = np.abs(2 * np.arange(t + 1) - t) > cutoff
        crossing += float(distribution[hit].sum())
        distribution[hit] = 0
    assert math.isclose(crossing + float(distribution.sum()), 1, abs_tol=1e-12)
    return crossing


def evaluation():
    forecasts = np.array([[.8, .8, .2, .2], [.4, .4, .6, .6]])
    vintage1, vintage2 = np.array([0, 0, 1, 1]), np.array([1, 1, 0, 0])
    selected_labels = np.array([1, 0])  # same observable labels in two worlds
    unknown_worlds = np.array([[0, 0], [1, 1]])
    risk = np.array([.1, .9])
    constant = np.array([.5, .5])
    conditional_expected = risk * (1 - constant)**2 + (1 - risk) * constant**2
    best_expected = risk * (1 - risk)
    return {
        "monitor_first_crossing": {k: monitor(k) for k in ("fixed", "peek", "union")},
        "vintage_brier_model_a_b": [((forecasts - truth)**2).mean(axis=1).tolist() for truth in (vintage1, vintage2)],
        "selection_observed_risk": float(selected_labels.mean()),
        "selection_full_risk_two_worlds": ((selected_labels.sum() + unknown_worlds.sum(axis=1)) / 4).tolist(),
        "group_calibration_errors": (constant - risk).tolist(),
        "marginal_calibration_error": float((constant - risk).mean()),
        "group_brier_constant_vs_oracle": [conditional_expected.tolist(), best_expected.tolist()],
        "selective_score_example": {
            "conditional_brier_before_after": [.25, .09],
            "request_coverage_before_after": [1, .5],
            "per_request_loss_before": .25,
            "per_request_loss_after_with_cost": {str(cost): .5 * .09 + .5 * cost for cost in (.1, .5)},
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = {
        "B-E001": exact_binomial(), "B-E002": borrowing(),
        "B-E003": standardization(), "B-E004": competing_risks(), "B-E005": evaluation(),
    }
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

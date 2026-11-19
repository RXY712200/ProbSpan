"""B-E007: comparative forecasts on an archived season split."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.special import betaln, logsumexp

INPUT_SHA256 = "cd0f074d7e4acd394e5a538314eec04f0d332d764211b889dc62bc81a3a55d5e"


def load(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != INPUT_SHA256:
        raise ValueError(f"Archived input hash mismatch: {digest}")
    with path.open(encoding="utf-8", newline="") as stream:
        data = list(csv.DictReader(stream, delimiter="\t"))
    early = np.array([int(r["Hits"]) for r in data])
    late_hits = np.array([int(r["SeasonHits"]) - int(r["Hits"]) for r in data])
    late_n = np.array([int(r["RemainingAt-Bats"]) for r in data])
    assert len(data) == 18 and all(int(r["At-Bats"]) == 45 for r in data)
    assert all(int(r["SeasonAt-Bats"]) == int(r["RemainingAt-Bats"]) + 45 for r in data)
    assert np.all((0 <= late_hits) & (late_hits <= late_n))
    assert np.allclose(late_hits / late_n, [float(r["RemainingAverage"]) for r in data], atol=.000051)
    return early, late_hits, late_n


def pooling(early, size, max_concentration):
    mean, log_concentration = np.meshgrid(
        np.linspace(.05, .65, size), np.linspace(0, np.log(max_concentration), size),
        indexing="ij",
    )
    concentration = np.exp(log_concentration)
    alpha = mean[..., None] * concentration[..., None]
    beta = (1 - mean[..., None]) * concentration[..., None]
    marginal = (betaln(alpha + early, beta + 45 - early) - betaln(alpha, beta)).sum(axis=-1)
    best = np.unravel_index(np.argmax(marginal), marginal.shape)
    conditional_means = (alpha + early) / (concentration[..., None] + 45)
    # Trapezoidal weights integrate the continuous uniform prior over means/log concentration.
    edges = np.ones(size)
    edges[[0, -1]] = .5
    log_weights = marginal + np.log(edges[:, None] * edges[None, :])
    weights = np.exp(log_weights - logsumexp(log_weights))
    return conditional_means[best], (conditional_means * weights[..., None]).sum(axis=(0, 1)), {
        "resolution": size, "prior_max_concentration": max_concentration,
        "ml_mean": float(mean[best]), "ml_concentration": float(concentration[best]),
        "ml_on_grid_edge": any(i in (0, size - 1) for i in best),
        "posterior_mass_last_concentration_decile_log_grid": float(weights[:, -max(1, size // 10):].sum()),
    }


def evaluate(p, y, n):
    binary_losses = {
        "brier": (y * (1 - p)**2 + (n - y) * p**2) / n,
        "log": -(y * np.log(p) + (n - y) * np.log1p(-p)) / n,
    }
    return {
        key: {"at_bat_weighted": float(loss @ n / n.sum()), "player_weighted": float(loss.mean())}
        for key, loss in binary_losses.items()
    }


def analyze(path):
    early, late_hits, late_n = load(path)
    forecasts = {
        "no_pool": (early + .5) / 46,
        "pool": np.full(18, (early.sum() + .5) / (45 * len(early) + 1)),
    }
    eb, hier, diag = pooling(early, 121, 2048)
    _, finer, fine_diag = pooling(early, 241, 2048)
    _, prior, wider_diag = pooling(early, 241, 16384)
    forecasts.update(eb=eb, hierarchical=hier, hierarchical_wider_prior=prior)
    losses = {k: evaluate(v, late_hits, late_n) for k, v in forecasts.items()}
    # Exclude a player's test contribution, keeping every training forecast fixed.
    loo_difference = []
    for keep in ~np.eye(18, dtype=bool):
        def score(p):
            return evaluate(p[keep], late_hits[keep], late_n[keep])["brier"]["at_bat_weighted"]

        loo_difference.append(score(hier) - score(forecasts["pool"]))
    return {
        "input_sha256": INPUT_SHA256, "players": len(early),
        "early_at_bats": int(len(early) * 45), "late_at_bats": int(late_n.sum()),
        "late_hits": int(late_hits.sum()), "metrics": losses,
        "grid_diagnostics": [diag, fine_diag, wider_diag],
        "grid_refinement_max_prediction_change": float(np.max(np.abs(finer - hier))),
        "wider_prior_max_prediction_change": float(np.max(np.abs(prior - hier))),
        "hier_minus_pool_drop_one_test_brier_range": [min(loo_difference), max(loo_difference)],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps({"B-E007": analyze(args.archive)}, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()

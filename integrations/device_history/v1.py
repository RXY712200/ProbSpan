"""Invoke the installed-library consumer only after a successful count review."""

from dataclasses import dataclass
import json
from math import isfinite
import subprocess

from .evidence import Applicability, Path, Review


@dataclass(frozen=True)
class V1History:
    review: Review
    status: str
    history: dict | None = None
    algorithm: str = "probspan_history_estimate"
    result_type: str = "v1_history"


def _check_payload(history, size):
    if (type(history["size"]) is not int or history["size"] != size
            or (history["product_version"], history["abi_version"],
                history["model_version"], history["gate_version"]) != ("1.0.0", 1, 1, 1)):
        raise ValueError("incompatible result")
    state, ready, estimate = (history[k] for k in ("state", "statistically_ready", "estimate"))
    if size == 0:
        if state != "NO_HISTORY" or ready is not False or estimate is not None:
            raise ValueError("malformed empty history")
        return
    if state not in ("INSUFFICIENT", "VALID") or ready is not (state == "VALID"):
        raise ValueError("malformed gate result")
    low, mean, high = (estimate[k] for k in ("lower", "mean", "upper"))
    if (any(type(x) not in (int, float) or not isfinite(x) for x in (low, mean, high))
            or not 0 <= low <= mean <= high <= 1):
        raise ValueError("malformed estimate")


def estimate_v1(review: Review, executable) -> V1History:
    if (review.path not in (Path.STRICT, Path.POOL)
            or review.applicability != Applicability.SUPPORTED or review.counts is None):
        return V1History(review, "unavailable_review")
    counts, = review.counts
    try:
        # Use an explicit local executable. No shell, dynamic loader or raw
        # struct serialization is involved in crossing this process boundary.
        completed = subprocess.run([str(executable.resolve()), str(counts.events),
                                   str(counts.complements)], check=True, capture_output=True,
                                   text=True, encoding="ascii", timeout=15)
        history = json.loads(completed.stdout)
        if type(history["c_status"]) is not int:
            raise ValueError("malformed status")
        if history["c_status"] != 0:
            return V1History(review, "c_failure", {"c_status": history["c_status"]})
        _check_payload(history, counts.size)
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError, OverflowError):
        return V1History(review, "consumer_failure")
    return V1History(review, "ok", history)

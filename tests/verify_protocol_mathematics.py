"""Numerical verification of review equations; no dataset or model fitting.
Run from any checkout: bundled Python tests/verify_protocol_mathematics.py.
"""
from __future__ import annotations
import hashlib
import json
import math
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from statistics import NormalDist
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "logs/mathematical_preflight.json"
checks = []
def record(name, details):
    checks.append({"name": name, "status": "PASS", "details": details})

def gaussian_conditioning():
    gamma = np.array([-0.25, 0.40])
    sigma_g = np.array([[0.30, 0.07], [0.07, 0.20]])
    prior_mean = np.array([0.20, -0.10])
    age_beta = 4.0
    sigma_z, sigma_r = 0.45, 0.30
    maximum_error = 0.0
    cases = 0
    for length in (1, 2, 30):
        t = np.arange(101 - length, 101, dtype=float)
        B = np.column_stack((np.ones(length), (t - 100.0) / 30.0))
        z = B @ prior_mean + 0.1 * np.sin(t / 7.0)
        for rho in (-0.50, 0.0, 0.50, 0.95):
            K = rho ** np.abs(t[:, None] - t[None, :])
            noise = sigma_z**2 * K
            Czz = B @ sigma_g @ B.T + noise
            Czy = B @ sigma_g @ gamma
            Cyy = gamma @ sigma_g @ gamma + sigma_r**2
            joint = np.block([[Czz, Czy[:, None]], [Czy[None, :], np.array([[Cyy]])]])
            np.linalg.cholesky(joint)
            centered = z - B @ prior_mean
            # Direct conditional joint (z,y), independently of the latent posterior.
            direct_mean = age_beta + gamma @ prior_mean + Czy @ np.linalg.solve(Czz, centered)
            direct_var = Cyy - Czy @ np.linalg.solve(Czz, Czy)
            # Latent posterior calculated using precision form rather than draft formula.
            prior_precision = np.linalg.solve(sigma_g, np.eye(2))
            posterior_precision = prior_precision + B.T @ np.linalg.solve(noise, B)
            latent_var = np.linalg.solve(posterior_precision, np.eye(2))
            latent_mean = latent_var @ (prior_precision @ prior_mean + B.T @ np.linalg.solve(noise, z))
            latent_response_mean = age_beta + gamma @ latent_mean
            latent_response_var = sigma_r**2 + gamma @ latent_var @ gamma
            np.testing.assert_allclose([direct_mean, direct_var],
                                       [latent_response_mean, latent_response_var],
                                       rtol=1e-10, atol=1e-10)
            np.linalg.cholesky(latent_var)
            assert direct_var >= sigma_r**2 - 1e-12
            # Joint log density equals marginal sensor plus conditional response density.
            y = direct_mean + 0.2
            vector = np.r_[centered, y - age_beta - gamma @ prior_mean]
            joint_ld = -0.5 * ((length + 1) * math.log(2 * math.pi) +
                              np.linalg.slogdet(joint)[1] + vector @ np.linalg.solve(joint, vector))
            sensor_ld = -0.5 * (length * math.log(2 * math.pi) +
                               np.linalg.slogdet(Czz)[1] + centered @ np.linalg.solve(Czz, centered))
            response_ld = -0.5 * (math.log(2 * math.pi * direct_var) +
                                 (y - direct_mean)**2 / direct_var)
            np.testing.assert_allclose(joint_ld, sensor_ld + response_ld, rtol=1e-10, atol=1e-10)
            maximum_error = max(maximum_error,
                                abs(direct_mean - latent_response_mean),
                                abs(direct_var - latent_response_var),
                                abs(joint_ld - sensor_ld - response_ld))
            cases += 1
    record("Gaussian conditional moments and joint density factorization",
           {"cases": cases, "history_lengths": [1, 2, 30],
            "rho": [-0.5, 0.0, 0.5, 0.95], "maximum_absolute_error": maximum_error,
            "scope": "Fixed positive-definite example parameters; no inference or identifiability claim."})

def interval_score_and_conformal():
    def score(y, lower, upper):
        assert lower <= upper
        return upper - lower + 20 * max(lower - y, 0) + 20 * max(y - upper, 0)
    for y, expected in [(15, 10), (5, 110), (25, 110), (10, 10), (20, 10)]:
        assert score(y, 10, 20) == expected
    # Exact decimal multiplication avoids a floating-point off-by-one at integer ranks.
    rank = lambda n: int((Decimal(n + 1) * Decimal("0.90")).to_integral_value(rounding=ROUND_CEILING))
    assert rank(8) > 8 and rank(9) == 9 and rank(25) == 24
    precision = json.loads((ROOT / "logs/sample_precision.json").read_text(encoding="utf-8"))
    for row in precision["conformal_rank_scenarios"]:
        assert row["rank"] == rank(row["n"])
        assert row["finite"] == (rank(row["n"]) <= row["n"])
    # For supported outcomes, clipping a lower negative endpoint to zero preserves membership.
    for lower in (-10.0, 0.0, 5.0):
        for upper in (5.0, 20.0):
            if lower > upper:
                continue
            for q in (0.0, 2.0, 10.0):
                L, U = lower - q, upper + q
                for y in np.arange(0.0, 31.0):
                    assert (L <= y <= U) == (max(0.0, L) <= y <= max(0.0, U))
    record("Interval score, finite conformal rank, nonnegative support",
           {"score_cases": 5, "rank_n25": rank(25),
            "coverage_guarantee": "Not established for official test cutoff distribution."})

def precision_calculations():
    precision = json.loads((ROOT / "logs/sample_precision.json").read_text(encoding="utf-8"))
    z = NormalDist().inv_cdf(0.975)
    n, successes = 100, 90
    p = successes / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    np.testing.assert_allclose(precision["coverage_90_of_100_wilson95"],
                               [center - half, center + half], rtol=1e-12, atol=1e-12)
    assert math.ceil(z*z*0.9*0.1/0.02**2) == 865
    assert math.ceil(z*z*0.9*0.1/0.05**2) == 139
    mde = (NormalDist().inv_cdf(0.95) + NormalDist().inv_cdf(0.80))/math.sqrt(100)
    np.testing.assert_allclose(mde, precision["standardized_paired_mde_80pct_one_sided_0_05_normal_approx"])
    record("Wilson and normal-approximation planning precision",
           {"hypothetical_wilson95": [center - half, center + half],
            "scope": "Hypothetical 90 successes, not observed model coverage."})

def bootstrap_pivot_direction():
    mean, se, q025, q05, q975 = -3.0, 0.8, -2.1, -1.7, 2.4
    lower, upper = mean - q975 * se, mean - q025 * se
    one_sided_upper = mean - q05 * se
    for population_mean in np.linspace(-8, 2, 200):
        pivot = (mean - population_mean) / se
        assert (q025 <= pivot <= q975) == (lower <= population_mean <= upper)
        assert (q05 <= pivot) == (population_mean <= one_sided_upper)
    record("Bootstrap-t interval and directional upper-bound inversion",
           {"scope": "Algebraic inversion only; bootstrap adequacy/stability not evaluated."})

def main():
    if OUTPUT.exists():
        raise FileExistsError("Preserve original verification log; use a new version before rerunning.")
    gaussian_conditioning()
    interval_score_and_conformal()
    precision_calculations()
    bootstrap_pivot_direction()
    result = {"status": "PASS", "scope": "Numerical preimplementation equation checks only",
              "numpy_version": np.__version__, "checks": checks,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "model_fitting_performed": False, "test_files_read": False,
              "sampling_validated": False, "scientific_validation": "DEFERRED"}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

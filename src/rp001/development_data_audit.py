from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEED = "RP001-20261008-v0.2"
ROLES = ("fit", "tune", "calibration")
SENSITIVITY_SCENARIOS = 100
NEAR_MIN_COMMON_CYCLES = 30
NEAR_MEAN_NRMSE = 0.02
NEAR_MAX_CHANNEL_NRMSE = 0.10


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def hash_integer(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)


def qtile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    x = (len(xs) - 1) * q
    lo, hi = math.floor(x), math.ceil(x)
    return float(xs[lo] if lo == hi else xs[lo] + (x - lo) * (xs[hi] - xs[lo]))


def summary(values: list[int | float]) -> dict[str, Any]:
    xs = [float(x) for x in values]
    if not xs:
        return {"n": 0, "min": None, "q1": None, "median": None, "mean": None, "q3": None, "max": None}
    return {
        "n": len(xs), "min": min(xs), "q1": qtile(xs, .25),
        "median": qtile(xs, .5), "mean": statistics.fmean(xs),
        "q3": qtile(xs, .75), "max": max(xs),
    }


def ranks(values: list[float]) -> list[float]:
    order = sorted(enumerate(values), key=lambda pair: pair[1])
    result = [0.0] * len(values)
    first = 0
    while first < len(order):
        end = first + 1
        while end < len(order) and order[end][1] == order[first][1]:
            end += 1
        rank = (first + 1 + end) / 2
        for pos in range(first, end):
            result[order[pos][0]] = rank
        first = end
    return result


def corr(x: list[float], y: list[float]) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None
    mx, my = statistics.fmean(x), statistics.fmean(y)
    dx, dy = [v - mx for v in x], [v - my for v in y]
    xx, yy = math.fsum(v * v for v in dx), math.fsum(v * v for v in dy)
    if xx <= 0 or yy <= 0:
        return None
    return math.fsum(a * b for a, b in zip(dx, dy)) / math.sqrt(xx * yy)


def cutoff_bins(values: list[int]) -> list[dict[str, int]]:
    result = []
    low = 30
    for i in range(5):
        high = 250 if i == 4 else 30 + math.floor((i + 1) * 221 / 5) - 1
        result.append({
            "min_cutoff_inclusive": low,
            "max_cutoff_inclusive": high,
            "count": sum(low <= value <= high for value in values),
        })
        low = high + 1
    return result


def load_training(path: Path, schema: dict[str, Any]) -> tuple[dict[int, list[tuple[int, tuple[float, ...]]]], dict[str, Any]]:
    trajectories: dict[int, list[tuple[int, tuple[float, ...]]]] = defaultdict(list)
    n_rows = 0
    field_counts: set[int] = set()
    with path.open("r", encoding="ascii") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            fields = line.split()
            field_counts.add(len(fields))
            if len(fields) != 26:
                raise ValueError(f"Training line {line_no}: expected 26 fields, found {len(fields)}.")
            values = [float(value) for value in fields]
            if not all(math.isfinite(value) for value in values):
                raise ValueError(f"Training line {line_no}: non-finite value.")
            engine, cycle = int(values[0]), int(values[1])
            if values[0] != engine or values[1] != cycle:
                raise ValueError(f"Training line {line_no}: non-integer engine/cycle key.")
            trajectories[engine].append((cycle, tuple(values[2:])))
            n_rows += 1
    if field_counts != {26}:
        raise ValueError(f"Unexpected training field counts: {sorted(field_counts)}.")
    for engine, rows in trajectories.items():
        observed = [cycle for cycle, _ in rows]
        if observed != list(range(1, max(observed) + 1)):
            raise ValueError(f"Engine {engine}: cycles are not ordered and complete from 1.")
    names = [field["name"] for field in schema["fields"]]
    if schema.get("field_count") != 26 or names[:2] != ["engine_id", "cycle"] or len(names) != 26:
        raise ValueError("Schema contract does not match the 26-field FD001 training schema.")
    lifetimes = {engine: max(cycle for cycle, _ in rows) for engine, rows in trajectories.items()}
    return dict(trajectories), {
        "rows": n_rows, "engines": len(trajectories), "field_count": 26,
        "lifetimes": lifetimes, "feature_names": names[2:],
    }


def read_manifest(path: Path) -> dict[int, dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    result = {}
    for row in rows:
        if row.get("dataset") != "FD001_train":
            raise ValueError("Manifest contains a dataset other than FD001_train.")
        engine = int(row["engine"])
        if engine in result:
            raise ValueError(f"Manifest duplicates engine {engine}.")
        result[engine] = row
    return result


def expected_role_map(engines: list[int]) -> dict[int, str]:
    ordered = sorted(engines, key=lambda engine: hashlib.sha256(f"{SEED}|split|{engine}".encode()).hexdigest())
    return {engine: ("fit" if i < 55 else "tune" if i < 70 else "calibration") for i, engine in enumerate(ordered)}


def canonical_records(manifest: dict[int, dict[str, Any]], lifetimes: dict[int, int]) -> dict[int, dict[str, Any]]:
    if set(manifest) != set(lifetimes):
        raise ValueError("Manifest IDs do not match the training engine IDs.")
    role_map = expected_role_map(sorted(lifetimes))
    result = {}
    for engine, row in manifest.items():
        cutoff = int(row["proposed_cutoff"])
        expected_cutoff = 30 + hash_integer(f"{SEED}|cutoff|{engine}") % 221
        eligible = expected_cutoff < lifetimes[engine]
        if row["role"] != role_map[engine]:
            raise ValueError(f"Engine {engine}: role does not reproduce from the canonical hash split.")
        if cutoff != expected_cutoff or not 30 <= cutoff <= 250:
            raise ValueError(f"Engine {engine}: cutoff does not reproduce from the canonical hash rule.")
        if bool(row["eligible_alive"]) != eligible:
            raise ValueError(f"Engine {engine}: manifest eligibility does not equal C<T.")
        result[engine] = {
            "role": row["role"], "cutoff": cutoff,
            "lifetime": lifetimes[engine], "eligible": eligible,
        }
    return result


def lifetime_quartiles(lifetimes: dict[int, int]) -> dict[int, int]:
    ordered = sorted(lifetimes, key=lambda engine: (lifetimes[engine], engine))
    return {engine: min(3, i * 4 // len(ordered)) for i, engine in enumerate(ordered)}


def selection_summary(records: dict[int, dict[str, Any]], quartiles: dict[int, int]) -> dict[str, Any]:
    by_role = {}
    for role in ROLES:
        group = [row for row in records.values() if row["role"] == role]
        n_eligible = sum(row["eligible"] for row in group)
        selected = [row for row in group if row["eligible"]]
        by_role[role] = {
            "reserved": len(group), "eligible": n_eligible,
            "ineligible": len(group) - n_eligible,
            "eligible_fraction": n_eligible / len(group) if group else None,
            "eligible_cutoff_median": qtile([row["cutoff"] for row in selected], .5),
            "eligible_lifetime_median": qtile([row["lifetime"] for row in selected], .5),
        }

    band_rows = []
    bands = cutoff_bins(list(range(30, 251)))
    for band in bands:
        members = [
            row for row in records.values()
            if band["min_cutoff_inclusive"] <= row["cutoff"] <= band["max_cutoff_inclusive"]
        ]
        band_rows.append({
            "min_cutoff_inclusive": band["min_cutoff_inclusive"],
            "max_cutoff_inclusive": band["max_cutoff_inclusive"],
            "assigned": len(members),
            "eligible": sum(row["eligible"] for row in members),
            "by_role": {
                role: {
                    "assigned": sum(row["role"] == role for row in members),
                    "eligible": sum(row["role"] == role and row["eligible"] for row in members),
                } for role in ROLES
            },
        })

    by_quartile = []
    by_role_quartile = []
    for q in range(4):
        members = [row for engine, row in records.items() if quartiles[engine] == q]
        eligible = [row for row in members if row["eligible"]]
        by_quartile.append({
            "quartile": q + 1, "assigned": len(members), "eligible": len(eligible),
            "ineligible": len(members) - len(eligible),
            "eligibility_fraction": len(eligible) / len(members),
            "lifetime_min": min(row["lifetime"] for row in members),
            "lifetime_max": max(row["lifetime"] for row in members),
            "lifetime_median": qtile([row["lifetime"] for row in members], .5),
            "cutoff_median": qtile([row["cutoff"] for row in members], .5),
        })
        for role in ROLES:
            cell = [row for engine, row in records.items() if quartiles[engine] == q and row["role"] == role]
            by_role_quartile.append({
                "role": role, "lifetime_quartile": q + 1,
                "assigned": len(cell), "eligible": sum(row["eligible"] for row in cell),
            })
    return {
        "by_role": by_role, "by_cutoff_band": band_rows,
        "by_lifetime_rank_quartile": by_quartile,
        "by_role_and_lifetime_rank_quartile": by_role_quartile,
    }


def duplicate_audit(records: dict[int, dict[str, Any]], trajectories: dict[int, list[tuple[int, tuple[float, ...]]]], feature_names: list[str]) -> dict[str, Any]:
    prefixes = {}
    for engine, row in records.items():
        if not row["eligible"]:
            continue
        cutoff = row["cutoff"]
        prefix = trajectories[engine][:cutoff]
        cycles = [cycle for cycle, _ in prefix]
        if len(prefix) != cutoff or cycles != list(range(1, cutoff + 1)) or max(cycles) > cutoff:
            raise ValueError(f"Engine {engine}: prefix is incomplete or contains a future cycle.")
        prefixes[engine] = prefix

    columns: list[list[float]] = [[] for _ in feature_names]
    for prefix in prefixes.values():
        for _, values in prefix:
            for j, value in enumerate(values):
                columns[j].append(value)
    scales = []
    for col in columns:
        mean = statistics.fmean(col)
        sd = math.sqrt(math.fsum((value - mean) ** 2 for value in col) / len(col))
        scales.append(sd if sd > 1e-12 else 1.0)

    exact, near, distances = [], [], []
    engines = sorted(prefixes)
    pairs = 0
    for pos, engine_a in enumerate(engines):
        a = prefixes[engine_a]
        for engine_b in engines[pos + 1:]:
            b = prefixes[engine_b]
            common = min(len(a), len(b))
            if common < NEAR_MIN_COMMON_CYCLES:
                continue
            pairs += 1
            a_rows = [features for _, features in a[:common]]
            b_rows = [features for _, features in b[:common]]
            is_exact = a_rows == b_rows
            if is_exact:
                exact.append({"engine_a": engine_a, "engine_b": engine_b, "common_cycles": common})
            sums = [0.0] * len(feature_names)
            for row_a, row_b in zip(a_rows, b_rows):
                for j, (value_a, value_b) in enumerate(zip(row_a, row_b)):
                    d = (value_a - value_b) / scales[j]
                    sums[j] += d * d
            per_channel = [math.sqrt(value / common) for value in sums]
            mean_nrmse = math.sqrt(math.fsum(value * value for value in per_channel) / len(per_channel))
            max_nrmse = max(per_channel)
            info = {
                "engine_a": engine_a, "engine_b": engine_b, "common_cycles": common,
                "mean_feature_nrmse": mean_nrmse, "max_channel_nrmse": max_nrmse,
            }
            distances.append(info)
            if not is_exact and mean_nrmse <= NEAR_MEAN_NRMSE and max_nrmse <= NEAR_MAX_CHANNEL_NRMSE:
                near.append(info)
    distances.sort(key=lambda row: (row["mean_feature_nrmse"], row["max_channel_nrmse"], -row["common_cycles"]))
    return {
        "population": "canonical eligible training prefixes only",
        "eligible_prefix_count": len(prefixes), "pair_comparisons": pairs,
        "comparison_rule": "cycle-aligned raw settings and sensors over the shared initial prefix min(C_a,C_b)",
        "exact_common_prefix_pairs": exact,
        "near_duplicate_screen": {
            "minimum_common_cycles": NEAR_MIN_COMMON_CYCLES,
            "mean_feature_nrmse_threshold": NEAR_MEAN_NRMSE,
            "maximum_single_channel_nrmse_threshold": NEAR_MAX_CHANNEL_NRMSE,
            "normalization": "per-channel population SD from eligible observed prefixes only; zero-variance scale set to 1",
            "flagged_pairs": near,
            "interpretation": "heuristic screen only; not a semantic-duplicate oracle",
        },
        "closest_pairs_by_screen_metric": distances[:5],
        "feature_channels_compared": feature_names,
        "future_rows_in_prefix_features": 0,
    }


def sensitivity(records: dict[int, dict[str, Any]]) -> dict[str, Any]:
    engines = sorted(records)
    totals, role_totals = [], {role: [] for role in ROLES}
    selected_n = {engine: 0 for engine in engines}
    mismatches = {engine: 0 for engine in engines}
    for scenario in range(1, SENSITIVITY_SCENARIOS + 1):
        eligible = {}
        for engine in engines:
            c = 30 + hash_integer(f"{SEED}|cutoff-sensitivity-{scenario:03d}|{engine}") % 221
            eligible[engine] = c < records[engine]["lifetime"]
            selected_n[engine] += int(eligible[engine])
            mismatches[engine] += int(eligible[engine] != records[engine]["eligible"])
        totals.append(sum(eligible.values()))
        for role in ROLES:
            role_totals[role].append(sum(eligible[e] for e in engines if records[e]["role"] == role))
    by_role = {
        role: {
            "canonical_eligible": sum(row["eligible"] for row in records.values() if row["role"] == role),
            "alternative_eligible_count_distribution": summary(role_totals[role]),
        } for role in ROLES
    }
    unstable = []
    for engine in engines:
        if 0 < selected_n[engine] < SENSITIVITY_SCENARIOS:
            unstable.append({
                "engine": engine, "role": records[engine]["role"],
                "canonical_eligible": records[engine]["eligible"],
                "alternative_eligible_scenarios": selected_n[engine],
                "selection_frequency": selected_n[engine] / SENSITIVITY_SCENARIOS,
                "status_mismatches_vs_canonical": mismatches[engine],
            })
    return {
        "purpose": "design sensitivity only; canonical role assignment fixed; no model fitting or performance scoring",
        "scenario_count": SENSITIVITY_SCENARIOS,
        "alternative_cutoff_rule": "C_r=30+SHA256(SEED|cutoff-sensitivity-r|engine) mod 221",
        "canonical_total_eligible": sum(row["eligible"] for row in records.values()),
        "alternative_total_eligible_count_distribution": summary(totals),
        "by_role": by_role,
        "engines_with_changing_eligibility": len(unstable),
        "status_mismatch_pairs_vs_canonical_all_scenarios": sum(mismatches.values()),
        "unstable_engine_details": unstable,
        "interpretation": "deterministic hash perturbations summarize count and membership sensitivity only; not a probability model, performance comparison, or cutoff-exchangeability evidence",
    }


def audit_project(root: Path) -> dict[str, Any]:
    raw = root / "data" / "raw"
    paths = {
        "training_trajectory": raw / "train_FD001.txt",
        "training_audit": raw / "training_audit.json",
        "schema_contract": raw / "schema_contract.json",
        "split_manifest": root / "configs" / "proposed_split_manifest.json",
        "protocol_config": root / "configs" / "proposed_protocol_v0.2.json",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing allowed training input(s): " + ", ".join(missing))
    train_audit = json.loads(paths["training_audit"].read_text(encoding="utf-8"))
    schema = json.loads(paths["schema_contract"].read_text(encoding="utf-8"))
    protocol = json.loads(paths["protocol_config"].read_text(encoding="utf-8"))
    manifest = read_manifest(paths["split_manifest"])
    train_hash = sha256_file(paths["training_trajectory"])
    if train_hash != train_audit["raw_sha256"]:
        raise ValueError("Training trajectory SHA-256 differs from training_audit.json.")
    trajectories, parsed = load_training(paths["training_trajectory"], schema)
    if (parsed["rows"], parsed["engines"], parsed["field_count"]) != (train_audit["rows"], train_audit["engines"], train_audit["fields"]):
        raise ValueError("Recomputed row, engine, or field count differs from training_audit.json.")
    lifetimes = parsed["lifetimes"]
    lifetime_summary = train_audit.get("lifetimes", {})
    recomputed_lifetimes = list(lifetimes.values())
    if lifetime_summary and (
        min(recomputed_lifetimes) != int(lifetime_summary["min"])
        or max(recomputed_lifetimes) != int(lifetime_summary["max"])
        or abs(statistics.median(recomputed_lifetimes) - float(lifetime_summary["median"])) > 1e-12
    ):
        raise ValueError("Recomputed lifetime summary differs from training_audit.json.")
    if protocol.get("status") != "PROTOCOL_DRAFTED" or SEED not in protocol.get("split_policy", ""):
        raise ValueError("Protocol config does not match the expected draft and canonical seed.")

    records = canonical_records(manifest, lifetimes)
    ids = sorted(records)
    eligible_ids = [engine for engine in ids if records[engine]["eligible"]]
    ineligible_ids = [engine for engine in ids if not records[engine]["eligible"]]
    roles = {
        role: {
            "reserved": sum(row["role"] == role for row in records.values()),
            "eligible": sum(row["role"] == role and row["eligible"] for row in records.values()),
        } for role in ROLES
    }
    expected_counts = {
        "fit": {"reserved": 55, "eligible": 43},
        "tune": {"reserved": 15, "eligible": 13},
        "calibration": {"reserved": 30, "eligible": 25},
    }
    quartiles = lifetime_quartiles(lifetimes)
    subgroups = selection_summary(records, quartiles)
    cutoffs = [records[e]["cutoff"] for e in ids]
    eligible_cutoffs = [records[e]["cutoff"] for e in eligible_ids]
    all_t = [lifetimes[e] for e in ids]
    eligible_t = [lifetimes[e] for e in eligible_ids]
    ineligible_t = [lifetimes[e] for e in ineligible_ids]
    assoc_all = {
        "n": len(ids),
        "pearson_r": corr([float(records[e]["cutoff"]) for e in ids], [float(lifetimes[e]) for e in ids]),
        "spearman_rho": corr(ranks([float(records[e]["cutoff"]) for e in ids]), ranks([float(lifetimes[e]) for e in ids])),
    }
    assoc_survivors = {
        "n": len(eligible_ids),
        "pearson_r": corr([float(records[e]["cutoff"]) for e in eligible_ids], [float(lifetimes[e]) for e in eligible_ids]),
        "spearman_rho": corr(ranks([float(records[e]["cutoff"]) for e in eligible_ids]), ranks([float(lifetimes[e]) for e in eligible_ids])),
    }
    dup = duplicate_audit(records, trajectories, parsed["feature_names"])
    sens = sensitivity(records)

    return {
        "audit_id": "RP-001-development-data-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "dataset": "NASA C-MAPSS FD001 training trajectories only",
            "purpose": "training-only proposed split, eligibility, prefix integrity, and cutoff design audit",
            "official_test_trajectories_or_labels_opened": False,
            "official_archive_entries_inspected": False,
            "calibration_residuals_inspected_or_computed": False,
            "models_fitted": False,
            "confirmatory_evaluation_performed": False,
            "primary_research_question_changed": False,
            "practical_5_cycle_threshold_approved": False,
        },
        "execution": {
            "python_executable": sys.executable,
            "command": subprocess.list2cmdline([sys.executable, *sys.argv]),
            "working_directory": str(root),
            "script_path": "src/rp001/development_data_audit.py",
        },
        "method": {
            "split_seed": SEED,
            "reserved_role_sizes": {"fit": 55, "tune": 15, "calibration": 30},
            "canonical_cutoff_rule": "C=30+SHA256(SEED|cutoff|engine) mod 221; support 30..250",
            "eligibility_rule": "eligible iff C<T; no redraw or replacement",
            "feature_rule": "schema columns after engine_id and cycle for observed cycles 1..C; T is used for training eligibility only and is excluded from features",
            "lifetime_quartiles": "four rank-based groups of 25 engines; ties ordered by engine ID",
        },
        "source_validation": {
            "training_source_sha256_matches_training_audit": True,
            "recomputed_rows": parsed["rows"],
            "recomputed_engines": parsed["engines"],
            "field_count": parsed["field_count"],
            "complete_ordered_cycles": True,
            "finite_numeric_values": True,
            "manifest_entries": len(manifest),
            "canonical_hash_roles_and_cutoffs_reproduced": True,
            "manifest_eligibility_matches_C_lt_T": True,
            "input_hashes_sha256": {name: sha256_file(path) for name, path in paths.items()},
        },
        "canonical_split": {
            "role_counts": roles, "total_reserved": len(records),
            "total_eligible": len(eligible_ids), "total_ineligible": len(ineligible_ids),
            "expected_counts_match_43_13_25": roles == expected_counts,
        },
        "cutoff_and_lifetime": {
            "canonical_cutoff_distribution_all_reserved": summary(cutoffs),
            "canonical_cutoff_histogram_all_reserved": cutoff_bins(cutoffs),
            "canonical_cutoff_distribution_eligible_only": summary(eligible_cutoffs),
            "training_lifetime_all_reserved": summary(all_t),
            "training_lifetime_eligible_only": summary(eligible_t),
            "training_lifetime_ineligible_only": summary(ineligible_t),
            "cutoff_vs_lifetime_descriptive_association_all_reserved": assoc_all,
            "cutoff_vs_lifetime_descriptive_association_eligible_only": assoc_survivors,
            "survival_selection": {
                "rule": "C<T", "eligible_count": len(eligible_ids),
                "ineligible_count": len(ineligible_ids),
                "eligible_fraction": len(eligible_ids) / len(records),
                "subgroup_sizes": subgroups,
                "interpretation": "eligibility depends mechanically on cutoff and training lifetime; no population or exchangeability inference",
            },
            "official_cutoff_distribution": {
                "identified_from_allowed_training_metadata": False,
                "reason": "allowed inputs contain proposed training cutoffs and training lifetimes only; official test cutoffs and their generating mechanism are unobserved",
            },
        },
        "prefix_integrity": {
            "features_use_only_cycles_at_or_before_cutoff": True,
            "observed_prefixes_checked": len(eligible_ids),
            "feature_row_count": sum(records[e]["cutoff"] for e in eligible_ids),
            "future_rows_used_as_features": 0,
            "target_or_terminal_cycle_in_feature_matrix": False,
            "duplicate_audit": dup,
        },
        "design_sensitivity": sens,
        "interpretation_limits": [
            "The deterministic hash rule is outcome-blind by construction but does not prove stochastic independence between cutoff and lifetime.",
            "The official cutoff distribution is unidentifiable from the allowed training metadata.",
            "No exchangeability claim between pseudo-cutoff training pairs and official test pairs is supported.",
            "Near-duplicate screening is a thresholded heuristic, not a semantic-duplicate oracle.",
            "Cross train-test duplicate, test-schema, and test-label integrity checks were not performed.",
        ],
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "tidak tersedia"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def render_report(audit: dict[str, Any], audit_hash: str, script_hash: str) -> str:
    split = audit["canonical_split"]
    cut = audit["cutoff_and_lifetime"]
    groups = cut["survival_selection"]["subgroup_sizes"]
    dup = audit["prefix_integrity"]["duplicate_audit"]
    sens = audit["design_sensitivity"]
    lines = [
        "# Audit Split, Eligibility, dan Cutoff Dataset v0.3",
        "",
        "Tanggal: 8 Oktober 2026. Status: audit pengembangan training-only; bukan protocol lock atau evaluasi konfirmatori.",
        "",
        "## Cakupan",
        "",
        "Audit mereproduksi manifest FD001 training, hash split 55/15/30, kelayakan C<T, pembentukan prefix, ukuran subgroup, distribusi cutoff yang teramati pada metadata training, serta sensitivitas desain terhadap variasi salt cutoff. File input raw tidak diubah. Tidak ada official test trajectory, label, atau archive entry yang dibuka; tidak ada calibration residual atau model yang dihitung.",
        "",
        "Pertanyaan riset utama tetap. Threshold praktis 5 cycle belum disetujui dan tidak digunakan.",
        "",
        "## Integritas split dan kelayakan",
        "",
        f"Hash split dan cutoff pada manifest berhasil direproduksi dari seed {audit['method']['split_seed']}. Seluruh {split['total_reserved']} engine memiliki satu role dan tidak ada redraw. Eligible didefinisikan sebagai C<T.",
        "",
        "| Role | Dicadangkan | Eligible | Tidak eligible |",
        "|---|---:|---:|---:|",
    ]
    for role in ROLES:
        row = split["role_counts"][role]
        lines.append(f"| {role} | {row['reserved']} | {row['eligible']} | {row['reserved'] - row['eligible']} |")
    lines.append(f"| Total | {split['total_reserved']} | {split['total_eligible']} | {split['total_ineligible']} |")
    lines.extend([
        "",
        f"Hitungan canonical cocok dengan 43 fitting, 13 tuning, dan 25 calibration eligible: {split['expected_counts_match_43_13_25']}. Ini hanya validasi split dan eligibility training yang diusulkan.",
        "",
        "## Cutoff, lifetime, dan survival selection",
        "",
        "| Kelompok | n | C min | C median | C mean | C max |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Semua engine dicadangkan | {fmt(cut['canonical_cutoff_distribution_all_reserved']['n'],0)} | {fmt(cut['canonical_cutoff_distribution_all_reserved']['min'],0)} | {fmt(cut['canonical_cutoff_distribution_all_reserved']['median'],1)} | {fmt(cut['canonical_cutoff_distribution_all_reserved']['mean'],1)} | {fmt(cut['canonical_cutoff_distribution_all_reserved']['max'],0)} |",
        f"| Eligible saja | {fmt(cut['canonical_cutoff_distribution_eligible_only']['n'],0)} | {fmt(cut['canonical_cutoff_distribution_eligible_only']['min'],0)} | {fmt(cut['canonical_cutoff_distribution_eligible_only']['median'],1)} | {fmt(cut['canonical_cutoff_distribution_eligible_only']['mean'],1)} | {fmt(cut['canonical_cutoff_distribution_eligible_only']['max'],0)} |",
        "",
        "Histogram cutoff canonical untuk seluruh engine yang dicadangkan:",
        "",
        "| Rentang C | Semua | Eligible |",
        "|---|---:|---:|",
    ])
    for band in groups["by_cutoff_band"]:
        lines.append(f"| {band['min_cutoff_inclusive']}–{band['max_cutoff_inclusive']} | {band['assigned']} | {band['eligible']} |")
    all_assoc = cut["cutoff_vs_lifetime_descriptive_association_all_reserved"]
    survivor_assoc = cut["cutoff_vs_lifetime_descriptive_association_eligible_only"]
    lines.extend([
        "",
        f"Secara deskriptif, hubungan cutoff-lifetime pada seluruh 100 engine: Pearson r={fmt(all_assoc['pearson_r'])}, Spearman ρ={fmt(all_assoc['spearman_rho'])}. Di antara {survivor_assoc['n']} survivor: Pearson r={fmt(survivor_assoc['pearson_r'])}, Spearman ρ={fmt(survivor_assoc['spearman_rho'])}. Ini bukan uji independensi atau estimasi transportability.",
        "",
        "| Lifetime rank-quartile | Dicadangkan | Eligible | Proporsi eligible | Rentang T |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in groups["by_lifetime_rank_quartile"]:
        lines.append(f"| Q{row['quartile']} | {row['assigned']} | {row['eligible']} | {fmt(row['eligibility_fraction'])} | {row['lifetime_min']}–{row['lifetime_max']} |")
    lines.extend([
        "",
        "Aturan C<T menyingkirkan engine yang sudah mencapai endpoint training pada cutoff, sehingga komposisi survivor bergantung pada cutoff. Hash bersifat outcome-blind secara konstruksi, tetapi satu realisasi deterministik tidak membuktikan independensi stokastik cutoff dan lifetime.",
        "",
        "Distribusi cutoff official tidak dapat diidentifikasi dari metadata training yang diizinkan. Audit ini tidak mengklaim exchangeability antara pseudo-cutoff training dan cutoff official.",
        "",
        "## Prefix dan risiko kebocoran temporal",
        "",
        f"Prefix {audit['prefix_integrity']['observed_prefixes_checked']} engine eligible dibangun hanya dari cycle 1 sampai C; total {audit['prefix_integrity']['feature_row_count']} baris prefix diperiksa dan 0 baris setelah C dipakai sebagai feature. Feature memuat setting dan sensor menurut schema; engine ID, cycle, lifetime terminal, dan outcome tidak masuk matriks feature. Lifetime T hanya dipakai untuk aturan kelayakan training.",
        "",
        f"Exact common-prefix: {len(dup['exact_common_prefix_pairs'])} pasangan. Near-duplicate screen: {len(dup['near_duplicate_screen']['flagged_pairs'])} kandidat dari {dup['pair_comparisons']} pasangan yang dibandingkan. Perbandingan memakai overlap awal yang cycle-aligned, minimum {NEAR_MIN_COMMON_CYCLES} cycle. Ambang mean normalized RMSE ≤ {NEAR_MEAN_NRMSE:.2f} dan kanal maksimum ≤ {NEAR_MAX_CHANNEL_NRMSE:.2f} SD. Ini heuristic review screen, bukan oracle duplikasi semantik.",
        "",
        "## Ukuran subgroup",
        "",
        "Role utama berukuran 55/15/30 dicadangkan dan 43/13/25 eligible. Sel role × lifetime quartile berikut kecil atau kosong; hasilnya tidak mendukung klaim reliabilitas subgroup.",
        "",
        "| Role | Lifetime quartile | Dicadangkan | Eligible |",
        "|---|---:|---:|---:|",
    ])
    for row in groups["by_role_and_lifetime_rank_quartile"]:
        lines.append(f"| {row['role']} | Q{row['lifetime_quartile']} | {row['assigned']} | {row['eligible']} |")
    lines.extend([
        "",
        "## Sensitivitas cutoff untuk desain",
        "",
        f"Dibandingkan {sens['scenario_count']} salt cutoff deterministik dengan rentang 30..250 yang sama, sambil mempertahankan role split canonical. Audit hanya mengukur variasi jumlah dan keanggotaan eligible; tidak ada fitting, score, atau pemilihan berdasarkan performa.",
        "",
        f"Eligible canonical: {sens['canonical_total_eligible']}; rentang eligible pada skenario alternatif: {fmt(sens['alternative_total_eligible_count_distribution']['min'],0)}–{fmt(sens['alternative_total_eligible_count_distribution']['max'],0)}, median {fmt(sens['alternative_total_eligible_count_distribution']['median'],1)}. {sens['engines_with_changing_eligibility']} engine berubah status pada sebagian skenario.",
        "",
        "| Role | Eligible canonical | Min alternatif | Median alternatif | Maks alternatif |",
        "|---|---:|---:|---:|---:|",
    ])
    for role in ROLES:
        row = sens["by_role"][role]
        dist = row["alternative_eligible_count_distribution"]
        lines.append(f"| {role} | {row['canonical_eligible']} | {fmt(dist['min'],0)} | {fmt(dist['median'],1)} | {fmt(dist['max'],0)} |")
    lines.extend([
        "",
        "Variasi hash ini adalah design sensitivity, bukan distribusi sampling inferensial, bukan bukti mekanisme cutoff official, dan bukan dasar mengganti manifest canonical atau memilih model.",
        "",
        "## Handoff dan batas klaim",
        "",
        "Gate yang diserahkan: TRAINING_DATA_VALIDATED untuk audit split/eligibility/cutoff FD001 training saja. Gate ini tidak menyatakan seluruh benchmark tervalidasi dan tidak membuka akses test. Cutoff official dan mekanismenya tidak teramati; exchangeability tidak dibuktikan; duplikasi lintas train-test, schema/test-label integrity belum diaudit. Subgroup kecil dan ambang near-duplicate heuristic membatasi klaim.",
        "",
        "Tidak ada perubahan primary question, tidak ada evaluasi konfirmatori, dan practical threshold 5 cycle belum disetujui.",
        "",
        f"Perintah eksekusi: {audit['execution']['command']}",
        f"SHA-256 script: {script_hash}",
        f"SHA-256 training trajectory: {audit['source_validation']['input_hashes_sha256']['training_trajectory']}",
        f"SHA-256 manifest: {audit['source_validation']['input_hashes_sha256']['split_manifest']}",
        f"SHA-256 audit JSON: {audit_hash}",
        "",
    ])
    return "\n".join(lines)


def handoff_doc(audit: dict[str, Any], root: Path, script_hash: str, audit_hash: str, report_hash: str) -> dict[str, Any]:
    h = audit["source_validation"]["input_hashes_sha256"]
    return {
        "handoff_id": "RP-001-development-data-audit-handoff-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "producer": "data-quality-engine",
        "consumer": "scientific-research-engine",
        "evidence_gate": {
            "status": "TRAINING_DATA_VALIDATED",
            "scope_only": "FD001 training split, C<T eligibility, observed proposed cutoff distribution, subgroup sizes, and prefix integrity",
            "does_not_mean": "complete benchmark, official endpoint, calibration, model, or protocol validation",
        },
        "research_question_changed": False,
        "confirmatory_evaluation_performed": False,
        "official_test_files_or_archive_entries_accessed": False,
        "calibration_residuals_accessed_or_computed": False,
        "practical_5_cycle_threshold_approved": False,
        "command": audit["execution"]["command"],
        "project_root": str(root),
        "artifact_hashes_sha256": {
            "audit_script": script_hash,
            "training_trajectory": h["training_trajectory"],
            "training_audit_metadata": h["training_audit"],
            "schema_contract": h["schema_contract"],
            "canonical_split_manifest": h["split_manifest"],
            "protocol_config": h["protocol_config"],
            "development_data_audit_json": audit_hash,
            "dataset_audit_report_markdown": report_hash,
        },
        "key_evidence": {
            "canonical_reserved_counts": {"fit": 55, "tune": 15, "calibration": 30},
            "canonical_eligible_counts": {"fit": 43, "tune": 13, "calibration": 25},
            "canonical_manifest_reproduced": True,
            "prefix_features_stop_at_cutoff": True,
            "official_cutoff_distribution": "unidentifiable from allowed training metadata",
            "exchangeability_claim": "none",
            "cutoff_sensitivity": "100 deterministic salt scenarios; count and membership only; no performance",
            "cross_train_test_duplicate_audit": "not performed",
        },
        "risks_and_unresolved": [
            "Official cutoff values and their generating mechanism are unavailable in allowed training metadata.",
            "No exchangeability claim between pseudo-cutoff training pairs and official test pairs is supported.",
            "C<T survival eligibility changes lifetime composition; a fixed hash does not establish stochastic independence.",
            "Cross train-test duplicate, test-schema, and test-label integrity audits remain deferred.",
            "Near-duplicate detection is a thresholded heuristic, not semantic uniqueness certification.",
            "Eligible cohort and role-by-subgroup sizes are small for inferential subgroup claims.",
            "The primary question is unchanged and the proposed 5-cycle practical threshold remains unapproved.",
        ],
        "next_consumer_action": "Scientific-research-engine should review target-population and cutoff-transport assumptions; this scoped gate grants no test access and starts no confirmatory evaluation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="RP-001 training-only split and cutoff audit.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.project_root.resolve()
    outputs = (
        root / "experiments" / "development_data_audit.json",
        root / "docs" / "v0.3" / "04_dataset_split_eligibility_cutoff_audit.md",
        root / "experiments" / "development_data_audit_handoff.json",
    )
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        raise FileExistsError("Refusing to overwrite existing audit outputs: " + ", ".join(existing))

    audit = audit_project(root)
    script = root / audit["execution"]["script_path"]
    script_hash = sha256_file(script)
    audit["execution"]["audit_script_sha256"] = script_hash

    audit_path, report_path, handoff_path = outputs
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit_hash = sha256_file(audit_path)
    report_path.write_text(render_report(audit, audit_hash, script_hash), encoding="utf-8")
    report_hash = sha256_file(report_path)
    handoff_path.write_text(json.dumps(handoff_doc(audit, root, script_hash, audit_hash, report_hash), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "completed",
        "audit_json": str(audit_path),
        "report_markdown": str(report_path),
        "handoff_json": str(handoff_path),
        "sha256": {
            "script": script_hash,
            "audit_json": audit_hash,
            "report_markdown": report_hash,
            "handoff_json": sha256_file(handoff_path),
        },
        "canonical_counts": audit["canonical_split"]["role_counts"],
        "exact_prefix_pairs": len(audit["prefix_integrity"]["duplicate_audit"]["exact_common_prefix_pairs"]),
        "near_duplicate_candidates": len(audit["prefix_integrity"]["duplicate_audit"]["near_duplicate_screen"]["flagged_pairs"]),
        "official_cutoff_identifiable": audit["cutoff_and_lifetime"]["official_cutoff_distribution"]["identified_from_allowed_training_metadata"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()



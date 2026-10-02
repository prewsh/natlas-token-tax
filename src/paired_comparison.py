"""Direct paired N-ATLaS versus Gemma 4 comparisons on FLORES+."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


INPUT_PATH = Path("results/raw/tokenization_metrics.csv")
OUTPUT_PATH = Path("results/summary/natlas_gemma_paired_comparison.csv")
MARKDOWN_PATH = Path("results/summary/NATLAS_GEMMA_PAIRED.md")
METADATA_PATH = Path("results/summary/paired_comparison_metadata.json")

LANGUAGE_ORDER = ["eng", "hau", "ibo", "yor"]
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20260930
BOOTSTRAP_BATCH_SIZE = 250


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def paired_bootstrap(
    natlas_tokens: np.ndarray,
    gemma_tokens: np.ndarray,
    words: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, tuple[float, float]]:
    count = len(words)
    fertility_difference = np.empty(BOOTSTRAP_REPLICATES)
    relative_reduction = np.empty(BOOTSTRAP_REPLICATES)
    token_difference = np.empty(BOOTSTRAP_REPLICATES)

    position = 0
    while position < BOOTSTRAP_REPLICATES:
        batch_size = min(
            BOOTSTRAP_BATCH_SIZE,
            BOOTSTRAP_REPLICATES - position,
        )
        indices = rng.integers(0, count, size=(batch_size, count))
        sampled_words = words[indices].sum(axis=1)
        sampled_natlas = natlas_tokens[indices].sum(axis=1)
        sampled_gemma = gemma_tokens[indices].sum(axis=1)
        natlas_fertility = sampled_natlas / sampled_words
        gemma_fertility = sampled_gemma / sampled_words

        selection = slice(position, position + batch_size)
        fertility_difference[selection] = (
            natlas_fertility - gemma_fertility
        )
        relative_reduction[selection] = (
            1 - gemma_fertility / natlas_fertility
        )
        token_difference[selection] = sampled_natlas - sampled_gemma
        position += batch_size

    return {
        "fertility_difference": tuple(
            np.percentile(fertility_difference, [2.5, 97.5])
        ),
        "relative_reduction": tuple(
            np.percentile(relative_reduction, [2.5, 97.5])
        ),
        "total_token_difference": tuple(
            np.percentile(token_difference, [2.5, 97.5])
        ),
    }


def holm_adjust(p_values: list[float]) -> list[float]:
    count = len(p_values)
    order = np.argsort(p_values)
    adjusted = np.empty(count, dtype=float)
    running_max = 0.0
    for rank, original_index in enumerate(order):
        candidate = min(1.0, (count - rank) * p_values[original_index])
        running_max = max(running_max, candidate)
        adjusted[original_index] = running_max
    return adjusted.tolist()


def dataframe_to_markdown(dataframe: pd.DataFrame) -> str:
    headers = [str(column) for column in dataframe.columns]
    rows = [headers, ["---"] * len(headers)]
    rows.extend(
        [str(value) for value in row]
        for row in dataframe.itertuples(index=False, name=None)
    )
    return "\n".join(
        "| " + " | ".join(row) + " |" for row in rows
    )


def main() -> None:
    data = pd.read_csv(INPUT_PATH)
    paired_source = data[data["tokenizer"].isin(["natlas", "gemma4"])]
    keys = ["split", "sentence_id", "language_code"]
    tokens = paired_source.pivot(
        index=keys,
        columns="tokenizer",
        values="token_count",
    ).sort_index()
    words = paired_source.pivot(
        index=keys,
        columns="tokenizer",
        values="word_count",
    ).sort_index()

    if tokens[["natlas", "gemma4"]].isna().any().any():
        raise RuntimeError("Missing paired tokenizer measurements.")
    if not (words["natlas"] == words["gemma4"]).all():
        raise RuntimeError("Word counts differ between paired tokenizer rows.")

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    results: list[dict[str, float | int | str]] = []
    raw_p_values: list[float] = []

    for language_code in LANGUAGE_ORDER:
        mask = tokens.index.get_level_values("language_code") == language_code
        language_tokens = tokens.loc[mask]
        language_words = words.loc[mask, "natlas"].to_numpy(dtype=np.float64)
        natlas = language_tokens["natlas"].to_numpy(dtype=np.float64)
        gemma = language_tokens["gemma4"].to_numpy(dtype=np.float64)
        differences = natlas - gemma
        intervals = paired_bootstrap(natlas, gemma, language_words, rng)

        natlas_total = int(natlas.sum())
        gemma_total = int(gemma.sum())
        total_words = int(language_words.sum())
        natlas_fertility = natlas_total / total_words
        gemma_fertility = gemma_total / total_words

        test = wilcoxon(
            natlas,
            gemma,
            zero_method="zsplit",
            alternative="two-sided",
            method="approx",
        )
        raw_p_values.append(float(test.pvalue))
        language_name = paired_source.loc[
            paired_source["language_code"] == language_code,
            "language",
        ].iloc[0]

        results.append(
            {
                "language_code": language_code,
                "language": language_name,
                "paired_sentences": len(natlas),
                "natlas_total_tokens": natlas_total,
                "gemma_total_tokens": gemma_total,
                "total_token_difference_natlas_minus_gemma": (
                    natlas_total - gemma_total
                ),
                "token_difference_ci95_low": intervals[
                    "total_token_difference"
                ][0],
                "token_difference_ci95_high": intervals[
                    "total_token_difference"
                ][1],
                "natlas_tokens_per_word": natlas_fertility,
                "gemma_tokens_per_word": gemma_fertility,
                "fertility_difference_natlas_minus_gemma": (
                    natlas_fertility - gemma_fertility
                ),
                "fertility_difference_ci95_low": intervals[
                    "fertility_difference"
                ][0],
                "fertility_difference_ci95_high": intervals[
                    "fertility_difference"
                ][1],
                "gemma_relative_token_reduction": (
                    1 - gemma_fertility / natlas_fertility
                ),
                "relative_reduction_ci95_low": intervals[
                    "relative_reduction"
                ][0],
                "relative_reduction_ci95_high": intervals[
                    "relative_reduction"
                ][1],
                "sentences_gemma_fewer_tokens": int((differences > 0).sum()),
                "sentences_equal_tokens": int((differences == 0).sum()),
                "sentences_gemma_more_tokens": int((differences < 0).sum()),
                "wilcoxon_statistic": float(test.statistic),
                "wilcoxon_p_raw": float(test.pvalue),
            }
        )

    adjusted = holm_adjust(raw_p_values)
    for result, p_adjusted in zip(results, adjusted, strict=True):
        result["wilcoxon_p_holm"] = p_adjusted

    output = pd.DataFrame(results)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False)

    display = output[
        [
            "language",
            "natlas_tokens_per_word",
            "gemma_tokens_per_word",
            "fertility_difference_natlas_minus_gemma",
            "gemma_relative_token_reduction",
            "relative_reduction_ci95_low",
            "relative_reduction_ci95_high",
            "sentences_gemma_fewer_tokens",
            "sentences_equal_tokens",
            "sentences_gemma_more_tokens",
            "wilcoxon_p_holm",
        ]
    ].copy()
    for column in [
        "natlas_tokens_per_word",
        "gemma_tokens_per_word",
        "fertility_difference_natlas_minus_gemma",
        "gemma_relative_token_reduction",
        "relative_reduction_ci95_low",
        "relative_reduction_ci95_high",
    ]:
        display[column] = display[column].map(lambda value: f"{value:.4f}")
    display["wilcoxon_p_holm"] = display["wilcoxon_p_holm"].map(
        lambda value: "<1e-300" if value == 0 else f"{value:.3e}"
    )

    markdown = "\n".join(
        [
            "# Paired N-ATLaS versus Gemma 4 comparison",
            "",
            "Positive fertility differences and reductions indicate fewer tokens ",
            "under Gemma 4. Confidence intervals come from 10,000 paired ",
            "sentence-set bootstrap resamples. Wilcoxon p-values are two-sided ",
            "and Holm-adjusted across the four language comparisons.",
            "",
            dataframe_to_markdown(display),
            "",
        ]
    )
    MARKDOWN_PATH.write_text(markdown, encoding="utf-8")

    metadata = {
        "analysis": "Paired N-ATLaS versus Gemma 4 comparison",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": str(INPUT_PATH),
        "input_sha256": sha256_file(INPUT_PATH),
        "bootstrap": {
            "replicates": BOOTSTRAP_REPLICATES,
            "seed": BOOTSTRAP_SEED,
            "resampling_unit": "aligned split/sentence_id within language",
            "interval": "percentile 95%",
        },
        "test": {
            "name": "Wilcoxon signed-rank",
            "paired_measure": "sentence token count",
            "alternative": "two-sided",
            "zero_method": "zsplit",
            "multiple_comparison_adjustment": "Holm, four languages",
        },
        "output_csv": str(OUTPUT_PATH),
        "output_csv_sha256": sha256_file(OUTPUT_PATH),
        "output_markdown": str(MARKDOWN_PATH),
        "output_markdown_sha256": sha256_file(MARKDOWN_PATH),
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    print(display.to_string(index=False))
    print(f"\nPaired results: {OUTPUT_PATH}")
    print(f"Readable table: {MARKDOWN_PATH}")
    print(f"Metadata: {METADATA_PATH}")


if __name__ == "__main__":
    main()

"""Run a controlled Unicode diacritics-stripping experiment."""

from __future__ import annotations

import csv
import hashlib
import json
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from transformers import AutoTokenizer


INPUT_PATH = Path("data/processed/flores_plus_four_languages.csv")
RAW_OUTPUT_PATH = Path("results/raw/diacritics_metrics.csv")
SUMMARY_PATH = Path("results/summary/diacritics_summary.csv")
MARKDOWN_PATH = Path("results/summary/DIACRITICS_RESULTS.md")
METADATA_PATH = Path("results/summary/diacritics_metadata.json")

TOKENIZERS = {
    "natlas_llama": {
        "model_id": "NCAIR1/N-ATLaS",
        "revision": "e294476928aca9030e924ca27bb8e085e8581273",
    },
    "gemma4": {
        "model_id": "google/gemma-4-12B",
        "revision": "023679ed352de9bb66cc873c9009ce3482585c08",
    },
}
TARGET_LANGUAGES = {"ibo": "Igbo", "yor": "Yoruba"}
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20260930
BOOTSTRAP_BATCH_SIZE = 250


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )
    return unicodedata.normalize("NFC", without_marks)


def bootstrap_reduction(
    original: np.ndarray,
    stripped: np.ndarray,
    rng: np.random.Generator,
) -> tuple[float, float]:
    count = len(original)
    samples = np.empty(BOOTSTRAP_REPLICATES)
    position = 0
    while position < BOOTSTRAP_REPLICATES:
        batch_size = min(
            BOOTSTRAP_BATCH_SIZE,
            BOOTSTRAP_REPLICATES - position,
        )
        indices = rng.integers(0, count, size=(batch_size, count))
        original_total = original[indices].sum(axis=1)
        stripped_total = stripped[indices].sum(axis=1)
        samples[position : position + batch_size] = (
            1 - stripped_total / original_total
        )
        position += batch_size
    return tuple(np.percentile(samples, [2.5, 97.5]))


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
    with INPUT_PATH.open(encoding="utf-8", newline="") as file_handle:
        source_rows = [
            row
            for row in csv.DictReader(file_handle)
            if row["language_code"] in TARGET_LANGUAGES
        ]
    tokenizers = {
        name: AutoTokenizer.from_pretrained(
            specification["model_id"],
            revision=specification["revision"],
        )
        for name, specification in TOKENIZERS.items()
    }

    raw_rows = []
    for index, source in enumerate(source_rows, start=1):
        original = source["text"]
        stripped = strip_diacritics(original)
        for tokenizer_name, tokenizer in tokenizers.items():
            original_count = len(
                tokenizer.encode(original, add_special_tokens=False)
            )
            stripped_count = len(
                tokenizer.encode(stripped, add_special_tokens=False)
            )
            raw_rows.append(
                {
                    "split": source["split"],
                    "sentence_id": source["sentence_id"],
                    "language_code": source["language_code"],
                    "language": source["language"],
                    "tokenizer": tokenizer_name,
                    "text_changed": original != stripped,
                    "original_token_count": original_count,
                    "stripped_token_count": stripped_count,
                    "token_difference_original_minus_stripped": (
                        original_count - stripped_count
                    ),
                }
            )
        if index % 1_000 == 0 or index == len(source_rows):
            print(f"  {index}/{len(source_rows)} source rows complete")

    raw = pd.DataFrame(raw_rows)
    RAW_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RAW_OUTPUT_PATH, index=False)

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    summaries = []
    p_values = []
    for tokenizer_name in TOKENIZERS:
        for language_code, language in TARGET_LANGUAGES.items():
            group = raw[
                (raw["tokenizer"] == tokenizer_name)
                & (raw["language_code"] == language_code)
            ]
            original = group["original_token_count"].to_numpy(dtype=np.float64)
            stripped = group["stripped_token_count"].to_numpy(dtype=np.float64)
            difference = original - stripped
            interval = bootstrap_reduction(original, stripped, rng)
            test = wilcoxon(
                original,
                stripped,
                zero_method="zsplit",
                alternative="two-sided",
                method="approx",
            )
            p_values.append(float(test.pvalue))
            summaries.append(
                {
                    "tokenizer": tokenizer_name,
                    "language_code": language_code,
                    "language": language,
                    "sentence_count": len(group),
                    "sentences_text_changed": int(group["text_changed"].sum()),
                    "original_total_tokens": int(original.sum()),
                    "stripped_total_tokens": int(stripped.sum()),
                    "total_token_reduction": int(difference.sum()),
                    "relative_token_reduction": 1 - stripped.sum() / original.sum(),
                    "reduction_ci95_low": interval[0],
                    "reduction_ci95_high": interval[1],
                    "sentences_stripping_reduced_tokens": int((difference > 0).sum()),
                    "sentences_equal_tokens": int((difference == 0).sum()),
                    "sentences_stripping_increased_tokens": int((difference < 0).sum()),
                    "wilcoxon_statistic": float(test.statistic),
                    "wilcoxon_p_raw": float(test.pvalue),
                }
            )

    for summary, adjusted_p in zip(
        summaries,
        holm_adjust(p_values),
        strict=True,
    ):
        summary["wilcoxon_p_holm"] = adjusted_p

    summary_frame = pd.DataFrame(summaries)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary_frame.to_csv(SUMMARY_PATH, index=False)

    display = summary_frame[
        [
            "tokenizer",
            "language",
            "sentences_text_changed",
            "original_total_tokens",
            "stripped_total_tokens",
            "relative_token_reduction",
            "reduction_ci95_low",
            "reduction_ci95_high",
            "sentences_stripping_reduced_tokens",
            "sentences_equal_tokens",
            "sentences_stripping_increased_tokens",
            "wilcoxon_p_holm",
        ]
    ].copy()
    for column in [
        "relative_token_reduction",
        "reduction_ci95_low",
        "reduction_ci95_high",
    ]:
        display[column] = display[column].map(lambda value: f"{value:.4f}")
    display["wilcoxon_p_holm"] = display["wilcoxon_p_holm"].map(
        lambda value: "<1e-300" if value == 0 else f"{value:.3e}"
    )
    MARKDOWN_PATH.write_text(
        "\n".join(
            [
                "# Controlled diacritics experiment",
                "",
                (
                    "The derived condition removes all Unicode nonspacing "
                    "combining marks after NFD decomposition, then restores NFC. "
                    "Original corpus text remains unchanged."
                ),
                "",
                dataframe_to_markdown(display),
                "",
            ]
        ),
        encoding="utf-8",
    )

    metadata = {
        "experiment": "Controlled Igbo and Yoruba diacritics stripping",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": str(INPUT_PATH),
        "input_sha256": sha256_file(INPUT_PATH),
        "transformation": (
            "NFD decomposition; remove characters with Unicode category Mn; "
            "NFC recomposition"
        ),
        "tokenizers": TOKENIZERS,
        "bootstrap": {
            "replicates": BOOTSTRAP_REPLICATES,
            "seed": BOOTSTRAP_SEED,
            "resampling_unit": "paired split/sentence_id within language",
        },
        "multiple_comparison_adjustment": "Holm, four comparisons",
        "raw_output": str(RAW_OUTPUT_PATH),
        "raw_output_sha256": sha256_file(RAW_OUTPUT_PATH),
        "summary_output": str(SUMMARY_PATH),
        "summary_output_sha256": sha256_file(SUMMARY_PATH),
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    print(display.to_string(index=False))
    print(f"\nSummary: {SUMMARY_PATH}")
    print(f"Readable report: {MARKDOWN_PATH}")


if __name__ == "__main__":
    main()

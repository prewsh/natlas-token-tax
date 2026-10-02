"""Summarize the FLORES+ tokenizer experiment with bootstrap intervals."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path("results/raw/tokenization_metrics.csv")
OUTPUT_PATH = Path("results/summary/tokenizer_language_summary.csv")
MARKDOWN_PATH = Path("results/summary/BASELINE_RESULTS.md")
METADATA_PATH = Path("results/summary/summary_metadata.json")

BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20260930
BOOTSTRAP_BATCH_SIZE = 250
LANGUAGE_ORDER = ["eng", "hau", "ibo", "yor"]
TOKENIZER_ORDER = ["natlas", "llama3", "gemma4"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataframe_to_markdown(dataframe: pd.DataFrame) -> str:
    """Render a small DataFrame as Markdown without optional dependencies."""
    headers = [str(column) for column in dataframe.columns]
    rows = [headers, ["---"] * len(headers)]
    rows.extend(
        [str(value) for value in row]
        for row in dataframe.itertuples(index=False, name=None)
    )
    return "\n".join(
        "| " + " | ".join(row) + " |" for row in rows
    )


def bootstrap_fertility_and_tax(
    language_tokens: np.ndarray,
    language_words: np.ndarray,
    english_tokens: np.ndarray,
    english_words: np.ndarray,
    rng: np.random.Generator,
) -> tuple[tuple[float, float], tuple[float, float]]:
    fertility_samples = np.empty(BOOTSTRAP_REPLICATES)
    tax_samples = np.empty(BOOTSTRAP_REPLICATES)
    count = len(language_tokens)

    position = 0
    while position < BOOTSTRAP_REPLICATES:
        batch_size = min(
            BOOTSTRAP_BATCH_SIZE,
            BOOTSTRAP_REPLICATES - position,
        )
        indices = rng.integers(0, count, size=(batch_size, count))
        language_fertility = (
            language_tokens[indices].sum(axis=1)
            / language_words[indices].sum(axis=1)
        )
        english_fertility = (
            english_tokens[indices].sum(axis=1)
            / english_words[indices].sum(axis=1)
        )
        fertility_samples[position : position + batch_size] = (
            language_fertility
        )
        tax_samples[position : position + batch_size] = (
            language_fertility / english_fertility
        )
        position += batch_size

    fertility_ci = tuple(np.percentile(fertility_samples, [2.5, 97.5]))
    tax_ci = tuple(np.percentile(tax_samples, [2.5, 97.5]))
    return fertility_ci, tax_ci


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_PATH}. Run: python src/run_corpus_experiment.py"
        )

    data = pd.read_csv(INPUT_PATH)
    expected_rows = 8_036 * len(TOKENIZER_ORDER)
    if len(data) != expected_rows:
        raise RuntimeError(f"Expected {expected_rows} rows; found {len(data)}")

    fragment_columns = [
        "words_1_token",
        "words_2_tokens",
        "words_3_tokens",
        "words_4plus_tokens",
    ]
    fragment_total = data[fragment_columns].sum(axis=1)
    if not (fragment_total == data["word_count"]).all():
        raise RuntimeError("Fragmentation bins do not sum to word counts.")

    keys = ["split", "sentence_id"]
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    summaries: list[dict[str, float | int | str]] = []

    for tokenizer_name in TOKENIZER_ORDER:
        tokenizer_data = data[data["tokenizer"] == tokenizer_name].copy()
        token_pivot = tokenizer_data.pivot(
            index=keys,
            columns="language_code",
            values="token_count",
        ).sort_index()
        word_pivot = tokenizer_data.pivot(
            index=keys,
            columns="language_code",
            values="word_count",
        ).sort_index()
        if token_pivot[LANGUAGE_ORDER].isna().any().any():
            raise RuntimeError(f"Missing aligned token counts for {tokenizer_name}")

        english_tokens = token_pivot["eng"].to_numpy(dtype=np.float64)
        english_words = word_pivot["eng"].to_numpy(dtype=np.float64)
        english_fertility = english_tokens.sum() / english_words.sum()

        for language_code in LANGUAGE_ORDER:
            group = tokenizer_data[
                tokenizer_data["language_code"] == language_code
            ]
            language_tokens = token_pivot[language_code].to_numpy(
                dtype=np.float64
            )
            language_words = word_pivot[language_code].to_numpy(
                dtype=np.float64
            )
            total_tokens = int(group["token_count"].sum())
            total_words = int(group["word_count"].sum())
            fertility = total_tokens / total_words
            relative_tax = fertility / english_fertility
            fertility_ci, tax_ci = bootstrap_fertility_and_tax(
                language_tokens,
                language_words,
                english_tokens,
                english_words,
                rng,
            )

            summaries.append(
                {
                    "tokenizer": tokenizer_name,
                    "model_id": group["model_id"].iloc[0],
                    "model_revision": group["model_revision"].iloc[0],
                    "language_code": language_code,
                    "language": group["language"].iloc[0],
                    "sentence_count": len(group),
                    "total_words": total_words,
                    "total_tokens": total_tokens,
                    "mean_tokens_per_sentence": group["token_count"].mean(),
                    "corpus_tokens_per_word": fertility,
                    "fertility_ci95_low": fertility_ci[0],
                    "fertility_ci95_high": fertility_ci[1],
                    "median_sentence_tokens_per_word": group[
                        "tokens_per_word"
                    ].median(),
                    "sd_sentence_tokens_per_word": group[
                        "tokens_per_word"
                    ].std(ddof=1),
                    "relative_tax_vs_english": relative_tax,
                    "tax_ci95_low": tax_ci[0],
                    "tax_ci95_high": tax_ci[1],
                    "percent_more_tokens_per_word_vs_english": (
                        relative_tax - 1
                    )
                    * 100,
                    "corpus_characters_per_token": (
                        group["character_count"].sum() / total_tokens
                    ),
                    "corpus_non_whitespace_characters_per_token": (
                        group["non_whitespace_character_count"].sum()
                        / total_tokens
                    ),
                    "share_words_1_token": (
                        group["words_1_token"].sum() / total_words
                    ),
                    "share_words_2_tokens": (
                        group["words_2_tokens"].sum() / total_words
                    ),
                    "share_words_3_tokens": (
                        group["words_3_tokens"].sum() / total_words
                    ),
                    "share_words_4plus_tokens": (
                        group["words_4plus_tokens"].sum() / total_words
                    ),
                }
            )

    summary = pd.DataFrame(summaries)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_PATH, index=False)

    display = summary[
        [
            "tokenizer",
            "language",
            "corpus_tokens_per_word",
            "fertility_ci95_low",
            "fertility_ci95_high",
            "relative_tax_vs_english",
            "share_words_1_token",
            "share_words_4plus_tokens",
        ]
    ].copy()
    for column in display.columns[2:]:
        display[column] = display[column].map(lambda value: f"{value:.3f}")

    markdown = "\n".join(
        [
            "# FLORES+ baseline tokenization results",
            "",
            "These are corpus-level descriptive results. Tokens were counted ",
            "with `add_special_tokens=False`. Fertility is total tokens divided ",
            "by total whitespace-delimited words. Confidence intervals use ",
            f"{BOOTSTRAP_REPLICATES:,} paired sentence-set bootstrap replicates.",
            "",
            dataframe_to_markdown(display),
            "",
            "The relative tax is each language's corpus fertility divided by ",
            "English fertility for the same tokenizer. It represents relative ",
            "tokens per whitespace-delimited word, not monetary cost or model quality.",
            "",
        ]
    )
    MARKDOWN_PATH.write_text(markdown, encoding="utf-8")

    metadata = {
        "analysis": "FLORES+ baseline descriptive summary",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": str(INPUT_PATH),
        "input_sha256": sha256_file(INPUT_PATH),
        "input_row_count": len(data),
        "bootstrap": {
            "replicates": BOOTSTRAP_REPLICATES,
            "seed": BOOTSTRAP_SEED,
            "resampling_unit": "aligned split/sentence_id",
            "interval": "percentile 95%",
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
    print(f"\nSummary CSV: {OUTPUT_PATH}")
    print(f"Readable table: {MARKDOWN_PATH}")
    print(f"Analysis metadata: {METADATA_PATH}")


if __name__ == "__main__":
    main()

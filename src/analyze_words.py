"""Analyze word-level token fragmentation in Hausa, Igbo, and Yoruba."""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
import regex
from transformers import AutoTokenizer


INPUT_PATH = Path("data/processed/flores_plus_four_languages.csv")
OUTPUT_DIR = Path("results/word_analysis")

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
TARGET_LANGUAGES = {"hau": "Hausa", "ibo": "Igbo", "yor": "Yoruba"}
MIN_OCCURRENCES_FOR_RANKING = 5
TOP_COUNT = 20

# Exploratory lexical units: Unicode letters/marks with internal apostrophes or
# hyphens. This deliberately excludes surrounding punctuation and differs from
# the whitespace-word denominator used by the primary fertility analysis.
WORD_PATTERN = regex.compile(
    r"\p{L}[\p{L}\p{M}]*(?:[-'’]\p{L}[\p{L}\p{M}]*)*"
)


def load_source_rows() -> list[dict[str, str]]:
    with INPUT_PATH.open(encoding="utf-8", newline="") as file_handle:
        return [
            row
            for row in csv.DictReader(file_handle)
            if row["language_code"] in TARGET_LANGUAGES
        ]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    source_rows = load_source_rows()
    tokenizers = {
        name: AutoTokenizer.from_pretrained(
            specification["model_id"],
            revision=specification["revision"],
        )
        for name, specification in TOKENIZERS.items()
    }

    aggregates: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(
        lambda: {
            "surfaces": Counter(),
            "token_counts": [],
            "tokenizations": Counter(),
        }
    )

    for row_index, row in enumerate(source_rows, start=1):
        text = row["text"]
        matches = list(WORD_PATTERN.finditer(text))
        for tokenizer_name, tokenizer in tokenizers.items():
            encoding = tokenizer(
                text,
                add_special_tokens=False,
                return_attention_mask=False,
                return_token_type_ids=False,
                return_offsets_mapping=True,
            )
            token_ids = encoding["input_ids"]
            offsets = [tuple(offset) for offset in encoding["offset_mapping"]]
            token_pieces = tokenizer.convert_ids_to_tokens(token_ids)

            for match in matches:
                start, end = match.span()
                indices = [
                    index
                    for index, (token_start, token_end) in enumerate(offsets)
                    if token_end > start and token_start < end
                    and token_end > token_start
                ]
                if not indices:
                    raise RuntimeError(
                        f"No tokens aligned to {match.group()!r} in {text!r}"
                    )
                surface = unicodedata.normalize("NFC", match.group())
                normalized = surface.casefold()
                key = (row["language_code"], tokenizer_name, normalized)
                record = aggregates[key]
                record["surfaces"][surface] += 1
                record["token_counts"].append(len(indices))
                record["tokenizations"][
                    tuple(token_pieces[index] for index in indices)
                ] += 1

        if row_index % 1_000 == 0 or row_index == len(source_rows):
            print(f"  {row_index}/{len(source_rows)} source rows analyzed")

    rows: list[dict[str, Any]] = []
    for (language_code, tokenizer_name, normalized), record in aggregates.items():
        counts = record["token_counts"]
        occurrences = len(counts)
        representative_surface = record["surfaces"].most_common(1)[0][0]
        representative_tokens = record["tokenizations"].most_common(1)[0][0]
        rows.append(
            {
                "language_code": language_code,
                "language": TARGET_LANGUAGES[language_code],
                "tokenizer": tokenizer_name,
                "word_normalized": normalized,
                "representative_surface": representative_surface,
                "occurrences": occurrences,
                "total_tokens": sum(counts),
                "total_excess_tokens": sum(max(0, count - 1) for count in counts),
                "mean_tokens": statistics.fmean(counts),
                "median_tokens": statistics.median(counts),
                "max_tokens": max(counts),
                "share_fragmented": sum(count > 1 for count in counts)
                / occurrences,
                "representative_tokenization": json.dumps(
                    representative_tokens,
                    ensure_ascii=False,
                ),
            }
        )

    all_words = pd.DataFrame(rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_words.sort_values(
        ["language_code", "tokenizer", "total_excess_tokens"],
        ascending=[True, True, False],
    ).to_csv(OUTPUT_DIR / "word_type_fragmentation.csv", index=False)

    eligible = all_words[
        all_words["occurrences"] >= MIN_OCCURRENCES_FOR_RANKING
    ]
    top_severity = (
        eligible.sort_values(
            ["language_code", "tokenizer", "mean_tokens", "occurrences"],
            ascending=[True, True, False, False],
        )
        .groupby(["language_code", "tokenizer"], sort=False)
        .head(TOP_COUNT)
    )
    top_severity.to_csv(
        OUTPUT_DIR / "top_fragmented_word_types.csv",
        index=False,
    )

    top_burden = (
        eligible.sort_values(
            [
                "language_code",
                "tokenizer",
                "total_excess_tokens",
                "occurrences",
            ],
            ascending=[True, True, False, False],
        )
        .groupby(["language_code", "tokenizer"], sort=False)
        .head(TOP_COUNT)
    )
    top_burden.to_csv(
        OUTPUT_DIR / "top_excess_token_burden.csv",
        index=False,
    )

    comparison = all_words.pivot_table(
        index=["language_code", "language", "word_normalized"],
        columns="tokenizer",
        values=["occurrences", "total_tokens", "mean_tokens"],
        aggfunc="first",
    )
    comparison.columns = [f"{metric}_{tokenizer}" for metric, tokenizer in comparison]
    comparison = comparison.reset_index().dropna()
    comparison["natlas_minus_gemma_total_tokens"] = (
        comparison["total_tokens_natlas_llama"]
        - comparison["total_tokens_gemma4"]
    )
    comparison["natlas_minus_gemma_mean_tokens"] = (
        comparison["mean_tokens_natlas_llama"]
        - comparison["mean_tokens_gemma4"]
    )
    comparison.sort_values(
        ["language_code", "natlas_minus_gemma_total_tokens"],
        ascending=[True, False],
    ).to_csv(OUTPUT_DIR / "natlas_gemma_word_savings.csv", index=False)

    markdown_lines = [
        "# Word-level fragmentation analysis",
        "",
        (
            "Words are exploratory Unicode lexical units stripped of surrounding "
            "punctuation. Rankings require at least "
            f"{MIN_OCCURRENCES_FOR_RANKING} corpus occurrences."
        ),
        "",
    ]
    for language_code, language in TARGET_LANGUAGES.items():
        markdown_lines.extend([f"## {language}", ""])
        for tokenizer_name, label in (
            ("natlas_llama", "N-ATLaS / Llama 3"),
            ("gemma4", "Gemma 4"),
        ):
            subset = top_severity[
                (top_severity["language_code"] == language_code)
                & (top_severity["tokenizer"] == tokenizer_name)
            ].head(10)
            markdown_lines.extend(
                [
                    f"### {label}: most severely fragmented frequent types",
                    "",
                    "| Word | Occurrences | Mean tokens | Maximum | Representative tokens |",
                    "|---|---:|---:|---:|---|",
                ]
            )
            for row in subset.itertuples(index=False):
                pieces = row.representative_tokenization.replace("|", "\\|")
                markdown_lines.append(
                    f"| {row.representative_surface} | {row.occurrences} | "
                    f"{row.mean_tokens:.2f} | {row.max_tokens} | `{pieces}` |"
                )
            markdown_lines.append("")

    report_path = OUTPUT_DIR / "WORD_FRAGMENTATION.md"
    report_path.write_text(
        "\n".join(markdown_lines) + "\n",
        encoding="utf-8",
    )

    output_names = [
        "word_type_fragmentation.csv",
        "top_fragmented_word_types.csv",
        "top_excess_token_burden.csv",
        "natlas_gemma_word_savings.csv",
        "WORD_FRAGMENTATION.md",
    ]
    metadata = {
        "input": {
            "path": str(INPUT_PATH),
            "sha256": sha256(INPUT_PATH),
            "source_rows": len(source_rows),
        },
        "tokenizers": TOKENIZERS,
        "languages": TARGET_LANGUAGES,
        "method": {
            "word_pattern": WORD_PATTERN.pattern,
            "normalization": "NFC surface form followed by Unicode casefold for aggregation",
            "token_alignment": "token offset overlaps lexical word span",
            "add_special_tokens": False,
            "minimum_occurrences_for_ranking": MIN_OCCURRENCES_FOR_RANKING,
            "top_count_per_language_tokenizer": TOP_COUNT,
        },
        "counts": {
            "word_type_tokenizer_records": len(all_words),
            "eligible_records": len(eligible),
        },
        "outputs": {
            name: sha256(OUTPUT_DIR / name) for name in output_names
        },
    }
    (OUTPUT_DIR / "word_analysis_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Word types analyzed: {len(all_words)}")
    print(f"Results directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

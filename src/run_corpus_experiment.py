"""Measure tokenization efficiency on the validated four-language corpus."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer


INPUT_PATH = Path("data/processed/flores_plus_four_languages.csv")
OUTPUT_PATH = Path("results/raw/tokenization_metrics.csv")
METADATA_PATH = Path("results/corpus_experiment_metadata.json")

TOKENIZERS = {
    "natlas": {
        "model_id": "NCAIR1/N-ATLaS",
        "revision": "e294476928aca9030e924ca27bb8e085e8581273",
    },
    "llama3": {
        "model_id": "meta-llama/Meta-Llama-3-8B",
        "revision": "8cde5ca8380496c9a6cc7ef3a8b46a0372a1d920",
    },
    "gemma4": {
        "model_id": "google/gemma-4-12B",
        "revision": "023679ed352de9bb66cc873c9009ce3482585c08",
    },
}

WORD_PATTERN = re.compile(r"\S+")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def word_fragment_counts(
    text: str,
    offsets: list[tuple[int, int]],
) -> list[int]:
    """Count token spans overlapping each whitespace-delimited word."""
    counts: list[int] = []
    for match in WORD_PATTERN.finditer(text):
        word_start, word_end = match.span()
        count = sum(
            token_end > word_start and token_start < word_end
            for token_start, token_end in offsets
            if token_end > token_start
        )
        counts.append(count)
    return counts


def measure_text(tokenizer: Any, text: str) -> tuple[dict[str, Any], list[int]]:
    encoding = tokenizer(
        text,
        add_special_tokens=False,
        return_attention_mask=False,
        return_token_type_ids=False,
        return_offsets_mapping=True,
    )
    token_ids = encoding["input_ids"]
    offsets = [tuple(offset) for offset in encoding["offset_mapping"]]
    words = WORD_PATTERN.findall(text)
    fragments = word_fragment_counts(text, offsets)

    if len(fragments) != len(words) or any(count == 0 for count in fragments):
        raise RuntimeError(
            "Could not align every whitespace-delimited word to at least one "
            f"token for text: {text!r}"
        )

    token_count = len(token_ids)
    word_count = len(words)
    character_count = len(text)
    non_whitespace_character_count = sum(
        not character.isspace() for character in text
    )
    bins = Counter(
        "4plus" if count >= 4 else str(count) for count in fragments
    )

    metrics = {
        "word_count": word_count,
        "character_count": character_count,
        "non_whitespace_character_count": non_whitespace_character_count,
        "token_count": token_count,
        "tokens_per_word": token_count / word_count,
        "characters_per_token": character_count / token_count,
        "non_whitespace_characters_per_token": (
            non_whitespace_character_count / token_count
        ),
        "words_1_token": bins["1"],
        "words_2_tokens": bins["2"],
        "words_3_tokens": bins["3"],
        "words_4plus_tokens": bins["4plus"],
        "max_tokens_for_word": max(fragments),
    }
    return metrics, token_ids


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_PATH}. Run: python src/prepare_flores.py"
        )

    with INPUT_PATH.open(encoding="utf-8", newline="") as file_handle:
        source_rows = list(csv.DictReader(file_handle))
    if not source_rows:
        raise RuntimeError("The prepared FLORES+ file contains no rows.")

    loaded_tokenizers = {}
    for name, specification in TOKENIZERS.items():
        print(
            f"Loading {name}: {specification['model_id']} "
            f"at {specification['revision']}"
        )
        loaded_tokenizers[name] = AutoTokenizer.from_pretrained(
            specification["model_id"],
            revision=specification["revision"],
        )

    output_rows: list[dict[str, Any]] = []
    natlas_llama_mismatches: list[dict[str, Any]] = []

    print(f"\nMeasuring {len(source_rows)} source rows...")
    for index, source in enumerate(source_rows, start=1):
        ids_by_tokenizer: dict[str, list[int]] = {}
        for tokenizer_name, tokenizer in loaded_tokenizers.items():
            metrics, token_ids = measure_text(tokenizer, source["text"])
            ids_by_tokenizer[tokenizer_name] = token_ids
            output_rows.append(
                {
                    "dataset": source["dataset"],
                    "dataset_release": source["dataset_release"],
                    "dataset_revision": source["dataset_revision"],
                    "split": source["split"],
                    "sentence_id": source["sentence_id"],
                    "language_code": source["language_code"],
                    "language": source["language"],
                    "tokenizer": tokenizer_name,
                    "model_id": TOKENIZERS[tokenizer_name]["model_id"],
                    "model_revision": TOKENIZERS[tokenizer_name]["revision"],
                    **metrics,
                }
            )

        if ids_by_tokenizer["natlas"] != ids_by_tokenizer["llama3"]:
            natlas_llama_mismatches.append(
                {
                    "split": source["split"],
                    "sentence_id": source["sentence_id"],
                    "language_code": source["language_code"],
                    "text": source["text"],
                    "natlas_ids": ids_by_tokenizer["natlas"],
                    "llama3_ids": ids_by_tokenizer["llama3"],
                }
            )

        if index % 500 == 0 or index == len(source_rows):
            print(f"  {index}/{len(source_rows)} source rows complete")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    row_counts = Counter(
        (row["tokenizer"], row["language_code"]) for row in output_rows
    )
    metadata = {
        "experiment": "FLORES+ four-language tokenizer efficiency baseline",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": str(INPUT_PATH),
        "input_sha256": sha256_file(INPUT_PATH),
        "input_row_count": len(source_rows),
        "tokenizers": TOKENIZERS,
        "settings": {
            "add_special_tokens": False,
            "word_definition": "maximal non-whitespace sequence (regex \\S+)",
            "fragmentation_method": (
                "count tokenizer offset spans overlapping each whitespace word"
            ),
        },
        "output_file": str(OUTPUT_PATH),
        "output_sha256": sha256_file(OUTPUT_PATH),
        "output_row_count": len(output_rows),
        "row_count_by_tokenizer_and_language": {
            f"{tokenizer}:{language}": row_counts[(tokenizer, language)]
            for tokenizer in TOKENIZERS
            for language in ("eng", "hau", "ibo", "yor")
        },
        "natlas_llama_token_id_mismatch_count": len(
            natlas_llama_mismatches
        ),
        "natlas_llama_mismatch_examples": natlas_llama_mismatches[:10],
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nExperiment complete")
    print(f"Output rows: {len(output_rows)}")
    print(
        "N-ATLaS/Llama token-ID mismatches: "
        f"{len(natlas_llama_mismatches)}"
    )
    print(f"Raw metrics: {OUTPUT_PATH}")
    print(f"Metadata: {METADATA_PATH}")


if __name__ == "__main__":
    main()

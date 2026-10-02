"""Download, filter, and validate the four-language FLORES+ corpus."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from datasets import load_dataset
from huggingface_hub import HfApi


DATASET_ID = "openlanguagedata/flores_plus"
DATASET_RELEASE = "4.6"
SPLITS = ("dev", "devtest")
TARGET_LANGUAGES = {
    "eng": "English",
    "hau": "Hausa",
    "ibo": "Igbo",
    "yor": "Yoruba",
}
TARGET_SCRIPT = "Latn"
OUTPUT_PATH = Path("data/processed/flores_plus_four_languages.csv")
METADATA_PATH = Path("data/flores_plus_metadata.json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def matching_row(row: dict[str, Any]) -> bool:
    return (
        row["iso_639_3"] in TARGET_LANGUAGES
        and row["iso_15924"] == TARGET_SCRIPT
    )


def main() -> None:
    dataset_revision = HfApi().dataset_info(DATASET_ID).sha
    records: list[dict[str, Any]] = []

    print(f"Dataset: {DATASET_ID}")
    print(f"Pinned revision: {dataset_revision}")

    for split in SPLITS:
        print(f"\nLoading split: {split}")
        dataset = load_dataset(
            DATASET_ID,
            split=split,
            revision=dataset_revision,
        )
        filtered = dataset.filter(matching_row)
        print(f"Selected rows: {len(filtered)}")

        for row in filtered:
            records.append(
                {
                    "dataset": "FLORES+",
                    "dataset_release": DATASET_RELEASE,
                    "dataset_revision": dataset_revision,
                    "split": split,
                    "sentence_id": int(row["id"]),
                    "language_code": row["iso_639_3"],
                    "language": TARGET_LANGUAGES[row["iso_639_3"]],
                    "script": row["iso_15924"],
                    "glottocode": row["glottocode"],
                    "variant": row.get("variant") or "",
                    "text": row["text"],
                }
            )

    duplicate_counts = Counter(
        (row["split"], row["sentence_id"], row["language_code"])
        for row in records
    )
    duplicates = [key for key, count in duplicate_counts.items() if count != 1]
    if duplicates:
        preview = duplicates[:10]
        raise RuntimeError(
            "Expected exactly one row per split/sentence/language. "
            f"Found invalid keys, including: {preview}"
        )

    languages_by_sentence: dict[tuple[str, int], set[str]] = defaultdict(set)
    for row in records:
        languages_by_sentence[(row["split"], row["sentence_id"])].add(
            row["language_code"]
        )

    expected_languages = set(TARGET_LANGUAGES)
    incomplete = {
        key: sorted(expected_languages - languages)
        for key, languages in languages_by_sentence.items()
        if languages != expected_languages
    }
    if incomplete:
        preview = list(incomplete.items())[:10]
        raise RuntimeError(
            "Some sentence IDs are not aligned across all four languages. "
            f"Examples: {preview}"
        )

    records.sort(
        key=lambda row: (
            SPLITS.index(row["split"]),
            row["sentence_id"],
            list(TARGET_LANGUAGES).index(row["language_code"]),
        )
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    counts = Counter(
        (row["split"], row["language_code"]) for row in records
    )
    aligned_counts = Counter(split for split, _ in languages_by_sentence)
    metadata = {
        "dataset_id": DATASET_ID,
        "dataset_release_from_card": DATASET_RELEASE,
        "dataset_revision": dataset_revision,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "license": "CC-BY-SA-4.0",
        "splits": list(SPLITS),
        "target_languages": TARGET_LANGUAGES,
        "target_script": TARGET_SCRIPT,
        "row_count": len(records),
        "aligned_sentence_count_by_split": dict(aligned_counts),
        "row_count_by_split_and_language": {
            f"{split}:{language}": counts[(split, language)]
            for split in SPLITS
            for language in TARGET_LANGUAGES
        },
        "validation": {
            "one_row_per_split_sentence_language": True,
            "all_sentence_ids_have_all_target_languages": True,
        },
        "processed_file": str(OUTPUT_PATH),
        "processed_file_sha256": sha256_file(OUTPUT_PATH),
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nValidation passed")
    for split in SPLITS:
        print(f"{split}: {aligned_counts[split]} aligned sentence IDs")
        for code, language in TARGET_LANGUAGES.items():
            print(f"  {language}: {counts[(split, code)]} rows")
    print(f"\nProcessed corpus: {OUTPUT_PATH}")
    print(f"Metadata: {METADATA_PATH}")


if __name__ == "__main__":
    main()

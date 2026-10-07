"""Record short aligned FLORES+ examples with exact NFC token offsets."""

from __future__ import annotations

import csv
import hashlib
import json
import unicodedata
from pathlib import Path

from transformers import AutoTokenizer

from example_word_table import TOKENIZERS


SELECTED = [("dev", "212"), ("dev", "245"), ("dev", "610")]
LANGUAGES = ["eng", "hau", "ibo", "yor"]
SOURCE = Path("data/processed/flores_plus_four_languages.csv")
OUTPUT = Path("results/raw/sentence_examples")


def main() -> None:
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        indexed = {
            (row["split"], row["sentence_id"], row["language_code"]): row
            for row in csv.DictReader(handle)
        }
    tokenizers = {
        name: AutoTokenizer.from_pretrained(model, revision=revision, local_files_only=True)
        for name, (model, revision) in TOKENIZERS.items()
    }
    examples = []
    lines = [
        "# Short aligned FLORES+ NFC examples", "",
        "Counts include punctuation. Characters include whitespace and punctuation and are Unicode code points after NFC. Inputs have no added prefix or suffix; add_special_tokens=False.", "",
        "Offsets are the exact N-ATLaS return_offsets_mapping=True values, zero-based half-open [start,end) indices into each displayed NFC string. Order corresponds to token IDs. Byte-level splits may have repeated/overlapping offsets; these are not necessarily a disjoint character partition.", "",
    ]
    for split, sentence_id in SELECTED:
        english = unicodedata.normalize("NFC", indexed[(split, sentence_id, "eng")]["text"])
        if len(english.split()) >= 15:
            raise ValueError("Selected English sentence exceeds requested length")
        records = []
        for code in LANGUAGES:
            source_row = indexed[(split, sentence_id, code)]
            text = unicodedata.normalize("NFC", source_row["text"])
            enc = tokenizers["natlas"](
                text, add_special_tokens=False, return_offsets_mapping=True,
                return_attention_mask=False, return_token_type_ids=False,
            )
            gemma_ids = tokenizers["gemma"].encode(text, add_special_tokens=False)
            records.append({
                "language_code": code, "language": source_row["language"],
                "text_NFC": text, "characters_including_whitespace": len(text),
                "natlas_count": len(enc["input_ids"]), "gemma_count": len(gemma_ids),
                "natlas_ids": enc["input_ids"], "gemma_ids": gemma_ids,
                "natlas_offsets": [list(pair) for pair in enc["offset_mapping"]],
                "natlas_internal_pieces": tokenizers["natlas"].convert_ids_to_tokens(enc["input_ids"]),
            })
        for record in records:
            for name in ["natlas", "gemma"]:
                record[f"{name}_ratio_to_English"] = record[f"{name}_count"] / records[0][f"{name}_count"]
                record[f"{name}_ratio_exact"] = f"{record[f'{name}_count']}/{records[0][f'{name}_count']}"
        examples.append({"split": split, "sentence_id": int(sentence_id), "English_whitespace_words": len(english.split()), "languages": records})
        lines += [f"## {split}:{sentence_id} — {len(english.split())} English words", "",
                  "| Language | NFC text | Characters | N-ATLaS | N/English | Gemma 4 | G/English |",
                  "|---|---|---:|---:|---:|---:|---:|"]
        for record in records:
            lines.append(f"| {record['language']} | {record['text_NFC']} | {record['characters_including_whitespace']} | {record['natlas_count']} | {record['natlas_ratio_exact']} = {record['natlas_ratio_to_English']:.3f} | {record['gemma_count']} | {record['gemma_ratio_exact']} = {record['gemma_ratio_to_English']:.3f} |")
        lines += ["", "N-ATLaS offsets in token order:", "", "```text"]
        for record in records:
            lines.append(f"{record['language']}: {json.dumps(record['natlas_offsets'])}")
        lines += ["```", ""]
    metadata = {
        "dataset": json.loads(Path("data/flores_plus_metadata.json").read_text()),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "tokenizers": {name: {"model_id": model, "revision": revision} for name, (model, revision) in TOKENIZERS.items()},
        "normalization": "NFC", "add_special_tokens": False,
        "character_count": "Unicode code points including spaces and punctuation, after NFC",
        "ratios": "Each tokenizer's target count divided by its English count for the same split/sentence_id",
        "offsets": "Exact returned character offsets; zero-based half-open; ordered by token ID; repeated and overlapping spans retained",
        "selection": "Three illustrative short English sentences, manually checked for no names or numerical expressions; no selection based on tokenizer counts",
        "examples": examples,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "sentence_examples.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = "\n".join(lines) + "\n"
    (OUTPUT / "SENTENCE_EXAMPLES.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()

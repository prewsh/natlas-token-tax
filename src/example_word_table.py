"""Count selected FLORES+ word examples as standalone NFC strings."""

from __future__ import annotations

import csv
import hashlib
import json
import unicodedata
from pathlib import Path

from transformers import AutoTokenizer


TOKENIZERS = {
    "natlas": ("NCAIR1/N-ATLaS", "e294476928aca9030e924ca27bb8e085e8581273"),
    "gemma": ("google/gemma-4-12B", "023679ed352de9bb66cc873c9009ce3482585c08"),
}
EXAMPLES = [
    ("hau", "Hausa", "frequent short", "da"),
    ("hau", "Hausa", "hooked letter", "ƙasa"),
    ("hau", "Hausa", "hooked letter", "ɗaya"),
    ("hau", "Hausa", "long", "muhimmanci"),
    ("ibo", "Igbo", "frequent short", "na"),
    ("ibo", "Igbo", "marked letter", "ndị"),
    ("ibo", "Igbo", "marked letter", "ahụ"),
    ("ibo", "Igbo", "long", "gburugburu"),
    ("yor", "Yoruba", "frequent short", "ní"),
    ("yor", "Yoruba", "marked letter", "àwọn"),
    ("yor", "Yoruba", "marked letter and tone", "wọ́n"),
    ("yor", "Yoruba", "long", "lọ́wọ́lọ́wọ́"),
    ("eng", "English", "short comparison", "in"),
    ("eng", "English", "comparison", "home"),
    ("eng", "English", "comparison", "school"),
    ("eng", "English", "long comparison", "information"),
]


def bytelevel_inverse() -> dict[str, int]:
    """Invert the standard reversible ByteLevel byte alphabet."""
    original = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256))
    characters = list(original)
    for value in range(256):
        if value not in original:
            original.append(value)
            characters.append(256 + len(characters) - 188)
    return {chr(character): value for value, character in zip(original, characters)}


def main() -> None:
    source = Path("results/word_analysis/word_type_fragmentation.csv")
    with source.open(encoding="utf-8", newline="") as handle:
        inventory = {
            (row["language_code"], row["representative_surface"]): row
            for row in csv.DictReader(handle)
            if row["tokenizer"] == "natlas_llama"
        }
    tokenizers = {
        name: AutoTokenizer.from_pretrained(model, revision=revision, local_files_only=True)
        for name, (model, revision) in TOKENIZERS.items()
    }
    decoder = json.loads(tokenizers["natlas"].backend_tokenizer.to_str())["decoder"]
    if decoder["type"] != "ByteLevel":
        raise RuntimeError("Lossless piece display requires the audited ByteLevel decoder")
    inverse = bytelevel_inverse()
    rows = []
    details = []
    for code, language, category, surface in EXAMPLES:
        word = unicodedata.normalize("NFC", surface)
        inventory_row = inventory.get((code, word))
        if code != "eng" and inventory_row is None:
            raise ValueError(f"Word absent from recorded analysis: {word!r}")
        ids = {
            name: tokenizer.encode(word, add_special_tokens=False)
            for name, tokenizer in tokenizers.items()
        }
        raw_pieces = tokenizers["natlas"].convert_ids_to_tokens(ids["natlas"])
        piece_bytes = [bytes(inverse[character] for character in piece) for piece in raw_pieces]
        if b"".join(piece_bytes) != word.encode("utf-8"):
            raise RuntimeError(f"Token bytes do not reconstruct input: {word!r}")
        pieces = [part.decode("utf-8", errors="backslashreplace") for part in piece_bytes]
        rows.append({
            "word": word,
            "language": language,
            "category": category,
            "characters_NFC_codepoints": len(word),
            "N_ATLaS_tokens": len(ids["natlas"]),
            "Gemma_4_tokens": len(ids["gemma"]),
            "N_ATLaS_decoded_pieces": json.dumps(pieces, ensure_ascii=False),
            "FLORES_word_analysis_occurrences": int(inventory_row["occurrences"]) if inventory_row else "",
        })
        details.append({
            **rows[-1],
            "token_ids": ids,
            "N_ATLaS_internal_token_strings": raw_pieces,
            "N_ATLaS_piece_bytes_hex": [part.hex() for part in piece_bytes],
            "N_ATLaS_individually_decoded_with_replacement": [
                tokenizers["natlas"].decode([token_id], clean_up_tokenization_spaces=False)
                for token_id in ids["natlas"]
            ],
        })
    output = Path("results/example_words")
    output.mkdir(parents=True, exist_ok=True)
    with (output / "standalone_NFC_words.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = {
        "tokenizers": {name: {"model_id": model, "revision": revision} for name, (model, revision) in TOKENIZERS.items()},
        "normalization": "NFC",
        "input": "Standalone word, with no leading or trailing space",
        "add_special_tokens": False,
        "characters": "Unicode code points after NFC, not grapheme clusters",
        "selection": "Illustrative words from recorded FLORES+ analysis: frequent short, two marked/hooked, and long per language; four common English words spanning comparable lengths. Selection is not a statistical sample or translation matching.",
        "piece_display": "Decode each ByteLevel token's bytes as UTF-8; preserve incomplete UTF-8 bytes as backslash xNN escapes. Joining bytes reproduces the NFC input exactly. Ordinary single-token decoding may instead return replacement characters.",
        "inventory_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "examples": details,
    }
    (output / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Standalone NFC word examples", "",
        "Pinned tokenizers; add_special_tokens=False; no leading/trailing spaces. Characters are NFC Unicode code points. These illustrative counts differ from sentence-context word alignment. English words are length comparisons, not translations.", "",
        "Short-word frequencies are from FLORES+ release 4.6, dev plus devtest (997 + 1,012 = 2,009 sentences per language), using the recorded lexical-word regex, NFC surface normalization and casefold aggregation: Hausa da = 3,795; Igbo na = 2,552; Yoruba ní = 1,286. These are word occurrence counts, not sentence counts; the news and tweet corpora are not included.", "",
        "Decoded pieces retain incomplete UTF-8 bytes as \\xNN escapes. Each listed piece is one token; combine bytes before decoding to recover the full word.", "",
        "| Word | Language | Characters | N-ATLaS | Gemma 4 | N-ATLaS decoded pieces |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(f"| {row['word']} | {row['language']} | {row['characters_NFC_codepoints']} | {row['N_ATLaS_tokens']} | {row['Gemma_4_tokens']} | `{row['N_ATLaS_decoded_pieces']}` |")
    report = "\n".join(lines) + "\n"
    (output / "EXAMPLE_WORDS.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()

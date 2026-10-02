"""Compare the N-ATLaS and Llama 3 tokenizers reproducibly.

This script records the exact Hugging Face revisions used, compares complete
vocabulary mappings and tokenizer metadata, exercises a small multilingual
smoke-test set, and writes a machine-readable report to results/.
"""

from __future__ import annotations

import hashlib
import argparse
import json
from pathlib import Path
from typing import Any

from huggingface_hub import hf_hub_download
from huggingface_hub.errors import EntryNotFoundError
from transformers import AutoTokenizer


MODEL_IDS = {
    "natlas": "NCAIR1/N-ATLaS",
    "llama3": "meta-llama/Meta-Llama-3-8B",
}

TEST_TEXTS = {
    "english": "The children went to school today.",
    "hausa": "Yara sun tafi makaranta yau.",
    "igbo": "Ụmụaka gara ụlọ akwụkwọ taa.",
    "yoruba": "Àwọn ọmọ náà lọ sí ilé ẹ̀kọ́ lónìí.",
    "punctuation": "Nigeria: Hausa, Igbo & Yorùbá — 2026!",
    "whitespace": "one  two\nthree",
}

TOKENIZER_FILES = (
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
)


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_hashes(model_id: str, revision: str) -> dict[str, str | None]:
    hashes: dict[str, str | None] = {}
    for filename in TOKENIZER_FILES:
        try:
            path = hf_hub_download(
                repo_id=model_id,
                filename=filename,
                revision=revision,
            )
            hashes[filename] = sha256_file(path)
        except EntryNotFoundError:
            hashes[filename] = None
    return hashes


def tokenizer_record(model_id: str, revision: str) -> tuple[Any, dict[str, Any]]:
    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
    backend_definition = json.loads(tokenizer.backend_tokenizer.to_str())
    canonical_backend = json.dumps(
        backend_definition,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    record = {
        "model_id": model_id,
        "revision": revision,
        "tokenizer_class": type(tokenizer).__name__,
        "vocabulary_size": len(tokenizer),
        "special_tokens_map": tokenizer.special_tokens_map,
        "all_special_tokens": tokenizer.all_special_tokens,
        "all_special_ids": tokenizer.all_special_ids,
        "backend_sha256": hashlib.sha256(canonical_backend).hexdigest(),
        "file_sha256": file_hashes(model_id, revision),
    }
    return tokenizer, record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--llama-model', default=MODEL_IDS['llama3'])
    parser.add_argument('--llama-revision', default=None)
    parser.add_argument('--output', default='results/tokenizer_identity.json')
    args = parser.parse_args()
    MODEL_IDS['llama3'] = args.llama_model
    if args.llama_model != 'meta-llama/Meta-Llama-3-8B' and not args.llama_revision:
        parser.error('An explicit --llama-revision is required for alternative models.')
    revisions = {
        'natlas': 'e294476928aca9030e924ca27bb8e085e8581273',
        'llama3': args.llama_revision or '8cde5ca8380496c9a6cc7ef3a8b46a0372a1d920',
    }

    natlas, natlas_record = tokenizer_record(
        MODEL_IDS["natlas"], revisions["natlas"]
    )
    llama3, llama_record = tokenizer_record(
        MODEL_IDS["llama3"], revisions["llama3"]
    )

    natlas_vocab = natlas.get_vocab()
    llama_vocab = llama3.get_vocab()
    natlas_tokens = set(natlas_vocab)
    llama_tokens = set(llama_vocab)
    common_tokens = natlas_tokens & llama_tokens
    id_mismatches = [
        {
            "token": token,
            "natlas_id": natlas_vocab[token],
            "llama3_id": llama_vocab[token],
        }
        for token in common_tokens
        if natlas_vocab[token] != llama_vocab[token]
    ]
    id_mismatches.sort(key=lambda item: (item["natlas_id"], item["token"]))

    # Both tokenizers begin their added/control-token range at ID 128000.
    # Derive the boundary from the first special ID rather than hard-coding it.
    lexical_id_cutoff = min(
        min(natlas.all_special_ids),
        min(llama3.all_special_ids),
    )
    natlas_lexical_vocab = {
        token: token_id
        for token, token_id in natlas_vocab.items()
        if token_id < lexical_id_cutoff
    }
    llama_lexical_vocab = {
        token: token_id
        for token, token_id in llama_vocab.items()
        if token_id < lexical_id_cutoff
    }
    lexical_range_mismatches = [
        item
        for item in id_mismatches
        if item["natlas_id"] < lexical_id_cutoff
        or item["llama3_id"] < lexical_id_cutoff
    ]

    natlas_backend = json.loads(natlas.backend_tokenizer.to_str())
    llama_backend = json.loads(llama3.backend_tokenizer.to_str())

    smoke_tests: dict[str, Any] = {}
    for label, text in TEST_TEXTS.items():
        natlas_ids = natlas.encode(text, add_special_tokens=False)
        llama_ids = llama3.encode(text, add_special_tokens=False)
        smoke_tests[label] = {
            "text": text,
            "natlas_ids": natlas_ids,
            "llama3_ids": llama_ids,
            "identical_ids": natlas_ids == llama_ids,
        }

    comparison = {
        "same_vocabulary_size": len(natlas) == len(llama3),
        "same_token_strings": natlas_tokens == llama_tokens,
        "same_token_to_id_mapping": natlas_vocab == llama_vocab,
        "tokens_only_in_natlas": len(natlas_tokens - llama_tokens),
        "tokens_only_in_llama3": len(llama_tokens - natlas_tokens),
        "common_token_id_mismatches": len(id_mismatches),
        "lexical_id_cutoff": lexical_id_cutoff,
        "same_lexical_token_to_id_mapping": (
            natlas_lexical_vocab == llama_lexical_vocab
        ),
        "id_mismatches_touching_lexical_range": len(
            lexical_range_mismatches
        ),
        "same_merge_rules": (
            natlas_backend.get("model", {}).get("merges")
            == llama_backend.get("model", {}).get("merges")
        ),
        "same_normalizer": (
            natlas_backend.get("normalizer") == llama_backend.get("normalizer")
        ),
        "same_pre_tokenizer": (
            natlas_backend.get("pre_tokenizer")
            == llama_backend.get("pre_tokenizer")
        ),
        "same_decoder": (
            natlas_backend.get("decoder") == llama_backend.get("decoder")
        ),
        "same_post_processor": (
            natlas_backend.get("post_processor")
            == llama_backend.get("post_processor")
        ),
        "same_special_tokens_map": (
            natlas.special_tokens_map == llama3.special_tokens_map
        ),
        "same_backend_definition": (
            natlas_record["backend_sha256"] == llama_record["backend_sha256"]
        ),
        "all_smoke_test_ids_identical": all(
            test["identical_ids"] for test in smoke_tests.values()
        ),
    }

    report = {
        "purpose": "N-ATLaS and Llama 3 tokenizer identity comparison",
        "tokenizers": {
            "natlas": natlas_record,
            "llama3": llama_record,
        },
        "comparison": comparison,
        "difference_details": {
            "tokens_only_in_natlas": [
                {"token": token, "id": natlas_vocab[token]}
                for token in sorted(
                    natlas_tokens - llama_tokens,
                    key=lambda token: natlas_vocab[token],
                )
            ],
            "tokens_only_in_llama3": [
                {"token": token, "id": llama_vocab[token]}
                for token in sorted(
                    llama_tokens - natlas_tokens,
                    key=lambda token: llama_vocab[token],
                )
            ],
            "common_token_id_mismatches": id_mismatches,
            "mismatches_touching_lexical_range": lexical_range_mismatches,
            "natlas_added_vocab": natlas.get_added_vocab(),
            "llama3_added_vocab": llama3.get_added_vocab(),
        },
        "smoke_tests": smoke_tests,
    }

    report['purpose'] = 'N-ATLaS versus ' + args.llama_model + ' tokenizer comparison'
    report['note'] = 'llama3 field names denote the selected comparison model; see its model_id and pinned revision.'
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nN-ATLaS versus {args.llama_model} tokenizer comparison")
    print("-" * 47)
    print(f"N-ATLaS revision: {revisions['natlas']}")
    print(f"Llama 3 revision: {revisions['llama3']}")
    for key, value in comparison.items():
        print(f"{key}: {value}")
    print("\nTokens only in N-ATLaS:")
    for item in report["difference_details"]["tokens_only_in_natlas"]:
        print(f"  {item['id']}: {item['token']}")
    print("Tokens only in Llama 3:")
    for item in report["difference_details"]["tokens_only_in_llama3"]:
        print(f"  {item['id']}: {item['token']}")
    print(f"\nFull report: {output_path}")


if __name__ == "__main__":
    main()

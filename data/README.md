# Data provenance

## FLORES+

- Hugging Face repository: `openlanguagedata/flores_plus`
- Dataset release named in the dataset card when the protocol was prepared: `4.6`
- License shown by the repository: CC BY-SA 4.0
- Intended splits: `dev` and `devtest`
- Target varieties: English (`eng`, `Latn`), Hausa (`hau`, `Latn`), Igbo (`ibo`, `Latn`), and Yoruba (`yor`, `Latn`)

The source dataset has access conditions. Each researcher must authenticate with Hugging Face and accept those conditions before running the preparation script.

Prepare and validate the local four-language corpus with:

```bash
source .venv/bin/activate
python src/prepare_flores.py
```

The script pins the current repository commit, filters the four target varieties, validates one row per language for every aligned sentence ID, and writes:

```text
data/processed/flores_plus_four_languages.csv
data/flores_plus_metadata.json
```

The processed CSV is excluded from Git. The metadata file is suitable for version control and records the exact source revision, retrieval date, row counts, filters, and output checksum.

## MasakhaNER 2.0 news extension

Use the Hausa (`hau`), Igbo (`ibo`), and Yoruba (`yor`) CoNLL files in the original Masakhane repository, as specified by the Hugging Face loader at revision `60512e89e68841b6b5ed1be59caf97b169f0d27a`.

```bash
python src/run_masakhaner.py --download
```

The first download pins the GitHub source commit. Further downloads reuse the commit in `data/masakhaner2_metadata.json`. To rerun from downloaded files:

```bash
MPLCONFIGDIR=.cache/matplotlib python src/run_masakhaner.py
```

All three splits are used for descriptive analysis. The script joins published tokens with one space and removes exact duplicate reconstructed sentences within each language. Original tokens, capitalization, spelling, and diacritics are preserved. The whitespace denominator includes separately spaced punctuation; it is not identical to the FLORES+ word denominator. No parallel alignment across languages or English-relative tax is assumed.

Raw CoNLL files, reconstructed text, and sentence-level metrics are excluded from Git. Provenance, checksums, corpus counts, aggregate results, and figures are versionable. The original repository states CC BY-NC 4.0 for the NER dataset; the Hugging Face header's conflicting AFL-3.0 label is recorded. Cite Adelani et al. (2022), *MasakhaNER 2.0: Africa-centric Transfer Learning for Named Entity Recognition* (https://aclanthology.org/2022.emnlp-main.298/).

## NaijaSenti social-media extension

Use Hausa, Igbo, and Yoruba from the original `HausaNLP/NaijaSenti-Twitter` release (HF loader revision `a3d0415a828178edf3466246f49cfcd83b946ab3`). The loader points to annotated TSV files in `hausanlp/NaijaSenti`. The preparation script pins that source repository commit and records file checksums.

```bash
MPLCONFIGDIR=.cache/matplotlib python src/run_naijasenti.py --download
```

To rerun downloaded data, omit `--download`. To reuse primary tokenization measurements, use `--summarize-only` (secondary sensitivity tokenization is still computed).

All splits contribute descriptive text evidence. Empty rows and exact duplicate tweet strings within each language are removed. Published strings are otherwise unchanged. Sentiment labels are not needed for tokenizer comparisons. A secondary condition removes regex-matched mentions and HTTP(S) URLs, then collapses whitespace; empty derived tweets are excluded only from that condition. Diacritic strata detect combining marks attached to letters after Unicode NFD, excluding emoji variation selectors.

Original license: CC BY-NC-SA 4.0. Cite Muhammad et al. (2022), *NaijaSenti: A Nigerian Twitter Sentiment Corpus for Multilingual Sentiment Analysis*, https://aclanthology.org/2022.lrec-1.63/. Raw/processed text and per-tweet measurements are excluded from Git. Aggregate results, provenance, scripts, and figures are retained.

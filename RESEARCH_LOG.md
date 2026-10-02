# N-ATLaS Tokenizer Tax — Research Log

This is the living record of the project. Update it whenever we make a research decision, run an experiment, discover a limitation, or produce a result. Entries must distinguish preliminary observations from verified findings. This record will support the eventual methodology, results, limitations, and discussion sections of the paper.

Do not record access tokens, passwords, or other credentials here.

## Project question

Does N-ATLaS tokenize Hausa, Igbo, and Yoruba more efficiently than the Llama 3 tokenizer from which it may have inherited its text representation, and how do both compare with Gemma 4?

## Working hypotheses

- **H1:** N-ATLaS uses the same, or a practically equivalent, tokenizer as Llama 3 8B.
- **H2:** If H1 holds, N-ATLaS and Llama 3 will produce identical token IDs for the same text under identical settings.
- **H3:** Hausa, Igbo, and Yoruba will require more tokens per word than English under the N-ATLaS/Llama tokenizer.
- **H4:** Gemma 4 will produce different tokenization patterns. We do not assume in advance that they will be more efficient.

## Models and data sources

| Resource | Repository | Status |
|---|---|---|
| N-ATLaS | `NCAIR1/N-ATLaS` | Access granted; tokenizer loaded successfully |
| Llama 3 8B | `meta-llama/Meta-Llama-3-8B` | Access granted; tokenizer loaded successfully |
| Gemma 4 12B | `google/gemma-4-12B` | Publicly accessible; tokenizer loaded successfully |
| FLORES+ | `openlanguagedata/flores_plus` | Access confirmed; preparation script ready |

The study uses tokenizer files only during its initial phases. No full model weights are required for the tokenizer comparison.

## Local environment

Environment created on 2026-09-27:

- macOS on Apple Silicon (`arm64`)
- Python 3.11.15 in `.venv`
- Git 2.50.1
- VS Code 1.138.0
- `transformers==5.17.0`
- `tokenizers==0.23.2`
- `datasets==5.0.1`
- `huggingface-hub==1.33.0`
- `pandas==3.0.6`
- `numpy==2.4.6`
- `scipy==1.17.1`
- `matplotlib==3.11.2`

The environment deliberately omits PyTorch because the current work loads tokenizers rather than full model weights. Transformers therefore prints an informational warning that model functionality is unavailable.

Dependency versions are recorded in `requirements.txt`.

## Chronological record

### 2026-09-27 — Repository and environment setup

- Confirmed that the workspace was an empty Git repository on `main` with no commits.
- Added `PROJECT_START_GUIDE.md` to define the research stages and interpretation limits.
- Confirmed Python 3.11, Git, and VS Code were installed.
- Created the project virtual environment at `.venv`.
- Installed and imported all required tokenizer, dataset, analysis, statistics, and plotting libraries.
- Added `.gitignore` so the virtual environment, caches, credentials files, and Python build artifacts are not committed.
- Added pinned direct dependencies to `requirements.txt`.

### 2026-09-30 — Hugging Face authentication and access verification

- Authenticated the local Hugging Face CLI as the account `Mrprewsh`.
- Confirmed access to all three tokenizer repositories by successfully downloading their tokenizer-related files.
- Authentication credentials are stored by the Hugging Face CLI outside the repository and are not recorded here.

### 2026-09-30 — Initial tokenizer smoke tests

Test sentence used for all three tokenizers:

```text
The children went to school today.
```

Tokenization used `add_special_tokens=False`.

#### N-ATLaS

Repository: `NCAIR1/N-ATLaS`

```text
Tokens:
['The', 'Ġchildren', 'Ġwent', 'Ġto', 'Ġschool', 'Ġtoday', '.']

Token IDs:
[791, 2911, 4024, 311, 2978, 3432, 13]

Token count: 7
Vocabulary size: 128256
```

#### Gemma 4

Repository: `google/gemma-4-12B`

```text
Tokens:
['The', '▁children', '▁went', '▁to', '▁school', '▁today', '.']

Token IDs:
[818, 2940, 3939, 531, 2528, 3124, 236761]

Token count: 7
Vocabulary size: 262144
```

#### Llama 3

Repository: `meta-llama/Meta-Llama-3-8B`

```text
Tokens:
['The', 'Ġchildren', 'Ġwent', 'Ġto', 'Ġschool', 'Ġtoday', '.']

Token IDs:
[791, 2911, 4024, 311, 2978, 3432, 13]

Token count: 7
Vocabulary size: 128256
```

#### Preliminary observation

For this single English sentence, N-ATLaS and Llama 3 produced identical token strings, token IDs, token counts, and reported vocabulary sizes. Gemma 4 produced the same token count but different token strings and IDs and reported a vocabulary twice as large.

This is a smoke-test observation, not a final research finding. One sentence and equal vocabulary sizes do not prove tokenizer identity or language-wide efficiency.

### 2026-09-30 — Formal tokenizer comparison prepared

- Added `src/compare_tokenizers.py`.
- The script records exact Hugging Face repository revisions and compares complete vocabulary mappings, token IDs, special tokens, backend tokenizer definitions, tokenizer-file hashes, and multilingual smoke-test outputs.
- Planned output: `results/tokenizer_identity.json`.
- Status: script prepared and syntax-checked; formal comparison subsequently run and recorded below.

### 2026-09-30 — Formal N-ATLaS/Llama tokenizer comparison run

Command:

```bash
python src/compare_tokenizers.py
```

Pinned Hugging Face revisions:

```text
N-ATLaS: e294476928aca9030e924ca27bb8e085e8581273
Llama 3: 8cde5ca8380496c9a6cc7ef3a8b46a0372a1d920
```

Comparison summary:

| Check | Result |
|---|---:|
| Same reported vocabulary size | Yes |
| Same token strings | No |
| Same complete token-to-ID mapping | No |
| Tokens found only in N-ATLaS | 3 |
| Tokens found only in Llama 3 | 3 |
| Shared tokens assigned different IDs | 246 |
| Same lexical token-to-ID mapping below ID 128000 | Yes |
| ID mismatches touching the lexical range | 0 |
| Same BPE merge rules | Yes |
| Same normalizer, pre-tokenizer, decoder, and post-processor | Yes |
| Same special-token map | No |
| Same serialized backend definition | No |
| Identical IDs for all six smoke tests | Yes |

The raw tokenizer files and backend definitions also had different SHA-256 hashes.

Special-token configuration differed materially:

```text
N-ATLaS
bos_token: <|begin_of_text|> (128000)
eos_token: <|eot_id|> (128009)
pad_token: <|eot_id|> (128009)

Llama 3
bos_token: <|begin_of_text|> (128000)
eos_token: <|end_of_text|> (128001)
no pad token recorded in the tested special-token map
```

All token-ID sequences were identical for the fixed English, Hausa, Igbo, Yoruba, punctuation, and whitespace smoke tests. These tests used `add_special_tokens=False`.

A focused follow-up established that all 246 shared-token ID mismatches occur at or above ID 128000, the start of the added/control-token range. No mismatch touches the lexical range. The complete lexical token-to-ID mapping below that boundary is identical, as are the BPE merge rules, normalizer, pre-tokenizer, decoder, and post-processor.

The three token strings unique to each tokenizer are:

```text
N-ATLaS only
128004  <|finetune_right_pad_id|>
128008  <|eom_id|>
128010  <|python_tag|>

Llama 3 only
128253  <|reserved_special_token_248|>
128254  <|reserved_special_token_249|>
128255  <|reserved_special_token_250|>
```

#### Formal interpretation

H1 is rejected if “same tokenizer” means byte-for-byte identity, identical complete vocabulary mappings, or identical special-token configuration. N-ATLaS and Llama 3 are not strictly identical tokenizers at the pinned revisions.

For ordinary lexical text tokenized with `add_special_tokens=False`, the tokenization machinery is equivalent at the inspected revisions: the lexical vocabulary and IDs, merge rules, and processing components match exactly. The observed differences from the tested Llama 3 release are confined to the added/control-token range and special-token configuration. Corpus-wide equality checks on FLORES+ will serve as an empirical confirmation over the full benchmark.

Corrected interpretation: N-ATLaS differs from the tested Llama 3 release in control-token handling and has equivalent ordinary-text segmentation. This does not establish that N-ATLaS introduced those control-token differences; comparison with Llama 3.1 is required. This finding concerns tokenization, not model language capability.

Machine-readable evidence: `results/tokenizer_identity.json`.

### 2026-09-30 — FLORES+ access confirmed and preparation protocol added

- Confirmed access from the authenticated Hugging Face Dataset Viewer: dataset rows, schema, and both `dev` and `devtest` splits were visible.
- Added `src/prepare_flores.py` to pin the current dataset revision, select English, Hausa, Igbo, and Yoruba in Latin script, validate aligned sentence IDs, and produce a local long-format CSV.
- Added `data/README.md` with provenance and reproduction instructions.
- The processed corpus is excluded from Git; versioned metadata and checksums will be retained.
- Status: preparation script subsequently run and validated as recorded below.

### 2026-09-30 — FLORES+ four-language corpus prepared and validated

Command:

```bash
python src/prepare_flores.py
```

Pinned dataset revision:

```text
5fec6c13f9e5a4db2f745d4ec0d7c9721ddc4f06
```

Validation result:

| Split | Aligned sentence IDs | Rows per language | Total rows |
|---|---:|---:|---:|
| `dev` | 997 | 997 | 3,988 |
| `devtest` | 1,012 | 1,012 | 4,048 |
| Combined | 2,009 | 2,009 | 8,036 |

- Exactly one row was present for every split/sentence/language key.
- Every retained sentence ID had English, Hausa, Igbo, and Yoruba rows.
- Processed CSV SHA-256: `3be0e3183b9708b3fa2d39f838de5b498d75994f148344e0824c088a32cc2103`.
- Local corpus: `data/processed/flores_plus_four_languages.csv`.
- Versioned provenance: `data/flores_plus_metadata.json`.

### 2026-09-30 — Corpus tokenization protocol prepared

- Pinned all three tokenizer revisions, including Gemma 4 revision `023679ed352de9bb66cc873c9009ce3482585c08`.
- Added `src/run_corpus_experiment.py`.
- Predefined sentence metrics: word count, character counts, token count, tokens per word, characters per token, and word-fragmentation bins.
- Defined a word as a maximal non-whitespace sequence (`\\S+`).
- Defined word fragmentation using tokenizer offset spans overlapping each whitespace-delimited word.
- Retained `add_special_tokens=False` for cross-tokenizer comparability.
- The script will also test N-ATLaS/Llama token-ID equality for every one of the 8,036 source rows.
- Status: experiment script subsequently run and validated as recorded below.

### 2026-09-30 — Full FLORES+ corpus tokenization completed

Command:

```bash
python src/run_corpus_experiment.py
```

Run result:

- Input source rows: 8,036.
- Output tokenizer-language rows: 24,108.
- Each tokenizer/language group: 2,009 rows.
- N-ATLaS/Llama token-ID mismatches across all source texts: **0**.
- Raw output SHA-256: `ae76c1bc47e450220f8f8ce4c28a43f2bec95cc65ba363f9e5a79d9021220fc9`.
- Raw metrics: `results/raw/tokenization_metrics.csv`.
- Run metadata: `results/corpus_experiment_metadata.json`.

#### Interpretation

Across all 8,036 English, Hausa, Igbo, and Yoruba FLORES+ texts, N-ATLaS and Llama 3 produced exactly the same token-ID sequences when `add_special_tokens=False`. Combined with the identical lexical vocabulary and merge pipeline, this confirms corpus-wide practical equivalence for ordinary text at the pinned revisions. Differences from the tested Llama 3 release are confined to control/special-token handling; their origin is unresolved pending Llama 3.1 comparison. The measured lexical segmentation is equivalent for these four language varieties.

### 2026-09-30 — Descriptive analysis protocol prepared

- Added `src/summarize_results.py`.
- Primary fertility estimator: total corpus tokens divided by total whitespace-delimited words.
- Relative tax: language corpus fertility divided by English corpus fertility within the same tokenizer.
- Confidence intervals: percentile intervals from 10,000 paired bootstrap resamples of aligned sentence IDs; deterministic seed `20260930`.
- Fragmentation summaries aggregate offset-aligned word bins.
- Status: summary script run successfully; results recorded below.

### 2026-09-30 — FLORES+ baseline descriptive results

Command:

```bash
python src/summarize_results.py
```

The analysis used 10,000 paired sentence-set bootstrap replicates with seed `20260930`. Fertility is total corpus tokens divided by total whitespace-delimited words. Relative tax is fertility divided by English fertility for the same tokenizer.

| Tokenizer | Language | Tokens/word | 95% CI | Relative tax vs English | One-token words | Words using 4+ tokens |
|---|---|---:|---:|---:|---:|---:|
| N-ATLaS | English | 1.236 | 1.229–1.243 | 1.000 | 82.9% | 1.1% |
| N-ATLaS | Hausa | 2.164 | 2.153–2.175 | 1.751 | 34.0% | 10.7% |
| N-ATLaS | Igbo | 2.599 | 2.584–2.615 | 2.103 | 23.9% | 19.6% |
| N-ATLaS | Yoruba | 2.904 | 2.873–2.934 | 2.350 | 25.4% | 28.4% |
| Llama 3 | English | 1.236 | 1.229–1.243 | 1.000 | 82.9% | 1.1% |
| Llama 3 | Hausa | 2.164 | 2.153–2.175 | 1.751 | 34.0% | 10.7% |
| Llama 3 | Igbo | 2.599 | 2.584–2.615 | 2.103 | 23.9% | 19.6% |
| Llama 3 | Yoruba | 2.904 | 2.873–2.933 | 2.350 | 25.4% | 28.4% |
| Gemma 4 | English | 1.237 | 1.229–1.244 | 1.000 | 84.2% | 1.5% |
| Gemma 4 | Hausa | 1.876 | 1.867–1.885 | 1.517 | 44.1% | 5.6% |
| Gemma 4 | Igbo | 2.345 | 2.331–2.360 | 1.897 | 35.0% | 18.4% |
| Gemma 4 | Yoruba | 2.569 | 2.543–2.595 | 2.077 | 32.6% | 22.1% |

N-ATLaS and Llama 3 results are identical because their token-ID sequences matched for every corpus text. Relative to their English fertility, Hausa used 75.1% more tokens per whitespace word, Igbo used 110.3% more, and Yoruba used 135.0% more.

Gemma 4 used fewer tokens per word than N-ATLaS/Llama 3 for all three Nigerian languages in this corpus. The descriptive reductions were approximately 13.3% for Hausa, 9.8% for Igbo, and 11.5% for Yoruba. Gemma still exhibited substantial within-tokenizer gaps relative to English: 51.7% more tokens per word for Hausa, 89.7% more for Igbo, and 107.7% more for Yoruba.

The fragmentation distributions reinforce the fertility result. Under N-ATLaS/Llama 3, 82.9% of English whitespace words used one token, compared with 34.0% of Hausa, 23.9% of Igbo, and 25.4% of Yoruba words. Yoruba also had the largest 4+-token share at 28.4%.

#### Interpretation limits

- These values describe FLORES+ and the stated whitespace word rule; they are not universal language constants.
- Relative tax means additional tokens per whitespace-delimited word, not a measured monetary or latency cost.
- Separate confidence intervals describe each estimate. A direct paired N-ATLaS/Gemma difference analysis is still required before formal comparative inference.
- Tokenization efficiency does not measure comprehension, generation quality, or downstream task performance.

Evidence:

- `results/summary/tokenizer_language_summary.csv`
- `results/summary/BASELINE_RESULTS.md`
- `results/summary/summary_metadata.json`

### 2026-09-30 — Direct paired N-ATLaS versus Gemma 4 comparison

The same 2,009 sentences within each language were compared across tokenizers. Primary effect estimates use corpus fertility differences and relative token reduction. Confidence intervals use 10,000 paired sentence-set bootstrap resamples. A two-sided Wilcoxon signed-rank test on paired sentence token counts was Holm-adjusted across the four languages.

| Language | N-ATLaS tokens/word | Gemma tokens/word | Gemma reduction | 95% CI | Gemma fewer / equal / more-token sentences | Holm-adjusted p |
|---|---:|---:|---:|---:|---:|---:|
| English | 1.2359 | 1.2366 | -0.06% | -0.35%–0.23% | 623 / 855 / 531 | 0.0673 |
| Hausa | 2.1637 | 1.8761 | 13.29% | 13.03%–13.55% | 1,933 / 43 / 33 | <1e-300 |
| Igbo | 2.5993 | 2.3454 | 9.77% | 9.56%–9.97% | 1,917 / 47 / 45 | <1e-300 |
| Yoruba | 2.9038 | 2.5690 | 11.53% | 11.32%–11.73% | 1,935 / 46 / 28 | <1e-300 |

Across the full corpus, Gemma used 14,225 fewer Hausa tokens, 12,283 fewer Igbo tokens, and 16,586 fewer Yoruba tokens than N-ATLaS. The English difference was 32 additional Gemma tokens and its paired confidence interval included zero.

The direct paired analysis supports lower Gemma token usage for all three Nigerian languages in FLORES+ at the pinned tokenizer revisions. It does not support a meaningful English difference. The very small Nigerian-language p-values underflowed to zero in SciPy's floating-point output and are reported conservatively as `<1e-300`, rather than as literal zero probability.

Evidence:

- `results/summary/natlas_gemma_paired_comparison.csv`
- `results/summary/NATLAS_GEMMA_PAIRED.md`
- `results/summary/paired_comparison_metadata.json`

### 2026-09-30 — Initial paper figures generated

Generated and visually inspected PNG and SVG versions of:

1. `figure_1_fertility`: corpus tokens per whitespace-delimited word with 95% bootstrap intervals.
2. `figure_2_relative_tax`: within-tokenizer fertility relative to English with 95% bootstrap intervals.
3. `figure_3_word_fragmentation`: shares of words represented by 1, 2, 3, or 4+ tokens.

N-ATLaS and Llama 3 are displayed as a combined series because their token-ID sequences and metrics were identical throughout the corpus. Figure metadata is stored at `results/figures/figure_metadata.json`.

### 2026-09-30 — Word-level fragmentation analysis

Added and ran `src/analyze_words.py` on all 6,027 Hausa, Igbo, and Yoruba source rows. This exploratory analysis defines a lexical word as a Unicode letter sequence, including combining marks and internal apostrophes or hyphens. It removes surrounding punctuation, normalizes surface forms to NFC, and uses Unicode casefolding for aggregation. Token counts are obtained by overlapping tokenizer offsets with each word span. Rankings require at least five corpus occurrences.

The severe-fragmentation ranking exposes orthographic patterns that the corpus averages conceal:

- **Hausa:** N-ATLaS/Llama used seven tokens for `ƙarƙashin`, `ƙirƙirar`, `ƙanƙarar`, `faɗaɗa`, `haƙiƙa`, `ƙwaƙwalwa`, and `kuɗaɗe`. Gemma generally reduced these examples to about five tokens, although repeated and hyphenated forms remained heavily split.
- **Igbo:** N-ATLaS/Llama used eight tokens for `n'agbanyeghị`, `N’agbanyeghị`, and `ndọrọndọrọ`; `ọnụọgụgụ` averaged 7.5 and reached nine tokens. Apostrophe constructions and letters with subdots were persistent sources of fragmentation under both tokenizers.
- **Yoruba:** N-ATLaS/Llama used 12 tokens for `lọ́wọ́lọ́wọ́` and `ìbáraẹnisọ̀rọ̀`; `oríṣìíríṣìí` averaged 11.8 and reached 14. Gemma improved these examples but still required 9.8–11 tokens on average. Yoruba tone marks and underdots frequently became separate or byte-level pieces.

The aggregate-burden ranking shows that frequent short words matter more to total cost than some spectacular rare examples. Under N-ATLaS/Llama, leading excess-token burdens included Hausa `cikin` (814 excess tokens), Igbo `nke` (1,414), and Yoruba `àwọn` (2,703). Gemma's largest word-type savings included 807 tokens for Hausa `cikin`, 1,342 for Igbo `nke`, and 849 for Yoruba `tó`.

Raw token strings from byte-level BPE tokenizers can appear as mojibake-like symbols in diagnostic output. These strings are tokenizer-internal byte representations; the source words and offset-based counts remain Unicode text.

This is a word-type diagnostic over FLORES+, not a linguistic claim that the displayed types are intrinsically difficult. Context can affect the initial token piece, case variants may remain separate surface forms, and the five-occurrence cutoff favors interpretability over exhaustive rare-word discovery.

Evidence:

- `results/word_analysis/WORD_FRAGMENTATION.md`
- `results/word_analysis/word_type_fragmentation.csv`
- `results/word_analysis/top_fragmented_word_types.csv`
- `results/word_analysis/top_excess_token_burden.csv`
- `results/word_analysis/natlas_gemma_word_savings.csv`
- `results/word_analysis/word_analysis_metadata.json`

### 2026-09-30 — Controlled diacritics experiment

Added and ran `src/diacritics_experiment.py` for Igbo and Yoruba. The derived comparison condition decomposes each source sentence to Unicode NFD, removes all nonspacing combining marks (`Mn`), and recomposes it to NFC. Original corpus files are unchanged. Each original sentence is paired with its transformed version. Confidence intervals use 10,000 paired sentence-set bootstrap resamples; two-sided Wilcoxon signed-rank tests are Holm-adjusted across four tokenizer-language comparisons.

| Tokenizer | Language | Original tokens | Marks removed | Relative reduction | 95% CI | Sentences reduced / equal / increased | Holm p |
|---|---|---:|---:|---:|---:|---:|---:|
| N-ATLaS / Llama 3 | Igbo | 125,755 | 107,448 | 14.56% | 14.23%–14.89% | 1,797 / 212 / 0 | <1e-300 |
| N-ATLaS / Llama 3 | Yoruba | 143,881 | 89,883 | 37.53% | 36.96%–38.09% | 1,705 / 304 / 0 | <1e-300 |
| Gemma 4 | Igbo | 113,472 | 98,171 | 13.48% | 13.17%–13.78% | 1,794 / 215 / 0 | <1e-300 |
| Gemma 4 | Yoruba | 127,295 | 83,825 | 34.15% | 33.59%–34.70% | 1,702 / 306 / 1 | <1e-300 |

Removing marks caused a large token-count decrease for both languages and tokenizers, with the strongest effect in Yoruba. This controlled perturbation supports the interpretation that correct marked orthography incurs a substantial representational penalty. It does **not** recommend stripping diacritics: the transformation removes linguistically meaningful tone and vowel distinctions and can create ambiguous or incorrect text. It also changes multiple marks simultaneously, so it estimates their combined effect rather than the causal contribution of any individual mark.

Generated and visually inspected `figure_4_diacritics_effect` in PNG and SVG formats.

Evidence:

- `results/summary/DIACRITICS_RESULTS.md`
- `results/summary/diacritics_summary.csv`
- `results/summary/diacritics_metadata.json`
- `results/raw/diacritics_metrics.csv`
- `results/figures/figure_4_diacritics_effect.png`
- `results/figures/figure_4_diacritics_effect.svg`

### 2026-10-01 — MasakhaNER 2.0 news extension completed

User authorized using the dataset for analysis under the authors' stated noncommercial research terms. Working license: CC BY-NC 4.0 according to the original repository README; Hugging Face's AFL-3.0 header conflicts and remains documented. Raw and processed text are excluded from Git. Citation: Adelani et al. (2022), *MasakhaNER 2.0: Africa-centric Transfer Learning for Named Entity Recognition*.

The HF loader at revision `60512e89e68841b6b5ed1be59caf97b169f0d27a` references original GitHub CoNLL files. We downloaded the nine Hausa/Igbo/Yoruba train/dev/test files at GitHub commit `ba5843cd08aa491d5f96a5e809e71eb9ec461391`. Subsequent downloads reuse this pinned revision. Each published token sequence was joined with one ASCII space, preserving punctuation, spelling, case, and diacritics. Exact duplicate reconstructed sentences were removed across splits within each language. All splits are descriptive data; no training is performed.

Commands:

```bash
MPLCONFIGDIR=.cache/matplotlib python src/run_masakhaner.py --download
MPLCONFIGDIR=.cache/matplotlib python src/run_masakhaner.py --summarize-only
```

| Language | Unique sentences | Letter-containing units | Exact duplicates removed | N-ATLaS tokens/spacing unit | Gemma tokens/spacing unit | Gemma reduction | 95% sentence-bootstrap CI |
|---|---:|---:|---:|---:|---:|---:|---:|
| Hausa | 7,913 | 194,106 | 252 | 1.8840 | 1.6804 | 10.80% | 10.67%–10.94% |
| Igbo | 10,381 | 286,732 | 524 | 2.1990 | 1.9591 | 10.91% | 10.84%–10.98% |
| Yoruba | 9,633 | 213,256 | 190 | 3.4860 | 3.1018 | 11.02% | 10.90%–11.15% |

Measured 27,927 unique source sentences and produced 83,781 tokenizer measurements. N-ATLaS/Llama token-ID mismatches: **0**. Gemma used fewer tokens in 7,261 Hausa, 9,922 Igbo, and 9,211 Yoruba sentences. Two-sided Wilcoxon signed-rank p-values, Holm-adjusted across three languages, underflowed and are displayed as `<1e-300`. Paired bootstrap uses 10,000 replicates and seed `20260930`.

The original source count has 6,876 Yoruba training rows rather than the card's 6,877; the actual pinned files determine our counts. Unicode NFD combining marks occur in 10,201 Igbo and 9,597 Yoruba sentences. None occur in Hausa; this indicator does not count hooked letters such as ƙ or ɗ, which are not removable combining marks.

The news replication supports the FLORES+ findings of N-ATLaS/Llama lexical equivalence and lower Gemma token usage in all three languages. Yoruba remains the most fragmented under both tokenizers. N-ATLaS four-plus-token spacing-unit shares were Hausa 5.71%, Igbo 13.94%, Yoruba 41.23%; Gemma shares were 3.41%, 12.16%, 34.98%.

Interpretation limits: punctuation is separately spaced in CoNLL, so fertility uses a different denominator from FLORES+ and absolute values should not be treated as a matched cross-corpus effect. The languages contain different news content and have unequal sample sizes. No English-relative tax is estimated here. News may include translated source material and does not establish universally original-language authorship. Source article identifiers are unavailable, so sentence bootstrap cannot account for within-article dependence; intervals are conditional on an independence assumption. Only exact duplicates were removed; near-duplicate and source-specific sensitivity checks remain extensions.

Generated and visually inspected `results/masakhaner2/cross_corpus_comparison.png` and its SVG companion. The figure compares within-language paired tokenizer reductions across corpora.

Evidence: `src/run_masakhaner.py`, `data/masakhaner2_metadata.json`, `results/masakhaner2/RESULTS.md`, `results/masakhaner2/corpus_audit.csv`, `results/masakhaner2/summary.csv`, `results/masakhaner2/paired_comparison.csv`, `results/masakhaner2/paired_metadata.json`, `results/masakhaner2/tokenization_metadata.json`, and `results/masakhaner2/output_manifest.json`. Input checksum: `b673146f9201d3975d7691589c8db6d4689f716f39391b374a4c6db1a6b635ad`.

### 2026-10-01 — NaijaSenti social-media replication completed

User authorized a third text setting: released Hausa, Igbo, and Yoruba tweets from `HausaNLP/NaijaSenti-Twitter`. HF loader revision: `a3d0415a828178edf3466246f49cfcd83b946ab3`. Original GitHub source revision: `3f267dd565573500ee34e99df19171be3e056be0`. Working license is CC BY-NC-SA 4.0 per the original dataset card; we used the original release rather than the MTEB copy with a different license label. Cite Muhammad et al. (2022), *NaijaSenti: A Nigerian Twitter Sentiment Corpus for Multilingual Sentiment Analysis*, https://aclanthology.org/2022.lrec-1.63/.

Downloaded all nine annotated TSV files and preserved published tweet strings. Removed 215 exact duplicates for Hausa, 38 for Igbo, and 237 for Yoruba across splits; no empty rows were found. Sentiment labels were not used. No model training was performed. Source hashes and corpus preparation are recorded in `data/naijasenti_metadata.json`; prepared CSV checksum: `856b6eeb68301d6199af05ef62461495ec9c21b0e7661029035eaa05da12517c`.

Commands:

```bash
MPLCONFIGDIR=.cache/matplotlib python src/run_naijasenti.py --download
MPLCONFIGDIR=.cache/matplotlib python src/run_naijasenti.py --summarize-only
```

| Language | Unique tweets | Whitespace units | N-ATLaS fertility | Gemma fertility | Gemma token reduction | 95% paired tweet-bootstrap CI |
|---|---:|---:|---:|---:|---:|---:|
| Hausa | 21,937 | 298,517 | 2.2211 | 1.8437 | 16.99% | 16.83%–17.15% |
| Igbo | 15,677 | 185,661 | 2.3227 | 2.1089 | 9.20% | 9.01%–9.40% |
| Yoruba | 14,890 | 316,888 | 2.7917 | 2.4755 | 11.33% | 11.21%–11.44% |

Measured 52,504 tweets and produced 157,512 primary measurements. N-ATLaS/Llama token-ID mismatches were **0**. Gemma used fewer tokens on 20,807 Hausa, 11,666 Igbo, and 13,693 Yoruba tweets. Confidence intervals use 10,000 paired tweet resamples, seed `20260930`; two-sided Wilcoxon signed-rank tests are Holm-adjusted across three languages. P-values underflowed and are displayed as `<1e-300`.

N-ATLaS four-plus-token whitespace-unit shares were Hausa 8.86%, Igbo 10.63%, Yoruba 25.76%; Gemma shares were 4.36%, 7.96%, 19.60%. Yoruba remained the most fragmented of these subsets. This replicates the direction of tokenizer differences across translated benchmark, news, and released tweets. It does not establish an English-relative social-media tax because no matched English subset is present.

The audit found URLs in 501 Hausa, 3,032 Igbo, and 2,187 Yoruba tweets despite the card's URL-removal claim. Mentions occurred in 16,626, 8,211, and 4,566 tweets respectively. A secondary condition removes HTTP(S) URLs and regex-matched mentions and collapses whitespace, preserving other text. All derived tweets remained nonempty. Gemma reductions then became Hausa **18.67%**, Igbo **12.36%**, and Yoruba **12.24%**. Thus the direction persisted after removal; platform features do not explain away the aggregate tokenizer advantage in this perturbation.

Diacritic grouping detects Unicode letters followed by combining marks after NFD, excluding emoji variation selectors. It found 122 marked Hausa, 4,219 marked Igbo, and 11,739 marked Yoruba tweets. Hooked letters are not included. Gemma reduction on marked/unmarked tweets was Hausa 14.02%/17.01%, Igbo 9.65%/8.99%, Yoruba 12.10%/6.48%. These are descriptive comparisons of different posts, not controlled effects of mark removal. Borrowed accented words can count as marked, and this flag does not identify code mixing or language purity.

Limits: released tweets have prior anonymization and processing; selection for sentiment annotation may bias genre and tone; cross-language subsets are not parallel content; author/thread identifiers are unavailable for clustered resampling, so tweet intervals assume independence; near duplicates are not removed; code mixing is not quantified or causally analyzed. Language labels indicate dataset subsets rather than pure monolingual text. Absolute fertility differences across corpora also reflect spacing, emoji, content, and orthography differences.

Generated and visually inspected PNG/SVG versions of `results/naijasenti/three_corpus_comparison`. Full evidence: `src/run_naijasenti.py`, `data/naijasenti_metadata.json`, `results/naijasenti/RESULTS.md`, `corpus_audit.csv`, `summary.csv`, `paired_comparison.csv`, `sensitivity_summary.csv`, `tokenization_metadata.json`, `paired_metadata.json`, and `output_manifest.json` under `results/naijasenti/`. Raw/processed text and per-tweet measurements are excluded from Git.

### 2026-10-01 — Orthography refinement and reporting cleanup

Added and ran `src/orthography_experiments.py` on 6,027 FLORES+ sentences, using cached pinned tokenizers. Every perturbation uses NFC reference text. Published-versus-NFC and NFC-versus-NFD contrasts are separate. Tone removal targets U+0300/U+0301/U+0304; underdot removal targets U+0323; a separately labeled condition also targets U+0329. All Mn removal, the tone/underdot union, and uppercase-aware Hausa ƙ/ɗ/ɓ/ƴ substitutions are included. Intervals use 10,000 paired sentence resamples, seed `20261001`.

Normalization audit: 0 Hausa, 69 Igbo, and 576 Yoruba sentences were not already NFC. New NFC-reference all-Mn reductions are Igbo 14.54% N-ATLaS / 13.43% Gemma and Yoruba 36.88% / 33.27%. Earlier raw-reference estimates remain recorded as historical measurements; they combined normalization and mark removal. Primary baseline/news/tweet measurements do not require replacement.

Tone-only reductions: Igbo 0.24% / 0.21%, Yoruba 25.93% / 25.30%. Underdot-only reductions: Igbo 14.27% / 13.20%, Yoruba 14.24% / 11.45%. Hausa hooked-letter substitution reduced counts by 5.30% / 2.97%. NFD increased counts versus NFC by Igbo 7.99% / 11.57% and Yoruba 18.74% / 26.49%, despite canonical equivalence.

The mark inventory includes small numbers of marks outside the tone/underdot sets, so pure additivity is evaluated using the explicit union condition. Yoruba's union savings were 4,726 N-ATLaS and 4,415 Gemma tokens less than the individual savings sum; Igbo interaction was 3 and 2 tokens. U+0329 was absent in this corpus. The decoded vocabulary audit uses backend decoding rather than raw byte-token notation and reports partial UTF-8 replacement pieces separately. Zero complete-letter entries does not imply that a tokenizer cannot encode the letter across multiple pieces.

Generated and visually inspected the new NFC-reference `results/orthography/orthography_effects.png` and SVG. Its report, CSVs, raw-measurement checksum, tokenizer revisions, transformations, and output hashes are in `results/orthography/`. Original figure 4 remains the raw-reference historical artifact; use the new split figure for the paper's refined mechanism discussion.

Added `RESEARCH_UPDATE.md` as the consolidated current version, with effect sizes leading, vocabulary-size caveats, normalization implications, and interpretation limits. Updated the project guide, checklist, and evidence index to include news, NaijaSenti, and focused orthography. Gemma's larger vocabulary is a potential confound; the study cannot disentangle vocabulary capacity, training data, and segmentation design or measure embedding costs. Existing p-values remain supporting tables, not the basis of the current contribution statement.

### 2026-10-01 — Exact premium refinement, normalization ranking check, and remaining identity gate

Updated `src/compare_tokenizers.py` to use the original pinned N-ATLaS and Llama 3 revisions by default and require an explicit revision for other models. Prepared Llama 3.1 comparison at `d04e592bb4f6aa9cfee91e2e20afa771667e1d4b`; its file download failed with Hugging Face 403 because the account is not authorized. No identity result was produced. Llama 3.1 remains pending, and statements assigning control-token changes to N-ATLaS were withdrawn.

Added and ran `src/refine_premiums.py`. English and target-language reference text are both NFC. All 2,009 split/sentence IDs are aligned, and a common index resample is used across English, target languages, tokenizers, and conditions. Confidence intervals use 10,000 percentile paired replicates and seed `20260930`. Premium is language fertility divided by English fertility; excess removed is `(premium_before - premium_after)/(premium_before - 1)`.

N-ATLaS/Llama results: Hausa hooked-letter substitution 1.7508× → 1.6580×, excess removed 12.36% (95% CI 11.78%–12.93%); Igbo all-Mn removal 2.1026× → 1.7970×, 27.72% (27.18%–28.25%); Yoruba all-Mn removal 2.3255× → 1.4678×, 64.71% (64.11%–65.28%). These quantify specific lossy transformation effects and do not establish causal shares of the entire excess. Residual Hausa burden remains unexplained by the hooked-letter experiment.

Gemma's Yoruba advantage was directly recomputed: NFC 11.80% (11.60%–12.00%), NFD 6.04% (5.91%–6.18%). Normalization changes advantage magnitude without reversing the tokenizer ranking. Canonical NFC preserves spelling information and saves tokens in the tested pipeline, subject to application-specific input requirements.

Implemented operational Unicode default-word-boundary sensitivity using `regex.WORD` and VERSION1, counting only segments containing Unicode letters/numbers. N-ATLaS premiums were Hausa 1.7530×, Igbo 2.0455×, Yoruba 2.3337×; ordering persisted. This is UAX-29-based sensitivity, not language-specific morphological segmentation or a conformance certification. Library version, input checksums, and output hashes are recorded in `results/refinements/metadata.json`.

Seed rationale: the orthography run uses `20261001` as its deterministic experiment identifier; baseline and subsequent premium refinements use `20260930`. This documented difference does not alter point estimates or estimators and does not require a full rerun.

Wording: use tone marks, underdotted letters, and hooked letters for the respective contrasts. A zero decoded vocabulary count means no entry decoded individually contains that complete lowercase character, not that encoding is unsupported. Prior NaijaSenti marked/unmarked groups do not isolate tone usage. Updated current summary and paper notes accordingly.

Evidence: `results/refinements/REFINED_RESULTS.md`, `premium_perturbations.csv`, `normalization_comparison.csv`, `word_boundary_sensitivity.csv`, and `metadata.json`; `RESEARCH_UPDATE.md` contains the consolidated current interpretation.

## Methodological decisions

1. All baseline token counts will use `add_special_tokens=False` so different model wrappers do not add incomparable control tokens.
2. Exact Hugging Face commit revisions will be recorded before results are treated as evidence.
3. Vocabulary size alone will not be used to claim tokenizer identity.
4. The identity analysis will compare vocabulary strings, token-to-ID mappings, special tokens, backend definitions, relevant file hashes, and actual tokenization output.
5. FLORES+ will be used as the controlled parallel corpus once its version, split, access conditions, and language-file structure are verified.
6. Target varieties are English, Hausa, Igbo, and Yoruba in Latin script.
7. Tokens per whitespace-delimited word will be reported as one measure, with its linguistic limitation stated explicitly.
8. Characters per token and sentence-level distributions will be reported alongside tokens per word.
9. “Tokenizer tax” initially means a relative difference in token counts. It does not by itself establish pricing, latency, energy consumption, or model quality.
10. Diacritics transformations and any natural Nigerian corpus will be separate extensions, not mixed into the primary baseline.
11. Orthography perturbations use an NFC reference; published-versus-NFC effects and NFC-versus-NFD effects are reported separately.
12. Token reductions and bootstrap intervals lead the paper's results; p-values remain secondary supporting tables.
13. Gemma vocabulary size (262,144 versus 128,256) is a potential confound. Vocabulary size, training data, and segmentation design cannot be separated by this study. Embedding cost and language quality are not measured.

## Pending work

- [x] Run `python src/compare_tokenizers.py`.
- [x] Inspect and interpret `results/tokenizer_identity.json`.
- [x] Identify the three tokens unique to each tokenizer and all regions containing the 246 shared-token ID mismatches.
- [x] Determine whether the core lexical vocabulary and merge rules are identical after excluding added/control tokens.
- [x] Verify acceptance of the FLORES+ dataset conditions.
- [x] Record the exact FLORES+ version, revision, license, splits, and language-file identifiers.
- [x] Create a corpus-loading and alignment-validation script.
- [x] Predefine the row-level results schema and primary measurement rules.
- [x] Run the four languages through all three tokenizers.
- [x] Calculate fertility, relative tokenization cost, characters per token, and word fragmentation.
- [x] Produce paired statistical summaries and initial figures.
- [x] Run word-level error analysis for Hausa, Igbo, and Yoruba.
- [x] Run the separately documented controlled diacritics extension.
- [x] Run a natural-corpus extension: MasakhaNER 2.0 news replication.
- [x] Run NaijaSenti social-media replication and mention/URL sensitivity checks.
- [x] Run focused FLORES+ orthography experiments with an NFC reference.
- [x] Add vocabulary-size caveats and prioritize effect sizes and confidence intervals.
- [x] Pin original identity-comparison revisions and support explicitly pinned alternative models.
- [x] Calculate exact NFC English-relative perturbation premiums and intervals.
- [x] Calculate paired Gemma advantage under NFC versus NFD.
- [x] Run operational UAX-29 word-boundary sensitivity.
- [ ] Obtain access to and compare `meta-llama/Llama-3.1-8B` before attributing control-token changes to N-ATLaS.

## Evidence index

| Evidence | Location | Status |
|---|---|---|
| Project protocol | `PROJECT_START_GUIDE.md` | Current starting guide |
| Environment specification | `requirements.txt` | Recorded |
| Single-tokenizer inspection | `src/inspect_tokenizer.py` | Working |
| Formal identity comparison | `src/compare_tokenizers.py` | Run successfully |
| Identity report | `results/tokenizer_identity.json` | Generated and interpreted |
| Word-level analysis | `results/word_analysis/WORD_FRAGMENTATION.md` | Generated and interpreted |
| Word-analysis metadata | `results/word_analysis/word_analysis_metadata.json` | Generated |
| Diacritics report | `results/summary/DIACRITICS_RESULTS.md` | Generated and interpreted |
| Diacritics figure | `results/figures/figure_4_diacritics_effect.png` | Generated and inspected |
| News replication | `results/masakhaner2/RESULTS.md` | Generated and interpreted |
| Tweet replication | `results/naijasenti/RESULTS.md` | Generated and interpreted |
| Three-corpus comparison | `results/naijasenti/three_corpus_comparison.png` | Generated and inspected |
| Focused orthography | `results/orthography/ORTHOGRAPHY_RESULTS.md` | Run with NFC reference |
| Orthography figure | `results/orthography/orthography_effects.png` | Generated |
| Updated research summary | `RESEARCH_UPDATE.md` | Consolidated current results |
| Premium and normalization refinements | `results/refinements/REFINED_RESULTS.md` | Generated and interpreted |
| Llama 3.1 identity comparison | Planned `results/tokenizer_identity_llama31.json` | Pending Hugging Face access; no result yet |

## Paper notes

### 2026-10-02: Configuration, orthography statistics and publication

Pinned Meta-Llama-3-8B config: max_position_embeddings=8192, rope_scaling=null. On standalone NFC words without special tokens, N-ATLaS uses 7 tokens for ƙarƙashin and 12 for lọ́wọ́lọ́wọ́; Gemma uses 5 and 12 respectively. Added fewer/equal/more sentence counts and two-sided approximate Wilcoxon tests (zsplit) to orthography_summary.csv using saved token counts; Holm correction uses all 34 existing summary comparisons, including published and auxiliary conditions. Existing bootstrap estimates are unchanged. Numerical zero p-values denote floating-point underflow.

Both Llama-3.1-8B and Llama-3.1-8B-Instruct still return HTTP 403. Pinned reproduction commands are recorded in results/llama31_access_status.json. The supplied approval screenshot names Meta-Llama-Guard-2-8B, a different repository.

GitHub publication excludes raw/processed corpora, raw sentence-level results and corpus-derived word-analysis inventories/reports. Those artifacts remain available locally; aggregate results, figures, metadata and analysis scripts are included.

### 2026-10-02: Token-total premium audit

Ran `src/token_total_premiums.py` locally using cached pinned tokenizers on all 2,009 aligned FLORES+ sentences per language, normalized to NFC. Results and reproducibility metadata are in `results/token_total_premiums/`. This metric is total language tokens divided by total English tokens, distinct from the fertility-relative premiums in `src/refine_premiums.py`. Used the same percentile bootstrap method, 10,000 replicates, seed 20260930, and paired sentence indices across English, target language and perturbations. All 2,009 English sentences were already NFC. Under this definition Yoruba all-mark removal eliminates 58.72% [58.08%, 59.35%] of N-ATLaS excess and 57.54% [56.86%, 58.21%] of Gemma excess. These are perturbation effects, not causal allocations of linguistic burden.

Rechecked Llama 3.1 access: Hugging Face returned HTTP 403; no identity conclusion is available. Cached pinned N-ATLaS config records max_position_embeddings=131072 and llama3 rope_scaling with factor=8.0, high_freq_factor=4.0, low_freq_factor=1.0 and original_max_position_embeddings=8192. Its chat template contains both 'Cutting Knowledge Date' and 'Environment: ipython'. These observations do not establish tokenizer identity with Llama 3.1.

The evidence establishes ordinary-text lexical equivalence between N-ATLaS and the tested Llama 3 tokenizer and substantial language fertility gaps in FLORES+. Control-token differences must be described relative to that tested release; their origin remains unresolved pending Llama 3.1 access. Lossy spelling perturbations quantify how much measured excess can be eliminated, without assigning causal shares or recommending altered spelling. Gemma uses fewer tokens across three corpora, but vocabulary capacity, training data, and segmentation design remain confounded. NFC/NFD changes advantage magnitude without reversing rank and supports NFC in the tested pipeline where canonical normalization is appropriate. These findings do not establish model quality, real monetary cost, or universal language behavior.

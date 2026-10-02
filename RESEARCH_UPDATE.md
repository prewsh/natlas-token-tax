# Updated research findings — 2026-10-01

This is the current interpretation of the completed experiments. Exact revisions, transformations, checksums, and historical results remain in RESEARCH_LOG.md and the experiment metadata.

## Findings across three text settings

N-ATLaS and Llama 3 produced identical ordinary-text token IDs throughout FLORES+, MasakhaNER news, and NaijaSenti tweets. Their control-token configurations differ, but the inspected lexical pipeline is equivalent.

The Llama 3.1 comparison is pending: the account received a Hugging Face 403 access denial for `meta-llama/Llama-3.1-8B`. We cannot attribute control-token differences from Llama 3 to N-ATLaS modifications until its likely base version is compared. The comparison script now pins revisions explicitly; the prepared Llama 3.1 revision is `d04e592bb4f6aa9cfee91e2e20afa771667e1d4b`.

Gemma uses fewer total tokens on identical text in each Nigerian-language subset:

| Language | FLORES+ reduction | News reduction | Tweet reduction |
|---|---:|---:|---:|
| Hausa | 13.29% | 10.80% | 16.99% |
| Igbo | 9.77% | 10.91% | 9.20% |
| Yoruba | 11.53% | 11.02% | 11.33% |

The primary evidence is the paired effect size and its bootstrap confidence interval, available in each corpus's paired comparison CSV. Wilcoxon tests remain supporting tables. Large samples can yield small p-values even for small effects; statistical significance does not establish practical importance.

Gemma has 262,144 vocabulary entries versus 128,256 for N-ATLaS/Llama 3. Vocabulary capacity, tokenizer training data, and segmentation design differ together. This study cannot attribute the advantage to any one factor or show that the language gap has been solved. At fixed embedding width a larger vocabulary entails a larger embedding table, but actual memory, runtime cost, and model quality were not measured.

## Refined orthography experiment

The new experiment uses NFC text as the reference, separating representation normalization from mark removal. The primary corpus experiments retain their published-text reference and remain valid as measurements of that input.

| Perturbation from NFC | N-ATLaS / Llama token reduction | Gemma token reduction |
|---|---:|---:|
| Igbo: tone marks removed | 0.24% | 0.21% |
| Igbo: underdots removed | 14.27% | 13.20% |
| Igbo: all Mn marks removed | 14.54% | 13.43% |
| Yoruba: tone marks removed | 25.93% | 25.30% |
| Yoruba: underdots removed | 14.24% | 11.45% |
| Yoruba: all Mn marks removed | 36.88% | 33.27% |
| Hausa: hooked letters replaced | 5.30% | 2.97% |

Tone removal makes the larger single-set difference in Yoruba. Underdot removal accounts for nearly all of the measured Igbo all-mark effect. These statements describe the corpus-wide perturbations, not the cost per individual mark.

Normalization matters: 576 Yoruba and 69 Igbo sentences were not already NFC. Changing published Yoruba text to NFC saved 1,472 N-ATLaS tokens and 1,684 Gemma tokens. Relative to the published totals those are 1.02% and 1.32%. The earlier raw-reference all-mark reductions (37.53% and 34.15%) therefore become 36.88% and 33.27% with the NFC reference. The old estimate includes both normalization and mark removal.

NFD retained all spelling distinctions but increased token counts relative to NFC:

| Language | N-ATLaS / Llama increase | Gemma increase |
|---|---:|---:|
| Igbo | 7.99% | 11.57% |
| Yoruba | 18.74% | 26.49% |

Tone and underdot effects are not additive. In Yoruba, combined tone-and-underdot removal saved 4,726 fewer N-ATLaS tokens and 4,415 fewer Gemma tokens than the separate savings summed. Additional non-tone/non-underdot marks contributed only 52 and 46 tokens to the all-Mn contrast. Igbo interaction was close to zero (3 and 2 tokens). U+0329 did not occur in this FLORES+ corpus; that does not imply absence from other sources.

The decoded vocabulary audit found no complete lowercase ṣ, ƙ, ɗ, ɓ, or ƴ inside individually decoded N-ATLaS entries, while Gemma had complete-letter entries. This is a coverage diagnostic, not inability to encode these letters: partial UTF-8 pieces can combine across multiple tokens. Counts are not controlled for vocabulary size and do not establish causal tokenizer quality.

All spelling perturbations are diagnostic. Removing underdots also maps ṣ to s; hooked-letter replacement maps ƙ/ɗ/ɓ/ƴ and uppercase variants to k/d/b/y. These changes discard meaningful distinctions and are not writing recommendations.

## Current artifacts

### Exact premiums and normalization comparison

Both English and language reference text are NFC. Premium is corpus tokens per whitespace word divided by English fertility under the same tokenizer. Share of excess removed is `(premium before - premium after)/(premium before - 1)`.

| N-ATLaS / Llama contrast | NFC premium | After perturbation | Excess removed | 95% CI for excess removed |
|---|---:|---:|---:|---:|
| Hausa hooked-letter replacement | 1.7508× | 1.6580× | 12.36% | 11.78%–12.93% |
| Igbo all-Mn removal | 2.1026× | 1.7970× | 27.72% | 27.18%–28.25% |
| Yoruba all-Mn removal | 2.3255× | 1.4678× | 64.71% | 64.11%–65.28% |

These are transformation effects on measured excess, not causal attribution. Hausa's remaining excess is not explained by hooked-letter substitution; vocabulary coverage is a hypothesis. Tone-only and underdot-only effects must not be added as independent shares.

Gemma's paired Yoruba advantage is 11.80% (95% CI 11.60%–12.00%) on NFC and 6.04% (5.91%–6.18%) on NFD. Thus representation changes the magnitude of the advantage, without reversing ranking. NFC preserves canonical spelling information and saved tokens in the measured pipeline; prefer NFC where application requirements permit canonical normalization.

Unicode default-word-boundary sensitivity retained the Nigerian-language premium ordering. N-ATLaS premiums changed from 1.7508× to 1.7530× for Hausa, 2.1026× to 2.0455× for Igbo, and 2.3255× to 2.3337× for Yoruba. This is an operational UAX-29-based check using `regex.WORD`, counting letter/number-containing segments; it is not morphology-aware segmentation or a Unicode conformance certification.

Use **tone marks**, **underdotted letters**, and **hooked letters** when discussing the respective features. The Igbo all-mark perturbation is dominated by underdotted letters in this corpus. Do not generalize this to every writer or every text. The NaijaSenti marked/unmarked split detects any letter-attached combining marks, not tone usage alone.

The orthography run uses deterministic seed `20261001` to identify that experiment; other runs and these premium refinements use `20260930`. Different recorded seeds are valid; they do not change the estimator or point estimates.

- Focused report: [ORTHOGRAPHY_RESULTS.md](results/orthography/ORTHOGRAPHY_RESULTS.md)
- Effect estimates and intervals: `results/orthography/orthography_summary.csv`
- Normalization audit: `results/orthography/normalization_audit.csv`
- Mark inventory: `results/orthography/mark_inventory.csv`
- Interaction analysis: `results/orthography/additivity.csv`
- Decoded vocabulary audit: `results/orthography/vocabulary_audit.csv`
- Updated figure: `results/orthography/orthography_effects.png` and `.svg`
- Reproduction: `MPLCONFIGDIR=.cache/matplotlib python src/orthography_experiments.py`
- Exact premium, normalization and word-boundary refinements: `results/refinements/REFINED_RESULTS.md`, CSVs, and metadata; reproduce with `python src/refine_premiums.py`.

Use the new orthography figure for the refined mechanism discussion. The earlier figure 4 remains the historical raw-reference result. News and tweet results lack a matched English subset, so they establish cross-tokenizer replication rather than a new English-relative tax. News punctuation spacing, code mixing, dataset selection, and within-document/user dependence limit cross-corpus generalization.

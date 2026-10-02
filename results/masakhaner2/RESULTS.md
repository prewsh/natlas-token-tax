# MasakhaNER 2.0 news replication

Published CoNLL tokens are joined with one space. Exact duplicate sentences are removed within each language across all splits. No model training is performed; all splits provide descriptive text evidence.

The whitespace denominator includes separately spaced punctuation. Interpret fertility as tokens per published spacing unit, not a directly matched FLORES+ word denominator. Characters per token provides an additional view.

## Corpus audit

| language | sentences | whitespace_units_including_punctuation | lexical_units_containing_letters | sentences_with_combining_marks_after_NFD | exact_duplicate_sentences_removed |
| --- | --- | --- | --- | --- | --- |
| Hausa | 7913 | 213251 | 194106 | 0 | 252 |
| Igbo | 10381 | 328931 | 286732 | 10201 | 524 |
| Yoruba | 9633 | 241807 | 213256 | 9597 | 190 |

## Tokenization summary

| language | tokenizer | sentences | tokens_per_whitespace_unit | non_whitespace_characters_per_token | one_token_unit_share | four_plus_token_unit_share |
| --- | --- | --- | --- | --- | --- | --- |
| Hausa | gemma4 | 7913 | 1.6804 | 2.4932 | 0.5266 | 0.0341 |
| Hausa | llama3 | 7913 | 1.884 | 2.2238 | 0.421 | 0.0571 |
| Hausa | natlas | 7913 | 1.884 | 2.2238 | 0.421 | 0.0571 |
| Igbo | gemma4 | 10381 | 1.9591 | 1.8991 | 0.5085 | 0.1216 |
| Igbo | llama3 | 10381 | 2.199 | 1.6919 | 0.4105 | 0.1394 |
| Igbo | natlas | 10381 | 2.199 | 1.6919 | 0.4105 | 0.1394 |
| Yoruba | gemma4 | 9633 | 3.1018 | 1.4877 | 0.2459 | 0.3498 |
| Yoruba | llama3 | 9633 | 3.486 | 1.3237 | 0.2177 | 0.4123 |
| Yoruba | natlas | 9633 | 3.486 | 1.3237 | 0.2177 | 0.4123 |

## Direct paired comparison

# Paired N-ATLaS versus Gemma 4 comparison

Positive fertility differences and reductions indicate fewer tokens 
under Gemma 4. Confidence intervals come from 10,000 paired 
sentence-set bootstrap resamples. Wilcoxon p-values are two-sided 
and Holm-adjusted across the three language comparisons.

| language | natlas_tokens_per_word | gemma_tokens_per_word | fertility_difference_natlas_minus_gemma | gemma_relative_token_reduction | relative_reduction_ci95_low | relative_reduction_ci95_high | sentences_gemma_fewer_tokens | sentences_equal_tokens | sentences_gemma_more_tokens | wilcoxon_p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hausa | 1.8840 | 1.6804 | 0.2036 | 0.1080 | 0.1067 | 0.1094 | 7261 | 347 | 305 | <1e-300 |
| Igbo | 2.1990 | 1.9591 | 0.2399 | 0.1091 | 0.1084 | 0.1098 | 9922 | 401 | 58 | <1e-300 |
| Yoruba | 3.4860 | 3.1018 | 0.3842 | 0.1102 | 0.1090 | 0.1115 | 9211 | 391 | 31 | <1e-300 |


N-ATLaS/Llama token-ID mismatch count: 0.

## Limits

- News-domain evidence does not establish general everyday-language behavior.
- The languages are not translations of matching content; cross-language differences may reflect topic and source composition.
- Source spacing and earlier preprocessing may affect token counts; original website text is not reconstructed.
- Sentence confidence intervals do not account for dependence within source articles because document identifiers are unavailable.
- No English subset is included; an English-relative natural-corpus tax is not estimated.
- Working license: CC BY-NC 4.0 per original repository README; the conflicting Hugging Face AFL-3.0 label is recorded. Raw and processed text are excluded from Git.

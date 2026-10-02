# NaijaSenti social-media replication

Published text is preserved. All splits are used descriptively; exact duplicate tweets within each language and empty rows are removed. Sentiment labels are not used to infer language purity.

## Corpus audit

| language | unique_tweets | whitespace_units | exact_duplicates_removed | empty_rows_removed | tweets_with_mentions | tweets_with_urls | tweets_with_diacritics | tweets_with_hashtags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hausa | 21937 | 298517 | 215 | 0 | 16626 | 501 | 122 | 377 |
| Igbo | 15677 | 185661 | 38 | 0 | 8211 | 3032 | 4219 | 1237 |
| Yoruba | 14890 | 316888 | 237 | 0 | 4566 | 2187 | 11739 | 5867 |

## Primary paired results

# Paired N-ATLaS versus Gemma 4 comparison

Positive fertility differences and reductions indicate fewer tokens 
under Gemma 4. Confidence intervals come from 10,000 paired 
tweet-set bootstrap resamples. Wilcoxon p-values are two-sided 
and Holm-adjusted across the three language comparisons.

| language | natlas_tokens_per_word | gemma_tokens_per_word | fertility_difference_natlas_minus_gemma | gemma_relative_token_reduction | relative_reduction_ci95_low | relative_reduction_ci95_high | sentences_gemma_fewer_tokens | sentences_equal_tokens | sentences_gemma_more_tokens | wilcoxon_p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hausa | 2.2211 | 1.8437 | 0.3773 | 0.1699 | 0.1683 | 0.1715 | 20807 | 1012 | 118 | <1e-300 |
| Igbo | 2.3227 | 2.1089 | 0.2138 | 0.0920 | 0.0901 | 0.0940 | 11666 | 3028 | 983 | <1e-300 |
| Yoruba | 2.7917 | 2.4755 | 0.3162 | 0.1133 | 0.1121 | 0.1144 | 13693 | 847 | 350 | <1e-300 |


## Fragmentation and fertility

| language | tokenizer | tweets | tokens_per_whitespace_unit | non_whitespace_characters_per_token | one_token_unit_share | four_plus_token_unit_share |
| --- | --- | --- | --- | --- | --- | --- |
| Hausa | gemma4 | 21937 | 1.8437 | 2.4929 | 0.4185 | 0.0436 |
| Hausa | llama3 | 21937 | 2.2211 | 2.0694 | 0.3097 | 0.0886 |
| Hausa | natlas | 21937 | 2.2211 | 2.0694 | 0.3097 | 0.0886 |
| Igbo | gemma4 | 15677 | 2.1089 | 2.1458 | 0.3866 | 0.0796 |
| Igbo | llama3 | 15677 | 2.3227 | 1.9483 | 0.3059 | 0.1063 |
| Igbo | natlas | 15677 | 2.3227 | 1.9483 | 0.3059 | 0.1063 |
| Yoruba | gemma4 | 14890 | 2.4755 | 1.6663 | 0.393 | 0.196 |
| Yoruba | llama3 | 14890 | 2.7917 | 1.4776 | 0.3157 | 0.2576 |
| Yoruba | natlas | 14890 | 2.7917 | 1.4776 | 0.3157 | 0.2576 |

## Descriptive sensitivity checks

| language | condition | tweets | natlas_total_tokens | gemma4_total_tokens | gemma_relative_reduction |
| --- | --- | --- | --- | --- | --- |
| Hausa | published | 21937 | 663030 | 550387 | 0.1699 |
| Hausa | mentions_urls_removed | 21937 | 618672 | 503142 | 0.1867 |
| Hausa | published_with_diacritics | 122 | 5163 | 4439 | 0.1402 |
| Hausa | published_without_diacritics | 21815 | 657867 | 545948 | 0.1701 |
| Igbo | published | 15677 | 431228 | 391539 | 0.092 |
| Igbo | mentions_urls_removed | 15677 | 355947 | 311958 | 0.1236 |
| Igbo | published_with_diacritics | 4219 | 137689 | 124398 | 0.0965 |
| Igbo | published_without_diacritics | 11458 | 293539 | 267141 | 0.0899 |
| Yoruba | published | 14890 | 884656 | 784464 | 0.1133 |
| Yoruba | mentions_urls_removed | 14890 | 841253 | 738320 | 0.1224 |
| Yoruba | published_with_diacritics | 11739 | 763290 | 670968 | 0.121 |
| Yoruba | published_without_diacritics | 3151 | 121366 | 113496 | 0.0648 |

Mention/URL removal changes the text and is a secondary condition. Diacritics groups are observational, not paired mark-removal experiments. The indicator detects Unicode combining marks attached to letters after NFD, excluding emoji variation selectors. It includes accented borrowed words and does not identify language purity or tone alone.

N-ATLaS/Llama token-ID mismatches: 0.

## Interpretation limits

- Released tweets have prior anonymization/preprocessing. They are not untouched platform data.
- Code mixing, abbreviations, emojis, and subject matter can change token counts; no causal effect of code mixing is estimated.
- No matched English baseline exists; this estimates tokenizer differences rather than English-relative tax.
- No author/thread IDs are available for cluster resampling; tweet bootstrap assumes independence.
- The sample was selected for sentiment annotation and does not represent all Nigerian online writing.
- Original-release license is CC BY-NC-SA 4.0; data is excluded from Git. Cite Muhammad et al. (2022), https://aclanthology.org/2022.lrec-1.63/.

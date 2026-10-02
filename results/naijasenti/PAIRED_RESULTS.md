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

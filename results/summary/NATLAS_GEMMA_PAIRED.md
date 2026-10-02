# Paired N-ATLaS versus Gemma 4 comparison

Positive fertility differences and reductions indicate fewer tokens 
under Gemma 4. Confidence intervals come from 10,000 paired 
sentence-set bootstrap resamples. Wilcoxon p-values are two-sided 
and Holm-adjusted across the four language comparisons.

| language | natlas_tokens_per_word | gemma_tokens_per_word | fertility_difference_natlas_minus_gemma | gemma_relative_token_reduction | relative_reduction_ci95_low | relative_reduction_ci95_high | sentences_gemma_fewer_tokens | sentences_equal_tokens | sentences_gemma_more_tokens | wilcoxon_p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| English | 1.2359 | 1.2366 | -0.0007 | -0.0006 | -0.0035 | 0.0023 | 623 | 855 | 531 | 6.731e-02 |
| Hausa | 2.1637 | 1.8761 | 0.2876 | 0.1329 | 0.1303 | 0.1355 | 1933 | 43 | 33 | <1e-300 |
| Igbo | 2.5993 | 2.3454 | 0.2539 | 0.0977 | 0.0956 | 0.0997 | 1917 | 47 | 45 | <1e-300 |
| Yoruba | 2.9038 | 2.5690 | 0.3347 | 0.1153 | 0.1132 | 0.1173 | 1935 | 46 | 28 | <1e-300 |

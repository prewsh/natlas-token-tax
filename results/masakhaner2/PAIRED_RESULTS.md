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

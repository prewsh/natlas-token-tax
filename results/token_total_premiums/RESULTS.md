# Token-total premium audit — 2026-10-02

Token-total premium = total language tokens / total English tokens on the same 2,009 aligned sentences. This differs from the earlier fertility ratio. Both use NFC here. Bootstrap: 10,000 aligned paired resamples, seed 20260930, percentile 95% intervals.

## NFC totals and premiums

| language | tokenizer | NFC_total_tokens | English_total_tokens | token_total_premium | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| English | natlas_llama | 52963 | 52963 | 1.0 | 1.0 | 1.0 |
| Hausa | natlas_llama | 107034 | 52963 | 2.02092 | 2.00429 | 2.038409 |
| Igbo | natlas_llama | 125722 | 52963 | 2.37377 | 2.350787 | 2.396979 |
| Yoruba | natlas_llama | 142409 | 52963 | 2.688839 | 2.65407 | 2.723651 |
| English | gemma4 | 52995 | 52995 | 1.0 | 1.0 | 1.0 |
| Hausa | gemma4 | 92809 | 52995 | 1.751278 | 1.737367 | 1.765588 |
| Igbo | gemma4 | 113399 | 52995 | 2.139806 | 2.119601 | 2.160325 |
| Yoruba | gemma4 | 125611 | 52995 | 2.370242 | 2.340446 | 2.399907 |

## Share of excess removed

| language | tokenizer | condition | premium_before | premium_after | premium_after_ci95_low | premium_after_ci95_high | share_excess_removed | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hausa | natlas_llama | hooked_letters_replaced | 2.02092 | 1.913827 | 1.898879 | 1.929336 | 0.104899 | 0.099909 | 0.109779 |
| Igbo | natlas_llama | all_Mn_removed | 2.37377 | 2.028737 | 2.011673 | 2.046444 | 0.251158 | 0.246133 | 0.256119 |
| Yoruba | natlas_llama | all_Mn_removed | 2.688839 | 1.69709 | 1.681714 | 1.712419 | 0.587237 | 0.580776 | 0.593534 |
| Yoruba | natlas_llama | tone_only_removed | 2.688839 | 1.99173 | 1.971306 | 2.012425 | 0.412774 | 0.407333 | 0.41821 |
| Yoruba | natlas_llama | underdot_only_removed | 2.688839 | 2.305949 | 2.279439 | 2.332311 | 0.226718 | 0.222377 | 0.23105 |
| Hausa | gemma4 | hooked_letters_replaced | 1.751278 | 1.699179 | 1.686157 | 1.712672 | 0.069347 | 0.065684 | 0.073102 |
| Igbo | gemma4 | all_Mn_removed | 2.139806 | 1.852458 | 1.836355 | 1.868562 | 0.252103 | 0.247093 | 0.257178 |
| Yoruba | gemma4 | all_Mn_removed | 2.370242 | 1.581753 | 1.567781 | 1.59611 | 0.575438 | 0.568596 | 0.582061 |
| Yoruba | gemma4 | tone_only_removed | 2.370242 | 1.770658 | 1.753946 | 1.787381 | 0.437576 | 0.431554 | 0.443272 |
| Yoruba | gemma4 | underdot_only_removed | 2.370242 | 2.098896 | 2.075154 | 2.122802 | 0.198028 | 0.194085 | 0.201943 |

Share = (premium before - premium after)/(premium before - 1). These are effects of specified lossy transformations, not causal shares of orthographic burden.

## NFC characters and fragmentation

| language | tokenizer | characters_per_token_including_whitespace | characters_per_token_excluding_whitespace | share_1 | share_2 | share_3 | share_4plus |
| --- | --- | --- | --- | --- | --- | --- | --- |
| English | natlas_llama | 4.855465 | 4.084229 | 0.828888 | 0.133637 | 0.026065 | 0.011411 |
| Hausa | natlas_llama | 2.572033 | 2.128557 | 0.34024 | 0.351096 | 0.201383 | 0.107281 |
| Igbo | natlas_llama | 2.076733 | 1.707824 | 0.239061 | 0.359914 | 0.205473 | 0.195552 |
| Yoruba | natlas_llama | 1.728072 | 1.394238 | 0.2689 | 0.276589 | 0.176731 | 0.27778 |
| English | gemma4 | 4.852533 | 4.081762 | 0.841769 | 0.117886 | 0.025388 | 0.014957 |
| Hausa | gemma4 | 2.966253 | 2.454805 | 0.441073 | 0.342282 | 0.160265 | 0.05638 |
| Igbo | gemma4 | 2.30241 | 1.893412 | 0.349703 | 0.284885 | 0.182282 | 0.18313 |
| Yoruba | gemma4 | 1.959168 | 1.58069 | 0.342624 | 0.246882 | 0.197195 | 0.2133 |

Character counts are Python Unicode code-point counts, not bytes or grapheme clusters. Both whitespace-inclusive and whitespace-exclusive measures are given. Fragmentation uses tokenizer offsets overlapping whitespace units.

English normalization audit: {'English_sentences': 2009, 'English_not_NFC': 0}

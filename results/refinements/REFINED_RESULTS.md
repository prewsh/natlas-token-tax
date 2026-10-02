# Refined premium and normalization results

Premium = language corpus fertility / English corpus fertility for the same tokenizer. Both reference texts are NFC. Share of excess removed = (premium before - premium after)/(premium before - 1). All 2,009 aligned sentence IDs are resampled jointly across languages, tokenizers, and conditions; 10,000 replicates, seed 20260930.

## Paired orthography premiums

| language | tokenizer | condition | premium_NFC | premium_after | share_excess_removed | premium_NFC_ci95_low | premium_NFC_ci95_high | premium_after_ci95_low | premium_after_ci95_high | share_excess_removed_ci95_low | share_excess_removed_ci95_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hausa | natlas_llama | hooked_letters_replaced | 1.75076 | 1.65798 | 0.12358 | 1.73871 | 1.7633 | 1.64788 | 1.66812 | 0.11784 | 0.12933 |
| Hausa | gemma4 | hooked_letters_replaced | 1.51716 | 1.47203 | 0.08727 | 1.50753 | 1.52698 | 1.46318 | 1.481 | 0.08277 | 0.09176 |
| Igbo | natlas_llama | tone_only_removed | 2.10264 | 2.09749 | 0.00467 | 2.08663 | 2.11924 | 2.08161 | 2.11395 | 0.0038 | 0.0056 |
| Igbo | natlas_llama | underdot_only_removed | 2.10264 | 1.80267 | 0.27205 | 2.08663 | 2.11924 | 1.79112 | 1.81447 | 0.26663 | 0.27729 |
| Igbo | natlas_llama | tone_and_underdot_removed | 2.10264 | 1.79747 | 0.27676 | 2.08663 | 2.11924 | 1.78605 | 1.80908 | 0.27138 | 0.28213 |
| Igbo | natlas_llama | all_Mn_removed | 2.10264 | 1.79702 | 0.27717 | 2.08663 | 2.11924 | 1.78566 | 1.80862 | 0.27178 | 0.28253 |
| Igbo | gemma4 | tone_only_removed | 1.8954 | 1.89139 | 0.00448 | 1.88005 | 1.91107 | 1.8762 | 1.90689 | 0.00363 | 0.00536 |
| Igbo | gemma4 | underdot_only_removed | 1.8954 | 1.64527 | 0.27935 | 1.88005 | 1.91107 | 1.63355 | 1.65704 | 0.27382 | 0.28479 |
| Igbo | gemma4 | tone_and_underdot_removed | 1.8954 | 1.64122 | 0.28387 | 1.88005 | 1.91107 | 1.62963 | 1.6529 | 0.27838 | 0.28937 |
| Igbo | gemma4 | all_Mn_removed | 1.8954 | 1.64087 | 0.28426 | 1.88005 | 1.91107 | 1.62926 | 1.65252 | 0.27878 | 0.28981 |
| Yoruba | natlas_llama | tone_only_removed | 2.32553 | 1.72262 | 0.45485 | 2.29889 | 2.35123 | 1.70967 | 1.73563 | 0.44969 | 0.45999 |
| Yoruba | natlas_llama | underdot_only_removed | 2.32553 | 1.99438 | 0.24983 | 2.29889 | 2.35123 | 1.9749 | 2.01352 | 0.24525 | 0.25439 |
| Yoruba | natlas_llama | tone_and_underdot_removed | 2.32553 | 1.46864 | 0.64646 | 2.29889 | 2.35123 | 1.45982 | 1.47754 | 0.6405 | 0.65219 |
| Yoruba | natlas_llama | all_Mn_removed | 2.32553 | 1.46779 | 0.6471 | 2.29889 | 2.35123 | 1.45902 | 1.47665 | 0.64111 | 0.65285 |
| Yoruba | gemma4 | tone_only_removed | 2.04998 | 1.53141 | 0.49388 | 2.02749 | 2.07207 | 1.52024 | 1.54254 | 0.48799 | 0.4995 |
| Yoruba | gemma4 | underdot_only_removed | 2.04998 | 1.8153 | 0.22351 | 2.02749 | 2.07207 | 1.79803 | 1.8323 | 0.21925 | 0.22779 |
| Yoruba | gemma4 | tone_and_underdot_removed | 2.04998 | 1.36878 | 0.64877 | 2.02749 | 2.07207 | 1.36032 | 1.37729 | 0.64243 | 0.65487 |
| Yoruba | gemma4 | all_Mn_removed | 2.04998 | 1.36803 | 0.64949 | 2.02749 | 2.07207 | 1.35954 | 1.37656 | 0.64313 | 0.65557 |

## Gemma advantage by Unicode representation

| language | normalization | gemma_relative_reduction | ci95_low | ci95_high |
| --- | --- | --- | --- | --- |
| Hausa | NFC | 0.1329 | 0.13031 | 0.13554 |
| Hausa | NFD | 0.13282 | 0.13022 | 0.13545 |
| Igbo | NFC | 0.09802 | 0.09597 | 0.10006 |
| Igbo | NFD | 0.06807 | 0.06625 | 0.06988 |
| Yoruba | NFC | 0.11796 | 0.11598 | 0.11997 |
| Yoruba | NFD | 0.06043 | 0.05907 | 0.06175 |

## Word-boundary sensitivity

| language | tokenizer | denominator | language_word_units | english_word_units | premium_vs_English | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hausa | natlas_llama | whitespace | 49468 | 42855 | 1.75076 | 1.73871 | 1.7633 |
| Hausa | natlas_llama | unicode | 49800 | 43198 | 1.75301 | 1.74128 | 1.76512 |
| Hausa | gemma4 | whitespace | 49468 | 42855 | 1.51716 | 1.50753 | 1.52698 |
| Hausa | gemma4 | unicode | 49800 | 43198 | 1.51911 | 1.50987 | 1.52833 |
| Igbo | natlas_llama | whitespace | 48381 | 42855 | 2.10264 | 2.08663 | 2.11924 |
| Igbo | natlas_llama | unicode | 50131 | 43198 | 2.04548 | 2.03033 | 2.06122 |
| Igbo | gemma4 | whitespace | 48381 | 42855 | 1.8954 | 1.88005 | 1.91107 |
| Igbo | gemma4 | unicode | 50131 | 43198 | 1.84388 | 1.82992 | 1.85821 |
| Yoruba | natlas_llama | whitespace | 49550 | 42855 | 2.32553 | 2.29889 | 2.35123 |
| Yoruba | natlas_llama | unicode | 49772 | 43198 | 2.33369 | 2.30774 | 2.35894 |
| Yoruba | gemma4 | whitespace | 49550 | 42855 | 2.04998 | 2.02749 | 2.07207 |
| Yoruba | gemma4 | unicode | 49772 | 43198 | 2.05718 | 2.03527 | 2.0787 |

The Unicode sensitivity uses regex WORD default Unicode word boundaries, counting only boundary-delimited segments containing letters or numbers. It is an operational UAX-29-based sensitivity, not language-specific morphological segmentation or a conformance certification. Punctuation and emoji-only segments are excluded; tokenizer numerator is unchanged.

## Interpretation limits

Perturbation shares measure excess eliminated by a specific lossy text transformation. They do not establish causal attribution of all excess to orthography. Separate tone and underdot shares cannot be summed because their effects interact. Remaining Hausa excess is unexplained by this hooked-letter experiment; vocabulary coverage is a hypothesis.
NFC/NFD compare canonically equivalent forms. Results can support NFC normalization for this tokenizer pipeline, subject to application-specific input requirements. A change in advantage magnitude is not a ranking reversal.
All text metrics include finite-corpus and word-denominator limitations. Statistical intervals describe paired sentence resampling, not a universal population guarantee.

# Focused orthography experiments

All effects use NFC as the reference. Positive reduction means the condition uses fewer tokens. Intervals use 10,000 paired sentence bootstrap replicates, seed 20261001.

## Normalization audit

| language | sentences | not_already_NFC |
| --- | --- | --- |
| Hausa | 2009 | 0 |
| Igbo | 2009 | 69 |
| Yoruba | 2009 | 576 |

## Effects relative to NFC

| language | tokenizer | condition | sentences | NFC_total_tokens | condition_total_tokens | token_reduction | relative_reduction | ci95_low | ci95_high | changed_sentences |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hausa | gemma4 | NFD | 2009 | 92809 | 92838 | -29 | -0.00031 | -0.00049 | -0.00015 | 19 |
| Hausa | gemma4 | hooked_letters_replaced | 2009 | 92809 | 90048 | 2761 | 0.02975 | 0.02812 | 0.03139 | 1143 |
| Hausa | gemma4 | published | 2009 | 92809 | 92809 | 0 | 0.0 | 0.0 | 0.0 | 0 |
| Hausa | natlas_llama | NFD | 2009 | 107034 | 107057 | -23 | -0.00021 | -0.00036 | -9e-05 | 19 |
| Hausa | natlas_llama | hooked_letters_replaced | 2009 | 107034 | 101362 | 5672 | 0.05299 | 0.05037 | 0.05568 | 1143 |
| Hausa | natlas_llama | published | 2009 | 107034 | 107034 | 0 | 0.0 | 0.0 | 0.0 | 0 |
| Igbo | gemma4 | NFD | 2009 | 113399 | 126522 | -13123 | -0.11572 | -0.11841 | -0.11304 | 1810 |
| Igbo | gemma4 | all_Mn_removed | 2009 | 113399 | 98171 | 15228 | 0.13429 | 0.13123 | 0.13727 | 1810 |
| Igbo | gemma4 | published | 2009 | 113399 | 113472 | -73 | -0.00064 | -0.00085 | -0.00045 | 69 |
| Igbo | gemma4 | tone_and_underdot_removed | 2009 | 113399 | 98192 | 15207 | 0.1341 | 0.13106 | 0.13706 | 1810 |
| Igbo | gemma4 | tone_only_removed | 2009 | 113399 | 113159 | 240 | 0.00212 | 0.0017 | 0.00255 | 155 |
| Igbo | gemma4 | underdot_and_U0329_removed | 2009 | 113399 | 98434 | 14965 | 0.13197 | 0.12901 | 0.13498 | 1810 |
| Igbo | gemma4 | underdot_only_removed | 2009 | 113399 | 98434 | 14965 | 0.13197 | 0.12905 | 0.13488 | 1810 |
| Igbo | natlas_llama | NFD | 2009 | 125722 | 135763 | -10041 | -0.07987 | -0.08184 | -0.07791 | 1810 |
| Igbo | natlas_llama | all_Mn_removed | 2009 | 125722 | 107448 | 18274 | 0.14535 | 0.14205 | 0.14859 | 1810 |
| Igbo | natlas_llama | published | 2009 | 125722 | 125755 | -33 | -0.00026 | -0.0004 | -0.00014 | 69 |
| Igbo | natlas_llama | tone_and_underdot_removed | 2009 | 125722 | 107475 | 18247 | 0.14514 | 0.14184 | 0.14838 | 1810 |
| Igbo | natlas_llama | tone_only_removed | 2009 | 125722 | 125414 | 308 | 0.00245 | 0.00199 | 0.00295 | 155 |
| Igbo | natlas_llama | underdot_and_U0329_removed | 2009 | 125722 | 107786 | 17936 | 0.14266 | 0.13946 | 0.14588 | 1810 |
| Igbo | natlas_llama | underdot_only_removed | 2009 | 125722 | 107786 | 17936 | 0.14266 | 0.13947 | 0.14593 | 1810 |
| Yoruba | gemma4 | NFD | 2009 | 125611 | 158883 | -33272 | -0.26488 | -0.26949 | -0.26017 | 1705 |
| Yoruba | gemma4 | all_Mn_removed | 2009 | 125611 | 83825 | 41786 | 0.33266 | 0.32729 | 0.33805 | 1705 |
| Yoruba | gemma4 | published | 2009 | 125611 | 127295 | -1684 | -0.01341 | -0.0162 | -0.01088 | 576 |
| Yoruba | gemma4 | tone_and_underdot_removed | 2009 | 125611 | 83871 | 41740 | 0.3323 | 0.3268 | 0.33748 | 1704 |
| Yoruba | gemma4 | tone_only_removed | 2009 | 125611 | 93836 | 31775 | 0.25296 | 0.24842 | 0.25741 | 1656 |
| Yoruba | gemma4 | underdot_and_U0329_removed | 2009 | 125611 | 111231 | 14380 | 0.11448 | 0.11184 | 0.11711 | 1690 |
| Yoruba | gemma4 | underdot_only_removed | 2009 | 125611 | 111231 | 14380 | 0.11448 | 0.11183 | 0.11708 | 1690 |
| Yoruba | natlas_llama | NFD | 2009 | 142409 | 169101 | -26692 | -0.18743 | -0.19099 | -0.1839 | 1705 |
| Yoruba | natlas_llama | all_Mn_removed | 2009 | 142409 | 89883 | 52526 | 0.36884 | 0.36327 | 0.37417 | 1705 |
| Yoruba | natlas_llama | published | 2009 | 142409 | 143881 | -1472 | -0.01034 | -0.01271 | -0.0081 | 576 |
| Yoruba | natlas_llama | tone_and_underdot_removed | 2009 | 142409 | 89935 | 52474 | 0.36847 | 0.36285 | 0.37393 | 1704 |
| Yoruba | natlas_llama | tone_only_removed | 2009 | 142409 | 105488 | 36921 | 0.25926 | 0.25489 | 0.26354 | 1656 |
| Yoruba | natlas_llama | underdot_and_U0329_removed | 2009 | 142409 | 122130 | 20279 | 0.1424 | 0.13941 | 0.14542 | 1690 |
| Yoruba | natlas_llama | underdot_only_removed | 2009 | 142409 | 122130 | 20279 | 0.1424 | 0.13929 | 0.14538 | 1690 |

## Mark inventory

| language | codepoint | name | occurrences | covered_by_tone_or_underdot |
| --- | --- | --- | --- | --- |
| Hausa | U+0301 | COMBINING ACUTE ACCENT | 17 | True |
| Hausa | U+0303 | COMBINING TILDE | 3 | False |
| Hausa | U+0304 | COMBINING MACRON | 1 | True |
| Hausa | U+0306 | COMBINING BREVE | 1 | False |
| Hausa | U+0308 | COMBINING DIAERESIS | 6 | False |
| Hausa | U+0327 | COMBINING CEDILLA | 2 | False |
| Hausa | U+0329 | COMBINING VERTICAL LINE BELOW | 0 | False |
| Igbo | U+0300 | COMBINING GRAVE ACCENT | 251 | True |
| Igbo | U+0301 | COMBINING ACUTE ACCENT | 59 | True |
| Igbo | U+0303 | COMBINING TILDE | 13 | False |
| Igbo | U+0304 | COMBINING MACRON | 22 | True |
| Igbo | U+0306 | COMBINING BREVE | 1 | False |
| Igbo | U+0307 | COMBINING DOT ABOVE | 5 | False |
| Igbo | U+0308 | COMBINING DIAERESIS | 7 | False |
| Igbo | U+0323 | COMBINING DOT BELOW | 23745 | True |
| Igbo | U+0326 | COMBINING COMMA BELOW | 1 | False |
| Igbo | U+0327 | COMBINING CEDILLA | 2 | False |
| Igbo | U+0329 | COMBINING VERTICAL LINE BELOW | 0 | False |
| Yoruba | U+0300 | COMBINING GRAVE ACCENT | 23139 | True |
| Yoruba | U+0301 | COMBINING ACUTE ACCENT | 26184 | True |
| Yoruba | U+0302 | COMBINING CIRCUMFLEX ACCENT | 1 | False |
| Yoruba | U+0303 | COMBINING TILDE | 2 | False |
| Yoruba | U+0308 | COMBINING DIAERESIS | 12 | False |
| Yoruba | U+0323 | COMBINING DOT BELOW | 15736 | True |
| Yoruba | U+0327 | COMBINING CEDILLA | 1 | False |
| Yoruba | U+0328 | COMBINING OGONEK | 30 | False |
| Yoruba | U+0329 | COMBINING VERTICAL LINE BELOW | 0 | False |

## Additivity

| language | tokenizer | tone_savings | underdot_savings | all_Mn_savings | tone_and_underdot_savings | interaction_savings | additional_other_mark_savings | all_minus_sum_savings | sentences_nonadditive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Igbo | gemma4 | 240 | 14965 | 15228 | 15207 | 2 | 21 | 23 | 40 |
| Igbo | natlas_llama | 308 | 17936 | 18274 | 18247 | 3 | 27 | 30 | 29 |
| Yoruba | gemma4 | 31775 | 14380 | 41786 | 41740 | -4415 | 46 | -4369 | 1440 |
| Yoruba | natlas_llama | 36921 | 20279 | 52526 | 52474 | -4726 | 52 | -4674 | 1473 |

Positive interaction_savings means combined tone-and-underdot removal saves more tokens than the two separate removals summed. Additional other-mark savings compare all Mn removal with that union. All-minus-sum mixes interaction with other-mark effects.

## Vocabulary audit

| tokenizer | letter | vocabulary_entries | entries_containing_complete_decoded_letter | entries_with_replacement_character |
| --- | --- | --- | --- | --- |
| natlas_llama | ẹ | 128256 | 6 | 1361 |
| natlas_llama | ọ | 128256 | 24 | 1361 |
| natlas_llama | ṣ | 128256 | 0 | 1361 |
| natlas_llama | ị | 128256 | 28 | 1361 |
| natlas_llama | ụ | 128256 | 25 | 1361 |
| natlas_llama | ƙ | 128256 | 0 | 1361 |
| natlas_llama | ɗ | 128256 | 0 | 1361 |
| natlas_llama | ɓ | 128256 | 0 | 1361 |
| natlas_llama | ƴ | 128256 | 0 | 1361 |
| gemma4 | ẹ | 262144 | 11 | 134 |
| gemma4 | ọ | 262144 | 36 | 134 |
| gemma4 | ṣ | 262144 | 3 | 134 |
| gemma4 | ị | 262144 | 34 | 134 |
| gemma4 | ụ | 262144 | 29 | 134 |
| gemma4 | ƙ | 262144 | 2 | 134 |
| gemma4 | ɗ | 262144 | 1 | 134 |
| gemma4 | ɓ | 262144 | 1 | 134 |
| gemma4 | ƴ | 262144 | 1 | 134 |

Entries are individually decoded through the tokenizer backend. Counts include complete lowercase letters only; incomplete UTF-8 pieces may decode to replacement characters and are excluded from letter counts. This diagnostic does not measure usable segmentation coverage or control vocabulary size.

## Limits and interpretation

- Tone set: U+0300, U+0301, U+0304. Underdot-only set: U+0323. U+0329 is counted separately and removed only in the explicitly labeled additional condition.
- Removing the underdot maps ṣ to s as well as changing vowels. Hook substitution maps ƙ/ɗ/ɓ/ƴ to k/d/b/y, including uppercase forms. These perturbations remove meaningful distinctions; they are not spelling recommendations.
- NFC and NFD are canonically equivalent representations; their difference isolates input encoding sensitivity, while published versus NFC quantifies normalization of the corpus.
- Vocabulary size, tokenizer training data, and segmentation design differ between Gemma and N-ATLaS. Their contributions cannot be isolated here. Embedding costs and model quality are not measured.
- Effect sizes and confidence intervals are the primary results. Existing Wilcoxon tests remain supporting tabular evidence.
- Original baseline and previous raw-reference mark-removal results are retained. This report supplies the NFC-reference refinement.

## Supporting paired statistics (2026-10-02)

Two-sided approximate Wilcoxon with zsplit; Holm correction across all 34 summary rows. Counts compare each condition against NFC. Numerical zero p-values indicate floating-point underflow.

| language | tokenizer | condition | fewer_sentences | equal_sentences | more_sentences | wilcoxon_p_holm |
| --- | --- | --- | --- | --- | --- | --- |
| Hausa | gemma4 | NFD | 0 | 1994 | 15 | 1.0 |
| Hausa | gemma4 | hooked_letters_replaced | 1072 | 937 | 0 | 2.741347988930824e-207 |
| Hausa | gemma4 | published | 0 | 2009 | 0 | 1.0 |
| Hausa | natlas_llama | NFD | 0 | 1995 | 14 | 1.0 |
| Hausa | natlas_llama | hooked_letters_replaced | 1143 | 866 | 0 | 9.286346795912488e-223 |
| Hausa | natlas_llama | published | 0 | 2009 | 0 | 1.0 |
| Igbo | gemma4 | NFD | 0 | 222 | 1787 | 0.0 |
| Igbo | gemma4 | all_Mn_removed | 1794 | 215 | 0 | 0.0 |
| Igbo | gemma4 | published | 0 | 1959 | 50 | 0.2066151933256463 |
| Igbo | gemma4 | tone_and_underdot_removed | 1794 | 215 | 0 | 0.0 |
| Igbo | gemma4 | tone_only_removed | 135 | 1871 | 3 | 3.2407877137997905e-07 |
| Igbo | gemma4 | underdot_and_U0329_removed | 1793 | 216 | 0 | 0.0 |
| Igbo | gemma4 | underdot_only_removed | 1793 | 216 | 0 | 0.0 |
| Igbo | natlas_llama | NFD | 0 | 235 | 1774 | 0.0 |
| Igbo | natlas_llama | all_Mn_removed | 1797 | 212 | 0 | 0.0 |
| Igbo | natlas_llama | published | 2 | 1982 | 25 | 1.0 |
| Igbo | natlas_llama | tone_and_underdot_removed | 1797 | 212 | 0 | 0.0 |
| Igbo | natlas_llama | tone_only_removed | 132 | 1877 | 0 | 3.2407877137997905e-07 |
| Igbo | natlas_llama | underdot_and_U0329_removed | 1796 | 213 | 0 | 0.0 |
| Igbo | natlas_llama | underdot_only_removed | 1796 | 213 | 0 | 0.0 |
| Yoruba | gemma4 | NFD | 0 | 307 | 1702 | 0.0 |
| Yoruba | gemma4 | all_Mn_removed | 1702 | 306 | 1 | 0.0 |
| Yoruba | gemma4 | published | 57 | 1771 | 181 | 2.931819648448222e-06 |
| Yoruba | gemma4 | tone_and_underdot_removed | 1702 | 306 | 1 | 0.0 |
| Yoruba | gemma4 | tone_only_removed | 1655 | 354 | 0 | 5.53536532432498e-309 |
| Yoruba | gemma4 | underdot_and_U0329_removed | 1684 | 324 | 1 | 0.0 |
| Yoruba | gemma4 | underdot_only_removed | 1684 | 324 | 1 | 0.0 |
| Yoruba | natlas_llama | NFD | 2 | 313 | 1694 | 0.0 |
| Yoruba | natlas_llama | all_Mn_removed | 1705 | 304 | 0 | 0.0 |
| Yoruba | natlas_llama | published | 107 | 1772 | 130 | 1.0 |
| Yoruba | natlas_llama | tone_and_underdot_removed | 1704 | 305 | 0 | 0.0 |
| Yoruba | natlas_llama | tone_only_removed | 1656 | 353 | 0 | 4.80979243648243e-309 |
| Yoruba | natlas_llama | underdot_and_U0329_removed | 1690 | 319 | 0 | 0.0 |
| Yoruba | natlas_llama | underdot_only_removed | 1690 | 319 | 0 | 0.0 |

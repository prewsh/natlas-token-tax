# Controlled diacritics experiment

The derived condition removes all Unicode nonspacing combining marks after NFD decomposition, then restores NFC. Original corpus text remains unchanged.

| tokenizer | language | sentences_text_changed | original_total_tokens | stripped_total_tokens | relative_token_reduction | reduction_ci95_low | reduction_ci95_high | sentences_stripping_reduced_tokens | sentences_equal_tokens | sentences_stripping_increased_tokens | wilcoxon_p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| natlas_llama | Igbo | 1810 | 125755 | 107448 | 0.1456 | 0.1423 | 0.1489 | 1797 | 212 | 0 | <1e-300 |
| natlas_llama | Yoruba | 1705 | 143881 | 89883 | 0.3753 | 0.3696 | 0.3809 | 1705 | 304 | 0 | <1e-300 |
| gemma4 | Igbo | 1810 | 113472 | 98171 | 0.1348 | 0.1317 | 0.1378 | 1794 | 215 | 0 | <1e-300 |
| gemma4 | Yoruba | 1705 | 127295 | 83825 | 0.3415 | 0.3359 | 0.3470 | 1702 | 306 | 1 | <1e-300 |

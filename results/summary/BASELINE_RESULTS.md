# FLORES+ baseline tokenization results

These are corpus-level descriptive results. Tokens were counted 
with `add_special_tokens=False`. Fertility is total tokens divided 
by total whitespace-delimited words. Confidence intervals use 
10,000 paired sentence-set bootstrap replicates.

| tokenizer | language | corpus_tokens_per_word | fertility_ci95_low | fertility_ci95_high | relative_tax_vs_english | share_words_1_token | share_words_4plus_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| natlas | English | 1.236 | 1.229 | 1.243 | 1.000 | 0.829 | 0.011 |
| natlas | Hausa | 2.164 | 2.153 | 2.175 | 1.751 | 0.340 | 0.107 |
| natlas | Igbo | 2.599 | 2.584 | 2.615 | 2.103 | 0.239 | 0.196 |
| natlas | Yoruba | 2.904 | 2.873 | 2.934 | 2.350 | 0.254 | 0.284 |
| llama3 | English | 1.236 | 1.229 | 1.243 | 1.000 | 0.829 | 0.011 |
| llama3 | Hausa | 2.164 | 2.153 | 2.175 | 1.751 | 0.340 | 0.107 |
| llama3 | Igbo | 2.599 | 2.584 | 2.615 | 2.103 | 0.239 | 0.196 |
| llama3 | Yoruba | 2.904 | 2.873 | 2.933 | 2.350 | 0.254 | 0.284 |
| gemma4 | English | 1.237 | 1.229 | 1.244 | 1.000 | 0.842 | 0.015 |
| gemma4 | Hausa | 1.876 | 1.867 | 1.885 | 1.517 | 0.441 | 0.056 |
| gemma4 | Igbo | 2.345 | 2.331 | 2.360 | 1.897 | 0.350 | 0.184 |
| gemma4 | Yoruba | 2.569 | 2.543 | 2.595 | 2.077 | 0.326 | 0.221 |

The relative tax is each language's corpus fertility divided by 
English fertility for the same tokenizer. It represents relative 
tokens per whitespace-delimited word, not monetary cost or model quality.

# Standalone NFC word examples

Pinned tokenizers; add_special_tokens=False; no leading/trailing spaces. Characters are NFC Unicode code points. These illustrative counts differ from sentence-context word alignment. English words are length comparisons, not translations.

Short-word frequencies are from FLORES+ release 4.6, dev plus devtest (997 + 1,012 = 2,009 sentences per language), using the recorded lexical-word regex, NFC surface normalization and casefold aggregation: Hausa da = 3,795; Igbo na = 2,552; Yoruba ní = 1,286. These are word occurrence counts, not sentence counts; the news and tweet corpora are not included.

Decoded pieces retain incomplete UTF-8 bytes as \xNN escapes. Each listed piece is one token; combine bytes before decoding to recover the full word.

| Word | Language | Characters | N-ATLaS | Gemma 4 | N-ATLaS decoded pieces |
|---|---|---:|---:|---:|---|
| da | Hausa | 2 | 1 | 1 | `["da"]` |
| ƙasa | Hausa | 4 | 3 | 2 | `["\\xc6", "\\x99", "asa"]` |
| ɗaya | Hausa | 4 | 3 | 2 | `["\\xc9", "\\x97", "aya"]` |
| muhimmanci | Hausa | 10 | 5 | 4 | `["m", "uh", "imm", "anc", "i"]` |
| na | Igbo | 2 | 1 | 1 | `["na"]` |
| ndị | Igbo | 3 | 2 | 2 | `["nd", "ị"]` |
| ahụ | Igbo | 3 | 2 | 2 | `["ah", "ụ"]` |
| gburugburu | Igbo | 10 | 5 | 4 | `["gb", "ur", "ug", "bur", "u"]` |
| ní | Yoruba | 2 | 1 | 1 | `["ní"]` |
| àwọn | Yoruba | 4 | 3 | 3 | `["à", "w", "ọn"]` |
| wọ́n | Yoruba | 4 | 4 | 3 | `["w", "ọ", "́", "n"]` |
| lọ́wọ́lọ́wọ́ | Yoruba | 12 | 12 | 12 | `["l", "ọ", "́", "w", "ọ", "́", "l", "ọ", "́", "w", "ọ", "́"]` |
| in | English | 2 | 1 | 1 | `["in"]` |
| home | English | 4 | 1 | 1 | `["home"]` |
| school | English | 6 | 1 | 1 | `["school"]` |
| information | English | 11 | 1 | 1 | `["information"]` |

# N-ATLaS tokenizer audit

Research artifacts for **Adapted Weights, Inherited Tokenizer: Measuring the Token Cost of Hausa, Igbo and Yoruba in N-ATLaS**, a case study of N-ATLaS by Precious Ngwube.

Paper: [PDF](paper/Precious_Ngwube_N-ATLaS_token_cost.pdf)

The PDF reports results produced by the code at commit 0a7fda9, which the paper cites in Appendix A. Later commits change documentation only.

The primary metric is the **token-total premium**: total language tokens / total English tokens on the 2,009 aligned NFC-normalized FLORES+ sentences per language. Results are in [results/token_total_premiums/](results/token_total_premiums/).

The secondary metric is the **fertility premium**: tokens per whitespace unit in a language relative to tokens per whitespace unit in English. NFC results are in [results/refinements/](results/refinements/).

The two premiums differ because languages use different numbers of whitespace-separated words for the same content: fertility premium = token-total premium x (English words / language words). Normalization does not explain the gap between them. On NFC text, the paper reports token-total premiums of 2.021 (Hausa), 2.374 (Igbo) and 2.689 (Yoruba), and fertility premiums of 1.751, 2.103 and 2.326.

Separately, the baseline tables in RESEARCH_LOG.md and results/summary/BASELINE_RESULTS.md were computed on the published text before NFC normalization, and give a Yoruba fertility premium of 2.350. The paper normalizes to NFC (576 Yoruba and 69 Igbo sentences were not already NFC) and reports 2.326. Use the paper's values.

The completed Llama 3.1 tokenizer identity comparisons were committed in `0a7fda9`: [base report](results/tokenizer_identity_llama31.json) and [Instruct report](results/tokenizer_identity_llama31_instruct.json). They show the same token-to-ID mapping and lexical pipeline as N-ATLaS, with identical IDs on all 8,036 FLORES+ texts. The special-token maps differ, and N-ATLaS's chat template matches Llama 3.1 Instruct.

See [RESEARCH_UPDATE.md](RESEARCH_UPDATE.md) for current findings and [RESEARCH_LOG.md](RESEARCH_LOG.md) for historical experiments and the evidence index.

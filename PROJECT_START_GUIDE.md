# N-ATLaS Tokenizer Tax: Project Start Guide

This guide turns the project notes into a practical, staged research workflow. It is a starting protocol: we will record exact model and dataset versions before collecting results, and we will let the data determine the conclusions.

The dated record of decisions, runs, observations, and pending work is maintained in `RESEARCH_LOG.md`.

## The project in one paragraph

We will inspect the tokenizer distributed with N-ATLaS and compare it with the tokenizer from its Llama 3 base. Then we will measure how many tokens both tokenizers use for English, Hausa, Igbo, and Yoruba text. Gemma 4 is a secondary comparison that helps show how another tokenizer handles the same text. The first study measures text representation and token counts; it does not measure which model understands or translates a language better.

### Main questions

1. Is the N-ATLaS tokenizer identical or practically equivalent to the Llama 3 tokenizer?
2. How do token counts and word fragmentation vary across English, Hausa, Igbo, and Yoruba?
3. How does Gemma 4 tokenize the same material?
4. As an optional extension, how does preserving or removing language-specific diacritics affect tokenization?

We will use “tokenizer tax” as shorthand for a relative difference in tokenization cost. Unless we later measure provider billing or inference speed, it means **more tokens for the text under study**, not a proven increase in price, latency, or lower language quality.

## Stage 1 — Get access and prepare the laptop

### 1.1 Hugging Face access — start here

Use a Hugging Face account you control. In this order:

1. Open [N-ATLaS](https://huggingface.co/NCAIR1/N-ATLaS), sign in, and follow the repository's request or access-agreement steps.
2. Open [Llama 3 8B](https://huggingface.co/meta-llama/Meta-Llama-3-8B), sign in, and complete its access steps.
3. Open [Gemma 4 12B](https://huggingface.co/google/gemma-4-12B) and complete any access or terms steps shown there.
4. Keep a note of each request date and status. A gated tokenizer cannot be downloaded until that account has access.

Do not put a Hugging Face access token in a script, notebook, screenshot, or Git commit. We will authenticate through the Hugging Face CLI after the local environment is ready.

### 1.2 Check the local tools

The intended setup is a laptop, Python 3.11 or later, VS Code, Git, and a Python virtual environment. We need tokenizer files and text, not the full 8B or 12B model weights, so the initial experiment does not require a GPU.

Open the project folder in VS Code and its integrated terminal. Check:

```bash
python3 --version
git --version
```

Create and activate an isolated environment from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install the initial research libraries:

```bash
python -m pip install transformers tokenizers datasets huggingface_hub pandas numpy scipy matplotlib
```

After the environment works, record the installed package versions in the repository. If one tokenizer needs an additional dependency, add it deliberately and record why.

### 1.3 Authenticate and load one tokenizer

In the activated terminal, sign in:

```bash
hf auth login
```

Use a read token from your Hugging Face account. The CLI stores authentication outside the project files.

Create `src/inspect_tokenizer.py` and start with the Llama 3 tokenizer, provided access has been granted:

```python
from transformers import AutoTokenizer

model_id = "meta-llama/Meta-Llama-3-8B"
text = "The children went to school today."

tokenizer = AutoTokenizer.from_pretrained(model_id)
token_ids = tokenizer.encode(text, add_special_tokens=False)
tokens = tokenizer.convert_ids_to_tokens(token_ids)

print("Text:", text)
print("Tokens:", tokens)
print("Token IDs:", token_ids)
print("Token count:", len(token_ids))
```

Run it with:

```bash
python src/inspect_tokenizer.py
```

**Stage 1 is complete** when the script loads a tokenizer and prints the example sentence, its token pieces, token IDs, and count. Save the output as a setup record, not as a research result.

## Stage 2 — Verify tokenizer identity

Before comparing language efficiency, answer the narrower question: did N-ATLaS retain the Llama 3 tokenizer?

For both repositories, record the exact repository revision used and compare:

- tokenizer implementation and configuration;
- vocabulary entries and their token IDs;
- special tokens and their IDs;
- relevant tokenizer-file hashes;
- outputs on a fixed set of test strings, including English and correctly written Hausa, Igbo, and Yoruba examples.

Equal vocabulary sizes alone do not establish identity. Likewise, matching outputs on a few sentences is useful evidence but does not prove that every tokenizer setting or vocabulary entry is identical. The comparison script should report what was checked and any differences it finds.

If the tokenizers are identical, N-ATLaS and Llama 3 will have the same token counts for the same text under the same settings. That is a tokenizer result; it does not show that the two models have the same language capability.

## Stage 3 — Run the controlled language comparison

### Choose and pin the corpus

The project notes refer to both FLORES-200 and FLORES+. Before analysis, choose the specific maintained release that provides aligned English (`eng_Latn`), Hausa (`hau_Latn`), Igbo (`ibo_Latn`), and Yoruba (`yor_Latn`) text. Record the dataset name, configuration, split, revision, license, and download method in `data/README.md`.

Use the same sentence IDs across languages wherever the corpus provides parallel examples. Do not mix dataset releases or splits within one result table. Keep corpus text out of public Git history unless its terms permit redistribution; scripts and instructions for obtaining it can still be included.

### Measure the same text with each tokenizer

For each sentence and tokenizer, save at least:

```text
dataset, split, sentence_id, language, model_id, model_revision,
text, word_count, character_count, token_count
```

Count tokens without adding model-specific special tokens. State the word-count rule in the methods. A simple initial rule is whitespace-delimited words, applied consistently, but this is an imperfect proxy for linguistic words across languages. Report character-based measures and sentence-level distributions alongside tokens per word so the conclusion does not depend on one denominator.

Core measures:

- **Fertility:** tokens divided by the chosen word count.
- **Relative tokenization cost:** a language's fertility divided by English fertility for the same tokenizer.
- **Fragmentation:** the share of words represented by 1, 2, 3, or 4+ token pieces, using a documented word-to-token alignment method.
- **Characters per token:** a complementary measure that does not use whitespace word counts.

For parallel sentences, preserve sentence IDs and compare paired observations. Predefine whether summaries use sentence-level ratios or corpus-level totals; report the other as a secondary summary if useful. Later, use paired bootstrap confidence intervals or another justified paired method. Do not choose statistics after seeing which one produces the preferred result.

### Keep the model comparison in perspective

N-ATLaS versus Llama 3 is the key comparison because it tests the inherited-tokenizer question. Gemma 4 is a useful independent comparison, but it differs in more than vocabulary size. A Gemma result cannot by itself prove that vocabulary size caused an efficiency difference.

Gemma's reported vocabulary has 262,144 entries versus 128,256 for N-ATLaS/Llama 3. Vocabulary capacity, training data, and segmentation design vary together in this comparison; their contributions cannot be isolated. Larger vocabularies imply larger embedding tables at fixed embedding width, but actual embedding memory, latency, and model quality are not measured here. Report token reductions and confidence intervals as the primary results, retaining Wilcoxon tests as supporting tables.

For the focused orthography refinement, run `MPLCONFIGDIR=.cache/matplotlib python src/orthography_experiments.py`. It uses cached pinned tokenizers, an NFC reference, separate tone and underdot removal, NFC/NFD comparisons, Hausa hooked-letter substitutions, mark inventories, additivity, and a decoded vocabulary audit. The current consolidated findings are in `RESEARCH_UPDATE.md`.

## Stage 4 — Extensions after the baseline is reproducible

Only after the baseline scripts and outputs are stable, consider:

1. A separate, documented diacritics experiment for Yoruba and Igbo. Keep original text unchanged and create a clearly labeled transformed copy.
2. A second Nigerian-language corpus, with its source, collection procedure, consent or usage basis, cleaning rules, and license documented.
3. Word-level examples that explain which forms are split and how often.

Keep these as distinct experiments. Do not silently combine altered orthography or a new corpus with the controlled baseline.

## Suggested repository layout

```text
natlas-token-tax/
├── PROJECT_START_GUIDE.md
├── README.md
├── requirements.txt
├── data/
│   └── README.md          # sources and retrieval instructions; no restricted data
├── src/
│   ├── inspect_tokenizer.py
│   ├── compare_tokenizers.py
│   └── measure_corpus.py
├── experiments/
│   └── README.md          # protocol and run settings
└── results/
    ├── README.md          # generated outputs and provenance
    └── figures/
```

Keep raw data, credentials, and large downloaded tokenizer caches out of Git. Commit code, documentation, environment specifications, and only those derived outputs that the data license allows us to share.

## Milestones and order of work

| Milestone | Evidence that it is done |
|---|---|
| 1. Hugging Face access | Access status recorded for each of the three repositories |
| 2. Local setup | Python environment activates and required libraries import |
| 3. First tokenizer | Example sentence prints tokens, IDs, and token count |
| 4. Identity check | Versioned N-ATLaS/Llama comparison reports vocab, IDs, settings, and file-hash results |
| 5. Corpus protocol | Dataset release, language IDs, split, word rule, and token settings are recorded |
| 6. Baseline results | Re-runnable script produces row-level results and language/tokenizer summaries |
| 7. Extensions | Any diacritics or natural-corpus result is produced by a separate documented run |

The immediate task is **Milestone 1: request N-ATLaS access first**. Once that is submitted, we can check the Llama 3 and Gemma 4 access states while preparing the local setup. We will not interpret any tokenizer output as a finding until the exact tokenizer revision and measurement settings are recorded.

## Interpretation limits to keep in view

- More tokens indicate a longer tokenized representation for this text and tokenizer configuration; they do not directly prove lower model quality or a specific dollar cost.
- Parallel translations express comparable content, but translation choices and word boundaries still differ across languages.
- Whitespace counts are not equally natural word counts in every language. State the rule and use complementary measures.
- A benchmark corpus may not represent everyday Nigerian writing. A second corpus can test generality, but it needs its own documented protocol.
- Tokenizer comparison and model-performance evaluation are separate studies. This project begins with the former.

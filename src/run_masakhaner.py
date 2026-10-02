"""Prepare and analyze the official MasakhaNER 2.0 news corpus.

Run with --download once; subsequent analysis uses local, hashed inputs.
"""
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

import run_corpus_experiment as corpus
import paired_comparison as paired

RAW = Path('data/raw/masakhaner2')
INPUT = Path('data/processed/masakhaner2.csv')
OUT = Path('results/masakhaner2')
LANGUAGES = {'hau': 'Hausa', 'ibo': 'Igbo', 'yor': 'Yoruba'}
PROVENANCE = Path('data/masakhaner2_metadata.json')
HF_REVISION = '60512e89e68841b6b5ed1be59caf97b169f0d27a'


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={'User-Agent': 'natlas-token-tax-research'})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def prepare(download: bool) -> None:
    if download:
        if PROVENANCE.exists():
            revision = json.loads(PROVENANCE.read_text())['source_revision']
        else:
            revision = json.loads(fetch('https://api.github.com/repos/masakhane-io/masakhane-ner/commits/main'))['sha']
        RAW.mkdir(parents=True, exist_ok=True)
        for language in LANGUAGES:
            for split in ('train', 'dev', 'test'):
                path = RAW / f'{language}_{split}.txt'
                url = f'https://raw.githubusercontent.com/masakhane-io/masakhane-ner/{revision}/MasakhaNER2.0/data/{language}/{split}.txt'
                path.write_bytes(fetch(url))
                print(f'Downloaded {path}', flush=True)
        (RAW / 'revision.txt').write_text(revision)
    revision = (RAW / 'revision.txt').read_text().strip()
    rows = []
    counts = Counter()
    duplicates = Counter()
    hashes = {}
    for language, name in LANGUAGES.items():
        seen = set()
        for split in ('train', 'dev', 'test'):
            path = RAW / f'{language}_{split}.txt'
            hashes[str(path)] = corpus.sha256_file(path)
            sequences = []
            tokens = []
            for line in path.read_text(encoding='utf-8').splitlines() + ['']:
                if not line.strip():
                    if tokens:
                        sequences.append(tokens)
                        tokens = []
                else:
                    pieces = line.split()
                    if len(pieces) != 2 or pieces[1] not in {'O','B-PER','I-PER','B-ORG','I-ORG','B-LOC','I-LOC','B-DATE','I-DATE'}:
                        raise ValueError(f'Unexpected CoNLL record in {path}: {line!r}')
                    tokens.append(pieces[0])
            counts[f'{language}:{split}'] = len(sequences)
            for index, tokens in enumerate(sequences):
                text = ' '.join(tokens)
                if text in seen:
                    duplicates[language] += 1
                    continue
                seen.add(text)
                rows.append({'dataset':'MasakhaNER2.0','dataset_release':'2.0',
                             'dataset_revision':revision,'split':split,'sentence_id':index,
                             'language_code':language,'language':name,'text':text})
    INPUT.parent.mkdir(parents=True, exist_ok=True)
    with INPUT.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    audit = []
    for language, name in LANGUAGES.items():
        texts = [row['text'] for row in rows if row['language_code'] == language]
        audit.append({'language':name,'sentences':len(texts),
                      'whitespace_units_including_punctuation':sum(len(t.split()) for t in texts),
                      'lexical_units_containing_letters':sum(any(c.isalpha() for c in w) for t in texts for w in t.split()),
                      'sentences_with_combining_marks_after_NFD':sum(any(unicodedata.category(c)=='Mn' for c in unicodedata.normalize('NFD', t)) for t in texts),
                      'exact_duplicate_sentences_removed':duplicates[language]})
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit).to_csv(OUT / 'corpus_audit.csv', index=False)
    metadata = {'prepared_at_utc':datetime.now(timezone.utc).isoformat(),
                'huggingface_repository':'masakhane/masakhaner2','huggingface_loader_revision':HF_REVISION,
                'source_repository':'https://github.com/masakhane-io/masakhane-ner','source_revision':revision,
                'license_working_basis':'CC BY-NC 4.0 per original repository README; HF AFL-3.0 header conflicts',
                'source_hashes':hashes,'source_sentence_counts':dict(counts),
                'reconstruction':'Join published CoNLL tokens with one ASCII space; punctuation retains separate spacing; no spelling/diacritics changes',
                'deduplication':'Exact reconstructed-text duplicates within each language across splits; retain first',
                'input_sha256':corpus.sha256_file(INPUT),'audit':audit}
    PROVENANCE.write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
    print(pd.DataFrame(audit).to_string(index=False), flush=True)


def analyze(summarize_only: bool = False) -> None:
    corpus.INPUT_PATH = INPUT
    corpus.OUTPUT_PATH = Path('results/raw/masakhaner2_metrics.csv')
    corpus.METADATA_PATH = OUT / 'tokenization_metadata.json'
    if not summarize_only:
        corpus.main()
    meta = json.loads(corpus.METADATA_PATH.read_text())
    meta['experiment'] = 'MasakhaNER 2.0 reconstructed news-text replication'
    meta['row_count_by_tokenizer_and_language'] = {k:v for k,v in meta['row_count_by_tokenizer_and_language'].items() if v}
    corpus.METADATA_PATH.write_text(json.dumps(meta, indent=2)+'\n')
    paired.INPUT_PATH = corpus.OUTPUT_PATH
    paired.OUTPUT_PATH = OUT / 'paired_comparison.csv'
    paired.MARKDOWN_PATH = OUT / 'PAIRED_RESULTS.md'
    paired.METADATA_PATH = OUT / 'paired_metadata.json'
    paired.LANGUAGE_ORDER = list(LANGUAGES)
    paired.main()
    report = paired.MARKDOWN_PATH.read_text().replace('four language comparisons','three language comparisons')
    paired.MARKDOWN_PATH.write_text(report)
    pmeta = json.loads(paired.METADATA_PATH.read_text())
    pmeta['test']['multiple_comparison_adjustment'] = 'Holm, three languages'
    pmeta['output_markdown_sha256'] = corpus.sha256_file(paired.MARKDOWN_PATH)
    pmeta['limitation'] = 'Sentence bootstrap assumes independence; source document identifiers unavailable, so within-article dependence is not modeled.'
    paired.METADATA_PATH.write_text(json.dumps(pmeta, indent=2)+'\n')
    data = pd.read_csv(corpus.OUTPUT_PATH)
    summary = []
    for (language, tokenizer), group in data.groupby(['language','tokenizer']):
        words, tokens = group.word_count.sum(), group.token_count.sum()
        summary.append({'language':language,'tokenizer':tokenizer,'sentences':len(group),
                        'tokens_per_whitespace_unit':tokens/words,
                        'non_whitespace_characters_per_token':group.non_whitespace_character_count.sum()/tokens,
                        'one_token_unit_share':group.words_1_token.sum()/words,
                        'four_plus_token_unit_share':group.words_4plus_tokens.sum()/words})
    pd.DataFrame(summary).to_csv(OUT / 'summary.csv', index=False)
    figures()
    lines = ['# MasakhaNER 2.0 news replication', '',
             'Published CoNLL tokens are joined with one space. Exact duplicate sentences are removed within each language across all splits. No model training is performed; all splits provide descriptive text evidence.', '',
             'The whitespace denominator includes separately spaced punctuation. Interpret fertility as tokens per published spacing unit, not a directly matched FLORES+ word denominator. Characters per token provides an additional view.', '',
             '## Corpus audit', '', paired.dataframe_to_markdown(pd.read_csv(OUT / 'corpus_audit.csv')), '',
             '## Tokenization summary', '', paired.dataframe_to_markdown(pd.DataFrame(summary).round(4)), '',
             '## Direct paired comparison', '', paired.MARKDOWN_PATH.read_text(), '',
             f'N-ATLaS/Llama token-ID mismatch count: {meta["natlas_llama_token_id_mismatch_count"]}.', '',
             '## Limits', '',
             '- News-domain evidence does not establish general everyday-language behavior.',
             '- The languages are not translations of matching content; cross-language differences may reflect topic and source composition.',
             '- Source spacing and earlier preprocessing may affect token counts; original website text is not reconstructed.',
             '- Sentence confidence intervals do not account for dependence within source articles because document identifiers are unavailable.',
             '- No English subset is included; an English-relative natural-corpus tax is not estimated.',
             '- Working license: CC BY-NC 4.0 per original repository README; the conflicting Hugging Face AFL-3.0 label is recorded. Raw and processed text are excluded from Git.', '']
    (OUT / 'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    manifest = {'run_at_utc':datetime.now(timezone.utc).isoformat(),
                'outputs':{str(path):corpus.sha256_file(path) for path in OUT.iterdir() if path.is_file() and path.name != 'output_manifest.json'}}
    (OUT / 'output_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


def figures() -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    natural = pd.read_csv(OUT / 'paired_comparison.csv')
    flores = pd.read_csv('results/summary/natlas_gemma_paired_comparison.csv')
    fig, ax = plt.subplots(figsize=(9,5))
    x = np.arange(3)
    for shift, frame, label, color in [(-.18,flores,'FLORES+','#294c60'),(.18,natural,'MasakhaNER 2.0 news','#d96e39')]:
        frame = frame.set_index('language_code').loc[list(LANGUAGES)]
        values = frame.gemma_relative_token_reduction.to_numpy()*100
        error = np.vstack([values-frame.relative_reduction_ci95_low.to_numpy()*100,frame.relative_reduction_ci95_high.to_numpy()*100-values])
        ax.bar(x+shift,values,.36,label=label,color=color,yerr=error,capsize=4)
    ax.set_xticks(x,list(LANGUAGES.values()))
    ax.set_ylabel('Gemma token reduction versus N-ATLaS (%)')
    ax.set_title('Tokenizer savings across translation and news corpora')
    ax.legend(frameon=False)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout()
    for suffix in ('png','svg'):
        fig.savefig(OUT / f'cross_corpus_comparison.{suffix}',dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--summarize-only', action='store_true', help='Reuse existing tokenizer measurements')
    args = parser.parse_args()
    prepare(args.download)
    analyze(args.summarize_only)

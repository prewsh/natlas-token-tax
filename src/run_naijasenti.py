"""Pinned NaijaSenti social-media replication and platform-feature sensitivity."""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import regex
from transformers import AutoTokenizer

import run_corpus_experiment as corpus
import paired_comparison as paired
import run_masakhaner as news

RAW = Path('data/raw/naijasenti')
INPUT = Path('data/processed/naijasenti.csv')
OUT = Path('results/naijasenti')
PROVENANCE = Path('data/naijasenti_metadata.json')
HF_REVISION = 'a3d0415a828178edf3466246f49cfcd83b946ab3'
URL = re.compile(r'https?://\S+', re.IGNORECASE)
MENTION = re.compile(r'(?<!\w)@\w+')


def has_marks(text: str) -> bool:
    return bool(regex.search(r'\p{L}\p{M}+', unicodedata.normalize('NFD', text)))


def prepare(download: bool) -> list[dict]:
    if download:
        revision = (json.loads(PROVENANCE.read_text())['source_revision'] if PROVENANCE.exists()
                    else json.loads(news.fetch('https://api.github.com/repos/hausanlp/NaijaSenti/commits/main'))['sha'])
        RAW.mkdir(parents=True, exist_ok=True)
        for language in news.LANGUAGES:
            for split in ('train','dev','test'):
                path = RAW / f'{language}_{split}.tsv'
                path.write_bytes(news.fetch(f'https://raw.githubusercontent.com/hausanlp/NaijaSenti/{revision}/data/annotated_tweets/{language}/{split}.tsv'))
                print(f'Downloaded {path}', flush=True)
        (RAW / 'revision.txt').write_text(revision)
    revision = (RAW / 'revision.txt').read_text().strip()
    rows, audits, hashes, counts = [], [], {}, {}
    for language, name in news.LANGUAGES.items():
        seen, duplicate_count, empty_count = set(), 0, 0
        for split in ('train','dev','test'):
            path = RAW / f'{language}_{split}.tsv'
            hashes[str(path)] = corpus.sha256_file(path)
            frame = pd.read_csv(path, sep='\t', keep_default_na=False)
            counts[f'{language}:{split}'] = len(frame)
            for index, row in frame.iterrows():
                text = row['tweet']
                if not isinstance(text, str) or not text.strip():
                    empty_count += 1
                    continue
                if text in seen:
                    duplicate_count += 1
                    continue
                seen.add(text)
                rows.append({'dataset':'NaijaSenti','dataset_release':'1.0.0',
                             'dataset_revision':revision,'split':split,'sentence_id':index,
                             'language_code':language,'language':name,'text':text})
        texts = [r['text'] for r in rows if r['language_code']==language]
        audits.append({'language':name,'unique_tweets':len(texts),
                       'whitespace_units':sum(len(t.split()) for t in texts),
                       'exact_duplicates_removed':duplicate_count,'empty_rows_removed':empty_count,
                       'tweets_with_mentions':sum(bool(MENTION.search(t)) for t in texts),
                       'tweets_with_urls':sum(bool(URL.search(t)) for t in texts),
                       'tweets_with_diacritics':sum(has_marks(t) for t in texts),
                       'tweets_with_hashtags':sum(bool(re.search(r'#\w+', t)) for t in texts)})
    INPUT.parent.mkdir(parents=True, exist_ok=True)
    with INPUT.open('w',encoding='utf-8',newline='') as handle:
        writer = csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audits).to_csv(OUT / 'corpus_audit.csv',index=False)
    metadata = {'prepared_at_utc':datetime.now(timezone.utc).isoformat(),
                'huggingface_repository':'HausaNLP/NaijaSenti-Twitter','huggingface_loader_revision':HF_REVISION,
                'source_repository':'https://github.com/hausanlp/NaijaSenti','source_revision':revision,
                'license':'CC BY-NC-SA 4.0 per original HF dataset card',
                'citation':'Muhammad et al. (2022), NaijaSenti, https://aclanthology.org/2022.lrec-1.63/',
                'source_hashes':hashes,'source_counts':counts,'audit':audits,
                'preparation':'Published tweet strings unchanged; remove empty rows and exact duplicates within each language across splits',
                'diacritics_indicator':'Unicode letter followed by combining marks after NFD; emoji variation selectors excluded; hooked letters not counted',
                'input_sha256':corpus.sha256_file(INPUT)}
    PROVENANCE.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    print(pd.DataFrame(audits).to_string(index=False),flush=True)
    return rows


def sensitivity(rows: list[dict]) -> None:
    loaded = {name:AutoTokenizer.from_pretrained(**{'pretrained_model_name_or_path':spec['model_id'],'revision':spec['revision']},local_files_only=True)
              for name,spec in corpus.TOKENIZERS.items() if name in ('natlas','gemma4')}
    baseline = pd.read_csv('results/raw/naijasenti_metrics.csv')
    tokens = baseline.pivot(index=['language_code','split','sentence_id'],columns='tokenizer',values='token_count')
    records = []
    for index,row in enumerate(rows):
        key = (row['language_code'],row['split'],int(row['sentence_id']))
        text = row['text']
        cleaned = MENTION.sub('',URL.sub('',text))
        cleaned = ' '.join(cleaned.split())
        counts = {name:len(tok.encode(cleaned,add_special_tokens=False)) for name,tok in loaded.items()} if cleaned else {'natlas':0,'gemma4':0}
        records.append({'language':row['language'],'split':row['split'],'sentence_id':row['sentence_id'],
                        'has_diacritics':has_marks(text),'cleaned_nonempty':bool(cleaned),
                        'published_natlas_tokens':int(tokens.loc[key,'natlas']),
                        'published_gemma4_tokens':int(tokens.loc[key,'gemma4']),
                        'cleaned_natlas_tokens':counts['natlas'],'cleaned_gemma4_tokens':counts['gemma4']})
        if (index+1)%10000==0:
            print(f'Sensitivity: {index+1}/{len(rows)} tweets',flush=True)
    frame = pd.DataFrame(records)
    frame.to_csv('results/raw/naijasenti_sensitivity.csv',index=False)
    summary=[]
    for language,group in frame.groupby('language'):
        for condition,subset,ncol,gcol in [
            ('published',group,'published_natlas_tokens','published_gemma4_tokens'),
            ('mentions_urls_removed',group[group.cleaned_nonempty],'cleaned_natlas_tokens','cleaned_gemma4_tokens'),
            ('published_with_diacritics',group[group.has_diacritics],'published_natlas_tokens','published_gemma4_tokens'),
            ('published_without_diacritics',group[~group.has_diacritics],'published_natlas_tokens','published_gemma4_tokens')]:
            if len(subset):
                n,g = int(subset[ncol].sum()),int(subset[gcol].sum())
                summary.append({'language':language,'condition':condition,'tweets':len(subset),
                                'natlas_total_tokens':n,'gemma4_total_tokens':g,'gemma_relative_reduction':1-g/n})
    pd.DataFrame(summary).to_csv(OUT / 'sensitivity_summary.csv',index=False)


def figure() -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,5))
    x=np.arange(3)
    for shift,path,label,color in [(-.25,'results/summary/natlas_gemma_paired_comparison.csv','FLORES+','#294c60'),
                                    (0,'results/masakhaner2/paired_comparison.csv','News','#d96e39'),
                                    (.25,str(OUT / 'paired_comparison.csv'),'Tweets','#39866b')]:
        frame=pd.read_csv(path).set_index('language_code').loc[list(news.LANGUAGES)]
        values=frame.gemma_relative_token_reduction.to_numpy()*100
        error=np.vstack([values-frame.relative_reduction_ci95_low.to_numpy()*100,frame.relative_reduction_ci95_high.to_numpy()*100-values])
        ax.bar(x+shift,values,.25,color=color,label=label,yerr=error,capsize=3)
    ax.set_xticks(x,list(news.LANGUAGES.values()))
    ax.set_ylabel('Gemma token reduction versus N-ATLaS (%)')
    ax.set_title('Tokenizer savings across three text settings')
    ax.legend(frameon=False)
    ax.spines[['top','right']].set_visible(False)
    ax.axhline(0,color='gray',linewidth=.8)
    fig.tight_layout()
    for ext in ('png','svg'):
        fig.savefig(OUT / f'three_corpus_comparison.{ext}',dpi=200)
    plt.close(fig)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--download',action='store_true')
    parser.add_argument('--summarize-only',action='store_true')
    args=parser.parse_args()
    rows=prepare(args.download)
    news.INPUT,news.OUT = INPUT,OUT
    # Override corpus destinations independently of the news wrapper.
    corpus.INPUT_PATH=INPUT
    corpus.OUTPUT_PATH=Path('results/raw/naijasenti_metrics.csv')
    corpus.METADATA_PATH=OUT / 'tokenization_metadata.json'
    if not args.summarize_only:
        corpus.main()
    meta=json.loads(corpus.METADATA_PATH.read_text())
    if meta['input_sha256'] != corpus.sha256_file(INPUT):
        raise RuntimeError('Existing tokenizer measurements do not match the prepared corpus.')
    meta['experiment']='NaijaSenti published social-media tokenizer replication'
    meta['row_count_by_tokenizer_and_language']={k:v for k,v in meta['row_count_by_tokenizer_and_language'].items() if v}
    corpus.METADATA_PATH.write_text(json.dumps(meta,indent=2)+'\n')
    paired.INPUT_PATH=corpus.OUTPUT_PATH
    paired.OUTPUT_PATH=OUT / 'paired_comparison.csv'
    paired.MARKDOWN_PATH=OUT / 'PAIRED_RESULTS.md'
    paired.METADATA_PATH=OUT / 'paired_metadata.json'
    paired.LANGUAGE_ORDER=list(news.LANGUAGES)
    paired.main()
    paired.MARKDOWN_PATH.write_text(paired.MARKDOWN_PATH.read_text().replace('four language comparisons','three language comparisons').replace('sentence-set','tweet-set'))
    pmeta=json.loads(paired.METADATA_PATH.read_text())
    pmeta['test']['multiple_comparison_adjustment']='Holm, three languages'
    pmeta['bootstrap']['resampling_unit']='tweet within language; independence assumed, user/thread identifiers unavailable'
    pmeta['output_markdown_sha256']=corpus.sha256_file(paired.MARKDOWN_PATH)
    paired.METADATA_PATH.write_text(json.dumps(pmeta,indent=2)+'\n')
    data=pd.read_csv(corpus.OUTPUT_PATH)
    summary=[]
    for (language,tokenizer),group in data.groupby(['language','tokenizer']):
        words,tokens=group.word_count.sum(),group.token_count.sum()
        summary.append({'language':language,'tokenizer':tokenizer,'tweets':len(group),
                        'tokens_per_whitespace_unit':tokens/words,
                        'non_whitespace_characters_per_token':group.non_whitespace_character_count.sum()/tokens,
                        'one_token_unit_share':group.words_1_token.sum()/words,
                        'four_plus_token_unit_share':group.words_4plus_tokens.sum()/words})
    pd.DataFrame(summary).to_csv(OUT / 'summary.csv',index=False)
    sensitivity(rows)
    figure()
    report=['# NaijaSenti social-media replication','',
            'Published text is preserved. All splits are used descriptively; exact duplicate tweets within each language and empty rows are removed. Sentiment labels are not used to infer language purity.','',
            '## Corpus audit','',paired.dataframe_to_markdown(pd.read_csv(OUT / 'corpus_audit.csv')),'',
            '## Primary paired results','',paired.MARKDOWN_PATH.read_text(),'',
            '## Fragmentation and fertility','',paired.dataframe_to_markdown(pd.DataFrame(summary).round(4)),'',
            '## Descriptive sensitivity checks','',paired.dataframe_to_markdown(pd.read_csv(OUT / 'sensitivity_summary.csv').round(4)),'',
            'Mention/URL removal changes the text and is a secondary condition. Diacritics groups are observational, not paired mark-removal experiments. The indicator detects Unicode combining marks attached to letters after NFD, excluding emoji variation selectors. It includes accented borrowed words and does not identify language purity or tone alone.','',
            f'N-ATLaS/Llama token-ID mismatches: {meta["natlas_llama_token_id_mismatch_count"]}.','',
            '## Interpretation limits','',
            '- Released tweets have prior anonymization/preprocessing. They are not untouched platform data.',
            '- Code mixing, abbreviations, emojis, and subject matter can change token counts; no causal effect of code mixing is estimated.',
            '- No matched English baseline exists; this estimates tokenizer differences rather than English-relative tax.',
            '- No author/thread IDs are available for cluster resampling; tweet bootstrap assumes independence.',
            '- The sample was selected for sentiment annotation and does not represent all Nigerian online writing.',
            '- Original-release license is CC BY-NC-SA 4.0; data is excluded from Git. Cite Muhammad et al. (2022), https://aclanthology.org/2022.lrec-1.63/.','']
    (OUT / 'RESULTS.md').write_text('\n'.join(report),encoding='utf-8')
    manifest={'run_at_utc':datetime.now(timezone.utc).isoformat(),'outputs':{str(p):corpus.sha256_file(p) for p in OUT.iterdir() if p.is_file() and p.name!='output_manifest.json'},
              'sensitivity_raw_sha256':corpus.sha256_file(Path('results/raw/naijasenti_sensitivity.csv'))}
    (OUT / 'output_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    main()

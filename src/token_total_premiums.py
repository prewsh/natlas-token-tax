"""Token-total premiums on aligned NFC FLORES+ text, separate from fertility."""
import json
import unicodedata as ud
from pathlib import Path

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

import diacritics_experiment as orth
import paired_comparison as paired
import run_corpus_experiment as corpus

OUT=Path('results/token_total_premiums')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=pd.read_csv('data/processed/flores_plus_four_languages.csv',keep_default_na=False)
    rows=[]
    for name,spec in orth.TOKENIZERS.items():
        tok=AutoTokenizer.from_pretrained(spec['model_id'],revision=spec['revision'],local_files_only=True)
        for row in source.itertuples(index=False):
            text=ud.normalize('NFC',row.text)
            metrics,_=corpus.measure_text(tok,text)
            rows.append({'language':row.language,'split':row.split,'sentence_id':row.sentence_id,'tokenizer':name,**metrics})
    data=pd.DataFrame(rows)
    rawpath=Path('results/raw/flores_NFC_metrics.csv')
    data.to_csv(rawpath,index=False)
    transforms=pd.read_csv('results/raw/orthography_metrics.csv')
    rng=np.random.default_rng(20260930)
    premiums,effects,descriptive=[],[],[]
    for name in orth.TOKENIZERS:
        tokenwide=data[data.tokenizer==name].pivot(index=['split','sentence_id'],columns='language',values='token_count').sort_index()
        assert len(tokenwide)==2009 and not tokenwide.isna().any().any()
        english=tokenwide.English.to_numpy(dtype=float)
        for language in ['English','Hausa','Igbo','Yoruba']:
            arr=tokenwide[language].to_numpy(dtype=float)
            if language!='English':
                wide=transforms[(transforms.tokenizer==name)&(transforms.language==language)].pivot(index=['split','sentence_id'],columns='condition',values='tokens').sort_index()
                assert wide.index.equals(tokenwide.index) and np.array_equal(arr,wide.NFC.to_numpy())
                conditions={'Hausa':['hooked_letters_replaced'],'Igbo':['all_Mn_removed'],
                            'Yoruba':['all_Mn_removed','tone_only_removed','underdot_only_removed']}[language]
            else:
                conditions=[]
            before_samples=[]
            after_samples={c:[] for c in conditions}
            shares={c:[] for c in conditions}
            for start in range(0,10000,100):
                idx=rng.integers(0,len(arr),size=(100,len(arr)))
                eng=english[idx].sum(axis=1)
                before=arr[idx].sum(axis=1)/eng
                before_samples.extend(before)
                for c in conditions:
                    after=wide[c].to_numpy(dtype=float)[idx].sum(axis=1)/eng
                    after_samples[c].extend(after)
                    shares[c].extend((before-after)/(before-1))
            low,high=np.percentile(before_samples,[2.5,97.5])
            premium=arr.sum()/english.sum()
            premiums.append({'language':language,'tokenizer':name,'NFC_total_tokens':int(arr.sum()),'English_total_tokens':int(english.sum()),
                             'token_total_premium':premium,'ci95_low':low,'ci95_high':high})
            for c in conditions:
                after=wide[c].sum()/english.sum()
                low,high=np.percentile(shares[c],[2.5,97.5])
                alow,ahigh=np.percentile(after_samples[c],[2.5,97.5])
                effects.append({'language':language,'tokenizer':name,'condition':c,'premium_before':premium,'premium_after':after,
                                'premium_after_ci95_low':alow,'premium_after_ci95_high':ahigh,
                                'share_excess_removed':(premium-after)/(premium-1),'ci95_low':low,'ci95_high':high})
            group=data[(data.language==language)&(data.tokenizer==name)]
            words=group.word_count.sum()
            descriptive.append({'language':language,'tokenizer':name,'characters_per_token_including_whitespace':group.character_count.sum()/arr.sum(),
                                'characters_per_token_excluding_whitespace':group.non_whitespace_character_count.sum()/arr.sum(),
                                **{f'share_{k}':group[col].sum()/words for k,col in [('1','words_1_token'),('2','words_2_tokens'),('3','words_3_tokens'),('4plus','words_4plus_tokens')]}})
    for filename,records in [('premiums.csv',premiums),('excess_removed.csv',effects),('NFC_descriptive.csv',descriptive)]:
        pd.DataFrame(records).to_csv(OUT/filename,index=False)
    english=source[source.language=='English']
    normalization={'English_sentences':len(english),'English_not_NFC':sum(t!=ud.normalize('NFC',t) for t in english.text)}
    meta={'seed':20260930,'replicates':10000,'batch_size':100,'method':'Percentile 95% bootstrap; common aligned split/sentence_id indices for target and English and every condition within each comparison',
          'definition':'total target-language tokens / total English tokens; no word-count denominator',
          'normalization':'NFC','English_normalization_audit':normalization,'tokenizers':orth.TOKENIZERS,
          'source_sha256':orth.sha256_file(Path('data/processed/flores_plus_four_languages.csv')),
          'raw_sha256':orth.sha256_file(rawpath)}
    report=['# Token-total premium audit — 2026-10-02','',
            'Token-total premium = total language tokens / total English tokens on the same 2,009 aligned sentences. This differs from the earlier fertility ratio. Both use NFC here. Bootstrap: 10,000 aligned paired resamples, seed 20260930, percentile 95% intervals.','',
            '## NFC totals and premiums','',paired.dataframe_to_markdown(pd.DataFrame(premiums).round(6)),'',
            '## Share of excess removed','',paired.dataframe_to_markdown(pd.DataFrame(effects).round(6)),'',
            'Share = (premium before - premium after)/(premium before - 1). These are effects of specified lossy transformations, not causal shares of orthographic burden.','',
            '## NFC characters and fragmentation','',paired.dataframe_to_markdown(pd.DataFrame(descriptive).round(6)),'',
            'Character counts are Python Unicode code-point counts, not bytes or grapheme clusters. Both whitespace-inclusive and whitespace-exclusive measures are given. Fragmentation uses tokenizer offsets overlapping whitespace units.','',
            f'English normalization audit: {normalization}','']
    (OUT/'RESULTS.md').write_text('\n'.join(report))
    meta['outputs']={str(p):orth.sha256_file(p) for p in OUT.iterdir() if p.is_file() and p.name!='metadata.json'}
    (OUT/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(pd.DataFrame(premiums).round(6).to_string(index=False))
    print(pd.DataFrame(effects).round(6).to_string(index=False))
    print(normalization)


if __name__=='__main__':
    main()

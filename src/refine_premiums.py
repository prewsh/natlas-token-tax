"""Aligned NFC premiums, orthography contrasts, and Unicode word-boundary sensitivity."""
import json
import unicodedata as ud
from pathlib import Path

import numpy as np
import pandas as pd
import regex
from transformers import AutoTokenizer

import diacritics_experiment as orth
import paired_comparison as paired

OUT=Path('results/refinements')
SEED=20260930
REPLICATES=10000


def unicode_words(text):
    # regex WORD implements default Unicode boundaries; count only segments
    # containing a Unicode letter or number, excluding symbols/punctuation.
    return sum(bool(regex.search(r'[\p{L}\p{N}]',s)) for s in regex.split(r'\b',text,flags=regex.WORD|regex.VERSION1))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=pd.read_csv('data/processed/flores_plus_four_languages.csv',keep_default_na=False)
    raw=pd.read_csv('results/raw/orthography_metrics.csv')
    keys=['split','sentence_id']
    source=source.set_index(keys+['language'])
    counts={}
    for name,spec in orth.TOKENIZERS.items():
        tok=AutoTokenizer.from_pretrained(spec['model_id'],revision=spec['revision'],local_files_only=True)
        english=source.xs('English',level='language').sort_index()
        counts[name]=np.array([len(tok.encode(ud.normalize('NFC',t),add_special_tokens=False)) for t in english.text],dtype=float)
    english_words=np.array([len(t.split()) for t in english.text],dtype=float)
    english_unicode=np.array([unicode_words(ud.normalize('NFC',t)) for t in english.text],dtype=float)
    estimates, comparisons, sensitivity=[],[],[]
    rng=np.random.default_rng(SEED)
    for language in ['Hausa','Igbo','Yoruba']:
        texts=source.xs(language,level='language').sort_index()
        assert texts.index.equals(english.index)
        words=np.array([len(t.split()) for t in texts.text],dtype=float)
        uwords=np.array([unicode_words(ud.normalize('NFC',t)) for t in texts.text],dtype=float)
        wide={name:raw[(raw.language==language)&(raw.tokenizer==name)].pivot(index=keys,columns='condition',values='tokens').sort_index() for name in orth.TOKENIZERS}
        assert all(frame.index.equals(english.index) for frame in wide.values())
        conditions=['hooked_letters_replaced'] if language=='Hausa' else ['tone_only_removed','underdot_only_removed','tone_and_underdot_removed','all_Mn_removed']
        samples={(name,c):[] for name in wide for c in conditions}
        advantage={c:[] for c in ['NFC','NFD']}
        word_ci={(name,denom):[] for name in wide for denom in ['whitespace','unicode']}
        for start in range(0,REPLICATES,100):
            idx=rng.integers(0,len(words),size=(min(100,REPLICATES-start),len(words)))
            w=words[idx].sum(axis=1)
            uw=uwords[idx].sum(axis=1)
            ew=english_words[idx].sum(axis=1)
            eu=english_unicode[idx].sum(axis=1)
            for name,frame in wide.items():
                eng=counts[name][idx].sum(axis=1)
                nfc=frame.NFC.to_numpy(dtype=float)[idx].sum(axis=1)
                before=(nfc/w)/(eng/ew)
                word_ci[name,'whitespace'].extend(before)
                word_ci[name,'unicode'].extend((nfc/uw)/(eng/eu))
                for c in conditions:
                    after=(frame[c].to_numpy(dtype=float)[idx].sum(axis=1)/w)/(eng/ew)
                    share=(before-after)/(before-1)
                    samples[name,c].extend(zip(before,after,share))
            for c in advantage:
                n=wide['natlas_llama'][c].to_numpy(dtype=float)[idx].sum(axis=1)
                g=wide['gemma4'][c].to_numpy(dtype=float)[idx].sum(axis=1)
                advantage[c].extend(1-g/n)
        for name,frame in wide.items():
            eng_fert=counts[name].sum()/english_words.sum()
            before=(frame.NFC.sum()/words.sum())/eng_fert
            for c in conditions:
                after=(frame[c].sum()/words.sum())/eng_fert
                values=np.array(samples[name,c])
                record={'language':language,'tokenizer':name,'condition':c,'premium_NFC':before,'premium_after':after,
                        'share_excess_removed':(before-after)/(before-1)}
                for i,label in enumerate(['premium_NFC','premium_after','share_excess_removed']):
                    low,high=np.percentile(values[:,i],[2.5,97.5])
                    record[label+'_ci95_low']=low
                    record[label+'_ci95_high']=high
                estimates.append(record)
            for denominator,lw,ew in [('whitespace',words,english_words),('unicode',uwords,english_unicode)]:
                premium=(frame.NFC.sum()/lw.sum())/(counts[name].sum()/ew.sum())
                low,high=np.percentile(word_ci[name,denominator],[2.5,97.5])
                sensitivity.append({'language':language,'tokenizer':name,'denominator':denominator,'language_word_units':int(lw.sum()),
                                    'english_word_units':int(ew.sum()),'premium_vs_English':premium,'ci95_low':low,'ci95_high':high})
        for c in advantage:
            reduction=1-wide['gemma4'][c].sum()/wide['natlas_llama'][c].sum()
            low,high=np.percentile(advantage[c],[2.5,97.5])
            comparisons.append({'language':language,'normalization':c,'gemma_relative_reduction':reduction,'ci95_low':low,'ci95_high':high})
    pd.DataFrame(estimates).to_csv(OUT/'premium_perturbations.csv',index=False)
    pd.DataFrame(comparisons).to_csv(OUT/'normalization_comparison.csv',index=False)
    pd.DataFrame(sensitivity).to_csv(OUT/'word_boundary_sensitivity.csv',index=False)
    lines=['# Refined premium and normalization results','',
           'Premium = language corpus fertility / English corpus fertility for the same tokenizer. Both reference texts are NFC. Share of excess removed = (premium before - premium after)/(premium before - 1). All 2,009 aligned sentence IDs are resampled jointly across languages, tokenizers, and conditions; 10,000 replicates, seed 20260930.','',
           '## Paired orthography premiums','',paired.dataframe_to_markdown(pd.DataFrame(estimates).round(5)),'',
           '## Gemma advantage by Unicode representation','',paired.dataframe_to_markdown(pd.DataFrame(comparisons).round(5)),'',
           '## Word-boundary sensitivity','',paired.dataframe_to_markdown(pd.DataFrame(sensitivity).round(5)),'',
           'The Unicode sensitivity uses regex WORD default Unicode word boundaries, counting only boundary-delimited segments containing letters or numbers. It is an operational UAX-29-based sensitivity, not language-specific morphological segmentation or a conformance certification. Punctuation and emoji-only segments are excluded; tokenizer numerator is unchanged.','',
           '## Interpretation limits','',
           'Perturbation shares measure excess eliminated by a specific lossy text transformation. They do not establish causal attribution of all excess to orthography. Separate tone and underdot shares cannot be summed because their effects interact. Remaining Hausa excess is unexplained by this hooked-letter experiment; vocabulary coverage is a hypothesis.',
           'NFC/NFD compare canonically equivalent forms. Results can support NFC normalization for this tokenizer pipeline, subject to application-specific input requirements. A change in advantage magnitude is not a ranking reversal.',
           'All text metrics include finite-corpus and word-denominator limitations. Statistical intervals describe paired sentence resampling, not a universal population guarantee.','']
    (OUT/'REFINED_RESULTS.md').write_text('\n'.join(lines))
    meta={'seed':SEED,'replicates':REPLICATES,'reference':'NFC in both language and English',
          'unicode_library_version':regex.__version__,'inputs':{p:orth.sha256_file(Path(p)) for p in ['data/processed/flores_plus_four_languages.csv','results/raw/orthography_metrics.csv']},
          'outputs':{str(p):orth.sha256_file(p) for p in OUT.iterdir() if p.is_file() and p.name!='metadata.json'}}
    (OUT/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(pd.DataFrame(estimates)[['language','tokenizer','condition','premium_NFC','premium_after','share_excess_removed']].round(5).to_string(index=False))
    print(pd.DataFrame(comparisons).round(5).to_string(index=False))


if __name__=='__main__':
    main()

"""Focused FLORES+ orthography perturbations, with an NFC reference."""
from __future__ import annotations

import json
import unicodedata as ud
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

import diacritics_experiment as previous
import paired_comparison as paired

INPUT = Path('data/processed/flores_plus_four_languages.csv')
OUT = Path('results/orthography')
TONES = {'\u0300','\u0301','\u0304'}
DOTS = {'\u0323'}
HOOKS = str.maketrans({'ƙ':'k','ɗ':'d','ɓ':'b','ƴ':'y','Ƙ':'K','Ɗ':'D','Ɓ':'B','Ƴ':'Y'})


def remove(text: str, marks: set[str] | None) -> str:
    return ud.normalize('NFC', ''.join(c for c in ud.normalize('NFD',text)
                                      if not (ud.category(c)=='Mn' if marks is None else c in marks)))


def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    source = pd.read_csv(INPUT,keep_default_na=False)
    source = source[source.language_code.isin(['hau','ibo','yor'])]
    tokenizers = {name:AutoTokenizer.from_pretrained(spec['model_id'],revision=spec['revision'],local_files_only=True)
                  for name,spec in previous.TOKENIZERS.items()}
    rows, inventory, normalization = [], [], []
    for language,group in source.groupby('language'):
        marks = Counter(c for text in group.text for c in ud.normalize('NFD',text) if ud.category(c).startswith('M'))
        inventory.extend({'language':language,'codepoint':f'U+{ord(c):04X}','name':ud.name(c,'UNKNOWN'),'occurrences':marks[c],
                          'covered_by_tone_or_underdot':c in TONES|DOTS} for c in sorted(set(marks)|{'\u0329'}))
        normalization.append({'language':language,'sentences':len(group),'not_already_NFC':sum(t!=ud.normalize('NFC',t) for t in group.text)})
    for index,row in enumerate(source.itertuples(index=False),1):
        nfc = ud.normalize('NFC',row.text)
        variants = {'published':row.text,'NFC':nfc,'NFD':ud.normalize('NFD',nfc)}
        if row.language_code in ('ibo','yor'):
            variants.update({'tone_only_removed':remove(nfc,TONES),'underdot_only_removed':remove(nfc,DOTS),
                             'tone_and_underdot_removed':remove(nfc,TONES|DOTS),
                             'all_Mn_removed':remove(nfc,None),'underdot_and_U0329_removed':remove(nfc,DOTS|{'\u0329'})})
        else:
            variants['hooked_letters_replaced'] = nfc.translate(HOOKS)
        for name,tok in tokenizers.items():
            for condition,text in variants.items():
                rows.append({'split':row.split,'sentence_id':row.sentence_id,'language':row.language,'tokenizer':name,
                             'condition':condition,'changed_from_NFC':text!=nfc,'tokens':len(tok.encode(text,add_special_tokens=False))})
        if index%1000==0:
            print(f'{index}/{len(source)} sentences',flush=True)
    raw = pd.DataFrame(rows)
    raw_path=Path('results/raw/orthography_metrics.csv')
    raw.to_csv(raw_path,index=False)
    summaries, additions = [], []
    rng=np.random.default_rng(20261001)
    for (language,name),group in raw.groupby(['language','tokenizer']):
        wide=group.pivot(index=['split','sentence_id'],columns='condition',values='tokens')
        reference=wide.NFC.to_numpy(dtype=float)
        for condition in wide.columns:
            if condition=='NFC':
                continue
            transformed=wide[condition].to_numpy(dtype=float)
            low,high=previous.bootstrap_reduction(reference,transformed,rng)
            summaries.append({'language':language,'tokenizer':name,'condition':condition,'sentences':len(wide),
                              'NFC_total_tokens':int(reference.sum()),'condition_total_tokens':int(transformed.sum()),
                              'token_reduction':int((reference-transformed).sum()),
                              'relative_reduction':1-transformed.sum()/reference.sum(),'ci95_low':low,'ci95_high':high,
                              'changed_sentences':int(group.loc[group.condition==condition,'changed_from_NFC'].sum())})
        if 'all_Mn_removed' in wide:
            tone=wide.NFC-wide.tone_only_removed
            dot=wide.NFC-wide.underdot_only_removed
            union=wide.NFC-wide['all_Mn_removed']
            tone_dot=wide.NFC-wide['tone_and_underdot_removed']
            # Positive interaction means combined removal saves more than the separate savings sum.
            additions.append({'language':language,'tokenizer':name,'tone_savings':int(tone.sum()),
                              'underdot_savings':int(dot.sum()),'all_Mn_savings':int(union.sum()),
                              'tone_and_underdot_savings':int(tone_dot.sum()),
                              'interaction_savings':int((tone_dot-tone-dot).sum()),
                              'additional_other_mark_savings':int((union-tone_dot).sum()),
                              'all_minus_sum_savings':int((union-tone-dot).sum()),
                              'sentences_nonadditive':int(((union-tone-dot)!=0).sum())})
    from orthography_statistics import add_statistics
    summary=add_statistics(pd.DataFrame(summaries), raw)
    summary.to_csv(OUT/'orthography_summary.csv',index=False)
    pd.DataFrame(inventory).to_csv(OUT/'mark_inventory.csv',index=False)
    pd.DataFrame(normalization).to_csv(OUT/'normalization_audit.csv',index=False)
    pd.DataFrame(additions).to_csv(OUT/'additivity.csv',index=False)
    audit=[]
    for name,tok in tokenizers.items():
        vocab=tok.get_vocab()
        # Decode through each backend's byte/SentencePiece decoder, not raw token notation.
        decoded=[tok.backend_tokenizer.decoder.decode([piece]) for piece in vocab]
        for letter in 'ẹọṣịụƙɗɓƴ':
            audit.append({'tokenizer':name,'letter':letter,'vocabulary_entries':len(vocab),
                          'entries_containing_complete_decoded_letter':sum(letter in t for t in decoded),
                          'entries_with_replacement_character':sum('\ufffd' in t for t in decoded)})
    pd.DataFrame(audit).to_csv(OUT/'vocabulary_audit.csv',index=False)
    lines=['# Focused orthography experiments','',
           'All effects use NFC as the reference. Positive reduction means the condition uses fewer tokens. Intervals use 10,000 paired sentence bootstrap replicates, seed 20261001.','',
           '## Normalization audit','',paired.dataframe_to_markdown(pd.DataFrame(normalization)),'',
           '## Effects relative to NFC','',paired.dataframe_to_markdown(summary.round(5)),'',
           '## Mark inventory','',paired.dataframe_to_markdown(pd.DataFrame(inventory)),'',
           '## Additivity','',paired.dataframe_to_markdown(pd.DataFrame(additions)),'',
           'Positive interaction_savings means combined tone-and-underdot removal saves more tokens than the two separate removals summed. Additional other-mark savings compare all Mn removal with that union. All-minus-sum mixes interaction with other-mark effects.','',
           '## Vocabulary audit','',paired.dataframe_to_markdown(pd.DataFrame(audit)),'',
           'Entries are individually decoded through the tokenizer backend. Counts include complete lowercase letters only; incomplete UTF-8 pieces may decode to replacement characters and are excluded from letter counts. This diagnostic does not measure usable segmentation coverage or control vocabulary size.','',
           '## Limits and interpretation','',
           '- Tone set: U+0300, U+0301, U+0304. Underdot-only set: U+0323. U+0329 is counted separately and removed only in the explicitly labeled additional condition.',
           '- Removing the underdot maps ṣ to s as well as changing vowels. Hook substitution maps ƙ/ɗ/ɓ/ƴ to k/d/b/y, including uppercase forms. These perturbations remove meaningful distinctions; they are not spelling recommendations.',
           '- NFC and NFD are canonically equivalent representations; their difference isolates input encoding sensitivity, while published versus NFC quantifies normalization of the corpus.',
           '- Vocabulary size, tokenizer training data, and segmentation design differ between Gemma and N-ATLaS. Their contributions cannot be isolated here. Embedding costs and model quality are not measured.',
           '- Effect sizes and confidence intervals are the primary results. Existing Wilcoxon tests remain supporting tabular evidence.',
           '- Original baseline and previous raw-reference mark-removal results are retained. This report supplies the NFC-reference refinement.','']
    (OUT/'ORTHOGRAPHY_RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
    figure(summary)
    metadata={'run_at_utc':datetime.now(timezone.utc).isoformat(),'input':str(INPUT),'input_sha256':previous.sha256_file(INPUT),
              'tokenizers':previous.TOKENIZERS,'reference':'NFC','bootstrap_replicates':10000,'seed':20261001,
              'transformations':{'tones':['U+0300','U+0301','U+0304'],'underdot':['U+0323'],'additional_under_mark':['U+0329'],
                                 'hooks':'ƙɗɓƴ and uppercase to kdby'},
              'raw_sha256':previous.sha256_file(raw_path),
              'output_hashes':{str(p):previous.sha256_file(p) for p in OUT.iterdir() if p.is_file() and p.name!='metadata.json'}}
    (OUT/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    print(summary.round(5).to_string(index=False))


def figure(summary: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,5),sharey=True)
    conditions=['tone_only_removed','underdot_only_removed','all_Mn_removed']
    for ax,language in zip(axes,['Igbo','Yoruba']):
        x=np.arange(3)
        for shift,name,label,color in [(-.18,'natlas_llama','N-ATLaS / Llama 3','#294c60'),(.18,'gemma4','Gemma 4','#d96e39')]:
            frame=summary[(summary.language==language)&(summary.tokenizer==name)].set_index('condition').loc[conditions]
            values=frame.relative_reduction.to_numpy()*100
            error=np.vstack([values-frame.ci95_low.to_numpy()*100,frame.ci95_high.to_numpy()*100-values])
            ax.bar(x+shift,values,.36,color=color,label=label,yerr=error,capsize=3)
        ax.set_xticks(x,['Tone marks','Underdots','All Mn marks'])
        ax.set_title(language)
        ax.spines[['top','right']].set_visible(False)
        ax.axhline(0,color='gray',linewidth=.8)
    axes[0].set_ylabel('Token reduction from NFC reference (%)')
    axes[1].legend(frameon=False)
    fig.tight_layout()
    for ext in ['png','svg']:
        fig.savefig(OUT/f'orthography_effects.{ext}',dpi=200)
    plt.close(fig)


if __name__=='__main__':
    main()

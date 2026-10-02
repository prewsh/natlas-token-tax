"""Add paired supporting statistics without rerunning tokenization."""
import json
from pathlib import Path
import pandas as pd
from scipy.stats import wilcoxon
from paired_comparison import holm_adjust
from diacritics_experiment import sha256_file


def add_statistics(summary, raw):
    rows = []
    for row in summary.itertuples(index=False):
        group = raw[(raw.language == row.language) & (raw.tokenizer == row.tokenizer)]
        wide = group.pivot(index=['split', 'sentence_id'], columns='condition', values='tokens')
        difference = wide[row.condition] - wide.NFC
        p = 1.0 if (difference == 0).all() else float(wilcoxon(
            difference, zero_method='zsplit', alternative='two-sided', method='approx').pvalue)
        rows.append({'fewer_sentences': int((difference < 0).sum()),
                     'equal_sentences': int((difference == 0).sum()),
                     'more_sentences': int((difference > 0).sum()), 'wilcoxon_p_raw': p})
    stats = pd.DataFrame(rows)
    stats['wilcoxon_p_holm'] = holm_adjust(stats.wilcoxon_p_raw.tolist())
    return pd.concat([summary.drop(columns=stats.columns, errors='ignore').reset_index(drop=True), stats], axis=1)


if __name__ == '__main__':
    path = Path('results/orthography/orthography_summary.csv')
    frame = add_statistics(pd.read_csv(path), pd.read_csv('results/raw/orthography_metrics.csv'))
    frame.to_csv(path, index=False)
    metadata_path = path.parent / 'metadata.json'
    metadata = json.loads(metadata_path.read_text())
    metadata['supporting_statistics'] = {'test': 'two-sided Wilcoxon, zsplit, approximate',
        'holm_family': 'all 34 non-NFC condition/language/tokenizer rows, including published and auxiliary conditions',
        'updated': '2026-10-02', 'source': 'saved paired token counts; no retokenization'}
    metadata['output_hashes'][str(path)] = sha256_file(path)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    requested = ['tone_only_removed', 'underdot_only_removed', 'all_Mn_removed', 'hooked_letters_replaced', 'NFD']
    print(frame[frame.condition.isin(requested)][['language','tokenizer','condition','fewer_sentences','equal_sentences','more_sentences','wilcoxon_p_holm']].to_string(index=False))

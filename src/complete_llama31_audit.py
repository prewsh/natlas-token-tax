"""Extend prepared identity reports with templates and corpus ID equality."""
import hashlib
import json
from pathlib import Path
import pandas as pd
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer

SPECS = [
    ('natlas', 'NCAIR1/N-ATLaS', 'e294476928aca9030e924ca27bb8e085e8581273'),
    ('llama31', 'meta-llama/Llama-3.1-8B', 'd04e592bb4f6aa9cfee91e2e20afa771667e1d4b'),
    ('llama31_instruct', 'meta-llama/Llama-3.1-8B-Instruct', '0e9e39f249a16976918f6564b8830bc894c89659'),
]


def main():
    source = Path('data/processed/flores_plus_four_languages.csv')
    frame = pd.read_csv(source, keep_default_na=False)
    assert len(frame) == 8036
    records = {}
    for name, repo, revision in SPECS:
        tok = AutoTokenizer.from_pretrained(repo, revision=revision, local_files_only=True)
        config = json.loads(Path(hf_hub_download(repo, 'tokenizer_config.json',
                            revision=revision, local_files_only=True)).read_text())
        records[name] = (tok, config)
    baseline, config = records['natlas']
    ids = baseline(frame.text.tolist(), add_special_tokens=False)['input_ids']
    for name, repo, revision in SPECS[1:]:
        tok, other_config = records[name]
        other_ids = tok(frame.text.tolist(), add_special_tokens=False)['input_ids']
        mismatches = [i for i, (a, b) in enumerate(zip(ids, other_ids)) if a != b]
        path = Path(f'results/tokenizer_identity_{name}.json')
        report = json.loads(path.read_text())
        report['chat_template_audit'] = {
            'identical': config.get('chat_template') == other_config.get('chat_template'),
            'natlas_template': config.get('chat_template'),
            'comparison_template': other_config.get('chat_template'),
        }
        report['flores_audit'] = {
            'input': str(source), 'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'normalization': 'published text, unchanged', 'add_special_tokens': False,
            'texts': len(frame), 'identical_ids': len(frame) - len(mismatches),
            'mismatching_ids': len(mismatches),
            'mismatch_keys': frame.iloc[mismatches][['split', 'sentence_id', 'language']].to_dict('records'),
        }
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(name, json.dumps({'hashes':report['tokenizers'],
              'flores': report['flores_audit'], 'template_identical': report['chat_template_audit']['identical']},ensure_ascii=False))


if __name__ == '__main__':
    main()

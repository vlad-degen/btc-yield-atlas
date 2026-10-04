"""Seed English translations; preserve reviewed English articles as editorial sources."""
import collections
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(refresh=False):
    created=0;retained=0
    mappings = collections.defaultdict(dict)
    for line in (ROOT / 'tools/eth/english-reports.tsv').read_text().splitlines():
        name, index, english = line.split('\t', 2)
        mappings[name][int(index)] = english
    for name, translations in mappings.items():
        source = ROOT / 'research/eth' / name
        target = ROOT / 'research/eth/en' / name
        if target.exists() and not refresh:
            retained+=1
            continue
        created+=1
        output = []; index = 0
        for line in source.read_text().splitlines():
            if re.search('[А-Яа-яЁё]', line):
                output.append(translations[index]); index += 1
            else:
                output.append(line)
        assert index == len(translations), (name, index, len(translations))
        target = ROOT / 'research/eth/en' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        text='\n'.join(output) + '\n'
        def local_link(match):
            url=match[1]
            if url.startswith(('http:','https:','#','mailto:')):return match[0]
            dest=(source.parent/url.split('#')[0]).resolve()
            candidate=target.parent/url.split('#')[0]
            if candidate.exists():return match[0]
            if dest.exists():
                fragment='#'+url.split('#',1)[1] if '#' in url else ''
                return ']('+os.path.relpath(dest,target.parent)+fragment+')'
            return match[0]
        text=re.sub(r'\]\(([^)]+)\)',local_link,text)
        target.write_text(text)
    print(f'English reports: {created} seeded; {retained} reviewed sources retained')

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--refresh-translations',action='store_true',help='Explicitly regenerate the initial translations, replacing editorial copy.')
    run(parser.parse_args().refresh_translations)

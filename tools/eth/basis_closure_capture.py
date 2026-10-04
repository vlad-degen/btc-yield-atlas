"""Capture supplemental primary Ethena disclosures without changing snapshot T."""
import hashlib, json, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT/'raw/eth/research-closure-2026-10-04/basis'
URLS = {
    'ethena_attestation_index': 'https://docs.ethena.fi/resources/custodian-attestations.md',
    'ethena_data_repository': 'https://docs.ethena.fi/resources/data-repository.md',
    'ethena_june_update': 'https://gov.ethenafoundation.com/t/ethena-s-june-2026-governance-update/808.json',
    'ethena_august_attestation': 'https://ethena.fi/blog/custodian-attestations-of-assets-backing-usde-august-3',
    'ethena_weekly_reserves': 'https://data.ht.digital/por/ethena',
}

def run():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest=[]
    for name,url in URLS.items():
        at=datetime.now(timezone.utc).isoformat()
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'ETH Yield Research public-source review'})
            with urllib.request.urlopen(req,timeout=35) as response:
                body=response.read();status=response.status;ctype=response.headers.get('Content-Type','')
            digest=hashlib.sha256(body).hexdigest()
            suffix='.json' if 'json' in ctype else '.txt' if 'text/plain' in ctype or url.endswith('.md') else '.html'
            file=RAW/f'{name}-{digest[:16]}{suffix}'
            if not file.exists():file.write_bytes(body)
            manifest.append({'id':name,'url':url,'captured_at':at,'status':status,'path':str(file.relative_to(ROOT)),'sha256':digest})
        except Exception as exc:
            manifest.append({'id':name,'url':url,'captured_at':at,'error':str(exc)})
    (RAW/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':run()

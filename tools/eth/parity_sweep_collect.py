"""Read-only discovery sweep; later discovery is never substituted for frozen T."""
import concurrent.futures,datetime,hashlib,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'raw/eth/parity-sweep-2026-10-05';RAW.mkdir(parents=True,exist_ok=True)
SOURCES={
 'yield_pools':'https://yields.llama.fi/pools',
 'protocols':'https://api.llama.fi/protocols',
 'zensats_contracts':'https://www.zensats.app/docs/contracts',
 'zensats_strategy':'https://www.zensats.app/docs/strategy',
 'lucidly_home':'https://www.lucidly.finance/',
 'lucidly_research':'https://research.lucidly.finance/',
 'upshift_registry':'https://docs.upshift.finance/contracts/addresses',
 'lido_earn':'https://docs.lido.fi/earn/',
 'yieldbasis_overview':'https://docs.yieldbasis.com/',
}
def fetch(item):
 key,url=item;rec={'key':key,'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Post-T discovery only'}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ETH-Research-Review/1.0'}),timeout=40) as r:body=r.read();rec.update(status=r.status,source_date=r.headers.get('Date'))
  h=hashlib.sha256(body).hexdigest();ext='.json' if body.lstrip().startswith((b'{',b'[')) else '.html';out=RAW/(key+'-'+h[:16]+ext)
  if not out.exists():out.write_bytes(body)
  rec.update(sha256=h,path=str(out.relative_to(ROOT)),bytes=len(body))
 except Exception as e:rec.update(error=str(e)[:200])
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(fetch,SOURCES.items()))
(ROOT/'data/eth/parity_discovery_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['key','status','bytes','error'] if k in r} for r in rows]))

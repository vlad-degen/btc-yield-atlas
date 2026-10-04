"""Read-only official registry/document capture for the strategy expansion.

Usage: python3 tools/eth/strategy_universe_expansion_capture.py seeds
or: ... one KEY URL
No RPC transaction submission, signing, or mutable application operations.
"""
import concurrent.futures,datetime,hashlib,json,pathlib,sys,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[2]
RAW=ROOT/'raw/eth/strategy-universe-expansion-2026-10-04'
RAW.mkdir(parents=True,exist_ok=True)
SEEDS={
 'auto_index':'https://docs.auto.finance/llms.txt',
 'meth_index':'https://docs.mantle.xyz/meth/llms.txt',
 'stakewise_index':'https://docs.stakewise.io/llms.txt',
 'stakewise_core':'https://api.github.com/repos/stakewise/v3-core/git/trees/main?recursive=1',
 'pendle_market_registry':'https://api-v2.pendle.finance/core/v1/1/markets?limit=100&isActive=true',
 'pendle_loop_registry':'https://api-v2.pendle.finance/core/v1/pt-looping/loop/money-markets',
 'pendle_loop_docs':'https://docs.pendle.finance/pendle-v2/AppGuide/PTLooping',
 'gmx_market_registry':'https://arbitrum-api.gmxinfra.io/markets',
 'gmx_liquidity_docs':'https://docs.gmx.io/docs/providing-liquidity/',
 'gmx_deployments':'https://raw.githubusercontent.com/gmx-io/gmx-synthetics/main/deployments/arbitrum/MarketFactory.json',
 'yb_repository':'https://api.github.com/repos/yield-basis/yb-core/git/trees/master?recursive=1',
 'yb_readme':'https://raw.githubusercontent.com/yield-basis/yb-core/master/README.md',
 'euler_earn_docs':'https://docs.euler.finance/curate/vaults/euler-earn/introduction/',
 'euler_addresses':'https://docs.euler.finance/developers/contract-addresses/',
 'yearn_registry':'https://ydaemon.yearn.fi/1/vaults/all?orderBy=featuringScore&orderDirection=desc&strategiesDetails=withDetails&strategiesCondition=inQueue',
 'yearn_v3_docs':'https://docs.yearn.fi/developers/v3/vault_management',
 'ribbon_retro':'https://gov.ribbon.finance/t/retrospective-on-rgp-2/143.json',
 'ribbon_contracts':'https://docs.ribbon.finance/developers/contract-addresses',
 'ribbon_v2':'https://www.research.ribbon.finance/blog/ribbonv2',
 'thetanuts_registry':'https://docs.thetanuts.finance/contracts-and-security/deployed-contracts.md',
 'thetanuts_faq':'https://docs.thetanuts.finance/other-information/faq.md',
 'resolv_index':'https://docs.resolv.xyz/llms.txt',
 'grayscale_ethe':'https://www.grayscale.com/crypto-products/grayscale-ethereum-staking-etf',
 'binance_wbeth':'https://www.binance.com/en/support/faq/detail/e252366155174ba6887f6b32e3798273',
 'binance_fee':'https://www.binance.com/en/support/faq/detail/eecd04618b5042c79f2a5b07f895c498',
 'spectra_registry':'https://docs.spectra.finance/docs/spectra/technical-reference/contract-addresses',
 'spectra_faq':'https://docs.spectra.finance/docs/spectra/the-basics/faq',
}
FOLLOW={
 'auto_contracts':'https://docs.auto.finance/developer-docs/contracts-overview/contract-addresses.md',
 'auto_withdraw':'https://docs.auto.finance/using-the-app/app-guide/autopools/deposit-and-withdraw.md',
 'auto_strategy':'https://docs.auto.finance/developer-docs/contracts-overview/autopool-eth-contracts-overview/autopool-contracts-and-systems/autopool-strategy.md',
 'auto_large_exits':'https://docs.auto.finance/developer-docs/integrating/large-withdrawals.md',
 'auto_vault_terms':'https://docs.auto.finance/developer-docs/contracts-overview/autopool-eth-contracts-overview/autopool-contracts-and-systems/autopools.md',
 'meth_overview':'https://docs.mantle.xyz/meth/introduction/overview.md',
 'meth_contracts':'https://docs.mantle.xyz/meth/components/smart-contracts.md',
 'cmeth_contracts':'https://docs.mantle.xyz/meth/components/smart-contracts/restaking-cmeth.md',
 'stakewise_mainnet':'https://raw.githubusercontent.com/stakewise/v3-core/main/deployments/mainnet.json',
 'stakewise_networks':'https://docs.stakewise.io/contracts/networks/',
 'yb_deployments':'https://raw.githubusercontent.com/yield-basis/yb-core/master/scripts/deployment.log',
 'yb_whitepaper_text':'https://raw.githubusercontent.com/yield-basis/yb-paper/master/leveraged-liquidity-paper.tex',
 'euler_addresses_current':'https://docs.euler.finance/build/contract-addresses',
 'euler_monad_adapter':'https://raw.githubusercontent.com/DefiLlama/yield-server/master/src/adaptors/euler-v2/index.js',
 'resolv_recovery':'https://docs.resolv.xyz/litepaper/using-resolv/resolv-recovery-portal-overview.md',
 'resolv_deprecated':'https://docs.resolv.xyz/litepaper/using-resolv/vaults/deprecated-vaults.md',
 'resolv_collateral':'https://docs.resolv.xyz/litepaper/protocol-mechanics/collateral-pool.md',
 'resolv_futures':'https://docs.resolv.xyz/litepaper/protocol-mechanics/collateral-pool/futures-positions.md',
 'resolv_contracts':'https://docs.resolv.xyz/litepaper/for-developers/smart-contracts.md',
 'resolv_fees':'https://docs.resolv.xyz/litepaper/protocol-mechanics/fees.md',
 'yearn_incident':'https://raw.githubusercontent.com/yearn/yearn-security/master/disclosures/2025-12-01.md',
 'yearn_recovery':'https://gov.yearn.fi/t/yip-90-yeth-optimistic-recovery-plan/14573.json',
 'yearn_recovery_app':'https://yeth.yearn.fi/?action=stake-unstake',
 'grayscale_10k':'https://www.sec.gov/Archives/edgar/data/1725210/000119312526071965/ethe-20251231.htm',
 'grayscale_staking_faq':'https://www.sec.gov/Archives/edgar/data/1725210/000119312525238451/staking_faqs_10.8.2025.htm',
 'grayscale_etfs':'https://etfs.grayscale.com/ethe',
 'spectra_contract_index':'https://docs.spectra.finance/llms.txt',
 'pendle_registry_100':'https://api-v2.pendle.finance/core/v1/1/markets?limit=100&skip=100',
 'pendle_registry_200':'https://api-v2.pendle.finance/core/v1/1/markets?limit=100&skip=200',
 'pendle_registry_300':'https://api-v2.pendle.finance/core/v1/1/markets?limit=100&skip=300',
 'pendle_registry_400':'https://api-v2.pendle.finance/core/v1/1/markets?limit=100&skip=400',
 'pendle_eth_loop_pairs':'https://api-v2.pendle.finance/core/v1/pt-looping/loop/pts/1/looping',
}
def capture(item):
 key,url=item;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 meta={'key':key,'url':url,'observedUTC':now,'financialSnapshotTimestamp':1790985599,'scope':'Later official discovery/document capture, not a refreshed financial snapshot.'}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'ETHMarketResearch/1.0','Accept':'application/json,text/plain,text/html;q=0.9,*/*;q=0.8'})
  with urllib.request.urlopen(req,timeout=30)as response:
   content=response.read();meta.update(status=response.status,finalURL=response.url,contentType=response.headers.get('Content-Type'),HTTPDate=response.headers.get('Date'))
  sha=hashlib.sha256(content).hexdigest();ext='.json'if content.lstrip().startswith((b'{',b'['))else'.txt';path=RAW/(key+'-'+sha[:16]+ext);path.write_bytes(content);meta.update(path=str(path.relative_to(ROOT)),sha256=sha,bytes=len(content))
 except Exception as e:meta.update(error=str(e))
 return meta
def main():
 work=list(SEEDS.items())if len(sys.argv)<2 or sys.argv[1]=='seeds'else list(FOLLOW.items())if sys.argv[1]=='follow'else[(sys.argv[2],sys.argv[3])]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:results=list(pool.map(capture,work))
 with(RAW/'capture_manifest.jsonl').open('a')as f:
  for row in results:f.write(json.dumps(row)+'\n')
 print(json.dumps([{k:r.get(k)for k in ['key','status','bytes','path','error']}for r in results],indent=2))
if __name__=='__main__':main()

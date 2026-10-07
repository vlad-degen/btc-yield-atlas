"""Build the ETH research website from captured analytical outputs. No network calls."""
import csv, html, json, re, shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'tools/eth/site'
OUT = ROOT / 'eth'
DATA = ROOT / 'data/eth'
RESEARCH = ROOT / 'research/eth'
ENGLISH = RESEARCH / 'en'

def read(name):
    return json.loads((DATA / f'{name}.json').read_text())

ARTICLES = {
 'etherfi-liquid-eth': ('dossiers', 'ether.fi Liquid ETH'),
 'fluid-lite': ('dossiers', 'Fluid Lite ETH'),
 'treehouse-teth': ('dossiers', 'Treehouse tETH'),
 'cian-rseth': ('dossiers', 'CIAN rsETH'),
 'carry-credit': ('dossiers', 'Carry credit destinations'),
 'liquid-monad': ('dossiers', 'Liquid Monad ETH'),
 'justlend-tron': ('dossiers', 'JustLend / Tron'),
 'ethena-basis': ('dossiers', 'ETH basis leg Ethena'),
 'pendle-pt': ('dossiers', 'Pendle PT'),
 'staking-restaking': ('dossiers', 'Staking and restaking'),
 'lending-lp': ('dossiers', 'Lending and LP'),
 'MARKET-STRUCTURE': ('library', 'ETH market composition and history'),
 'CARRY-CATEGORY': ('library', 'ETH carry products and capital history'),
 'CARRY-MATH': ('library', 'Dollar carry: rates, payers and calculations'),
 'CARRY-PRODUCTS': ('library', 'Carry products: live positions, control and outcomes'),
 'BORROW-HISTORY': ('library', 'Liquid ETH: archived borrowing costs'),
 'MECHANICS': ('library', 'Yield mechanics'),
 'ECONOMICS': ('library', 'Economics and stress tests'),
 'HISTORY': ('library', 'History and comparable returns'),
 'LENDING-MARKETS': ('library', 'Five WETH lending markets'),
 'EVIDENCE': ('library', 'Evidence ledger'),
 'AUDIT': ('library', 'Verification and reproduction'),
 'scope': ('library', 'Research scope'),
 'methodology': ('library', 'Capital accounting rules'),
 'README': ('library', 'Research library guide'),
 'RETURN-DRIVERS': ('library', 'Returns, capital growth and fees'),
 'PRODUCT-TERMS': ('library', 'Withdrawals, fees and control'),
 'PRODUCT-SELECTION': ('library', 'Why these five products?'),
 'BRIEFING': ('library', 'ETH yield: briefing for the team'),
 'CAPITAL-INCOME-EXIT': ('library', 'Capital, earned income and investor exits'),
 'DOLLAR-FUNDING-ATLAS': ('library', 'Dollar financing across chains'),
 'STRATEGY-UNIVERSE-EXPANSION': ('library', 'The ETH strategy and product universe'),
 'CARRY-VARIANTS-EXPANSION': ('library', 'Nested carry, manager products and funding layers'),
 'CREDIT-EXPANSION': ('library', 'Credit markets and traced borrower destinations'),
 'MARKET-COVERAGE': ('library', 'Market coverage and remaining measurement limits'),
 'CARRY-LIFECYCLES': ('library', 'Three carry lifecycles: investment income and financing cost'),
 'PRODUCT-FINANCIAL-HISTORY': ('library', 'Additional ETH products: capital, returns and exits'),
 'BORROWER-USE': ('library', 'Large dollar borrowers: identities and use of proceeds'),
 'HGETH-LOAN-BOOK': ('library', 'hgETH: loan-book accounting, history and control'),
 'CARRY-COVERAGE-AUDIT': ('library', 'Carry coverage: public-feed sweep and product decisions'),
 'PRODUCT-EVOLUTION': ('library', 'Product development, ownership and carry economics'),
 'CONCRETE-DELTA': ('library', 'Concrete Delta: whose 307k ETH it is'),
 'ROCKSOLID-NEMO-SENTORA': ('library', 'Rocksolid, NEMO and Sentora: books, loans and closing'),
 'TOP5-RISK-LIQUIDITY': ('library', 'Top five: health factors, repayment ladders and reward payers'),
 'BORROWER-IDENTITIES': ('library', 'Who borrows dollars against ETH: the largest wallets named'),
 'LIQUID-LOOP': ('library', 'Liquid ETH: the loop, week by week'),
 'TOP5-KEYS-HOLDERS-TERMS': ('library', 'Top five: keys, holders, fees and terms'),
 'REWARDS-SPLIT': ('library', 'Top five: organic yield against rewards'),
 'CLOSED-CASES': ('library', 'Closed and stressed ETH products'),
 'RESTAKING-AND-LOOPS': ('library', 'Restaking in practice and the loop regime'),
 'OUTSIDE-AND-SMALL': ('library', 'Off-chain staking, ETFs, treasuries and the small categories'),
}

# removed from the library (parity audit 7 Oct): links to them go to the article that replaces them
ALIASES = {'ECONOMIC-ANSWERS':'CARRY-CATEGORY','concrete-eth':'CONCRETE-DELTA','MARKET-RESEARCH':'MARKET-STRUCTURE','MARKET-TABLES':'MARKET-STRUCTURE',
           'RESEARCH-PLAN':'README','EXECUTION-CHECKLIST':'README','SITE-PARITY':'README','DEPENDENCIES':'AUDIT'}
READER_DROP={'assets','balance','basisDisclosures','carryAssets','coverage','credit','economics','edges','etherfi','etherfiHistory','evidence',
 'marketPanel','pendle','stress','summary','fundingAtlas','marketNetting','creditExpansion','borrowerDeep','creditDeep','managerCase'}

def link(url, source):
    if url.startswith(('https://','http://','#','mailto:')):
        return url
    target = (source.parent / url.split('#')[0]).resolve()
    if not target.exists() and source.is_relative_to(ENGLISH):
        original = RESEARCH / source.relative_to(ENGLISH)
        target = (original.parent / url.split('#')[0]).resolve()
    frag = '#' + url.split('#',1)[1] if '#' in url else ''
    if target.suffix == '.md' and target.stem in ALIASES:
        folder, _ = ARTICLES[ALIASES[target.stem]]
        return f'../{folder}/{ALIASES[target.stem]}.html' + frag
    if target.suffix == '.md' and target.stem in ARTICLES and target.is_relative_to(RESEARCH):
        folder, _ = ARTICLES[target.stem]
        return f'../{folder}/{target.stem}.html' + frag
    if 'figures/' in url:
        return '../' + url[url.index('figures/'):]
    if target.is_dir():
        # a folder (scripts, captures): point at the research branch on GitHub
        return 'https://github.com/vlad-degen/btc-yield-atlas/tree/codex/eth-research/'+str(target.relative_to(ROOT))
    if target.exists():
        # Keep linked evidence portable in both site copies and the ZIP.
        if target.parent!=DATA:
            # research files, scripts and raw captures stay in the repository: link them on GitHub, do not publish copies
            return 'https://github.com/vlad-degen/btc-yield-atlas/blob/codex/eth-research/'+str(target.relative_to(ROOT))+frag
        shutil.copyfile(target,OUT/'data'/target.name)
        return '../data/' + target.name + frag
    return url

def inline(text, source):
    # Protect code and links before styling escaped prose.
    saved = []
    def hold(value):
        saved.append(value); return f'ZZPH{len(saved)-1}ZZ'
    text = re.sub(r'`([^`]+)`', lambda m: hold('<code>'+html.escape(m[1])+'</code>'), text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: hold(f'<img src="{html.escape(link(m[2],source),quote=True)}" alt="{html.escape(m[1],quote=True)}" loading="lazy">'),text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: hold(f'<a href="{html.escape(link(m[2],source),quote=True)}"'+(' target="_blank" rel="noopener"' if m[2].startswith('http') else '')+'>'+html.escape(m[1])+'</a>'),text)
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<em>\1</em>',text)
    for i, v in enumerate(saved): text=text.replace(f'ZZPH{i}ZZ',v)
    return text

def markdown(source):
    lines=source.read_text().splitlines(); out=[]; i=0; used={}
    def cell(s): return inline(s.strip(),source)
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1; continue
        if line.startswith('```'):
            lang=line[3:]; i+=1; code=[]
            while i<len(lines) and not lines[i].startswith('```'): code.append(lines[i]);i+=1
            out.append('<pre class="codeblock"><code>'+html.escape('\n'.join(code))+'</code></pre>');i+=1;continue
        m=re.match(r'^(#{1,6})\s+(.+)',line)
        if m:
            level=min(len(m[1])+1,6); title=m[2]
            slug=re.sub(r'[^\w\- ]','',title.lower()).replace(' ','-');count=used.get(slug,0);used[slug]=count+1
            if count:slug+='-'+str(count)
            out.append(f'<h{level} id="{slug}">{inline(title,source)}</h{level}>');i+=1;continue
        if line.startswith('|') and i+1<len(lines) and re.match(r'^\s*\|[\s:|\-]+\|\s*$',lines[i+1]):
            head=line.strip('|').split('|');i+=2;rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip().strip('|').split('|'));i+=1
            out.append('<div class="tblwrap"><table><thead><tr>'+''.join('<th>'+cell(v)+'</th>' for v in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+cell(v)+'</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table></div>');continue
        if re.match(r'^([-*]|\d+\.)\s+',line):
            ordered=bool(re.match(r'^\d+\.',line)); tag='ol' if ordered else 'ul';items=[]
            while i<len(lines) and re.match(r'^\s*([-*]|\d+\.)\s+',lines[i]):
                value=re.sub(r'^\s*([-*]|\d+\.)\s+','',lines[i]);items.append('<li>'+inline(value,source)+'</li>');i+=1
            out.append(f'<{tag}>'+''.join(items)+f'</{tag}>');continue
        if line.startswith('>'):
            out.append('<blockquote>'+inline(line.lstrip('> '),source)+'</blockquote>');i+=1;continue
        if line in ['---','***']:out.append('<hr>');i+=1;continue
        para=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||```|[-*]\s|\d+\.\s|>)',lines[i].strip()):para.append(lines[i].strip());i+=1
        out.append('<p>'+inline(' '.join(para),source)+'</p>')
    return '\n'.join(out)

def build():
    from english_reports import run as translate_reports
    translate_reports()
    from reader_market_build import run as build_reader_market
    build_reader_market()
    from reader_carry_build import run as build_reader_carry
    build_reader_carry()
    from finalization_reconstruction_build import augment as augment_final_measurements
    augment_final_measurements()
    from reader_analysis_build import run as build_reader_analysis
    build_reader_analysis()
    from parity_coverage_build import run as build_carry_coverage
    build_carry_coverage()
    from report_contract_build import run as build_report_contract
    # The coverage builder regenerates its discovery decisions; update the measured cases afterwards.
    augment_final_measurements()
    from parity_depth_build import augment as augment_substantive_history
    augment_substantive_history()
    from economic_build import run as build_economic_answers
    economic_answers = build_economic_answers()
    # Hash and analyse the final product chapters, including their history.
    build_reader_analysis()
    contract = build_report_contract()
    for name,source in [('STRATEGY-UNIVERSE-EXPANSION','STRATEGY-UNIVERSE-EXPANSION'),('CARRY-VARIANTS-EXPANSION','CARRY-VARIANTS-EXPANSION'),('CREDIT-EXPANSION','CREDIT-EXPANSION-2026-10-04')]:
        text=(RESEARCH/'review'/f'{source}.md').read_text()
        # These are English editorial sources. Preserve exact units and links.
        (ENGLISH/f'{name}.md').write_text(text.replace('—',', ').replace('–','-'))
    if (RESEARCH/'review/CREDIT-EXPANSION-DEEP.md').exists():
        (ENGLISH/'CARRY-LIFECYCLES.md').write_text((RESEARCH/'review/CREDIT-EXPANSION-DEEP.md').read_text().replace('—',', ').replace('–','-'))
    for target,source in [('PRODUCT-FINANCIAL-HISTORY','STRATEGY-UNIVERSE-DEEP'),('BORROWER-USE','FUNDING-BORROWER-DEEP')]:
        if (RESEARCH/'review'/f'{source}.md').exists():
            (ENGLISH/f'{target}.md').write_text((RESEARCH/'review'/f'{source}.md').read_text().replace('—',', ').replace('–','-'))
    for folder in ['dossiers','library','data','figures']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    css='\n'.join((SRC/name).read_text() for name in ['base.css','eth.css','closure.css','expansion.css','top5.css'])
    (OUT/'site.css').write_text(css)
    histories=read('protocol_eth_history_monthly')
    panel=read('market_panel')
    observations=[{'protocol':p['id'],'name':p['name'],'category_current_hint':p['source_category'],'period':'snapshot','eth_family_reported_usd':p['current']['usd'],'positive_usd':p['current']['gross_positive_usd'],'negative_usd':p['current']['negative_usd'],'tokens_usd':p['current'].get('selected_tokens_usd',{}),'source_timestamp':p['current']['source_timestamp'],'source_age_seconds':p['current']['source_age_seconds'],'source_url':p['source_url']} for p in panel['products']]
    market_histories=[{'protocol':p['id'],'period':r['period'],'eth_family_reported_usd':r['usd'] if r['status']=='observed' else None,'tokens_units':None,'source_timestamp':r['source_timestamp'],'source_age_seconds':r['source_age_seconds'],'target_timestamp':m['target_timestamp']} for p in panel['products'] for r,m in zip(p['history'],panel['months'])]
    pools=[{k:r.get(k) for k in ['chain','project','symbol','pool','tvlUsd','apy','apyBase','apyReward','apyMean30d','poolMeta','category_hint','underlyingTokens','matched_components']} for r in read('yield_pool_candidates')]
    from finalization_editorial_build import run as build_final_editorial
    build_final_editorial()
    from parity_depth_build import editorial as write_substantive_history
    write_substantive_history()
    from economic_build import editorial as write_economic_answers
    write_economic_answers(economic_answers,read('reader_product_chapters'))
    payload={
      'summary':read('market_summary'),'chains':read('chain_screen'),'protocols':observations,
      'coverage':read('protocol_source_coverage'),'pools':pools,
      'protocolHistory':[{k:r.get(k) for k in ['protocol','period','eth_family_reported_usd','tokens_units','source_timestamp','source_age_seconds','target_timestamp']} for r in market_histories],
      'wealth':read('comparable_ETH_wealth'),'returns':read('vault_history_comparison'),
      'etherfiReturns':read('etherfi_staking_comparison'),'etherfi':read('etherfi_verified_metrics'),
      'etherfiHistory':read('etherfi_history_monthly'),'balance':read('etherfi_partial_balance_sheet'),
      'lending':read('weth_lending_markets_T')['markets'],'economics':read('loop_economics_T'),
      'stress':read('stress_scenarios'),'credit':read('carry_credit_lookthrough'),
      'carryAssets':read('carry_collateral_assets_T')['assets'],
      'pendle':read('pendle_eth_market_screen'),'edges':read('dependency_graph')['edges'],
      'evidence':read('evidence_ledger')['claims'],'assets':read('asset_registry'),
      'review':read('presentation_analysis'),
      'marketPanel':read('market_panel'),
      'marketChapter':read('market_reader_chapter'),
      'borrowersChapter':read('research_borrowers'),
      'economicsChapter':read('carry_economics_chapter'),
      'productChapters':read('reader_product_chapters'),
      'borrowRateHistory':read('carry_borrow_rate_history'),
      'carryCategory':{'products':read('reader_carry_category')['products']},
      'readerAnalysis':read('reader_analysis'),
      'reportContract':contract,
      'economicAnswers':economic_answers,
      'productEvolution':read('parity_depth_reader'),
      'finalMeasurements':{k:v for k,v in read('finalization_reconstruction').items() if k not in ['topFiveHolderReconstruction','makinaMorpho','makinaAccountingInstructions','sourceFileHashes','avantPublishedAllocation','nativeHistory']},
      'carryCoverage':read('carry_coverage_audit'),
      'reportLibrary':[{'id':stem,'title':title,'href':f'{folder}/{stem}.html'} for stem,(folder,title) in ARTICLES.items()],
      'marketNetting':read('market_netting_closure'),
      'carryAttribution':read('carry_attribution_closure'),
      'backingExit':read('backing_exit_closure'),
      'basisDisclosures':read('basis_closure_disclosures'),
      'fundingAtlas':read('funding_atlas_chapter'),
      'strategyExpansion':read('strategy_universe_expansion'),
      'carryExpansion':read('carry_variants_expansion'),
      'creditExpansion':read('credit_expansion')
    }
    # The page needs reader-facing measurements, not every RPC request or receipt.
    # Full source ledgers remain separate downloadable evidence.
    def presentation_value(value):
        if isinstance(value,list):return [presentation_value(v) for v in value]
        if isinstance(value,dict):return {k:presentation_value(v) for k,v in value.items() if k not in ['request','response','source_response','raw','holder_pages','identity_verification','block_boundary','receipts']}
        return value
    for key in ['fundingAtlas','strategyExpansion','carryExpansion','creditExpansion']:
        payload[key]=presentation_value(payload[key])
    payload['fundingAtlas'].pop('borrower_discovery',None)
    for key,name in [('netmapCheck','netmap/crosscheck'),('atlasTop5Risk','atlas_top5_risk'),('creditDeep','credit_expansion_deep'),('strategyDeep','strategy_universe_deep'),('borrowerDeep','funding_borrower_deep_chapter'),('managerCase','manager_case_chapter')]:
        if (DATA/(name+'.json')).exists():payload[key]=presentation_value(read(name))
    translations=json.loads((SRC/'english-evidence.json').read_text())
    for claim in payload['evidence']:
        claim['claim'],claim['time_scope_and_limit']=translations[claim['id']]
    packed=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    (DATA/'site_payload.json').write_text(packed)
    for filename in read('parity_depth_measurements')['sourceFiles']:
        shutil.copyfile(DATA/filename,OUT/'data'/filename)
    for name in ['evidence_ledger','market_summary','weth_lending_markets_T','etherfi_partial_balance_sheet','comparable_ETH_wealth','dependency_graph','asset_registry','product_registry','presentation_analysis','permissions_review_T','presentation_terms_sources','btc_depth_review','market_panel','carry_category_candidates','reader_carry_category','reader_product_chapters','carry_category_sources','market_pool_screen','research_market_chapter','market_reader_chapter','research_borrowers','carry_economics_chapter','product_chapters']:
        shutil.copyfile(DATA/f'{name}.json',OUT/'data'/f'{name}.json')
    def copy_chapter_evidence(value):
        if isinstance(value,dict):
            for child in value.values():copy_chapter_evidence(child)
        elif isinstance(value,list):
            for child in value:copy_chapter_evidence(child)
        elif isinstance(value,str) and value.startswith('data/eth/'):
            source=ROOT/value
            if source.is_file():shutil.copyfile(source,OUT/'data'/source.name)
    for key in ['marketChapter','economicsChapter','productChapters','borrowersChapter','borrowRateHistory','marketNetting','carryAttribution','backingExit','basisDisclosures','fundingAtlas','strategyExpansion','carryExpansion','creditExpansion']:
        copy_chapter_evidence(payload[key])
    for prefix in ['economic','market_netting_','carry_attribution_','backing_exit_','basis_closure_','funding_atlas_','strategy_universe_expansion','strategy_universe_deep','carry_variants_expansion','credit_expansion','funding_borrower_deep','manager_case_','market_completeness_','research_expansion_']:
        for source in DATA.glob(prefix+'*'):
            if source.is_file():shutil.copyfile(source,OUT/'data'/source.name)
    for name in ['carry_coverage_audit.json','carry-discovery-dispositions.csv','yb_LT_holders_T.json']:
        if (DATA/name).is_file():shutil.copyfile(DATA/name,OUT/'data'/name)
    for name in ['report_contract.json','carry-common-30d.csv','carry-status-and-capital.csv','finalization_reconstruction.json','native-staking-observations.csv','carry-flow-adjusted-ledgers.csv','parity_depth_measurements.json','parity_depth_reader.json','parity-Liquid-Cash-beneficiaries.csv','parity-Liquid-monthly-debt.csv','parity-Liquid-cohort-sensitivity.csv','parity-savETH-holders.csv','parity-ybGauge-holders.csv']:
        shutil.copyfile(DATA/name,OUT/'data'/name)
    shutil.copyfile(DATA/'carry_borrow_rate_history.json',OUT/'data/carry_borrow_rate_history.json')
    # counted-once market map (tools/eth/netmap): CSVs and notes for download
    (OUT/'data/netmap').mkdir(parents=True,exist_ok=True)
    for source in (DATA/'netmap').glob('*'):
        if source.suffix in ('.csv','.md'):shutil.copyfile(source,OUT/'data/netmap'/source.name)
    ledger=read('evidence_ledger')
    ledger['claims']=payload['evidence']
    ledger['presentation_language']='en'
    ledger['translation_note']='Descriptions translated; original semantic inputs, source paths and evidence hashes unchanged.'
    (OUT/'data/evidence_ledger.json').write_text(json.dumps(ledger,indent=2))
    for name, rows in [('pools',pools),('protocols',observations),('lending',payload['lending'])]:
        fields={'pools':['chain','project','symbol','pool','tvlUsd','apy','apyBase','apyReward','apyMean30d','category_hint'], 'protocols':['protocol','name','category_current_hint','source_timestamp','source_age_seconds','eth_family_reported_usd','source_url'], 'lending':['chain','protocol','block','pool','lender_claim_units','debt_units','reserve_cash_units','supply_APR','variable_borrow_APR','lender_claim_minus_cash_and_debt_units']}[name]
        with (OUT/'data'/f'{name}.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    for source,dest in [('market_panel_monthly.csv','market-history.csv'),('market_panel_protocols.csv','market-protocols.csv'),('market_panel_chains.csv','market-chains.csv'),('market_panel_prices.csv','market-prices.csv'),('market_pool_screen.csv','liquidity-discovery.csv')]:
        shutil.copyfile(DATA/source,OUT/'data'/dest)
    # Real files support downloads in hosted, file:// and in-app previews.
    def write_csv(name,headers,rows):
        with (OUT/'data'/name).open('w',newline='') as f:
            writer=csv.writer(f);writer.writerow(headers);writer.writerows(rows)
    chapter=payload['marketChapter']
    for cohort in ['observed','constant']:
        # only the full set; the page builds the CSV for any other mix of switches in the browser (atlas.js)
        for mask in [2**len(chapter['categories'])-1]:
            selected=[c for i,c in enumerate(chapter['categories']) if mask&(1<<i)]
            rows=[]
            for month in chapter['months']:
                values=[]
                for c in selected:
                    base=month['by_category'][c['id']]
                    row=base['constant_cohort'] if cohort=='constant' else base
                    observed=row.get('protocol_count',0) if cohort=='constant' else base['coverage']['observed']
                    values.append(row if observed else {'eth_ref':None,'usd':None})
                total_eth=sum(v['eth_ref'] or 0 for v in values) if any(v['eth_ref'] is not None for v in values) else None
                total_usd=sum(v['usd'] or 0 for v in values) if any(v['usd'] is not None for v in values) else None
                rows.append([month['period'],*[cell for v in values for cell in [v['eth_ref'],v['usd'],None if v['eth_ref'] is None or not total_eth else v['eth_ref']/total_eth,None if v['usd'] is None or not total_usd else v['usd']/total_usd]],total_eth,total_usd])
            write_csv(f'market-series-{cohort}-{mask}.csv',['month',*[f"{c['id']}_{unit}" for c in selected for unit in ['ETH_equivalent','USD','share_ETH','share_USD']],'selected_total_ETH','selected_total_USD'],rows)
    write_csv('borrowers.csv',['chain','address','collateral_assets_and_units','collateral_USD_at_capture','debt_assets_and_units','debt_USD_at_capture','who','evidence','capture_start','capture_end'],[[r['chain'],r['address'],'; '.join(f"{a['units']} {a['symbol']}" for a in r['collateral_native']),r['collateral_usd'],'; '.join(f"{a['units']} {a['symbol']}" for a in r['debt_native']),r['debt_usd'],r['who'],r['evidence'],r['capture_start'],r['capture_end']] for r in payload['borrowersChapter']['borrowers']])
    write_csv('Liquid-ETH-monthly-history.csv',['month','book_NAV_ETH','Liquid_ETH_return_fraction','stETH_return_fraction','weETH_return_fraction'],[[r['month'],r['book_nav_eth'],r['liquidETH_monthly_return'],r['stETH_monthly_return'],r['weETH_monthly_return']] for r in payload['etherfiHistory']])
    write_csv('Liquid-ETH-borrow-rates.csv',['date','series','protocol','market','loan_asset','borrow_APR_fraction','status','account','block','source'],[[r['date'],r['series_id'],r['protocol'],r['market_id'],r['loan_symbol'],r['borrow_apr'],r['status'],r['account'],r['block'],r['sourceURL']] for r in payload['borrowRateHistory']['rows']])
    carry_rows=[[p['product'],r['month'],r.get('sizeNative'),r.get('sizeNativeSymbol'),r.get('sizeETH'),r.get('sizeUSD'),r.get('status'),r.get('carryAllocationPercent'),'reader_carry_category.json' if p['product']=='YieldBasis WETH' else 'carry_category_candidates.json'] for p in payload['carryCategory']['products'] for r in p.get('history',[])]
    shutil.copyfile(DATA/'reader_analysis.json',OUT/'data/reader_analysis.json')
    for path in DATA.glob('carry-history-*.csv'):
        shutil.copyfile(path,OUT/'data'/path.name)
    rocksolid=next(p for p in payload['productChapters']['products'] if p['id']=='rocksolid')
    rock_months={r['month']:r for r in rocksolid['charts']['capitalHistory']['rows']}
    for month in chapter['months']:
        r=rock_months.get(month['period'],{})
        carry_rows.append([rocksolid['name'],month['period'],r.get('sizeNative'),r.get('sizeNativeSymbol'),r.get('sizeETH'),r.get('sizeUSD'),r.get('status','no_observation'),None,'product_chapters.json'])
    write_csv('carry-category-history.csv',['product','month','book_NAV_native','native_asset','book_NAV_ETH','book_NAV_USD','status','historical_carry_allocation_percent','source_ledger'],carry_rows)

    series=payload['wealth']['series'];names=list(series)
    for mask in range(2**len(names)):
        selected=[name for i,name in enumerate(names) if mask&(1<<i)]
        maps={name:{r['timestamp']:r['normalized_ETH_book_wealth'] for r in series[name]} for name in selected}
        stamps=sorted({t for points in maps.values() for t in points})
        write_csv(f'wealth-series-{mask}.csv',['date_UTC',*selected],[[datetime.fromtimestamp(t,timezone.utc).date().isoformat(),*[maps[name].get(t) for name in selected]] for t in stamps])
    for slug in sorted({r['protocol'] for r in payload['protocolHistory']}):
        rows=sorted([r for r in payload['protocolHistory'] if r['protocol']==slug],key=lambda r:r['period'])
        write_csv(f'protocol-{slug}-history.csv',['month','ETH_family_reported_USD','source_timestamp','target_timestamp'],[[r['period'],r['eth_family_reported_usd'],r['source_timestamp'],r['target_timestamp']] for r in rows])
    for p in (RESEARCH/'figures').iterdir():shutil.copyfile(p,OUT/'figures'/p.name)
    for stem,(folder,title) in ARTICLES.items():
        source=(ENGLISH/'dossiers'/f'{stem}.md') if folder=='dossiers' else ENGLISH/f'{stem}.md'
        body=markdown(source)
        toc=''.join(f'<a href="#{m[2]}">{re.sub("<[^>]+>","",m[3])}</a>' for m in re.finditer(r'<h([34]) id="([^"]+)">(.*?)</h\1>',body))
        current=stem in ['BRIEFING','MARKET-STRUCTURE','CARRY-CATEGORY','MARKET-COVERAGE','PRODUCT-SELECTION','CARRY-PRODUCTS']
        earlier=stem in ['README']
        status='<p class="note">Current report · 6 October 2026 · financial snapshot 2 October.</p>' if current else '<p class="note">'+('Earlier research note. Product selection and coverage figures may refer to an earlier edition. ' if earlier else 'Supporting evidence with its own observation dates. ')+'For current comparisons and conclusions, read the <a href="../library/BRIEFING.html">team briefing</a>. Earlier scopes are retained for provenance.</p>'
        page=(SRC/'article.html').read_text().replace('@@TITLE@@',html.escape(title)).replace('@@CONTENT@@',status+body).replace('@@TOC@@',toc)
        (OUT/folder/f'{stem}.html').write_text(page)
    library_groups = [
      ('New findings, 7 October', ['CONCRETE-DELTA','TOP5-RISK-LIQUIDITY','ROCKSOLID-NEMO-SENTORA','BORROWER-IDENTITIES','LIQUID-LOOP','REWARDS-SPLIT','TOP5-KEYS-HOLDERS-TERMS','CLOSED-CASES','RESTAKING-AND-LOOPS','OUTSIDE-AND-SMALL']),
      ('Market size and counting', ['MARKET-STRUCTURE','MARKET-COVERAGE','CAPITAL-INCOME-EXIT']),
      ('Strategy families', ['STRATEGY-UNIVERSE-EXPANSION','MECHANICS','PRODUCT-FINANCIAL-HISTORY','HGETH-LOAN-BOOK','staking-restaking','pendle-pt','lending-lp']),
      ('Carry capital and products', ['CARRY-CATEGORY','CARRY-PRODUCTS','PRODUCT-EVOLUTION','CARRY-VARIANTS-EXPANSION','CARRY-COVERAGE-AUDIT','PRODUCT-SELECTION','etherfi-liquid-eth']),
      ('Financing and income', ['CARRY-MATH','BORROW-HISTORY','DOLLAR-FUNDING-ATLAS','CREDIT-EXPANSION','CARRY-LIFECYCLES','BORROWER-USE','carry-credit']),
      ('Returns and investor access', ['HISTORY','RETURN-DRIVERS','PRODUCT-TERMS','LENDING-MARKETS','ECONOMICS','fluid-lite','treehouse-teth','cian-rseth','ethena-basis','liquid-monad']),
      ('Evidence and reproduction', ['BRIEFING','README','scope','methodology','EVIDENCE','AUDIT','justlend-tron']),
    ]
    listed = [stem for _, group in library_groups for stem in group]
    assert len(listed) == len(set(listed)) == len(ARTICLES) and set(listed) == set(ARTICLES)
    body = f'<h1>Research library</h1><p>Start with the <a href="BRIEFING.html">current team briefing</a>, <a href="MARKET-STRUCTURE.html">market structure</a>, <a href="CARRY-CATEGORY.html">carry census</a> and <a href="MARKET-COVERAGE.html">coverage matrix</a>. Their comparisons are rebuilt from one dataset. The {len(ARTICLES)} linked investigations retain dated evidence and earlier discovery scopes; they are not competing final reports.</p>'
    library_toc = ''
    for group_number, (question, group) in enumerate(library_groups, 1):
        heading_id = f'group-{group_number}'
        library_toc += f'<a href="#{heading_id}">{html.escape(question)}</a>'
        body += f'<h2 id="{heading_id}">' + html.escape(question) + '</h2><ul>'
        for stem in group:
            folder, title = ARTICLES[stem]
            href = f'{stem}.html' if folder == 'library' else f'../{folder}/{stem}.html'
            body += f'<li><a href="{href}">{html.escape(title)}</a></li>'
        body += '</ul>'
    library = (SRC/'article.html').read_text().replace('@@TITLE@@','Complete research library').replace('@@CONTENT@@',body).replace('@@TOC@@',library_toc).replace('Reviewed 4 October 2026','Reviewed 5 October 2026')
    (OUT/'library/index.html').write_text(library)
    template=(SRC/'index.html').read_text()
    script='\n'.join((SRC/name).read_text() for name in ['app.js','compare.js','presentation.js','charts.js','market.js','strict.js','closure.js','expansion.js','reader.js','economic.js','atlas.js','top5.js'])+'\ninitChartInspection();if(document.body.dataset.edition==="reader"){initReader();economicReader();atlasFinal();}else{init();initPresentation();renderResearchAdditions();initMarket();initStrictResearch();initResearchClosure();initResearchExpansion();openHash(true);}'
    # The reader edition gets only what it reads (runtime trace, parity audit 7 Oct); exhibits keeps the full payload.
    reader_payload={k:v for k,v in payload.items() if k not in READER_DROP}
    reader_payload['pools']=[None]*len(payload.get('pools',[]))
    if isinstance(payload.get('carryAttribution'),dict):reader_payload['carryAttribution']={'top5_coverage':payload['carryAttribution'].get('top5_coverage')}
    packed_reader=json.dumps(reader_payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    page=template.replace('@@CSS@@',css).replace('@@DATA@@',packed_reader).replace('@@JS@@',script)
    (OUT/'index.html').write_text(page)
    exhibits=(SRC/'exhibits.html').read_text().replace('@@CSS@@',css).replace('@@DATA@@',packed).replace('@@JS@@',script)
    (OUT/'exhibits.html').write_text(exhibits)
    # The site/eth mirror is no longer written: GitHub Pages serves eth/ directly (parity audit 7 Oct).
    # Publish only data files that a page links to (in HTML or in the page script); the rest stays in data/eth.
    import re as _re
    texts=[(OUT/'index.html').read_text(),(OUT/'exhibits.html').read_text()]+[p.read_text() for d in ['library','dossiers'] for p in (OUT/d).glob('*.html')]
    wanted=set()
    for t in texts:
        for m in _re.finditer(r'data/([A-Za-z0-9_.\-/]+\.(?:json|csv|jsonl|md|txt|py))',t):wanted.add(m.group(1))
    prefixes={m.group(1) for t in texts for m in _re.finditer(r"data/([A-Za-z0-9_\-]+)(?:['\"]\s*\+|\$\{)",t)}  # names built in the script, e.g. 'data/wealth-series-'+mask
    removed=0
    for f in (OUT/'data').rglob('*'):
        rel=str(f.relative_to(OUT/'data'))
        if f.is_file() and f.suffix=='.json' and rel not in wanted and rel not in ('report_contract.json','market_netting_closure.json','carry_attribution_closure.json','backing_exit_closure.json','basis_closure_disclosures.json') and not any(rel.startswith(x) for x in prefixes):f.unlink();removed+=1  # CSV exports stay
    print('Published data files:',sum(1 for f in (OUT/'data').rglob('*') if f.is_file()),'kept;',removed,'unlinked removed')
    print(f'ETH site built: {len(page):,} characters; {len(ARTICLES)} articles; {len(pools)} pool rows; {len(observations)} protocols')

if __name__=='__main__':build()

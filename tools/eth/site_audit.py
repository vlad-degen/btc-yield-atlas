"""Validate generated research pages, local navigation, embedded data and financial units."""
import csv, collections, hashlib, importlib.util, json, math, re, subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[2]
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=[];self.data=[];self.in_data=False;self.lang=None;self.copy=[];self.excluded=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='html':self.lang=d.get('lang')
        if tag in ['script','style']:self.excluded=True
        if 'id' in d:self.ids.append(d['id'])
        if tag in ['a','img','link'] and (d.get('href') or d.get('src')):self.links.append(d.get('href') or d.get('src'))
        if tag=='script' and d.get('id')=='research-data':self.in_data=True
    def handle_endtag(self,tag):
        if tag=='script':self.in_data=False
        if tag in ['script','style']:self.excluded=False
    def handle_data(self,s):
        if self.in_data:self.data.append(s)
        if not self.excluded:self.copy.append(s)

def run():
    builder_spec=importlib.util.spec_from_file_location("eth_site_builder",ROOT/"tools/eth/site.py")
    builder=importlib.util.module_from_spec(builder_spec);builder_spec.loader.exec_module(builder)
    checks=[]
    def check(name,passed,details=None):checks.append({'check':name,'passed':bool(passed),'details':details})
    pages={p:Page() for folder in ['eth','site/eth'] for p in (ROOT/folder).rglob('*.html')}
    for p,parsed in pages.items():parsed.feed(p.read_text())
    errors=[];duplicates=[];fragments=[]
    for p,parsed in pages.items():
        if len(parsed.ids)!=len(set(parsed.ids)):duplicates.append(str(p.relative_to(ROOT)))
        for link in parsed.links:
            u=urlsplit(link)
            if u.scheme or u.netloc:continue
            dest=(p.parent/unquote(u.path)).resolve() if u.path else p.resolve()
            if dest.is_dir():dest=dest/'index.html'
            if not dest.exists():errors.append([str(p.relative_to(ROOT)),link])
            # Main-page evidence anchors are inserted by JS. Article fragments are static.
            if u.fragment and dest in pages and ('/library/' in str(dest) or '/dossiers/' in str(dest)):
                if unquote(u.fragment) not in pages[dest].ids:fragments.append([str(p.relative_to(ROOT)),link])
    check('all_local_site_links_and_assets_resolve',not errors,{'pages':len(pages),'errors':errors})
    check('all_article_fragment_links_resolve',not fragments,fragments)
    check('generated_pages_have_unique_IDs',not duplicates,duplicates)
    check('all_pages_and_static_copy_are_English',all(p.lang=='en' and not re.search('[А-Яа-яЁё]',''.join(p.copy)) for p in pages.values()))
    main=pages[ROOT/'eth/index.html'];embedded=json.loads(''.join(main.data))
    check('site_payload_equals_generated_data',embedded==json.loads((ROOT/'data/eth/site_payload.json').read_text()))
    check('full_catalog_preserves_scope_and_missing_values',len(embedded['pools'])==5688 and len(embedded['chains'])==57 and len(embedded['protocols'])==85 and embedded['summary']['unique_underlying_ETH'] is None and embedded['summary']['verified_external_depositor_equity_ETH'] is None)
    counts=collections.Counter(r['days'] for r in embedded['etherfiReturns'])
    check('returns_cover_all_displayed_windows',all(counts[x]==1 for x in [30,90,365,730]) and all(len([r for r in embedded['returns'] if r['days']==d and r['product']==p])==1 for d in [30,90,365,730] for p in ['Fluid Lite ETH','Treehouse tETH','CIAN rsETH']))
    check('ETH_book_wealth_matches_comparative_returns',all(math.isclose(rows[-1]['normalized_ETH_book_wealth']/100-1, next(r['liquidETH_cumulative_return'] if name=='Liquid ETH' else r['stETH_cumulative_return'] if name=='stETH' else r['weETH_cumulative_return'] for r in embedded['etherfiReturns'] if r['days']==730) if name in ['Liquid ETH','stETH','weETH'] else next(r['ETH_pps_cumulative_return'] for r in embedded['returns'] if r['days']==730 and r['product']==name),rel_tol=1e-9) for name,rows in embedded['wealth']['series'].items()))
    script=(ROOT/'tools/eth/site/app.js').read_text()
    enhancement=(ROOT/'tools/eth/site/compare.js').read_text()
    presentation='\n'.join((ROOT/'tools/eth/site'/name).read_text() for name in ['presentation.js','market.js','strict.js','closure.js','expansion.js'])
    check('English_dynamic_copy_and_evidence',not re.search('[А-Яа-яЁё]',script+enhancement+presentation) and all(not re.search('[А-Яа-яЁё]',r['claim']+r['time_scope_and_limit']) for r in embedded['evidence']))
    check('reader_copy_has_no_long_dashes',all(not re.search('[—–]',''.join(p.copy)) for p in pages.values()) and not re.search('[—–]',script+enhancement+presentation))
    check('colleague_edition_has_market_structure_and_product_panels',len(pages)==2*(len(builder.ARTICLES)+2) and all(x in (ROOT/'eth/index.html').read_text() for x in ['library/BRIEFING.html','id="exit-cost-table"','id="borrower-sample-summary"','id="liquid-permission-review"','class="scope-note"']))
    check('reader_has_compact_market_and_separate_complete_exhibits',all(x not in (ROOT/'tools/eth/site/index.html').read_text() for x in ['id="strategy-atlas"','id="market-net-capital"','id="additional-product-history"','id="hgeth-loan-book"','id="coverage-findings"']) and all(x in (ROOT/'eth/exhibits.html').read_text() for x in ['id="strategy-atlas"','id="market-net-capital"','id="additional-product-history"','id="hgeth-loan-book"']))
    review=embedded['review']
    check('review_inputs_preserved_at_frozen_snapshot',review['financial_snapshot_timestamp']==1790985599 and review['financial_data_refreshed'] is False and all(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in review['inputs']))
    check('24_month_capital_changes_reconcile',len(review['growth'])==24 and all(math.isclose(r['NAV_change_ETH'],r['accounting_rate_effect_ETH']+r['share_supply_effect_ETH'],abs_tol=1e-8) and r['is_external_deposit_ledger'] is False for r in review['growth']) and all(math.isclose(sum(r[k] for r in review['growth']),review['growth_summary'][k],abs_tol=1e-7) for k in ['NAV_change_ETH','accounting_rate_effect_ETH','share_supply_effect_ETH']))
    fees=review['fees'];time=fees['window_start'];rate=fees['initial_fee_bps'];integral=0
    for event in fees['changes']:
        if not event['within_730_day_window']:continue
        integral+=(event['timestamp']-time)*rate;time=event['timestamp'];rate=event['new_fee_bps']
    integral+=(fees['window_end']-time)*rate
    check('Ethereum_fee_integration_matches_chronology',math.isclose(integral/(fees['window_end']-fees['window_start']),fees['calendar_time_weighted_fee_bps'],abs_tol=1e-10) and rate==fees['current_fee_bps']==35 and len(fees['changes'])==12 and fees['fee_history_scope'].startswith('Ethereum Accountant only'))
    check('exit_fee_models_apply_cost_to_proceeds_once',len(review['exit_illustrations'])==8 and all(math.isclose(r['illustrative_after_exit_return'],(1+r['book_return'])*(1-r['one_exit_fee_fraction'])-1,abs_tol=1e-12) and math.isclose(r['illustrative_excess_vs_stETH_pp'],100*(r['illustrative_after_exit_return']-r['stETH_book_return']),abs_tol=1e-10) and r['not_executed_historical_return'] is True for r in review['exit_illustrations']))
    permissions=json.loads((ROOT/'data/eth/permissions_review_T.json').read_text())
    check('selected_permission_counts_match_historical_roles',permissions['block']==26108081 and permissions['logs_paginated_to_creation'] is True and all(r['count']==len([h for h in permissions['role_holders_T'] if set(h['roles'])&set(r['roles'])]) for r in review['permissions']) and next(r for r in review['permissions'] if r['function']=='updateExchangeRate(uint96)')['count']==3 and next(r for r in review['permissions'] if r['function']=='updateManagementFee(uint16)')['roles']==[8,55])
    check('chart_tables_exports_and_product_comparison_present',all(x in ((ROOT/'eth/index.html').read_text()+(ROOT/'eth/exhibits.html').read_text()) for x in ['id="product-comparison"','id="wealth-table"','data-export="wealth"','data-export="protocol"','data-export="pools"','function productHistoryPanel()']) and len(embedded['etherfiHistory'])==24)
    export_errors=[]
    names=list(embedded['wealth']['series'])
    for mask in range(2**len(names)):
        selected=[name for i,name in enumerate(names) if mask&(1<<i)]
        maps={name:{r['timestamp']:r['normalized_ETH_book_wealth'] for r in embedded['wealth']['series'][name]} for name in selected}
        stamps=sorted({t for points in maps.values() for t in points})
        with (ROOT/'eth/data'/f'wealth-series-{mask}.csv').open() as f: rows=list(csv.reader(f))
        if rows[0]!=['date_UTC',*selected] or len(rows)!=len(stamps)+1:export_errors.append(mask)
        for row,t in zip(rows[1:],stamps):
            for i,name in enumerate(selected,1):
                value=maps[name].get(t)
                if (value is None and row[i]!='') or (value is not None and float(row[i])!=value):export_errors.append([mask,t,name])
    for slug in {r['protocol'] for r in embedded['protocolHistory']}:
        expected=sorted([r for r in embedded['protocolHistory'] if r['protocol']==slug],key=lambda r:r['period'])
        with (ROOT/'eth/data'/f'protocol-{slug}-history.csv').open() as f: rows=list(csv.DictReader(f))
        if len(rows)!=24:export_errors.append(slug)
        for row,source in zip(rows,expected):
            value=source['eth_family_reported_usd']
            if row['month']!=source['period'] or (value is None and row['ETH_family_reported_USD']!='') or (value is not None and float(row['ETH_family_reported_USD'])!=value):export_errors.append([slug,row['month']])
    check('CSV_exports_match_selected_series_and_preserve_nulls',not export_errors,export_errors)
    check('all_five_product_renderers_exist',all('function '+name+'(' in script for name in ['renderEtherfi','renderFluid','renderTreehouse','renderConcrete','renderCian']))
    syntax=[subprocess.run(['node','--check',str(ROOT/'tools/eth/site'/name)],capture_output=True,text=True) for name in ['app.js','compare.js','presentation.js','charts.js','market.js','strict.js','closure.js','expansion.js','reader.js']]
    check('browser_script_syntax_valid',all(r.returncode==0 for r in syntax),[r.stderr.strip() for r in syntax if r.stderr])
    check('artifact_copy_matches_main_site',(ROOT/'site/eth/index.html').read_bytes()==(ROOT/'eth/index.html').read_bytes())
    result={'all_checks_passed':all(r['passed'] for r in checks),'checks':checks,'pages':len(pages),'scope':'Generated website integrity and arithmetic consistency; browser interaction QA recorded separately. Not a complete financial audit.','site_sha256':hashlib.sha256((ROOT/'eth/index.html').read_bytes()).hexdigest()}
    (ROOT/'data/eth/site_audit_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({'passed':sum(r['passed'] for r in checks),'checks':len(checks),'failed':[r for r in checks if not r['passed']],'pages':len(pages)},ensure_ascii=False))
    if not result['all_checks_passed']:raise SystemExit(1)

if __name__=='__main__':run()

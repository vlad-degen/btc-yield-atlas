"""Package the English website, derived evidence and BTC reference for offline use."""
import json, posixpath, shutil, zipfile
from pathlib import Path
from urllib.parse import unquote,urlsplit
from site_audit import Page

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'eth'
DEST=OUT/'ETH-Yield-Research.zip'

def run():
    # Package the latest check results, rather than stale copies from an earlier build.
    for name in ['audit_results.json','site_audit_results.json','market_audit_results.json','strict_audit_results.json','reader_alignment_audit.json','research_closure_audit.json','market_netting_validation.json','carry_attribution_verification.json','backing_exit_verification.json','research_expansion_verification.json','strategy_universe_deep_verification.json','credit_expansion_deep_validation.json','report_contract_verification.json']:
        source=ROOT/'data/eth'/name
        pass  # QA records stay in data/eth; the public eth/ folder carries no QA copies
    import hashlib
    site_hash=hashlib.sha256((OUT/'index.html').read_bytes()).hexdigest()
    for name in ['site_audit_results.json','market_audit_results.json','strict_audit_results.json','reader_alignment_audit.json','research_closure_audit.json']:
        report=json.loads((ROOT/'data/eth'/name).read_text())
        assert report['all_checks_passed'] and report['site_sha256']==site_hash, f'Stale or failed checks: {name}'
    backing_report=json.loads((ROOT/'data/eth/backing_exit_verification.json').read_text())
    assert backing_report['status']=='passed' and backing_report['outputSHA256']==hashlib.sha256((ROOT/'data/eth/backing_exit_closure.json').read_bytes()).hexdigest()
    assert json.loads((ROOT/'data/eth/carry_attribution_verification.json').read_text())['failed']==0
    assert json.loads((ROOT/'data/eth/market_netting_validation.json').read_text())['passed']
    expansion=json.loads((ROOT/'data/eth/research_expansion_verification.json').read_text())
    assert expansion['all_checks_passed'] and expansion['site_sha256']==site_hash
    product_check=json.loads((ROOT/'data/eth/strategy_universe_deep_verification.json').read_text())
    assert product_check['status']=='passed' and product_check['datasetSHA256']==hashlib.sha256((ROOT/'data/eth/strategy_universe_deep.json').read_bytes()).hexdigest()
    assert json.loads((ROOT/'data/eth/credit_expansion_deep_validation.json').read_text())['passed']
    browser_source=ROOT/'data/eth/site_browser_qa.json'
    browser_report=json.loads(browser_source.read_text())
    assert browser_report['all_recorded_checks_passed'] and browser_report['site_sha256']==site_hash, 'Stale or failed browser checks'

    # The archive's checksum and verification are sidecars written after it closes.
    files=[p for p in OUT.rglob('*') if p.is_file() and p.suffix!='.zip' and not p.name.endswith('.zip.sha256') and p.name not in ['.DS_Store','package_final_verification.json']]
    files.extend([ROOT/'index.html',ROOT/'assets/favicon.svg'])
    files.extend(p for p in (ROOT/'data/eth').glob('*.json') if p.name.endswith(('_results.json','_audit.json','_verification.json','_validation.json','site_browser_qa.json')))
    # Small public historical-permission capture. The much larger original raw
    # financial collection stays in the project and is described in README.
    for folder in ['raw/eth/presentation-review','raw/eth/carry-economics-2026-10-04','raw/eth/carry-borrow-history-2026-10-04','raw/eth/2026-10-04/strict-products','raw/eth/research-closure-2026-10-04','raw/eth/funding-atlas-2026-10-04','raw/eth/credit-expansion-2026-10-04','raw/eth/carry-variants-expansion-2026-10-04','raw/eth/strategy-universe-expansion-2026-10-04','raw/eth/strategy-universe-deep-2026-10-04','raw/eth/credit-expansion-deep-2026-10-04','raw/eth/manager-case-2026-10-04','raw/eth/funding-borrower-deep-2026-10-04','raw/eth/parity-sweep-2026-10-05']:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
    with zipfile.ZipFile(DEST,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(files):archive.write(path,path.relative_to(ROOT))
    with zipfile.ZipFile(DEST) as archive:
        assert archive.testzip() is None
        assert archive.read('eth/index.html')==(OUT/'index.html').read_bytes()
        assert archive.read('index.html')==(ROOT/'index.html').read_bytes()
        assert archive.read('eth/README.md')==(OUT/'README.md').read_bytes()

        names=set(archive.namelist());broken=[]
        pages=[n for n in names if n.endswith('.html') and (n.startswith('eth/') or n=='index.html')]
        for name in pages:
            page=Page();page.feed(archive.read(name).decode())
            for link in page.links:
                url=urlsplit(link)
                if url.scheme or url.netloc:continue
                target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(url.path))) if url.path else name
                if target not in names and posixpath.normpath(target+'/index.html') not in names:broken.append([name,link,target])
        assert not broken,broken
    sha=hashlib.sha256(DEST.read_bytes()).hexdigest()
    (OUT/(DEST.name+'.sha256')).write_text(sha+'  '+DEST.name+'\n')
    report={'all_checks_passed':True,'archive_SHA256':sha,'bytes':DEST.stat().st_size,'archive_files':len(names),'presentation_HTML_pages':len(pages),'broken_local_presentation_links':broken,'CRC_checked':True,'latest_site_and_QA_match':True,'mirror_matches':True,'financial_snapshot':'2026-10-02T23:59:59Z','scope':'Checks portable research pages and archive CRCs. Captured third-party HTML is immutable evidence, not a bundled runnable third-party website.'}
    for folder in ['data/eth']:(ROOT/folder/'package_final_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Portable archive: {len(files)} files; {DEST.stat().st_size:,} bytes')
    print('All local presentation links and final audit copies verified. SHA256:',sha)

if __name__=='__main__':run()

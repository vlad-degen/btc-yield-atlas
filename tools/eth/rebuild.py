"""Rebuild local analytical outputs from captured evidence, with no network calls."""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def run():
 modules=['discover','normalize','pilot_analyze','benchmark_analyze','vault_history_analyze','catalog','pilot_balance','package_metrics','report_tables','history_synthesis','economics','lending_synthesis','dependency_graph','evidence','presentation_analysis','market_data_probe','carry_economics_build','carry_borrow_history','market_netting_build','carry_attribution_build','carry_attribution_recycling','carry_attribution_organic','carry_attribution_tranches','carry_attribution_close','backing_exit_build','basis_closure_build','build_product_chapters','closure_reports']
 modules += ['funding_atlas_build','strategy_universe_expansion_build','carry_variants_expansion_build','credit_expansion_build','credit_expansion_deep_build','strategy_universe_deep_build','funding_borrower_deep_build','manager_case_build','research_expansion_build']
 # counted-once market map: offline steps over the saved DefiLlama pulls (fetch: netmap/01_fetch.py, 02b, 02c)
 for step in ['02_screen','03_build','04_chapter','05_verify']:
  subprocess.run([sys.executable,str(ROOT/'tools/eth/netmap'/f'{step}.py')],cwd=ROOT/'tools/eth/netmap',check=True,capture_output=True)
 modules=['atlas_build']+modules
 for name in modules:
  r=subprocess.run([sys.executable,str(ROOT/'tools/eth'/f'{name}.py')],cwd=ROOT,capture_output=True,text=True)
  if r.returncode:print(r.stdout[-1800:],r.stderr[-1800:]);raise SystemExit(r.returncode)
  print(name,'OK')
 fig=os.environ.get('ETH_FIGURE_PYTHON','/Users/vladdegen/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3')
 if os.path.exists(fig):subprocess.run([fig,str(ROOT/'tools/eth/figures.py')],cwd=ROOT,check=True)
 else:print('figures skipped: set ETH_FIGURE_PYTHON to a Python with PIL and reportlab')
 subprocess.run([sys.executable,str(ROOT/'tools/eth/site.py')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/site_audit.py')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/audit.py')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/market_audit.py')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/carry_economics_verify.py')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/carry_borrow_history.py'),'--verify'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/strict_audit.py')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/reader_alignment_audit.py')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/report_contract_verify.py')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/market_netting_validate.py')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/eth/carry_attribution_verify.py')],cwd=ROOT,check=True)
 verified=subprocess.run([sys.executable,str(ROOT/'tools/eth/backing_exit_verify.py')],cwd=ROOT,capture_output=True,text=True,check=True)
 backing_report=json.loads(verified.stdout)
 (ROOT/'data/eth/backing_exit_verification.json').write_text(json.dumps(backing_report,indent=2)+'\n')
 print('Backing and exit verification:',backing_report['checks'],'passed')
 subprocess.run([sys.executable,str(ROOT/'tools/eth/research_closure_audit.py')],cwd=ROOT,check=True)
 for name in ['strategy_universe_expansion_verify','strategy_universe_deep_verify','credit_expansion_deep_validate','research_expansion_verify']:
  subprocess.run([sys.executable,str(ROOT/'tools/eth'/f'{name}.py')],cwd=ROOT,check=True)
if __name__=='__main__':run()

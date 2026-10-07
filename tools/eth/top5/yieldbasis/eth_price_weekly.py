"""Chainlink ETH/USD (0x5f4e...8419 latestAnswer) at the YieldBasis weekly blocks; adds eth_usd to weekly.csv."""
import sys, pathlib, csv
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from weekly_lib import *
F='0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419'
p=ROOT/'data/eth/top5/yieldbasis/weekly.csv'
rows=list(csv.DictReader(open(p)))
for r in rows:
    a,u=call(F,'latestAnswer()',block=int(r['block']))
    r['eth_usd_chainlink']=a/1e8
    r['source']=r['source']+'; Chainlink ETH/USD latestAnswer'
write_csv(p,rows)

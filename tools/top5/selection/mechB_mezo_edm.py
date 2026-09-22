import sys; sys.path.insert(0,'.')
import mechB_rpc as R
from hashlib import sha3_256
from mechB_keccak import keccak256 as k
EDM='0x2C5e9aFBb670c4A61aC2DcAD62C258eE2391389a'
def c(sig, args=''):
    return R.call('mezo', EDM, '0x'+k(sig)[:8]+args)
for f in ['totalPrincipal()','getTotalOutstandingDebt()','totalMintedDebt()','totalDebtBurned()','mintCap()','veBTC()','priceFeed()']:
    r=c(f); v=int(r,16)
    print(f, v/1e18 if v>1e30 or 'otal' in f or 'Cap' in f else '0x'+r[-40:])
for pid in ['4da9e77114ee66d64ca9457d6a43a4fd00000000000000000000000000000000','147379a0174780570d07d70a6a5610d300000000000000000000000000000000']:
    col=int(c('getPositionCollateral(bytes32)',pid),16)
    r=c('getPositionDebt(bytes32)',pid)
    cr=int(c('getPositionCR(bytes32)',pid),16)
    print(pid[:10],'collateral BTC',col/1e18,'debt raw',[int(r[2+64*i:2+64*(i+1)],16)/1e18 for i in range((len(r)-2)//64)],'CR',cr/1e18)

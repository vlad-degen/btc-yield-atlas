import sys,json
sys.path.insert(0,'.')
from morpho import gql
def user(addr,chain):
    q='''query($a:String!,$c:Int){ userByAddress(address:$a, chainId:$c){ address marketPositions{ market{ marketId loanAsset{symbol} collateralAsset{symbol} } state{ supplyAssetsUsd borrowAssetsUsd collateralUsd collateral borrowAssets } } vaultPositions{ vault{ name address } state{ assetsUsd } } } }'''
    try:
        r=gql(q,{'a':addr,'c':chain})
    except Exception as e:
        return str(e)
    return r
if __name__=='__main__':
    print(json.dumps(user(sys.argv[1],int(sys.argv[2])),indent=1)[:4000])

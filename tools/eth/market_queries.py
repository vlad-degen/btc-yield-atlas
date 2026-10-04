"""Official Morpho public API schema and borrower discovery, never a fixed-block total."""
from collect import request

def run():
 q='''query{market:__type(name:"MarketFilters"){inputFields{name type{kind name ofType{kind name}}}} positions:__type(name:"MarketPositionFilters"){inputFields{name type{kind name ofType{kind name}}}} order:__type(name:"MarketPositionOrderBy"){enumValues{name}}}'''
 request('morpho_discovery_schema','https://api.morpho.org/graphql',{'query':q})
 q='''query{markets(first:1000,where:{chainId_in:[1,8453,42161,10],borrowAssetsUsd_gte:1000000}){items{marketId lltv loanAsset{address symbol decimals} collateralAsset{address symbol decimals} state{borrowAssetsUsd supplyAssetsUsd borrowApy supplyApy utilization}} pageInfo{count countTotal}}}'''
 request('morpho_markets_discovery','https://api.morpho.org/graphql',{'query':q})

if __name__=='__main__':run()

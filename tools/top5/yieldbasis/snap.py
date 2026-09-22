from ybrpc import *
from markets import M
def snap(m,block='latest'):
    lt,amm,pool,orc,st=m['lt'],m['amm'],m['pool'],m['oracle'],m['staker']
    d={}
    d['supply']=u(ec(lt,'totalSupply()',block=block))
    if not d['supply']: return d
    d['pps']=u(ec(lt,'pricePerShare()',block=block))
    d['redeem1']=u(ec(lt,'preview_withdraw(uint256)',eu(10**18),block=block))
    w=ec(lt,'liquidity()',block=block); ww=words(w) if w else None
    if ww: d['liq_admin']=s('0x'+hex(ww[0])[2:].rjust(64,'0')); d['liq_total'],d['ideal_staked'],d['staked']=ww[1],ww[2],ww[3]
    d['staked_bal']=u(ec(lt,'balanceOf(address)',ea(st),block=block))
    ub=words(ec(lt,'updated_balances()',block=block) or '0x')
    if ub: d['upd_supply'],d['upd_staked']=ub[0],ub[1]
    d['alloc']=u(ec(lt,'stablecoin_allocation()',block=block))
    d['allocated']=u(ec(lt,'stablecoin_allocated()',block=block))
    d['debt']=u(ec(amm,'get_debt()',block=block))
    d['coll']=u(ec(amm,'collateral_amount()',block=block))
    d['rate']=u(ec(amm,'rate()',block=block))
    d['fee']=u(ec(amm,'fee()',block=block))
    d['max_debt']=u(ec(amm,'max_debt()',block=block))
    vo=words(ec(amm,'value_oracle()',block=block) or '0x')
    if vo: d['vo_p'],d['vo_value']=vo
    d['killed']=u(ec(amm,'is_killed()',block=block))
    d['lp_price']=u(ec(orc,'price()',block=block))
    d['ps']=u(ec(pool,'price_scale()',block=block))
    d['po']=u(ec(pool,'price_oracle()',block=block))
    d['vp']=u(ec(pool,'virtual_price()',block=block))
    d['b0']=u(ec(pool,'balances(uint256)',eu(0),block=block))
    d['b1']=u(ec(pool,'balances(uint256)',eu(1),block=block))
    d['pool_supply']=u(ec(pool,'totalSupply()',block=block))
    return d

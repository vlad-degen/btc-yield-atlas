import lib,csv
det=lib.load('yield_detail.json'); T={r['month']:r for r in csv.DictReader(open('../tvl_monthly.csv'))}; Y={r['month'][:7]:r for r in csv.DictReader(open('../yield_monthly.csv'))}
tot_r=tot_g=tot_c=tot_n=tot_f=0; out=[]
for k,d in det.items():
    t=T[k]; y=Y[k[:7]]
    ny=float(t['yield_effect_usd'] or 0)
    fee=float(y['platform_fee_bps_avg'] or 0)/1e4*float(y['avg_nav_btc'] or 0)*d['days']/365*float(t['btc_usd'])
    g=ny+fee; rw=sum(d['rewards_usd'].values())
    co=sum((-1 if leg.startswith('B:') else 1)*v['avg_usd']*v['apy']/100*d['days']/365 for leg,v in d['legs'].items())
    tot_r+=rw; tot_g+=g; tot_c+=co; tot_n+=ny; tot_f+=fee
    out.append((k,round(ny),round(fee),round(g),round(rw),round(co)))
    print(k,round(ny),round(fee),round(g),round(rw),f"{rw/g*100:.0f}%" if g>1000 else '-',round(co))
print('TOTAL net',round(tot_n),'fees',round(tot_f),'gross',round(tot_g),'rewards',round(tot_r),'share',round(tot_r/tot_g*100,1),'organic stable carry',round(tot_c))
lib.save('incentive_share.json',{'rows':out,'net':tot_n,'fees':tot_f,'gross':tot_g,'rewards':tot_r,'organic_carry':tot_c})

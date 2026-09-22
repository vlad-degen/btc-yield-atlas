import re,html,sys
t=open(sys.argv[1]).read()
t=re.sub(r'<script.*?</script>','',t,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
kw=sys.argv[2].split(',') if len(sys.argv)>2 else None
if not kw: print(t); sys.exit()
seen=set()
for k in kw:
    for m in re.finditer(k,t):
        s=max(0,m.start()-250)
        if any(abs(s-x)<200 for x in seen): continue
        seen.add(s); print('['+k+']',t[s:m.start()+350]); print('--')

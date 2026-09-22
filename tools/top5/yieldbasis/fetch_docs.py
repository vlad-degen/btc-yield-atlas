import re,urllib.request,html,os,sys
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
sm=open('raw/sitemap.xml').read()
urls=[u for u in re.findall(r'<loc>([^<]*)</loc>',sm) if '/user/' in u or '/dev/' in u]
def txt(h):
    h=re.sub(r'(?s)<script.*?</script>|<style.*?</style>','',h)
    m=re.search(r'(?s)<article.*?</article>',h)
    if m: h=m.group(0)
    h=re.sub(r'<(br|/p|/li|/tr|/h\d|/div|/pre)[^>]*>','\n',h)
    h=re.sub(r'<(td|th)[^>]*>',' | ',h)
    h=re.sub(r'<[^>]+>','',h)
    h=html.unescape(h)
    h=re.sub(r'\n\s*\n+','\n',h)
    return h
for u in urls:
    name=u.split('docs.yieldbasis.com/')[1].replace('/','_')
    fn='raw/docs/'+name+'.txt'
    if os.path.exists(fn): continue
    try:
        h=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=30).read().decode()
        open(fn,'w').write(txt(h))
        print('ok',name,len(h))
    except Exception as e: print('ERR',u,e)

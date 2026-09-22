#!/usr/bin/env python3
"""Fetch a URL with a browser UA and dump readable text (script/style stripped)."""
import sys, re, html, urllib.request
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def text_of(raw):
    raw = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', raw)
    raw = re.sub(r'(?i)<br\s*/?>|</p>|</h\d>|</li>|</div>|</tr>', '\n', raw)
    raw = re.sub(r'<[^>]+>', ' ', raw)
    raw = html.unescape(raw)
    raw = re.sub(r'[ \t\r\f\v]+', ' ', raw)
    raw = re.sub(r'\n\s*\n+', '\n', raw)
    return raw.strip()
if __name__ == '__main__':
    url = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else None
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,*/*'})
    try:
        raw = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')
    except Exception as e:
        print('ERR', e); sys.exit(1)
    t = text_of(raw)
    if out:
        open(out, 'w').write(t)
        print(url, len(t))
    else:
        print(t)

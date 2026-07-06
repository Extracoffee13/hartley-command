#!/usr/bin/env python3
"""Fast BFS crawler for brand9signs.com — writes incremental JSON."""
import json, sys, time, os, re
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urljoin
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser

BASE = "https://brand9signs.com"
MAX_PAGES = 120
DELAY = 0.2
TIMEOUT = 10
OUT = "/tmp/crawl-results.json"
TS = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

class P(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.title = None; self.meta_desc = None; self.canonical = None
        self.h1s = []; self.int_links = []; self.ext_links = []
        self._in_t = False; self._in_h = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title': self._in_t = True
        elif tag == 'h1': self._in_h = True
        elif tag == 'meta' and a.get('name','').lower()=='description': self.meta_desc = a.get('content','')[:300]
        elif tag == 'link' and a.get('rel')=='canonical': self.canonical = a.get('href')
        elif tag == 'a' and a.get('href'):
            h = a['href'].strip()
            if h.startswith(('#','tel:','mailto:')): return
            f = urljoin(self.base, h)
            p = urlparse(f)
            if p.scheme in ('http','https'):
                if 'brand9signs.com' in p.netloc:
                    if f not in self.int_links: self.int_links.append(f)
                elif f not in self.ext_links: self.ext_links.append(f)
    def handle_endtag(self, tag):
        if tag == 'title': self._in_t = False
        elif tag == 'h1': self._in_h = False
    def handle_data(self, d):
        d = d.strip()
        if self._in_t and d: self.title = d[:200]
        elif self._in_h and d: self.h1s.append(d[:200])

def fetch(url):
    start = time.time()
    req = Request(url, headers={'User-Agent':'PRAGMA-SiteHealth/1.0','Accept':'text/html'})
    try:
        resp = urlopen(req, timeout=TIMEOUT)
        body = resp.read()
        return {'status': resp.status, 'redirect': resp.url if resp.url!=url else None,
                'content_type': resp.headers.get('Content-Type',''), 'size': len(body),
                'load_s': round(time.time()-start,3), 'body': body}
    except HTTPError as e:
        b = e.read() if e.fp else b''
        return {'status': e.code, 'redirect': None,
                'content_type': e.headers.get('Content-Type',''), 'size': len(b),
                'load_s': round(time.time()-start,3), 'body': b}
    except URLError as e:
        return {'status':0,'error':str(e.reason)[:100],'load_s':round(time.time()-start,3),'body':b''}

def crawl():
    visited = set()
    queue = [BASE]

    with open(OUT, 'w') as f:
        f.write('{"crawl_timestamp":"'+TS+'","pages":[\n')
        first = True

        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)
            clean = urlparse(url)._replace(fragment='').geturl()
            if clean in visited: continue
            visited.add(clean)

            pg = fetch(clean)
            e = {'url': clean, 'status_code': pg['status'],
                 'content_type': pg.get('content_type',''), 'content_length': pg.get('size',0),
                 'load_time_s': pg.get('load_s',0), 'error': pg.get('error',None)}

            body = pg.get('body',b'')
            ct = pg.get('content_type','')
            if pg['status'] < 400 and ('text/html' in ct):
                try:
                    parser = P(clean)
                    parser.feed(body.decode('utf-8','replace'))
                    e['title'] = parser.title
                    e['title_len'] = len(parser.title or '')
                    e['meta_description'] = parser.meta_desc
                    e['meta_desc_len'] = len(parser.meta_desc or '')
                    e['h1s'] = parser.h1s[:3]
                    e['h1_count'] = len(parser.h1s)
                    e['canonical'] = parser.canonical
                    e['internal_links'] = len(parser.int_links)
                    e['external_links'] = len(parser.ext_links)

                    for link in parser.int_links:
                        lp = urlparse(link)._replace(fragment='').geturl()
                        if lp not in visited and 'brand9signs.com' in lp:
                            dp = len(urlparse(lp).path.strip('/').split('/'))
                            if dp <= 4 and lp not in queue: queue.append(lp)
                except Exception as err:
                    e['parse_error'] = str(err)[:80]

            if not first: f.write(',\n')
            first = False
            f.write(json.dumps(e, default=str))
            time.sleep(DELAY)
            sys.stderr.write(f"  [{e['status_code']}] {clean} ({e.get('load_time_s','?')}s)\n")

        f.write(']}')
    return visited

start = time.time()
visited = crawl()
elapsed = round(time.time()-start, 1)
with open(OUT) as f:
    data = json.load(f)

pages = data['pages']
sc = {}
for p in pages:
    sc[p['status_code']] = sc.get(p['status_code'], 0) + 1

slow = [p for p in pages if p.get('load_time_s',0) > 2.0]
meta_long = [p for p in pages if p.get('title_len',0) > 60]
no_meta = [p for p in pages if p.get('status_code')==200 and not p.get('meta_description') and p.get('title')]
h1_issues = [p for p in pages if p.get('status_code')==200 and (not p.get('h1s') or p.get('h1_count',0)!=1) and p.get('title')]
redirects = [p for p in pages if p.get('redirect')]
errors = [p for p in pages if p['status_code'] >= 400]

iss = {
    'slow_pages': len(slow), 'slow_page_urls': [p['url'] for p in slow[:15]],
    'meta_description_long_or_missing': len(meta_long) + len(no_meta),
    'title_too_long': len(meta_long), 'title_long_urls': [p['url'] for p in meta_long[:10]],
    'h1_issues': len(h1_issues), 'h1_issue_urls': [p['url'] for p in h1_issues[:10]],
    'no_meta_description': len(no_meta), 'no_meta_urls': [p['url'] for p in no_meta[:10]],
    'status_4xx_5xx': len(errors), 'error_urls': [f"{p['status_code']} {p['url']}" for p in errors],
    'redirects': len(redirects), 'redirect_urls': [p['url'] for p in redirects[:5]],
}

summary = {
    'crawl_timestamp': TS, 'duration_s': elapsed,
    'pages_crawled': len(pages), 'status_codes': dict(sorted(sc.items())),
    'issues': iss
}
data['summary'] = summary

with open(OUT, 'w') as f:
    json.dump(data, f, indent=2, default=str)

print(f"\n=== CRAWL SUMMARY ===", file=sys.stderr)
print(f"Pages: {len(pages)} in {elapsed}s", file=sys.stderr)
print(f"Status: {dict(sorted(sc.items()))}", file=sys.stderr)
print(f"Issues: {iss['slow_pages']} slow, {iss['title_too_long']} title long, {iss['h1_issues']} H1, {iss['no_meta_description']} no meta, {iss['status_4xx_5xx']} HTTP errors, {iss['redirects']} redirects", file=sys.stderr)
print(json.dumps(summary, indent=2))
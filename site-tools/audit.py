#!/usr/bin/env python3
"""Audit every generated route, not just a few representative templates."""
import collections
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public'
BASE='https://www.bryanjunksitaway.com'
manifest=json.loads((ROOT/'site-tools/manifest.json').read_text())
pages={p['path']:p for p in manifest}
errors=[]

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.assets=[];self.canon=[];self.meta={};self.h1=0;self.ld=[];self.current=None;self.buffer='';self.ids=[];self.main=[];self.inmain=False;self.inh1=False;self.heading=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.append(d['id'])
        if tag=='main':self.inmain=True
        if tag=='a':self.links.append(d.get('href',''))
        if tag=='img':
            self.assets.append(d.get('src',''))
            if 'alt' not in d:errors.append('Image lacks alt')
            if 'width' not in d or 'height' not in d:errors.append('Image lacks dimensions')
        if tag=='script' and 'src' in d:self.assets.append(d['src'])
        if tag=='link' and d.get('rel')=='stylesheet':self.assets.append(d['href'])
        if tag=='link' and d.get('rel')=='canonical':self.canon.append(d['href'])
        if tag=='meta':self.meta[d.get('name',d.get('property',''))]=d.get('content','')
        if tag=='h1':self.h1+=1;self.inh1=True
        if tag=='script' and d.get('type')=='application/ld+json':self.current='ld';self.buffer=''
    def handle_data(self,text):
        if self.current:self.buffer+=text
        if self.inmain:self.main.append(text)
        if self.inh1:self.heading.append(text)
    def handle_endtag(self,tag):
        if tag=='main':self.inmain=False
        if tag=='h1':self.inh1=False
        if tag=='script' and self.current:
            try:self.ld.append(json.loads(self.buffer))
            except:errors.append('Invalid JSON-LD')
            self.current=None

parsed={}
for path,row in pages.items():
    text=(OUT/row['file']).read_text();p=Page();p.feed(text);parsed[path]=p
    if p.h1!=1:errors.append(path+': expected one H1')
    if p.canon!=[BASE+path]:errors.append(path+': canonical mismatch')
    if len(p.ids)!=len(set(p.ids)):errors.append(path+': duplicate IDs')
    if ('noindex' not in p.meta.get('robots',''))!=row['indexable']:errors.append(path+': robots mismatch')
    if p.meta.get('og:url')!=BASE+path:errors.append(path+': social URL mismatch')
    if not p.meta.get('description'):errors.append(path+': no description')
    if not p.ld:errors.append(path+': no schema')
    if row['indexable'] and len(' '.join(p.main).split())<120:errors.append(path+': thin indexable page')
    for graph in p.ld:
        for node in graph.get('@graph',[]):
            if node['@type']=='LocalBusiness' and any(k in node for k in ['address','aggregateRating','review','openingHours','geo']):errors.append(path+': unverified business attribute')
            if node['@type']=='BreadcrumbList':
                for n,item in enumerate(node['itemListElement']):
                    if item['position']!=n+1 or item['item'].removeprefix(BASE) not in pages:errors.append(path+': broken breadcrumb')
    for asset in p.assets:
        if asset.startswith('http'):continue
        target=OUT/(asset.lstrip('/') if asset.startswith('/') else str(Path(row['file']).parent/asset))
        if not target.is_file():errors.append(path+': missing asset '+asset)

inbound=collections.Counter();edges={}
for path,p in parsed.items():
    edges[path]=[]
    for link in p.links:
        u=urlsplit(link)
        if u.scheme and (u.netloc!='www.bryanjunksitaway.com'):continue
        if not u.path:target=path
        elif u.path.startswith('/'):target=u.path
        else:target='/'+str(Path(pages[path]['file']).parent/u.path)
        if target=='/index.html':errors.append(path+': link uses homepage alias')
        if target not in pages:errors.append(path+': broken link '+link);continue
        if u.fragment and unquote(u.fragment) not in parsed[target].ids:errors.append(path+': missing anchor '+link)
        inbound[target]+=1;edges[path].append(target)

seen=set();todo=['/']
while todo:
    page=todo.pop()
    if page in seen:continue
    seen.add(page);todo.extend(edges[page])
for path in pages:
    if path not in seen and path!='/confirmation.html':errors.append(path+': orphan page')
for key in ['path','title','description']:
    for value,count in collections.Counter(p[key] for p in manifest).items():
        if count>1:errors.append('Duplicate '+key+': '+value)
for value,count in collections.Counter(' '.join(p.heading) for p in parsed.values()).items():
    if count>1:errors.append('Duplicate H1: '+value)

ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls=[]
for file in ['sitemap-pages.xml','sitemap-services.xml']:
    urls += [el.text for el in ET.parse(OUT/file).findall('.//s:url/s:loc',ns)]
expected={BASE+p['path'] for p in manifest if p['indexable']}
if set(urls)!=expected or len(urls)!=len(set(urls)):errors.append('Sitemap differs from indexable routes')
locs=json.loads((ROOT/'site-tools/content/locations.json').read_text())
services=json.loads((ROOT/'site-tools/content/services.json').read_text())
regions=json.loads((ROOT/'site-tools/content/regions.json').read_text())
for loc in locs:
    for s in [s for s in services if s['core']]:
        if '/'+s['slug']+'/'+loc['slug']+'/' not in pages:errors.append('Missing service/location pair')
    actual={r['slug'] for r in regions if loc['slug'] in r['locations']}
    if actual!=set(loc['regions']):errors.append('Region mismatch '+loc['slug'])

# Normalize place names to reveal deliberate service-copy reuse, never hide it with synonyms.
groups=collections.defaultdict(list)
for row in manifest:
    if row['location']:groups[row['service']].append(row['path'])
reused=sum(len(v) for v in groups.values())
if any(p['indexable'] for p in manifest if p['location']):errors.append('Location indexing needs a separate editorial quality review')
report={'pages':len(pages),'indexable':len(expected),'noindex':len(pages)-len(expected),'locations':len(locs),'core_services':sum(s['core'] for s in services),'service_location_pages':reused,'shared_content_groups':{k:len(v) for k,v in groups.items()},'shared_content_action':'All service/location pages noindexed pending verified local editorial content. Noindex URLs excluded from sitemap.','errors':errors}
(ROOT/'site-tools/audit-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
sys.exit(bool(errors))

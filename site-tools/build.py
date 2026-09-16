#!/usr/bin/env python3
"""Build the static site. No runtime framework or content database required."""
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public'
CONTENT = ROOT / 'site-tools/content'
BASE = 'https://www.bryanjunksitaway.com'
BRAND = 'Bryan Junks It Away'
services = json.loads((CONTENT / 'services.json').read_text())
regions = json.loads((CONTENT / 'regions.json').read_text())
locations = json.loads((CONTENT / 'locations.json').read_text())
S = {x['slug']: x for x in services}
R = {x['slug']: x for x in regions}
L = {x['slug']: x for x in locations}
CORE = [x for x in services if x['core']]
LOAD_BANDS = {key:(int(low),int(high)) for key,low,high in re.findall(r'(\w+):\[(\d+),(\d+)\]',(ROOT/'pricing.js').read_text())}
manifest = []
e = lambda text: html.escape(str(text), quote=True)

REGIONAL = {
 'san-gabriel-valley': ('From our Baldwin Park base.', 'Baldwin Park is our home base, and the San Gabriel Valley is part of our service territory. Choose your area below for furniture pickup, mixed household junk, or a larger cleanout. We travel to the pickup location; these are service areas, not additional offices.', 'Junk Removal & Cleanouts Across the San Gabriel Valley', 'https://upload.wikimedia.org/wikipedia/commons/e/e4/Pasadena_City_Hall_David_Wakely.jpg', 'Pasadena City Hall'),
 'los-angeles': ('Find your part of LA.', 'Our Los Angeles service directory includes neighborhoods, communities, and cities across the area. Choose the place where the pickup is needed, then explore the service that fits. Bryan Junks It Away travels from its Baldwin Park base; there is no separate office at each location.', 'Junk Removal, Furniture Hauling & Cleanouts in Los Angeles', 'https://upload.wikimedia.org/wikipedia/commons/2/2d/Los_Angeles_skyline.jpg', 'Los Angeles skyline'),
 'san-fernando-valley': ('Less in the way. More room to live.', 'From a sofa pickup to a garage clear-out, use our San Fernando Valley directory to find the right service for your area. The list includes neighborhood and city names people use when arranging a pickup. Tell us the actual address and access details when you request an estimate.', 'Junk Removal & Hauling Across the San Fernando Valley', '/assets/sfv-studio-city.jpg', 'Palm-lined street in Studio City'),
 'inland-empire': ('A clear plan for the whole load.', 'Explore our Inland Empire service coverage for unwanted furniture, household junk, and cleanouts. Some locations also appear in our Riverside County directory; they link to the same service pages and use the same pricing guide. Share the amount and type of junk so we can plan around the real load.', 'Junk Removal & Hauling Across the Inland Empire', '/assets/inland-empire-landscape.jpg', 'Cityscape, palms, and mountains in the Inland Empire'),
 'riverside': ('From leftover items to a bigger reset.', 'Our Riverside County directory covers the listed pickup areas, including Riverside itself. Choose your community to explore single-item removal, furniture hauling, or a whole-property cleanout. Locations also listed under Inland Empire use one shared set of service pages.', 'Junk Removal & Cleanout Services in Riverside County', 'https://upload.wikimedia.org/wikipedia/commons/c/ce/Courtyard_of_Mission_Inn_with_Church_-_Riverside,_CA_-_USA_-_01_%286919712685%29.jpg', 'Courtyard and church at the Mission Inn in Riverside'),
 'orange-county': ('The room you need. The details upfront.', 'Need an old mattress gone, a garage back, or the leftovers from a move cleared out? Explore the Orange County pickup areas below. Our service guide uses the same starting-price framework across the territory, with the actual load and access reviewed before you approve the job.', 'Junk Removal & Property Cleanouts Across Orange County', '/assets/orange-county-selected.jpg', 'Orange County waterfront with boats and palms')
}

def a(url, label, cls=''):
    return f'<a href="{e(url)}"'+(f' class="{e(cls)}"' if cls else '')+f'>{e(label)}</a>'

def actions(location=None):
    query = '?' + urlencode({'city': location['name'], 'area': R[location['regions'][0]]['name']}) if location else ''
    return '<div class="hero-booking-actions">'+a('/estimate-survey.html'+query, 'Get a Free Estimate ↗', 'button')+a('/schedule.html'+query, 'Schedule Pickup ↗', 'button secondary-button')+'</div><p class="fine">Free booking · No deposit · Final price agreed before work begins</p>'

def chrome(path):
    links = [('/', 'Home'), ('/services/', 'Services'), ('/service-areas/', 'Service Areas'), ('/calculator.html', 'Get an Estimate'), ('/contact.html', 'Contact')]
    nav = ''.join(f'<a href="{url}"'+(' aria-current="page"' if path == url else '')+f'>{label}</a>' for url,label in links)
    header = '<a class="skip" href="#main-content">Skip to content</a><header>'+a('/', 'BRYAN', 'wordmark').replace('BRYAN</a>', 'BRYAN<span>JUNKS IT AWAY</span></a>')+f'<nav id="primary-nav" aria-label="Main navigation">{nav}</nav>'+a('/schedule.html','Book now ↗','button header-book')+'</header>'
    top = '<div class="top-areas" aria-label="Regional service directories"><span>Serving:</span>'+''.join(a(r['url'],r['name']) for r in regions)+'</div>'
    footer = '<footer class="site-footer"><div>'+a('/','BRYAN','wordmark').replace('BRYAN</a>','BRYAN<span>JUNKS IT AWAY</span></a>')+'<p>Big or small, Bryan junks it all away.</p><p>Based in Baldwin Park.<br>We come to you.</p>'+a('tel:+16263865623','626-386-5623')+a('mailto:bryanjunksitaway@gmail.com','bryanjunksitaway@gmail.com')+'</div><div><strong>Services</strong>'+''.join(a('/'+s['slug']+'/',s['name']) for s in CORE)+'</div><div><strong>Service Areas</strong>'+''.join(a(r['url'],r['name']) for r in regions)+'</div><div><strong>Plan your pickup</strong>'+''.join(a(u,t) for u,t in [('/calculator.html','Pricing & Estimates'),('/schedule.html','Schedule Pickup'),('/contact.html','Contact Bryan'),('/account.html','Account & Rewards'),('/merch.html','Merch'),('/services/','All services')])+'</div></footer>'
    footer+='<nav class="mobile-contact" aria-label="Call or text Bryan">'+a('tel:+16263865623','Call Bryan')+a('sms:+16263865623','Text Photos')+'</nav>'
    return header+top, footer

def crumbs(items):
    return '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'+''.join('<li>'+ (a(u,n) if i<len(items)-1 else f'<span aria-current="page">{e(n)}</span>')+'</li>' for i,(n,u) in enumerate(items))+'</ol></nav>'

def metadata(path,title,description,indexable,breadcrumbs=None,service=None,location=None,region=None):
    business={'@type':'LocalBusiness','@id':BASE+'/#business','name':BRAND,'url':BASE+'/','telephone':'+1-626-386-5623','email':'bryanjunksitaway@gmail.com','logo':BASE+'/assets/logo.png','description':'Junk removal and hauling service based in Baldwin Park, California. We travel to customers throughout our listed Southern California service areas.','areaServed':[{'@type':'Place','name':r['name']} for r in regions]}
    graph=[business]
    if service:
        graph.append({'@type':'Service','@id':BASE+path+'#service','name':service['name']+((' in '+location['name']) if location else ''),'serviceType':service['name'],'url':BASE+path,'provider':{'@id':BASE+'/#business'},'areaServed':{'@type':'Place','name':location['name']} if location else [{'@type':'Place','name':r['name']} for r in regions]})
    if region:graph.append({'@type':'Service','@id':BASE+path+'#service','name':'Junk Removal in '+region['name'],'provider':{'@id':BASE+'/#business'},'areaServed':{'@type':'Place','name':region['name']},'url':BASE+path})
    if breadcrumbs:graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':BASE+url} for i,(name,url) in enumerate(breadcrumbs)]})
    return f'<title>{e(title)}</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{BASE+path}"><meta name="robots" content="'+('index,follow' if indexable else 'noindex,follow')+'">'+''.join(f'<meta property="{k}" content="{e(v)}">' for k,v in {'og:type':'website','og:title':title,'og:description':description,'og:url':BASE+path,'og:site_name':BRAND,'og:image':BASE+'/assets/logo.png','og:image:alt':'Bryan Junks It Away illustrated logo'}.items())+'<meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')+'</script>'

def write(path, body, title, description, indexable=True, breadcrumbs=None, service=None, location=None, region=None, legacy=None):
    head=metadata(path,title,description,indexable,breadcrumbs,service,location,region)
    header,footer=chrome(path)
    if legacy:
        doc=re.sub(r'<title>.*?</title>','',legacy,flags=re.S)
        doc=re.sub(r'<meta name="description"[^>]*>','',doc)
        doc=re.sub(r'<header>.*?</header>',lambda _:header,doc,flags=re.S)
        # Original area ribbon follows the header; the shared header supplies its replacement.
        doc=re.sub(r'(</div>)<div class="top-areas".*?</div>',r'\1',doc,count=1,flags=re.S)
        doc=re.sub(r'<footer>.*?</footer>',lambda _:footer,doc,flags=re.S)
        doc=doc.replace('<main>','<main id="main-content">').replace('<main id="main">','<main id="main-content">')
        doc=doc.replace('</head>',head+'<link rel="stylesheet" href="/expansion.css"></head>')
        doc=re.sub(r'((?:href|src)=")((?:assets/|styles.css|script.js|pricing.js|account.js|config.js)[^"]*)"',r'\1/\2"',doc)
        doc=doc.replace('href="index.html"','href="/"')
    else:
        doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101b16">'+head+'<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/expansion.css"><script src="/script.js" defer></script></head><body>'+header+'<main id="main-content">'+(crumbs(breadcrumbs) if breadcrumbs else '')+body+'</main>'+footer+'</body></html>'
    # Existing imagery stays intact; fixed dimensions reserve layout space.
    def image_attrs(m):
        tag=m.group(0)
        if 'width=' not in tag:tag=tag[:-1]+' width="1200" height="800">'
        if 'loading=' not in tag and 'logo.png' not in tag:tag=tag[:-1]+' loading="lazy" decoding="async">'
        return tag
    doc=re.sub(r'<img\b[^>]*>',image_attrs,doc)
    dest=OUT/(path.lstrip('/')+('index.html' if path.endswith('/') else ''))
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(doc)
    manifest.append({'path':path,'file':str(dest.relative_to(OUT)),'title':title,'description':description,'indexable':indexable,'service':service['slug'] if service else None,'location':location['slug'] if location else None,'reason':location['indexing_reason'] if location and not indexable else ('Utility or coming-soon page' if not indexable else '')})

def section(eyebrow,title,body,cls=''):
    return f'<section class="section {cls}"><div class="section-heading"><p class="eyebrow">{e(eyebrow)}</p><h2>{e(title)}</h2></div>{body}</section>'

def service_cards(items,location=None):
    return '<div class="service-grid service-cards">'+''.join('<article><span class="index">'+f'{i+1:02d}'+'</span><h3>'+a('/'+s['slug']+'/'+(location['slug']+'/' if location else ''),s['name'])+'</h3><p>'+e(s['description'])+'</p>'+a('/'+s['slug']+'/'+(location['slug']+'/' if location else ''),'Explore '+s['name'].lower()+' ↗','text-link')+'</article>' for i,s in enumerate(items))+'</div>'

def region_cards():
    return '<div class="region-grid">'+''.join('<a class="region-card" href="'+r['url']+'"><img src="'+REGIONAL[r['slug']][3]+'" alt="'+e(REGIONAL[r['slug']][4])+'"><span>'+e(r['name'])+'</span><small>'+str(len(r['locations']))+' listed pickup areas · Explore services</small></a>' for r in regions)+'</div>'

def faq(items):
    return section('GOOD TO KNOW','A few helpful answers.','<div class="faq-list">'+''.join('<details><summary>'+e(q)+'</summary><p>'+e(ans)+'</p></details>' for q,ans in items)+'</div>','faq-section')

def process(service=None):
    first=service['prepare'] if service else 'Send photos and your pickup location, or use the estimate form to describe the load. Include weight and access details.'
    return section('YOU POINT. WE HAUL. IT’S GONE.','How pickup works.','<div class="service-grid"><article><span class="index">01 / SHOW US</span><h3>Start with the details.</h3><p>'+e(first)+'</p>'+a('sms:+16263865623','Send photos by text ↗','text-link')+'</article><article><span class="index">02 / PLAN IT</span><h3>Choose your pickup.</h3><p>Review your starting estimate, then select a date and available arrival time. Booking is free, with no deposit.</p></article><article><span class="index">03 / MAKE ROOM</span><h3>Approve. Then it goes.</h3><p>We’ll call about 1–2 hours before the scheduled arrival. We review the actual load and access, agree on the final price with you, and then load and haul.</p></article></div>')

def closing(location=None):
    return '<section class="closing"><p class="eyebrow">THE GOOD KIND OF EMPTY.</p><h2>Make room for what’s next.</h2>'+actions(location)+a('sms:+16263865623','Prefer photos? Text Bryan at 626-386-5623','closing-text')+'</section>'

def directory(service):
    if not service['core']:
        return section('FIND YOUR PICKUP AREA','Explore our service regions.',region_cards())
    return section('FIND YOUR PICKUP AREA','One service. Across the places we serve.','<p class="section-lede">Choose a region, then your pickup location. These are service areas—not separate offices.</p><div class="region-directory">'+''.join('<details><summary>'+e(r['name'])+f'<span>{len(r["locations"])} areas</span></summary><ul class="location-links">'+''.join('<li>'+a('/'+service['slug']+'/'+slug+'/',L[slug]['name'])+'</li>' for slug in sorted(r['locations'],key=lambda x:L[x]['name']))+'</ul>'+a(r['url'],'Explore the '+r['name']+' hub ↗','text-link')+'</details>' for r in regions)+'</div>')

def service_page(s,loc=None):
    path='/'+s['slug']+'/'+(loc['slug']+'/' if loc else '')
    title=s['name']+(' in '+loc['name']+', CA' if loc else ' in Southern California')+' | '+BRAND
    h1=s['name']+' in '+loc['name']+', CA' if loc else s['name']+' in Southern California'
    intro=(f'Planning {s["name"].lower()} in {loc["name"]}? ' if loc else '')+s['intro']
    desc=(s['description']+' '+('Available in '+loc['name']+'. ' if loc else 'Serving Southern California. ')+('Starting at $'+str(s['starting'])+'. ' if s['starting'] else '')+'Ask Bryan for an estimate.')
    breadcrumbs=[('Home','/'),('Services','/services/'),(s['name'],'/'+s['slug']+'/')]+([(loc['name'],path)] if loc else [])
    body='<section class="page-intro service-intro"><p class="eyebrow">'+e('BRYAN JUNKS IT AWAY · '+(loc['name'] if loc else 'BASED IN BALDWIN PARK'))+'</p><h1>'+e(h1)+'</h1><p class="intro">'+e(s['headline'])+'</p><p class="section-lede">'+e(intro)+'</p>'+actions(loc)+'</section>'
    body+=section('WHAT WE HAUL',s['intent'],'<div class="editorial-grid"><div><p>'+e(s['explanation'])+'</p><ul class="item-list">'+''.join('<li>'+e(i)+'</li>' for i in s['items'])+'</ul></div><aside class="pickup-note"><span class="eyebrow">A BETTER STARTING ESTIMATE</span><h3>Show us the route out.</h3><p>'+e(s['access'])+'</p>'+a('sms:+16263865623','Text photos of your pickup ↗','text-link')+'</aside></div>')
    body+=section('CLEAR PRICING',('Starting at $'+str(s['starting'])+'.' if s['starting'] else 'A quote for the actual materials.'),'<div class="pricing-callout"><p>'+e(s['pricing'])+'</p><p>Quantity, volume, weight, stairs, long carries, tight access, and disassembly can affect your price. Heavy materials and special-disposal items are quoted separately. You approve the final price in person before work begins.</p>'+a('/calculator.html','See the full pricing guide ↗','text-link')+'</div>')
    body+=process(s)
    if loc:
        membership=' and '.join(a(R[r]['url'],R[r]['name']) for r in loc['regions'])
        body+=section('YOUR PICKUP LOCATION','Serving '+loc['name']+'.','<div class="editorial-grid"><div><p>'+BRAND+' is one service-area business based in Baldwin Park. We come to your pickup address in '+e(loc['name'])+'; this is not a separate storefront.</p><p>You can find this area in our '+membership+' service '+('directories' if len(loc['regions'])>1 else 'directory')+'. These are our service groupings, rather than statements about municipal boundaries.</p></div><div class="pickup-note"><h3>Help us plan your visit.</h3><p>When you book, provide the full pickup address and describe where the items are. Mention stairs, parking access, and any arrangements needed to reach the load.</p>'+a('/contact.html','Talk through the details ↗','text-link')+'</div></div>')
        if s['slug']=='junk-removal':related=[x for x in CORE if x!=s]
        else:related=[S[k] for k in s['related'] if S[k]['core']]+([S['junk-removal']] if 'junk-removal' not in s['related'] else [])
        body+=section('MORE WAYS TO MAKE ROOM','Other services in '+loc['name'],service_cards(related,loc))
        if loc['nearby']:
            body+=section('AROUND YOUR AREA','Nearby pickup locations.','<ul class="nearby-links">'+''.join('<li>'+a('/'+s['slug']+'/'+n+'/',L[n]['name'])+'</li>' for n in loc['nearby'])+'</ul>','compact-section')
    else:
        body+=section('MAKE ONE PLAN','Related services.',service_cards([S[k] for k in s['related']]))
        body+=directory(s)
        body+='<figure class="brand-figure"><img src="/assets/logo.png" width="1389" height="1141" loading="lazy" alt="Bryan Junks It Away illustrated mascot with furniture and a junk truck"><figcaption>Big or small, Bryan junks it all away.</figcaption></figure>'
    body+=faq(s['faqs'])+closing(loc)
    write(path,body,title,desc,indexable=loc['indexable'] if loc else True,breadcrumbs=breadcrumbs,service=s,location=loc)

def regional_page(r):
    strap,intro,heading,img,alt=REGIONAL[r['slug']]
    body='<section class="page-intro"><p class="eyebrow">BRYAN JUNKS IT AWAY · BASED IN BALDWIN PARK</p><h1>Junk Removal in<br><em>'+e(r['name'])+'.</em></h1><p class="section-lede">'+e(strap)+'</p>'+actions()+'</section>'
    links='<ul class="location-links">'+''.join('<li>'+a('/junk-removal/'+k+'/',L[k]['name'])+'</li>' for k in sorted(r['locations'],key=lambda k:L[k]['name']))+'</ul>'
    body+='<section class="section local"><div><img class="area-photo" src="'+img+'" alt="'+e(alt)+'"><h2>'+e(heading)+'</h2><p>'+e(intro)+'</p></div><div class="area"><p class="eyebrow">FIND YOUR PICKUP AREA</p><h2>See where we can help.</h2><p>Choose a listed location for services and pickup details. Not sure which area to use? Send Bryan your location.</p><button class="button city-toggle" type="button" aria-expanded="false" aria-controls="cities">See areas we serve ↗</button><details id="cities"><summary>Pickup areas</summary><div class="city-list">'+links+'</div></details><noscript><style>#cities>summary{display:list-item}</style></noscript></div></section>'
    body+=section('LESS JUNK. MORE POSSIBILITY.','Services for the job you have.',service_cards(CORE))
    body+=section('STRAIGHTFORWARD JUNK REMOVAL PRICING','A starting estimate. A price you approve.','<p class="section-lede">Small pickups start at $95. The number and size of items, their weight, and the work to reach the truck shape your estimate. Larger room or whole-home cleanouts need a closer look. The same pricing guide applies across our listed areas.</p>'+actions())
    body+=process()+faq([('Does every area have its own office?','No. Bryan Junks It Away is one service-area business based in Baldwin Park. We travel to the listed pickup locations.'),('How do I get a quote for this area?','Send your location, photos, and access details, or use the online estimate form. We confirm the final price in person before work begins.'),('Do you handle both small pickups and cleanouts?','Yes. Choose the service that matches the items you want removed, from a single item to a whole-property cleanout.')])+closing()
    body=body.replace('href="/schedule.html"','href="/schedule.html?'+e(urlencode({'area':r['name']}))+'"')
    desc='Explore '+r['name']+' pickup areas for junk removal, furniture hauling, and cleanouts. See starting prices and plan your pickup with Bryan.'
    write(r['url'],body,'Junk Removal in '+r['name']+' | '+BRAND,desc,breadcrumbs=[('Home','/'),('Service Areas','/service-areas/'),(r['name'],r['url'])],region=r)

def legacy_pages():
    for source in ROOT.glob('*.html'):
        if source.stem in R:continue
        path='/' if source.name=='index.html' else '/'+source.name
        doc=source.read_text()
        title=html.unescape(re.search(r'<title>(.*?)</title>',doc).group(1))
        desc={'schedule.html':'Choose a pickup date and available arrival time, review your details, and reserve junk removal with Bryan Junks It Away.', 'confirmation.html':'Review your Bryan Junks It Away reservation details and the next steps for your scheduled pickup.', 'estimate-survey.html':'Describe your items, load size, and access to get a personal starting estimate for junk removal with Bryan Junks It Away.'}.get(source.name,'Contact Bryan Junks It Away for pickup help.')
        m=re.search(r'<meta name="description" content="([^"]*)"',doc)
        if m:desc=html.unescape(m[1])
        indexable=source.name in ['index.html','calculator.html','contact.html']
        if source.name=='index.html':
            title='Junk Removal & Hauling in Southern California | '+BRAND
            desc='Based in Baldwin Park, Bryan Junks It Away handles furniture, bulky items, and cleanouts across Southern California. Get an estimate and make room for what matters.'
            doc=doc.replace('LOCAL HAULING. A FRESH START.','JUNK REMOVAL &amp; HAULING ACROSS SOUTHERN CALIFORNIA')
            doc=doc.replace('From one item to a full cleanout, we clear the mess so you can enjoy your space again.','Based in Baldwin Park. Serving San Gabriel Valley, Los Angeles, San Fernando Valley, Inland Empire, Riverside County, and Orange County—from single items to full cleanouts.')
            doc=doc.replace('Your area.<br>Your clean slate.','Junk Removal Across<br>Southern California')
            doc=doc.replace('Choose your city below for local service details, nearby neighborhoods, and a faster way to get your junk gone.','Find your pickup area, explore our services, and make a plan for the space you want back.')
            doc=doc.replace('A starting estimate.<br>A price you agree to.','Simple Junk Removal Pricing')
            doc=doc.replace('Take back your space.<br>Feel the difference.','Junk Removal &amp;<br>Cleanout Services')
            doc=doc.replace('Try the calculator ↗','See pricing & estimates ↗')
            doc=doc.replace('SGV · LA · IE · Riverside · OC','SGV · LA · SFV · IE · Riverside County · OC')
            doc=doc.replace('<span>Riverside</span>','<span>Riverside County</span>')
            doc=doc.replace('<section class="closing">',section('FIND THE RIGHT FIT','You point. We haul. It’s gone.','<div class="hero-booking-actions">'+a('/services/','Explore services ↗','button')+a('/service-areas/','Find your service area ↗','button secondary-button')+'</div>')+'<section class="closing">')
        elif source.name=='calculator.html':
            title='Junk Removal Pricing & Estimates | '+BRAND
            desc='See current junk removal load ranges from $95, what affects your price, and how to get a personal pickup estimate from Bryan Junks It Away.'
            doc=doc.replace('See what shapes<br><em>your price.</em>','Junk Removal Pricing<br><em>&amp; Estimates.</em>').replace('Simple load pricing.','Junk Removal Pricing by Load Size')
            doc=doc.replace('<div class="pricing-row"><span>Small garage','<div class="pricing-row"><span>Small household or yard pile</span><span>⅛ truck</span><strong>$180–$290</strong></div><div class="pricing-row"><span>Small garage')
            doc=doc.replace('Most estimates land close to the final price, but the actual amount can be a little lower or higher once we see the items and access in person.','Your final price depends on the actual items and access we review in person.')
            labels=[('single','One small item','Single item'),('few','A few unwanted items','Few items'),('eighth','Small household or yard pile','⅛ truck'),('quarter','Small garage or room cleanout','¼ truck'),('half','Bedroom set or moderate cleanout','½ truck'),('threequarters','Large garage or multi-room load','¾ truck'),('full','Full truck of cleanout contents','Full truck cleanout')]
            table='<div class="pricing-table"><div class="pricing-row pricing-head"><b>Common job</b><b>Typical load</b><b>Starting range</b></div>'+''.join('<div class="pricing-row"><span>'+job+'</span><span>'+label+'</span><strong>$'+str(LOAD_BANDS[key][0])+'–$'+str(LOAD_BANDS[key][1])+('+' if key=='full' else '')+'</strong></div>' for key,job,label in labels)+'</div></section>'
            doc=re.sub(r'<div class="pricing-table">.*?</section>',lambda _:table,doc,count=1,flags=re.S)
            doc=doc.replace('</main>',section('ONE FRAMEWORK ACROSS OUR SERVICE AREA','Starting prices by service.','<div class="service-price-list">'+''.join('<p><strong>'+a('/'+s['slug']+'/',s['name'])+'</strong><span>'+('Starting at $'+str(s['starting']) if s['starting'] else 'Quoted separately')+'</span></p>' for s in services)+'</div><p>These are starting points, not flat prices. Whole studio / one-bedroom cleanouts start at $635; large or multi-load jobs need an in-person assessment.</p>')+'</main>')
        write(path,'',title,desc,indexable=indexable,legacy=doc)

def build():
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'assets',OUT/'assets')
    for name in ['styles.css','expansion.css','script.js','booking.js','account.js','pricing.js','config.js']:
        shutil.copy2(ROOT/name,OUT/name)
    legacy_pages()
    for r in regions:regional_page(r)
    body='<section class="page-intro service-intro"><p class="eyebrow">THE GOOD KIND OF EMPTY.</p><h1>Junk Removal &amp;<br><em>Cleanout Services</em></h1><p class="section-lede">One unwanted couch or a whole place to clear? Start with what you need gone. We’re based in Baldwin Park and travel throughout our listed Southern California service areas.</p>'+actions()+'</section>'
    body+=section('MAKE ROOM FOR WHAT MATTERS MOST.','Find the right kind of help.',service_cards(CORE))
    body+=section('MORE WAYS WE CAN HELP','Beyond the living room.',service_cards([s for s in services if not s['core']]))+process()+closing()
    write('/services/',body,'Junk Removal & Cleanout Services | '+BRAND,'Explore furniture, couch, mattress, appliance, garage, move-out, and property cleanout services. Find the right pickup and get a starting estimate.',breadcrumbs=[('Home','/'),('Services','/services/')])
    body='<section class="page-intro service-intro"><p class="eyebrow">BASED IN BALDWIN PARK. WE COME TO YOU.</p><h1>Junk Removal<br><em>Service Areas</em></h1><p class="section-lede">Find your region, then your pickup area. One local service-area business, with a simple way to plan removal across Southern California.</p>'+actions()+'</section>'+section('FIND YOUR NEIGHBORHOOD','Where can we help?',region_cards())+section('NOT SURE WHERE TO START?','Send us your location.','<p class="section-lede">Our directories include cities, neighborhoods, and communities. If you don’t see the name you use for your area, contact Bryan with the pickup location so we can check the fit before you plan a visit.</p>'+a('/contact.html','Check my pickup area ↗','button'))
    write('/service-areas/',body,'Southern California Junk Removal Service Areas | '+BRAND,'Based in Baldwin Park, serving SGV, Los Angeles, SFV, Inland Empire, Riverside County, and Orange County. Find your pickup area and explore services.',breadcrumbs=[('Home','/'),('Service Areas','/service-areas/')])
    for s in services:
        service_page(s)
        if s['core']:
            for loc in locations:service_page(s,loc)
    for group,rows in [('pages',[p for p in manifest if p['indexable'] and not p['service']]),('services',[p for p in manifest if p['indexable'] and p['service']])]:
        (OUT/f'sitemap-{group}.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+p['path']+'</loc></url>' for p in rows)+'</urlset>')
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<sitemap><loc>'+BASE+'/sitemap-'+g+'.xml</loc></sitemap>' for g in ['pages','services'])+'</sitemapindex>')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
    (ROOT/'site-tools/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Built {len(manifest)} pages: {sum(p["indexable"] for p in manifest)} indexable; {sum(not p["indexable"] for p in manifest)} noindex.')

if __name__=='__main__':build()

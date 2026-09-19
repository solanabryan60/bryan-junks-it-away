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
local_guides = json.loads((CONTENT / 'local-guides.json').read_text())
S = {x['slug']: x for x in services}
R = {x['slug']: x for x in regions}
L = {x['slug']: x for x in locations}
CORE = [x for x in services if x['core']]
LOAD_BANDS = {key:(int(low),int(high)) for key,low,high in re.findall(r'(\w+):\[(\d+),(\d+)\]',(ROOT/'pricing.js').read_text())}
manifest = []
MAPS = 'https://www.google.com/maps?cid=8312459433107439370'
CONTENT_REVIEWED = '2026-09-18'
e = lambda text: html.escape(str(text), quote=True)

REGIONAL = {
 'san-gabriel-valley': ('From our Baldwin Park base.', 'Baldwin Park is our home base, and the San Gabriel Valley is part of our service territory. Choose your area below for furniture pickup, mixed household junk, or a larger cleanout. We come to you and take care of the lifting, loading, and hauling.', 'Junk Removal & Cleanouts Across the San Gabriel Valley', 'https://upload.wikimedia.org/wikipedia/commons/e/e4/Pasadena_City_Hall_David_Wakely.jpg', 'Pasadena City Hall'),
 'los-angeles': ('Find your part of LA.', 'An old couch, a pile of boxes, or a room you want back—we help clear it out. Find your Los Angeles pickup area below, tell us what needs to go, and get a plan that fits your job.', 'Junk Removal, Furniture Hauling & Cleanouts in Los Angeles', 'https://upload.wikimedia.org/wikipedia/commons/2/2d/Los_Angeles_skyline.jpg', 'Los Angeles skyline'),
 'san-fernando-valley': ('Less in the way. More room to live.', 'From a sofa pickup to a garage clear-out, use our San Fernando Valley directory to find the right service for your area. We help with single items, mixed loads, and bigger cleanouts. Tell us the actual address and access details when you request an estimate.', 'Junk Removal & Hauling Across the San Fernando Valley', '/assets/sfv-studio-city.jpg', 'Palm-lined street in Studio City'),
 'inland-empire': ('A clear plan for the whole load.', 'Explore our Inland Empire service coverage for unwanted furniture, household junk, and cleanouts. From a small pickup to a larger cleanout, we make it easier to reclaim your space. Share the amount and type of junk so we can plan around the real load.', 'Junk Removal & Hauling Across the Inland Empire', '/assets/inland-empire-landscape.jpg', 'Cityscape, palms, and mountains in the Inland Empire'),
 'riverside': ('From leftover items to a bigger reset.', 'Our Riverside County directory covers the listed pickup areas, including Riverside itself. Choose your community to explore single-item removal, furniture hauling, or a whole-property cleanout. We handle the lifting and hauling so you can focus on what comes next.', 'Junk Removal & Cleanout Services in Riverside County', 'https://upload.wikimedia.org/wikipedia/commons/c/ce/Courtyard_of_Mission_Inn_with_Church_-_Riverside,_CA_-_USA_-_01_%286919712685%29.jpg', 'Courtyard and church at the Mission Inn in Riverside'),
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
    footer = '<footer class="site-footer"><div>'+a('/','BRYAN','wordmark').replace('BRYAN</a>','BRYAN<span>JUNKS IT AWAY</span></a>')+'<p>Big or small, we haul it all.</p><p>Based in Baldwin Park.<br>We come to you.</p><p>Open 24 hours · Pickup times subject to availability.</p>'+a('tel:+16263865623','626-386-5623')+a('mailto:bryanjunksitaway@gmail.com','bryanjunksitaway@gmail.com')+'</div><div><strong>Services</strong>'+''.join(a('/'+s['slug']+'/',s['name']) for s in CORE)+'</div><div><strong>Service Areas</strong>'+''.join(a(r['url'],r['name']) for r in regions)+'</div><div><strong>Plan your pickup</strong>'+''.join(a(u,t) for u,t in [('/calculator.html','Pricing & Estimates'),('/schedule.html','Schedule Pickup'),('/contact.html','Contact us'),('/account.html','Account & Rewards'),('/merch.html','Merch'),('/services/','All services'),('/junk-removal-questions/','Pickup questions & answers')])+'</div></footer>'
    footer+='<nav class="mobile-contact" aria-label="Call or text us">'+a('tel:+16263865623','Call us')+a('sms:+16263865623','Text Photos')+'</nav>'
    return header+top, footer

def crumbs(items):
    return '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'+''.join('<li>'+ (a(u,n) if i<len(items)-1 else f'<span aria-current="page">{e(n)}</span>')+'</li>' for i,(n,u) in enumerate(items))+'</ol></nav>'

def metadata(path,title,description,indexable,breadcrumbs=None,service=None,location=None,region=None):
    business={'@type':'LocalBusiness','@id':BASE+'/#business','name':BRAND,'url':BASE+'/','telephone':'+1-626-386-5623','email':'bryanjunksitaway@gmail.com','logo':BASE+'/assets/logo.png','description':'Junk removal and hauling service based in Baldwin Park, California. We travel to customers throughout our listed Southern California service areas.','areaServed':[{'@type':'Place','name':r['name']} for r in regions]}
    business.update({'sameAs':[MAPS], 'openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],'opens':'00:00','closes':'23:59'}]})
    graph=[business, {'@type':'WebSite','@id':BASE+'/#website','url':BASE+'/','name':BRAND,'publisher':{'@id':BASE+'/#business'},'inLanguage':'en-US'}, {'@type':'WebPage','@id':BASE+path+'#webpage','url':BASE+path,'name':title,'description':description,'isPartOf':{'@id':BASE+'/#website'},'about':{'@id':BASE+'/#business'},'inLanguage':'en-US'}]
    if service:
        graph.append({'@type':'Service','@id':BASE+path+'#service','name':service['name']+((' in '+location['name']) if location else ''),'serviceType':service['name'],'url':BASE+path,'provider':{'@id':BASE+'/#business'},'areaServed':{'@type':'Place','name':location['name']} if location else [{'@type':'Place','name':r['name']} for r in regions]})
    if region:graph.append({'@type':'Service','@id':BASE+path+'#service','name':'Junk Removal in '+region['name'],'provider':{'@id':BASE+'/#business'},'areaServed':{'@type':'Place','name':region['name']},'url':BASE+path})
    if breadcrumbs:graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':BASE+url} for i,(name,url) in enumerate(breadcrumbs)]})
    return f'<title>{e(title)}</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{BASE+path}"><meta name="robots" content="'+('index,follow,max-image-preview:large' if indexable else 'noindex,follow')+'">'+''.join(f'<meta property="{k}" content="{e(v)}">' for k,v in {'og:type':'website','og:title':title,'og:description':description,'og:url':BASE+path,'og:site_name':BRAND,'og:image':BASE+'/assets/logo.png','og:image:alt':'Bryan Junks It Away illustrated logo'}.items())+'<meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')+'</script>'

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
    # Schema describes the visible dedicated answer guide, not invented ratings or offers.
    if path == '/junk-removal-questions/':
        answers = re.findall(r'<details id="answer-\d+"><summary>(.*?)</summary><p>(.*?)</p></details>', doc, re.S)
        schema = {'@context':'https://schema.org','@type':'FAQPage','@id':BASE+path+'#answers','mainEntity':[{'@type':'Question','name':html.unescape(q),'acceptedAnswer':{'@type':'Answer','text':html.unescape(ans)}} for q,ans in answers]}
        doc = doc.replace('</head>', '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
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
    return section('GOOD TO KNOW','A few helpful answers.','<div class="faq-list">'+''.join('<details id="answer-'+str(i+1)+'"><summary>'+e(q)+'</summary><p>'+e(ans)+'</p></details>' for i,(q,ans) in enumerate(items))+'</div>','faq-section')

def process(service=None):
    first=service['prepare'] if service else 'Send photos and your pickup location, or use the estimate form to describe the load. Include weight and access details.'
    return section('YOU POINT. WE HAUL. IT’S GONE.','How pickup works.','<div class="service-grid"><article><span class="index">01 / SHOW US</span><h3>Start with the details.</h3><p>'+e(first)+'</p>'+a('sms:+16263865623','Send photos by text ↗','text-link')+'</article><article><span class="index">02 / PLAN IT</span><h3>Choose your pickup.</h3><p>Review your starting estimate, then select a date and available arrival time. Booking is free, with no deposit.</p></article><article><span class="index">03 / MAKE ROOM</span><h3>Approve. Then it goes.</h3><p>We’ll call about 1–2 hours before the scheduled arrival. We’ll confirm the final price with you in person or contact you and send an invoice for your approval before work begins. Once you approve, we load and haul.</p></article></div>')

def closing(location=None):
    return '<section class="closing"><p class="eyebrow">THE GOOD KIND OF EMPTY.</p><h2>Make room for what’s next.</h2>'+actions(location)+a('sms:+16263865623','Prefer photos? Text us at 626-386-5623','closing-text')+'</section>'

def directory(service):
    if not service['core']:
        return section('FIND YOUR PICKUP AREA','Explore our service regions.',region_cards())
    return section('FIND YOUR PICKUP AREA','One service. Across the places we serve.','<p class="section-lede">Choose a region, then your pickup location. Tell us where you need a pickup, and we’ll help you make room.</p><div class="region-directory">'+''.join('<details><summary>'+e(r['name'])+f'<span>{len(r["locations"])} areas</span></summary><ul class="location-links">'+''.join('<li>'+a('/'+service['slug']+'/'+slug+'/',L[slug]['name'])+'</li>' for slug in sorted(r['locations'],key=lambda x:L[x]['name']))+'</ul>'+a(r['url'],'More pickup options in '+r['name']+' ↗','text-link')+'</details>' for r in regions)+'</div>')

def service_page(s,loc=None):
    if loc and s['slug']=='junk-removal':
        return location_page(loc)
    path='/'+s['slug']+'/'+(loc['slug']+'/' if loc else '')
    title=s['name']+(' in '+loc['name']+', CA' if loc else ' in Southern California')+' | '+BRAND
    h1=s['name']+' in '+loc['name']+', CA' if loc else s['name']+' in Southern California'
    intro=(f'Planning {s["name"].lower()} in {loc["name"]}? ' if loc else '')+s['intro']
    desc=(s['description']+' '+('Available in '+loc['name']+'. ' if loc else 'Serving Southern California. ')+('Starting at $'+str(s['starting'])+'. ' if s['starting'] else '')+'Ask us for an estimate.')
    breadcrumbs=[('Home','/'),('Services','/services/'),(s['name'],'/'+s['slug']+'/')]+([(loc['name'],path)] if loc else [])
    body='<section class="page-intro service-intro"><p class="eyebrow">'+e('BRYAN JUNKS IT AWAY · '+(loc['name'] if loc else 'BASED IN BALDWIN PARK'))+'</p><h1>'+e(h1)+'</h1><p class="intro">'+e(s['headline'])+'</p><p class="section-lede">'+e(intro)+'</p>'+actions(loc)+'</section>'
    body+=section('WHAT WE HAUL',s['intent'],'<div class="editorial-grid"><div><p>'+e(s['explanation'])+'</p><ul class="item-list">'+''.join('<li>'+e(i)+'</li>' for i in s['items'])+'</ul></div><aside class="pickup-note"><span class="eyebrow">A BETTER STARTING ESTIMATE</span><h3>Show us the route out.</h3><p>'+e(s['access'])+'</p>'+a('sms:+16263865623','Text photos of your pickup ↗','text-link')+'</aside></div>')
    body+=section('CLEAR PRICING',('Starting at $'+str(s['starting'])+'.' if s['starting'] else 'A quote for the actual materials.'),'<div class="pricing-callout"><p>'+e(s['pricing'])+'</p><p>Quantity, volume, weight, stairs, long carries, tight access, and disassembly can affect your price. Heavy materials and special-disposal items are quoted separately. We’ll confirm the final price with you in person or contact you and send an invoice for your approval before work begins.</p>'+a('/calculator.html','See the full pricing guide ↗','text-link')+'</div>')
    body+=section('QUICK PICKUP GUIDE','What to know before booking '+s['name'].lower()+'.','<p>'+e(s['pricing'])+'</p><p>'+e(s['prepare'])+'</p>'+a('/junk-removal-questions/','Pickup, pricing, and booking answers ↗','text-link'))
    body+=process(s)
    if loc:
        membership=' and '.join(a(R[r]['url'],R[r]['name']) for r in loc['regions'])
        body+=section('YOUR PICKUP LOCATION','A little more room in '+loc['name']+'.','<div class="editorial-grid"><div><p>From the items you have been putting off to a space ready for a fresh start, we bring '+e(s['name'].lower())+' right to your door in '+e(loc['name'])+'. Tell us what needs to go, and we’ll help you plan the pickup.</p><p>Need help at another address? We also serve nearby communities across '+membership+'.</p></div><div class="pickup-note"><h3>You point. We take it from there.</h3><p>Share your item list, a few photos, and any stairs or access details. We’ll review the job with you and make sure you approve the price before we start.</p>'+a('/contact.html','Talk with our team ↗','text-link')+'</div></div>')
        if s['slug']=='junk-removal':related=[x for x in CORE if x!=s]
        else:related=[S[k] for k in s['related'] if S[k]['core']]+([S['junk-removal']] if 'junk-removal' not in s['related'] else [])
        body+=section('MORE WAYS TO MAKE ROOM','Other services in '+loc['name'],service_cards(related,loc))
        if loc['nearby']:
            body+=section('AROUND YOUR AREA','Nearby pickup locations.','<ul class="nearby-links">'+''.join('<li>'+a('/'+s['slug']+'/'+n+'/',L[n]['name'])+'</li>' for n in loc['nearby'])+'</ul>','compact-section')
    else:
        body+=section('MAKE ONE PLAN','Related services.',service_cards([S[k] for k in s['related']]))
        body+=directory(s)
        body+='<figure class="brand-figure"><img src="/assets/logo.png" width="1389" height="1141" loading="lazy" alt="Bryan Junks It Away illustrated mascot with furniture and a junk truck"><figcaption>Big or small, we haul it all.</figcaption></figure>'
    body+=faq(s['faqs'])+closing(loc)
    write(path,body,title,desc,indexable=True,breadcrumbs=breadcrumbs,service=s,location=loc)

def location_page(loc):
    """Complete local landing page alongside indexed service-specific pages."""
    name=loc['name']; path='/junk-removal/'+loc['slug']+'/'
    guide=local_guides['locations'][loc['slug']]
    resource=local_guides['resources'][guide['resource']]
    membership=' and '.join(a(R[r]['url'],R[r]['name']) for r in loc['regions'])
    nearby=', '.join(a('/junk-removal/'+slug+'/',L[slug]['name']) for slug in loc['nearby'])
    body='<section class="page-intro service-intro"><p class="eyebrow">WE COME TO YOU · '+e(name.upper())+'</p><h1>Junk Removal &amp; Cleanouts<br>in '+e(name)+', CA</h1><p class="intro">Make Room For What Matters Most.</p><p class="section-lede">An old sofa, a garage full of boxes, or a whole space ready for a fresh start—we handle the lifting, loading, and hauling in '+e(name)+'. Small pickups start at $95. Tell us what needs to go, get a personal estimate, and approve the price before we begin.</p>'+actions(loc)+'</section>'
    body+='<nav class="nearby-links local-jump" aria-label="On this page">'+''.join(a('#'+slug,label) for slug,label in [('pickup-services','What we take'),('pickup-prices','Pricing'),('pickup-plan','Plan your pickup'),('local-options','Local disposal options')])+'</nav>'
    body+=section('YOUR LOCAL PICKUP','Removal at your address in '+name+'.','<div class="editorial-grid"><div><p>'+e(guide['intro'])+'</p><p>Our team travels from Baldwin Park to your pickup address. '+('We also serve '+nearby+'.' if nearby else '')+'</p><p>Explore more pickup areas across '+membership+'.</p></div><aside class="pickup-note"><h3>A clear plan before we arrive.</h3><p>Share the items, your address, and the route to the truck. Choose from the available pickup times when you book. We’ll call about 1–2 hours before the scheduled arrival to confirm our arrival.</p>'+a('/schedule.html?'+urlencode({'city':name,'area':R[loc['regions'][0]]['name']}),'Check pickup times in '+name+' ↗','text-link')+'</aside></div>')
    cards=''
    for s in services:
        target='/'+s['slug']+'/'+(loc['slug']+'/' if s['core'] and s['slug']!='junk-removal' else '')
        cards+='<article><h3>'+a(target,s['name'])+'</h3><p>'+e(s['description'])+'</p><p class="fine">'+('From $'+str(s['starting'])+' · Depends on items and access' if s['starting'] else 'Material-specific quote')+'</p></article>'
    body+='<div id="pickup-services">'+section('ONE ITEM OR A BIGGER RESET','What can we remove in '+name+'?','<div class="service-grid service-cards">'+cards+'</div><p>Tell us about mixed loads together so we can estimate the whole pickup. Paint, chemicals, unknown materials, and unusually heavy items need a separate review before acceptance.</p>')+'</div>'
    rows=[('single','Single item'),('few','A few items'),('eighth','⅛ truck'),('quarter','¼ truck'),('half','½ truck'),('threequarters','¾ truck'),('full','Full truck')]
    pricing='<div class="service-price-list">'+''.join('<p><strong>'+label+'</strong><span>$'+str(LOAD_BANDS[key][0])+'–$'+str(LOAD_BANDS[key][1])+('+' if key=='full' else '')+'</span></p>' for key,label in rows)+'</div>'
    body+='<div id="pickup-prices">'+section('KNOW WHAT SHAPES YOUR PRICE','Junk removal pricing in '+name+'.','<div class="editorial-grid"><div>'+pricing+'</div><aside class="pickup-note"><h3>Your items set the starting point.</h3><p>These household-load ranges use the same pricing guide across our listed areas. Two lightweight wooden chairs with straightforward access can qualify for the $95 minimum. A couch, sleeper sofa, and sectional can take different amounts of space and handling.</p><p>Whole studio or one-bedroom cleanouts start at $635. That is a whole-cleanout starting point, not the price for a few leftover items. Dense construction debris and special-disposal materials need their own quote.</p></aside></div><p>Stairs, long carries, weight, and disassembly affect the estimate. We’ll confirm the final price with you in person or contact you and send an invoice for your approval before work begins.</p>'+actions(loc))+'</div>'
    body+='<div id="pickup-plan">'+section('A SMOOTHER PICKUP','Before your '+name+' pickup.','<div class="service-grid"><article><h3>Show everything that is going.</h3><p>Send wide photos and an item list. Mark what stays, include items behind the first row, and describe unusually heavy pieces. For a cleanout, show each room rather than only the front door.</p></article><article><h3>Plan the route out.</h3><p>'+e(guide['access'])+'</p></article><article><h3>Keep the details together.</h3><p>Review your name, contact details, pickup address, items, and chosen time before confirming. Use your confirmation number when sending photos or asking to update or cancel your reservation.</p></article></div>')+'</div>'
    local='<div class="editorial-grid"><div><h3>Check your existing collection service.</h3><p>'+e(guide.get('collection_note','Your regular trash provider may offer scheduled bulky-item collection. Ask about eligibility, item limits, placement, and dates for your exact address before putting anything out.'))+'</p>'
    if guide.get('collection_url'):local+=a(guide['collection_url'],guide['collection_label']+' ↗','text-link')
    local+='<p>Need help carrying items out or clearing a mixed load? Our paid pickup service includes lifting and loading, with the scope and price agreed before work starts.</p></div><aside class="pickup-note"><h3>Set special materials aside.</h3><p>'+e(resource['description'])+'</p>'+a(resource['url'],resource['label']+' ↗','text-link')+'<p class="fine">These are public programs, separate from our service. Check current eligibility and accepted materials with the program. Resident drop-off rules do not automatically cover commercial hauling.</p></aside></div>'
    body+='<div id="local-options">'+section('CHOOSE WHAT WORKS FOR YOUR ITEMS','Pickup and disposal options for '+name+'.',local)+'</div>'
    body+=faq([('Can you pick up just one item in '+name+'?','Yes. Small, straightforward pickups start at $95. Tell us the item, its size and weight, and access so we can calculate an estimate for the actual work.'),('Do I need to bring everything outside?','No. We can discuss indoor, garage, upstairs, and backyard pickups. Include the route to the truck and any stairs, gates, or disassembly in your estimate request.'),('How do I find an available pickup date?','Use Schedule Pickup to check available dates and times, then review your details before confirming. We do not promise same-day service or a particular time until availability is checked.'),('Can I combine furniture and other junk?','Yes. Describe the combined load in one request. Identify appliances, construction debris, and special materials separately so we can review handling and acceptance.'),('Is my estimate the final price?','It is a starting estimate based on your answers. We’ll confirm the final price in person or contact you and send an invoice for your approval before work begins.')])+closing(loc)
    write(path,body,'Junk Removal & Cleanouts in '+name+', CA | '+BRAND,'Junk removal in '+name+' from $95 for small pickups. Compare load pricing, furniture removal and cleanouts, local disposal options, and book a pickup.',indexable=True,breadcrumbs=[('Home','/'),('Service Areas','/service-areas/'),(R[loc['regions'][0]]['name'],R[loc['regions'][0]]['url']),(name,path)],service=S['junk-removal'],location=loc)

def regional_page(r):
    strap,intro,heading,img,alt=REGIONAL[r['slug']]
    body='<section class="page-intro"><p class="eyebrow">BRYAN JUNKS IT AWAY · BASED IN BALDWIN PARK</p><h1>Junk Removal in<br><em>'+e(r['name'])+'.</em></h1><p class="section-lede">'+e(strap)+'</p>'+actions()+'</section>'
    links='<ul class="location-links">'+''.join('<li>'+a('/junk-removal/'+k+'/',L[k]['name'])+'</li>' for k in sorted(r['locations'],key=lambda k:L[k]['name']))+'</ul>'
    body+='<section class="section local"><div><img class="area-photo" src="'+img+'" alt="'+e(alt)+'"><h2>'+e(heading)+'</h2><p>'+e(intro)+'</p></div><div class="area"><p class="eyebrow">FIND YOUR PICKUP AREA</p><h2>See where we can help.</h2><p>Choose a listed location for services and pickup details. Not sure which area to use? Send us your location.</p><button class="button city-toggle" type="button" aria-expanded="false" aria-controls="cities">See areas we serve ↗</button><details id="cities"><summary>Pickup areas</summary><div class="city-list">'+links+'</div></details><noscript><style>#cities>summary{display:list-item}</style></noscript></div></section>'
    body+=section('LESS JUNK. MORE POSSIBILITY.','Services for the job you have.',service_cards(CORE))
    body+=section('STRAIGHTFORWARD JUNK REMOVAL PRICING','A starting estimate. A price you approve.','<p class="section-lede">Small pickups start at $95. The number and size of items, their weight, and the work to reach the truck shape your estimate. Larger room or whole-home cleanouts need a closer look. The same pricing guide applies across our listed areas.</p>'+actions())
    body+=process()+faq([('Do you come to my address?','Yes. We bring our pickup service to your home, apartment, storage unit, or business in the listed service areas. Share your address and access details when you book.'),('How do I get a quote for this area?','Send your location, photos, and access details, or use the online estimate form. We’ll confirm the final price with you in person or contact you and send an invoice for your approval before work begins.'),('Do you handle both small pickups and cleanouts?','Yes. Choose the service that matches the items you want removed, from a single item to a whole-property cleanout.')])+closing()
    body=body.replace('href="/schedule.html"','href="/schedule.html?'+e(urlencode({'area':r['name']}))+'"')
    desc='Explore '+r['name']+' pickup areas for junk removal, furniture hauling, and cleanouts. See starting prices and plan your pickup with our team.'
    write(r['url'],body,'Junk Removal in '+r['name']+' | '+BRAND,desc,breadcrumbs=[('Home','/'),('Service Areas','/service-areas/'),(r['name'],r['url'])],region=r)

def legacy_pages():
    for source in ROOT.glob('*.html'):
        if source.stem in R:continue
        path='/' if source.name=='index.html' else '/'+source.name
        doc=source.read_text()
        title=html.unescape(re.search(r'<title>(.*?)</title>',doc).group(1))
        desc={'schedule.html':'Choose a pickup date and available arrival time, review your details, and reserve junk removal with Bryan Junks It Away.', 'confirmation.html':'Review your Bryan Junks It Away reservation details and the next steps for your scheduled pickup.', 'estimate-survey.html':'Describe your items, load size, and access to get a personal starting estimate for junk removal with Bryan Junks It Away.'}.get(source.name,'Contact us Junks It Away for pickup help.')
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
            doc=doc.replace('Most estimates land close to the final price, but the actual amount can be a little lower or higher after we review the items and access with you in person or remotely.','We’ll confirm the final price with you in person or contact you and send an invoice for your approval before work begins.')
            labels=[('single','One small item','Single item'),('few','A few unwanted items','Few items'),('eighth','Small household or yard pile','⅛ truck'),('quarter','Small garage or room cleanout','¼ truck'),('half','Bedroom set or moderate cleanout','½ truck'),('threequarters','Large garage or multi-room load','¾ truck'),('full','Full truck of cleanout contents','Full truck cleanout')]
            table='<div class="pricing-table"><div class="pricing-row pricing-head"><b>Common job</b><b>Typical load</b><b>Starting range</b></div>'+''.join('<div class="pricing-row"><span>'+job+'</span><span>'+label+'</span><strong>$'+str(LOAD_BANDS[key][0])+'–$'+str(LOAD_BANDS[key][1])+('+' if key=='full' else '')+'</strong></div>' for key,job,label in labels)+'</div></section>'
            doc=re.sub(r'<div class="pricing-table">.*?</section>',lambda _:table,doc,count=1,flags=re.S)
            doc=doc.replace('</main>',section('ONE FRAMEWORK ACROSS OUR SERVICE AREA','Starting prices by service.','<div class="service-price-list">'+''.join('<p><strong>'+a('/'+s['slug']+'/',s['name'])+'</strong><span>'+('Starting at $'+str(s['starting']) if s['starting'] else 'Quoted separately')+'</span></p>' for s in services)+'</div><p>These are starting points, not flat prices. Whole studio / one-bedroom cleanouts start at $635; large or multi-load jobs need a detailed assessment. We’ll confirm the final price with you in person or contact you and send an invoice for your approval before work begins.</p>')+'</main>')
        write(path,'',title,desc,indexable=indexable,legacy=doc)


def answer_page():
    questions = [
        ('How much does junk removal cost?', 'Small, straightforward pickups start at $95. The starting range for a few items is $150–$260. Larger household loads are estimated by truck space, with weight, stairs, carrying distance, and disassembly also affecting the price. Use our pricing guide and describe the full pickup for a personal estimate.'),
        ('Can two small wooden chairs qualify for the $95 pickup?', 'Yes. Two lightweight wooden chairs can qualify for the $95 minimum when access is straightforward. Tell us whether any item weighs more than 50 pounds and include other items going in the same pickup.'),
        ('How much does couch or sectional removal cost?', S['couch-removal']['pricing']),
        ('How much is a whole-home cleanout?', 'Whole studio or one-bedroom cleanouts start at $635. Larger homes, heavier contents, and multiple loads need a detailed assessment. Removing a few leftover items is priced for those items, not automatically as a whole-home cleanout.'),
        ('What is included in the pickup?', 'We handle lifting, loading, and hauling for the agreed items and scope. Describe indoor access, stairs, long carries, and any disassembly before booking so the estimate includes the work needed.'),
        ('Where do you provide junk removal?', 'We are based in Baldwin Park, California, and travel to listed pickup areas throughout the San Gabriel Valley, Los Angeles, San Fernando Valley, Inland Empire, Riverside County, and Orange County. Check our service-area directory or contact us with the exact pickup location.'),
        ('Can I get same-day junk removal?', 'Same-day pickup depends on availability and the job details. Check the scheduling page or call 626-386-5623. We are open 24 hours, but a particular pickup time is not guaranteed until availability and your reservation are confirmed.'),
        ('Do I need to carry my items outside?', 'No. Tell us whether the items are indoors, upstairs, in a garage, in a backyard, or at the curb. Describe gates, elevators, narrow turns, and the distance to the truck so we can plan the work.'),
        ('What items can you remove?', 'We offer household junk, furniture, couch, mattress, appliance, garage, move-out, property, storage-unit, yard-debris, and construction-debris removal. Describe mixed loads together. Acceptance and pricing for special materials must be reviewed before pickup.'),
        ('Can you take paint, chemicals, or treated wood?', 'Do not assume these materials are included in a household-junk quote. Identify paint, chemicals, treated wood, unknown materials, and other special-disposal items when contacting us. We must review acceptance and disposal requirements before agreeing to haul them.'),
        ('What should I include for the most useful estimate?', 'List each item and its approximate quantity, size, and weight. Include wide photos of the entire load, close-ups of heavy pieces, your pickup location, stairs, distance to the truck, and anything that needs disassembly. For a cleanout, describe and photograph each room.'),
        ('Is the online estimate the final price?', 'The online estimate is a starting range based on the details you provide. We confirm the final price in person or contact you and send an invoice for your approval before work begins.'),
        ('Is there a deposit to book?', 'Booking is free, with no deposit. Review your pickup details and chosen time before confirming. You approve the final job price before work begins.'),
        ('What happens before the pickup?', 'We call about 1–2 hours before the scheduled arrival to confirm our arrival. Keep the agreed items identifiable and tell us if the load or access has changed.'),
        ('How do I send photos or change my reservation?', 'Text photos or update and cancellation requests to 626-386-5623, or email bryanjunksitaway@gmail.com. Include your confirmation number so we can match the message to your reservation.'),
        ('Should I use city bulky-item pickup instead?', 'Your existing trash provider may offer bulky-item collection. Check eligibility, accepted items, placement requirements, and dates for your address. Our paid pickup can help when you need lifting, indoor removal, or a combined load. Local pages link to public disposal resources where available.')
    ]
    body='<section class="page-intro"><p class="eyebrow">PLAN YOUR PICKUP WITH CONFIDENCE</p><h1>Junk removal questions,<br><em>answered.</em></h1><p class="section-lede">What will it cost? Can we carry it downstairs? What happens after you book? Find the details here, then tell us about the space you want back.</p>'+actions()+'</section>'
    body+=section('BRYAN JUNKS IT AWAY','Your pickup at a glance.','<div class="service-grid"><article><h3>Small pickups from $95.</h3><p>Price depends on the actual items and access. Whole studio or one-bedroom cleanouts start at $635.</p>'+a('/calculator.html','Compare load prices ↗','text-link')+'</article><article><h3>Based in Baldwin Park.</h3><p>We travel to your pickup address across our listed Southern California service areas.</p>'+a('/service-areas/','Find your area ↗','text-link')+'</article><article><h3>Open 24 hours.</h3><p>Pickup appointments depend on availability. Call or text 626-386-5623.</p>'+a(MAPS,'Find our Google Business Profile ↗','text-link')+'</article></div>')
    body+=faq(questions)
    body+=section('READY WHEN YOU ARE','A few useful next steps.','<div class="hero-booking-actions">'+a('/services/','See what we remove','button secondary-button')+a('/calculator.html','Understand your estimate','button secondary-button')+a('/contact.html','Contact our team','button secondary-button')+'</div><p class="fine">Business information and answers reviewed September 18, 2026.</p>')+closing()
    write('/junk-removal-questions/',body,'Junk Removal Questions: Prices, Items & Booking | '+BRAND,'Answers about junk removal prices from $95, cleanouts, stairs, service areas, photos, and booking. Plan your pickup with Bryan Junks It Away.',breadcrumbs=[('Home','/'),('Pickup questions','/junk-removal-questions/')])

def build():
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'assets',OUT/'assets')
    for name in ['styles.css','expansion.css','script.js','booking.js','account.js','pricing.js','config.js']:
        shutil.copy2(ROOT/name,OUT/name)
    legacy_pages()
    answer_page()
    for r in regions:regional_page(r)
    body='<section class="page-intro service-intro"><p class="eyebrow">THE GOOD KIND OF EMPTY.</p><h1>Junk Removal &amp;<br><em>Cleanout Services</em></h1><p class="section-lede">One unwanted couch or a whole place to clear? Start with what you need gone. We’re based in Baldwin Park and travel throughout our listed Southern California service areas.</p>'+actions()+'</section>'
    body+=section('MAKE ROOM FOR WHAT MATTERS MOST.','Find the right kind of help.',service_cards(CORE))
    body+=section('MORE WAYS WE CAN HELP','Beyond the living room.',service_cards([s for s in services if not s['core']]))+process()+closing()
    write('/services/',body,'Junk Removal & Cleanout Services | '+BRAND,'Explore furniture, couch, mattress, appliance, garage, move-out, and property cleanout services. Find the right pickup and get a starting estimate.',breadcrumbs=[('Home','/'),('Services','/services/')])
    body='<section class="page-intro service-intro"><p class="eyebrow">BASED IN BALDWIN PARK. WE COME TO YOU.</p><h1>Junk Removal<br><em>Service Areas</em></h1><p class="section-lede">Find your region, then your pickup area. One local service-area business, with a simple way to plan removal across Southern California.</p>'+actions()+'</section>'+section('FIND YOUR NEIGHBORHOOD','Where can we help?',region_cards())+section('NOT SURE WHERE TO START?','Send us your location.','<p class="section-lede">Our directories include cities, neighborhoods, and communities. If you don’t see the name you use for your area, contact us with the pickup location so we can check the fit before you plan a visit.</p>'+a('/contact.html','Check my pickup area ↗','button'))
    write('/service-areas/',body,'Southern California Junk Removal Service Areas | '+BRAND,'Based in Baldwin Park, serving SGV, Los Angeles, SFV, Inland Empire, Riverside County, and Orange County. Find your pickup area and explore services.',breadcrumbs=[('Home','/'),('Service Areas','/service-areas/')])
    for s in services:
        service_page(s)
        if s['core']:
            for loc in locations:service_page(s,loc)
    for group,rows in [('pages',[p for p in manifest if p['indexable'] and not p['service']]),('services',[p for p in manifest if p['indexable'] and p['service'] and not p['location']]),('locations',[p for p in manifest if p['indexable'] and p['location']])]:
        (OUT/f'sitemap-{group}.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+p['path']+'</loc>'+('<lastmod>'+CONTENT_REVIEWED+'</lastmod>' if p['indexable'] else '')+'</url>' for p in rows)+'</urlset>')
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<sitemap><loc>'+BASE+'/sitemap-'+g+'.xml</loc></sitemap>' for g in ['pages','services','locations'])+'</sitemapindex>')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
    (ROOT/'site-tools/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Built {len(manifest)} pages: {sum(p["indexable"] for p in manifest)} indexable; {sum(not p["indexable"] for p in manifest)} noindex.')

if __name__=='__main__':build()

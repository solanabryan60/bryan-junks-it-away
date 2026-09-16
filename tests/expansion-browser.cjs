const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/Users/bryansolana/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
const base='https://www.bryanjunksitaway.com';
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const context=await browser.newContext();
 if(!process.env.LIVE)await context.route(base+'/**',route=>{const u=new URL(route.request().url());const file=path.join(root,'public',u.pathname+(u.pathname.endsWith('/')?'index.html':''));return fs.existsSync(file)?route.fulfill({path:file}):route.fulfill({status:404,body:'Not found'})});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const snapshots=path.join(root,'work/expansion-qa');fs.mkdirSync(snapshots,{recursive:true});
 const paths=['/','/services/','/service-areas/','/couch-removal/','/appliance-removal/','/construction-debris-removal/','/san-gabriel-valley.html','/los-angeles.html','/san-fernando-valley.html','/inland-empire.html','/riverside.html','/orange-county.html','/junk-removal/west-covina/','/junk-removal/silver-lake/','/junk-removal/van-nuys/','/junk-removal/ontario/','/junk-removal/menifee/','/junk-removal/anaheim/','/couch-removal/west-covina/','/mattress-removal/anaheim/','/appliance-removal/north-hollywood/','/garage-cleanouts/corona/','/move-out-cleanouts/pasadena/','/property-cleanouts/riverside/','/calculator.html','/estimate-survey.html','/schedule.html','/contact.html','/account.html','/merch.html','/confirmation.html'];
 for(const width of [390,1440]){
  await page.setViewportSize({width,height:1000});
  for(const url of paths){
   const response=await page.goto(base+url);assert.equal(response.status(),200,url);
   await page.locator('#menu-toggle').waitFor({state:'attached'});
   assert.equal(await page.locator('h1').count(),1,url+' H1');assert.equal(await page.locator('.top-areas').count(),1,url+' duplicate ribbon');
   assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),url+' overflow at '+width);
   for(const img of await page.locator('img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(i=>i.decode().catch(()=>{}));assert(await img.evaluate(i=>i.naturalWidth>0),url+' broken image')}
   await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
   await page.screenshot({path:path.join(snapshots,(url.replaceAll('/','_')||'home')+'-'+width+'-top.png')});
   await page.screenshot({path:path.join(snapshots,(url.replaceAll('/','_')||'home')+'-'+width+'.png'),fullPage:true});
  }
 }
 console.log('PASS 31 representative pages at mobile and desktop sizes; images, headings, no overflow.');
 await page.setViewportSize({width:390,height:850});await page.goto(base+'/services/');await page.locator('#menu-toggle').click();assert(await page.locator('#primary-nav').isVisible());await page.keyboard.press('Escape');assert(!await page.locator('#primary-nav').isVisible());
 await page.goto(base+'/san-gabriel-valley.html');assert.equal(await page.locator('#cities').getAttribute('open'),null);await page.locator('.city-toggle').click();assert.notEqual(await page.locator('#cities').getAttribute('open'),null);await page.locator('#cities a').filter({hasText:'West Covina'}).click();await page.waitForURL('**/junk-removal/west-covina/');await page.getByRole('heading',{name:'Couch Removal',exact:true}).getByRole('link').click();await page.waitForURL('**/couch-removal/west-covina/');
 await page.goto(base+'/couch-removal/');await page.locator('.region-directory summary').filter({hasText:'San Gabriel Valley'}).click();await page.locator('.region-directory a').filter({hasText:'West Covina'}).click();await page.waitForURL('**/couch-removal/west-covina/');
 console.log('PASS mobile menu, Escape, location-first and service-first navigation converge.');
 await page.goto(base+'/estimate-survey.html');assert.equal(await page.locator('input[type=radio]:checked').count(),0);await page.locator('[name="city"]').fill('Baldwin Park');
 for(const [name,value] of Object.entries({area:'San Gabriel Valley',load:'few',itemType:'chairs',weight:'light',access:'Driveway or curbside',disassembly:'no',tight:'no',carry:'short'}))await page.locator(`input[name="${name}"][value="${value}"]`).check();
 await page.locator('[name="quantity"]').fill('2');await page.locator('textarea[name="description"]').fill('2 wooden chairs');await page.locator('button[type="submit"]').click();assert.equal(await page.locator('#price-value').innerText(),'Estimated $95');await page.locator('#reserve-estimate').click();await page.waitForFunction(()=>document.querySelector('[name="items"]')?.value.includes('chairs'));
 await page.locator('[data-calendar-next]').click();await page.locator('#calendar-days button:not(:disabled)').first().click();await page.locator('#booking-status').filter({hasText:'Choose an available'}).waitFor({timeout:20000});await page.locator('[data-hour="10"]').click();
 for(const [name,value] of Object.entries({name:'Website audit',phone:'6265550100',email:'test@example.com',address:'Test address'}))await page.locator(`[name="${name}"]`).fill(value);
 await page.locator('button[type="submit"]').click();await page.locator('#booking-result').waitFor({state:'visible'});assert((await page.locator('#booking-details').innerText()).includes('Website audit'));await page.locator('#edit-booking').click();assert(await page.locator('#booking-result').isHidden());
 let sends=0;await page.route('**/functions/v1/create-booking',r=>{if(r.request().method()==='POST'){sends++;return r.fulfill({json:{confirmation_number:'TEST-EXPANSION',notification_status:'sent'}})}return r.continue()});
 await page.locator('button[type="submit"]').click();await page.locator('#confirm-booking').click();await page.waitForURL('**/confirmation.html?confirmation=TEST-EXPANSION');assert.equal(sends,1);assert((await page.locator('#saved-booking').innerText()).includes('Website audit'));
 console.log('PASS blank initial answers, $95 estimate, carryover, live availability, review/edit, simulated submission and confirmation.');
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(snapshots,'results.json'),JSON.stringify({pages:paths,widths:[390,1440],errors,booking:'POST mocked; no real reservation created'},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

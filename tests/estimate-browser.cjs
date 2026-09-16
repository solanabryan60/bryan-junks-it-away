const {chromium}=require('/Users/bryansolana/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext({viewport:{width:390,height:900}}),base='https://www.bryanjunksitaway.com',root=path.resolve(__dirname,'..');
if(!process.env.LIVE)await context.route(base+'/**',r=>{const u=new URL(r.request().url()),f=path.join(root,'public',u.pathname+(u.pathname.endsWith('/')?'index.html':''));return fs.existsSync(f)?r.fulfill({path:f}):r.fulfill({status:404})});
const p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
await p.goto(base+'/estimate-survey.html');
assert.equal(await p.locator('input:checked').count(),0);
await p.locator('[name=city]').fill('Baldwin Park');
async function choose(values){for(const [name,value] of Object.entries(values))await p.locator(`[name="${name}"][value="${value}"]`).check()}
async function price(){await p.locator('button[type=submit]').click();await p.locator('#price-result').waitFor({state:'visible'});return p.locator('#price-value').innerText()}
await choose({area:'San Gabriel Valley',itemType:'couch',load:'single',weight:'light',access:'Driveway or curbside',carry:'short',tight:'no',disassembly:'no'});
await p.locator('textarea[name=description]').fill('1 couch');assert.equal(await price(),'Estimated $150–$175');
await p.locator('#edit-estimate').click();await p.locator('[name=notes]').fill('2 flights of stairs.');assert(await p.locator('#price-result').isHidden());assert.equal(await p.evaluate(()=>sessionStorage.getItem('pickupEstimate')),null);assert.equal(await price(),'Estimated $200–$225');assert((await p.locator('#price-details').innerText()).includes('2 flights'));
await p.locator('[name=notes]').fill('No stairs.');await p.locator('textarea[name=description]').fill('1 sectional sofa');assert.equal(await price(),'Estimated $220–$245');
await choose({access:'Upstairs',elevator:'no'});assert(await p.locator('[name=flights]').isEnabled());await p.locator('[name=flights]').fill('2');assert.equal(await price(),'Estimated $270–$295');
await choose({elevator:'yes'});assert(await p.locator('[name=flights]').isDisabled());assert.equal(await price(),'Estimated $235–$260');
await choose({access:'Driveway or curbside',itemType:'property',load:'home',bedrooms:'1',fullness:'typical'});await p.locator('textarea[name=description]').fill('Entire apartment cleanout');assert.equal(await price(),'Estimated $635–$735');
await choose({bedrooms:'3'});assert.equal(await price(),'Estimated $815–$915');
await choose({itemType:'construction',material:'dense',load:'quarter',fullness:'light'});await p.locator('textarea[name=description]').fill('Concrete and tile');assert.equal(await price(),'Let’s fine-tune your quote');
await choose({itemType:'chairs',load:'few'});assert(await p.locator('[name=material]').first().isDisabled());await p.locator('textarea[name=description]').fill('2 wooden chairs. The couch is staying.');await p.locator('[name=quantity]').fill('2');assert.equal(await price(),'Estimated $95–$120');
assert(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2));
await p.locator('#price-result').screenshot({path:path.join(root,'work/estimate-result-mobile.png')});
await p.locator('textarea[name=description]').fill('<img src=x onerror=alert(1)> 2 wooden chairs');assert.equal(await price(),'Estimated $95–$120');assert.equal(await p.locator('#price-details img').count(),0);
await p.locator('#edit-estimate').click();await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:path.join(root,'work/estimate-form-mobile.png')});
assert.deepEqual(errors,[]);console.log('PASS responsive estimate: descriptions, notes, conditional questions, elevator/stairs, home size, dense materials, stale result reset, safe text rendering.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

'use strict';
// Planning estimates, anchored to the owner's load bands. Not a binding invoice.
// Kept in this compact form because the static pricing guide reads these bands.
const PICKUP_BANDS={single:[95,175],few:[150,260],eighth:[180,290],quarter:[250,390],half:[365,565],threequarters:[525,725],full:[675,950]};
const PICKUP_ITEMS=[
 {name:'Sectional sofa',pattern:'sectional(?: sofa| couch)?s?',space:3,minimum:220},
 {name:'Sofa',pattern:'(?:sofas?|couches|couch|loveseats?)',space:1.5,minimum:150},
 {name:'Mattress',pattern:'mattress(?:es)?',space:1,minimum:95},
 {name:'Box spring',pattern:'box springs?',space:.7,minimum:95},
 {name:'Chair',pattern:'(?:wooden |dining |office )?chairs?',space:.25,minimum:95},
 {name:'Recliner',pattern:'recliners?',space:1,minimum:150},
 {name:'Dresser',pattern:'dressers?',space:1,minimum:135},
 {name:'Table',pattern:'(?:dining |coffee |end )?tables?',space:1,minimum:125},
 {name:'Desk',pattern:'desks?',space:1,minimum:125},
 {name:'Bed frame',pattern:'bed frames?',space:.75,minimum:125},
 {name:'Refrigerator',pattern:'(?:refrigerators?|fridges?|freezers?)',space:1.25,minimum:150},
 {name:'Appliance',pattern:'(?:washers?|dryers?|dishwashers?|ovens?|stoves?|water heaters?)',space:1,minimum:135},
 {name:'Box',pattern:'box(?:es)?',space:.08,minimum:95},
 {name:'Bag',pattern:'(?:trash |garbage |yard )?bags?',space:.08,minimum:95},
 {name:'Rug',pattern:'rugs?|carpets?',space:.6,minimum:95},
 {name:'Bicycle',pattern:'bicycles?|bikes?',space:.3,minimum:95},
 {name:'Grill',pattern:'grills?|barbecues?',space:.8,minimum:125},
 {name:'Bookshelf',pattern:'(?:bookshel(?:f|ves)|bookcases?|shelving units?)',space:.8,minimum:125}
];
const COUNT_WORDS={a:1,an:1,one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10,eleven:11,twelve:12};
function pickupTextHas(text,pattern){
 const re=new RegExp(pattern,'gi');let m;
 while((m=re.exec(text))){const before=text.slice(Math.max(0,m.index-45),m.index).split(/[.,;\n]/).pop();if(!/\b(?:no|not|without|zero)\b(?:\s+[\w-]+){0,4}\s*$/.test(before))return true;}return false;
}
function parsePickupDescription(text){
 text=String(text||'').toLowerCase();const found=[];
 const pattern=new RegExp('\\b('+PICKUP_ITEMS.map(i=>i.pattern).join('|')+')\\b','gi');let match;
 while((match=pattern.exec(text))){
  const before=text.slice(Math.max(0,match.index-60),match.index).split(/[.,;\n]/).pop();
  if(/\b(?:no|not|without|keeping|keep)\b(?:\s+[\w-]+){0,4}\s*$/.test(before))continue;
  if(/^\s+(?:is|are|will be)\s+(?:staying|kept|not going)/.test(text.slice(match.index+match[0].length)))continue;
  const spec=PICKUP_ITEMS.find(i=>new RegExp('^(?:'+i.pattern+')$','i').test(match[0]));
  const count=before.match(/\b(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(?:x\s*)?(?:(?:small|large|wooden|dining|old|queen|king|twin|size|sized|lightweight)\s+){0,3}$/);
  const quantity=count?Number(COUNT_WORDS[count[1]]||count[1]):1;
  if(quantity===0)continue;
  found.push({...spec,quantity:Math.min(quantity,1000),explicit:!!count});
 }
 return found;
}
function estimatePickup(d){
 const description=[d.description,d.otherItem].filter(Boolean).join('. ');
 const text=(description+'. '+(d.notes||'')).toLowerCase();
 const items=parsePickupDescription(description);const assumptions=[];const factors=[];
 const review=note=>({amount:null,low:null,high:null,note,items:items.map(i=>`${i.quantity} × ${i.name}`),factors,assumptions});
 if(pickupTextHas(text,'\\b(?:asbestos|hazardous|chemicals?|concrete|dirt|bricks?|tile|roofing|hot tubs?|safes?|pianos?|pool tables?)\\b')||d.itemType==='special'||d.material==='dense')return review('This pickup needs a handling or material review. Send us photos and we’ll contact you with an invoice to approve.');
 let quantity=Math.max(0,Number(d.quantity)||0),known=items.reduce((n,i)=>n+i.quantity,0);
 if(items.length===1&&!items[0].explicit&&quantity){items[0].quantity=quantity;known=quantity;}
 const count=Math.max(quantity,known,1);
 let space=items.reduce((n,i)=>n+i.space*i.quantity,0);
 const defaults={chairs:.25,couch:1.5,mattress:1,appliances:1.1,furniture:1,office:.8,household:.3,other:.5};
 if(quantity>known)space+=(quantity-known)*(defaults[d.itemType]||.4);
 if(!items.length)space=count*(defaults[d.itemType]||.4);
 if(quantity&&known>quantity)assumptions.push(`Your description lists ${known} items, so we used that count instead of ${quantity}.`);
 if(items.some(i=>!i.explicit)&&items.length>1)assumptions.push('Items without a written quantity are counted as one each.');
 let key=d.load==='unknown'?d.roughSize:d.load;
 const cleanout=['threequarters','full','home'].includes(key);
 // Space units are approximate bulky-item equivalents, not advertised truck dimensions.
 const spacePrice=v=>{const points=[[0,95],[.5,95],[1,125],[1.5,150],[2,180],[4,250],[8,365],[12,525],[16,675]];for(let i=1;i<points.length;i++){if(v<=points[i][0]){const [x,y]=points[i-1],[xx,yy]=points[i];return y+(v-x)/(xx-x)*(yy-y);}}return 675+(v-16)*42;};
 const writtenFlights=text.match(/\b(\d+|one|two|three|four)\s+flights?\s+(?:of\s+)?stairs/);
 const floors=Math.max(1,Math.min(10,Number(d.flights)||Number(writtenFlights&&(COUNT_WORDS[writtenFlights[1]]||writtenFlights[1]))||1));
 const stairs=d.access==='Upstairs'&&d.elevator!=='yes'||pickupTextHas(text,'\\b(?:stairs|upstairs|walk[- ]?up|second floor|third floor)\\b');
 const longCarry=d.carry==='long'||/longer carry/.test(d.parking||'')||/long carry/.test(d.access||'')||pickupTextHas(text,'\\b(?:long carry|long walk|far from (?:the )?truck)\\b');
 const dismantle=d.disassembly==='yes'||pickupTextHas(text,'\\b(?:needs? (?:to be )?(?:taken apart|disassembl\\w*)|requires? disassembl\\w*|disassembly (?:required|needed)|must be taken apart)\\b');
 const tight=d.tight==='yes'||pickupTextHas(text,'\\b(?:tight (?:doorways?|hallways?|access)|narrow (?:doorways?|hallways?))\\b');
 const veryHeavy=d.weight==='veryheavy'||pickupTextHas(text,'\\b(?:[2-9]\\d{2}|1\\d{3})\\s*(?:lbs?|pounds)\\b');
 if(veryHeavy)return review('Items over 200 pounds need a quick handling review. Send us photos so we can prepare a price for you to approve.');
 const heavy=d.weight==='heavy'||pickupTextHas(text,'\\b(?:heavy|solid wood|over 50 (?:lbs?|pounds))\\b');
 const minimum=Math.max(95,...items.map(i=>i.minimum),({couch:150,appliances:135})[d.itemType]||95);
 let amount;
 if(key==='home'){
  const beds=Number(d.bedrooms);if(!beds)return review('Choose the size of the home so we can finish your estimate.');if(beds>=5)return review('For a property this size, send us photos of the rooms to clear. We’ll contact you and prepare an invoice for your approval.');
  amount=Math.max(635+Math.max(0,beds-1)*90+(d.fullness==='packed'?175:0),spacePrice(space));
  factors.push(`Whole-home cleanout: ${beds===1?'studio / one bedroom':beds+' bedrooms'}${d.fullness==='packed'?', densely filled':''}`);
 }else{
  if(!PICKUP_BANDS[key]){
   if(!items.length)return review('Choose the approximate amount, or describe common items with quantities—for example, “2 wooden chairs and 1 mattress.”');
   amount=spacePrice(space);assumptions.push('Load size estimated from the items recognized in your description.');
  }else{
   const [low,high]=PICKUP_BANDS[key];
   amount=Math.max(low,minimum,spacePrice(space));
   if(!['single','few'].includes(key))amount=Math.max(amount,low+(high-low)*(d.fullness==='packed'?.7:d.fullness==='light'?.1:.35));
   factors.push('Amount: '+({single:'one item',few:'a few items',eighth:'small pile',quarter:'small room / quarter load',half:'half load',threequarters:'multi-room / three-quarter load',full:'full load'})[key]);
  }
  if(!cleanout&&amount>=635)return review('Your item list looks larger than a small pickup. Choose a room / cleanout-sized load so we can price the full amount.');
 }
 if(['single','few'].includes(key)&&count<=2&&d.weight==='light'&&(d.itemType==='chairs'||items.length>0&&items.every(i=>i.name==='Chair')))amount=95;
 if(stairs){const cost=25*floors;amount+=cost;factors.push(`Stairs: ${floors} flight${floors===1?'':'s'} (+$${cost})`);}
 if(longCarry){amount+=35;factors.push('Long carry (+$35)');}else if(d.carry==='medium'){amount+=15;factors.push('Carry of about 30–75 feet (+$15)');}
 if(d.access==='Inside the home'){amount+=15;factors.push('Indoor pickup (+$15)');}
 if(d.access==='Upstairs'&&d.elevator==='yes'&&!stairs){amount+=15;factors.push('Elevator pickup (+$15)');}
 if(dismantle){amount+=35;factors.push('Disassembly allowance (+$35)');}
 if(tight){amount+=20;factors.push('Tight access (+$20)');}
 if(heavy){amount+=25;factors.push('Heavy-item handling allowance (+$25)');}
 if(d.itemType==='construction'||d.material==='light-debris'){amount+=40;factors.push('Light renovation debris allowance (+$40)');}
 if(d.weight==='unknown')assumptions.push('Weight is unconfirmed; unusual lifting requirements may change the price.');
 if(d.disassembly==='unknown'||d.tight==='unknown'||d.carry==='unknown')assumptions.push('Some access details are unconfirmed and will be reviewed with you.');
 if(!items.length)assumptions.push('We used your selected service and amount. Your written description will also be reviewed by our team.');
 if(!cleanout&&amount>=635)return review('The amount and handling look more involved than a standard small pickup. We’ll review the details and send a price for your approval.');
 amount=Math.max(95,Math.round(amount/5)*5);
 return {amount,low:amount,high:amount,note:'Your estimated pickup price, based on the items, amount, and access details below. We’ll confirm the final price in person or contact you and send an invoice for approval before work begins.',items:items.map(i=>`${i.quantity} × ${i.name}`),factors,assumptions};
}
if(typeof module!=='undefined'){module.exports=estimatePickup;module.exports.parsePickupDescription=parsePickupDescription;}

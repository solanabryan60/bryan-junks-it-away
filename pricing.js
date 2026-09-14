'use strict';
// Reference bands supplied by Bryan. Difficulty narrows a band; it does not add unapproved fees.
function estimatePickup(d){
 const bands={single:[95,175],few:[150,260],eighth:[180,290],quarter:[250,390],half:[365,565],threequarters:[525,725],full:[675,900]};
 const difficult=d.weight==='heavy'||['appliances','construction','special'].includes(d.itemType)||/Upstairs|long carry/.test(d.access||'')||d.tight==='yes'||d.disassembly==='yes'||d.parking==='No, it’s a longer carry';
 if(d.load==='home')return {low:635,high:Number(d.bedrooms)<=1&&!difficult?635:900,note:'Studio / one-bedroom cleanouts start at $635. Larger or more involved cleanouts require an in-person assessment; $900 is the online estimate cap, not a final-price limit.'};
 let key=d.load;
 if(key==='single'&&Number(d.quantity)>1)key=Number(d.quantity)<=3?'few':'eighth';
 if(['single','few'].includes(d.load)&&d.itemType==='chairs'&&Number(d.quantity)<=2&&d.weight==='light'&&!difficult)return {low:95,high:95,note:'Small pickup of up to two lightweight wooden chairs. Final price confirmed after reviewing access in person.'};
 let [low,high]=bands[key]||bands.few;
 if(difficult)low=Math.round(((low+high)/2)/5)*5;
 let note;
 if(d.load==='unknown') note='This range is based on the details you shared. We’ll confirm the exact load and final price in person.';
 else if(d.itemType==='special') note='This range accounts for an unusual or heavy item. We’ll confirm access, handling, and the final price in person.';
 else note=difficult?'Extra handling places this pickup toward the upper part of its load-size range. We’ll confirm the final price in person.':'This range follows your selected load size. Larger loads require an in-person assessment. The online estimate is capped at $900.';
 return {low,high,note};
}
if(typeof module!=='undefined')module.exports=estimatePickup;

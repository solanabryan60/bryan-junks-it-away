'use strict';
// Bryan's reference ranges. Only explicitly selected cleanout-sized loads exceed $634.
function estimatePickup(d){
 const bands={single:[95,175],few:[150,260],eighth:[180,290],quarter:[250,390],half:[365,565],threequarters:[525,725],full:[675,950]};
 let key=d.load==='unknown'?d.roughSize:d.load;
 const difficult=d.weight==='heavy'||['appliances','construction','special'].includes(d.itemType)||/Upstairs|long carry/.test(d.access||'')||d.tight==='yes'||d.disassembly==='yes';
 if(key==='home')return {low:635,high:Number(d.bedrooms)===1&&!difficult?635:900,note:'Whole-home cleanout estimate. Studio / one-bedroom cleanouts start at $635. Final price requires an in-person review.'};
 if(!bands[key])return {low:null,high:null,note:'Choose the space your items roughly fill so we can estimate the load.'};
 if(key==='single'&&Number(d.quantity)>1)key=Number(d.quantity)<=3?'few':'eighth';
 if(['single','few'].includes(key)&&d.itemType==='chairs'&&Number(d.quantity)>0&&Number(d.quantity)<=2&&d.weight==='light'&&!difficult)return {low:95,high:95,note:'Up to two lightweight wooden chairs. Final price confirmed in person.'};
 let [low,high]=bands[key];
 if(difficult)low=Math.round((low+high)/10)*5;
 return {low,high,note:['threequarters','full'].includes(key)?'Room / cleanout-sized load estimate. We’ll review the full load in person before agreeing on the final price.':d.itemType==='special'?'Load-size estimate only. Safes, hot tubs, and unusual items need a handling review before the final price is agreed.':'Based on the space your items take up and the access details. Final price confirmed before work begins.'};
}
if(typeof module!=='undefined')module.exports=estimatePickup;

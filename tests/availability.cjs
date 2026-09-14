const {test}=require('node:test');
const assert=require('node:assert/strict');
const {available,finishEarly}=require('../lib/availability.cjs');
const minute=60000;
const base={start:120*minute,durationMinutes:60,bookings:[],windowStart:0,windowEnd:600*minute,now:0,leadMinutes:30,travelMinutes:()=>30};
test('leaves travel time before and after the job',()=>{
 assert.equal(available({...base,bookings:[{start:190*minute,end:250*minute,status:'confirmed'}]}),false);
 assert.equal(available({...base,bookings:[{start:210*minute,end:270*minute,status:'confirmed'}]}),true);
});
test('rejects overlapping jobs and closed hours',()=>{
 assert.equal(available({...base,bookings:[{start:150*minute,end:200*minute,status:'confirmed'}]}),false);
 assert.equal(available({...base,windowEnd:170*minute}),false);
 assert.equal(available({...base,now:110*minute}),false);
});
test('finishing early releases work time while preserving travel constraints',()=>{
 const done=finishEarly({start:60*minute,end:180*minute,status:'confirmed'},100*minute);
 assert.equal(available({...base,bookings:[done]}),false);
 assert.equal(available({...base,start:130*minute,bookings:[done]}),true);
});
test('unknown travel estimates cannot create bookable slots',()=>assert.equal(available({...base,travelMinutes:()=>NaN}),false));
test('future jobs cannot be marked completed to bypass their reservation',()=>assert.throws(()=>finishEarly({start:60*minute,end:180*minute,status:'confirmed'},30*minute)));

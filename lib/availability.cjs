'use strict';
// Times are absolute milliseconds. Travel estimates must be supplied by the
// server for the specific origin, destination, departure time and weekday.
function available({start, durationMinutes, bookings, windowStart, windowEnd, now, leadMinutes, travelMinutes}) {
 if (![start,durationMinutes,windowStart,windowEnd,now,leadMinutes].every(Number.isFinite) || durationMinutes <= 0 || leadMinutes < 0) return false;
 const end = start + durationMinutes * 60000;
 if (start < now + leadMinutes * 60000 || start < windowStart || end > windowEnd) return false;
 const active = bookings.filter(b => b.status !== 'cancelled').slice().sort((a,b)=>a.start-b.start);
 if(active.some(b=>start < b.end && end > b.start)) return false;
 const before = active.filter(b=>b.end<=start).at(-1);
 const after = active.find(b=>b.start>=end);
 const inbound = travelMinutes(before || null, {start,end});
 const outbound = after ? travelMinutes({start,end},after) : 0;
 if(!Number.isFinite(inbound) || inbound<0 || !Number.isFinite(outbound) || outbound<0) return false;
 return start >= Math.max(windowStart, before ? before.end : windowStart) + inbound*60000 && (!after || end+outbound*60000<=after.start);
}
function finishEarly(booking, now) {
 if(booking.status !== 'confirmed' || now < booking.start || now >= booking.end) throw new Error('Only an active booking can be finished early.');
 return {...booking,end:now,status:'completed'};
}
module.exports={available,finishEarly};

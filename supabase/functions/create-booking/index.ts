import {createClient} from 'https://esm.sh/@supabase/supabase-js@2.57.4';
const allowed=['https://www.bryanjunksitaway.com','https://bryanjunksitaway.com'];
Deno.serve(async(req)=>{
 const origin=req.headers.get('origin')||allowed[0];
 const headers={'content-type':'application/json','Access-Control-Allow-Origin':allowed.includes(origin)?origin:allowed[0],'Vary':'Origin','Access-Control-Allow-Headers':'apikey, authorization, content-type','Access-Control-Allow-Methods':'GET, POST, OPTIONS','Cache-Control':'no-store'};
 const reply=(data:unknown,status=200)=>new Response(JSON.stringify(data),{status,headers});
 if(req.method==='OPTIONS')return new Response(null,{headers});
 const db=createClient(Deno.env.get('SUPABASE_URL')!,Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);
 try{
  if(req.method==='GET'){
   const date=new URL(req.url).searchParams.get('date');
   if(!/^\d{4}-\d{2}-\d{2}$/.test(date||''))return reply({error:'Invalid date'},400);
   const {data,error}=await db.from('bookings').select('pickup_time').eq('pickup_date',date).in('status',['requested','confirmed']);
   if(error){console.error('Availability read failed',error.code);return reply({error:'Unable to check availability'},503)}
   return reply({times:data.map(x=>x.pickup_time)});
  }
  if(req.method!=='POST')return reply({error:'POST required'},405);
  const raw=await req.text();if(raw.length>4500000)return reply({error:'Photos are too large. Maximum 3 MB total.'},413);
  const body=JSON.parse(raw);
  if(['contact_name','phone','email','address','city','items','pickup_date','pickup_time'].some(k=>typeof body[k]!=='string'||!body[k].trim()||body[k].length>10000))return reply({error:'Please complete all contact and pickup details.'},400);
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email)||!/^\d{4}-\d{2}-\d{2}$/.test(body.pickup_date))return reply({error:'Enter a valid email and date.'},400);
  // Older clients can still submit; new clients keep this ID for safe retries.
  body.request_id ||= crypto.randomUUID();
  if(!/^[0-9a-f-]{36}$/i.test(body.request_id))return reply({error:'Invalid request'},400);
  const match=body.pickup_time.match(/^(1[0-2]|[1-9]):00 (AM|PM)$/);
  if(!match)return reply({error:'Choose a valid arrival time.'},400);
  const hour=Number(match[1])%12+(match[2]==='PM'?12:0);
  const wall=new Date(`${body.pickup_date}T${String(hour).padStart(2,'0')}:00:00Z`);
  const zone=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',timeZoneName:'shortOffset'}).formatToParts(wall).find(p=>p.type==='timeZoneName')!.value;
  const starts=new Date(wall.getTime()-Number(zone.replace('GMT',''))*3600000);
  const local=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',hourCycle:'h23'}).formatToParts(starts);
  const parts=Object.fromEntries(local.map(p=>[p.type,p.value]));
  if(`${parts.year}-${parts.month}-${parts.day}`!==body.pickup_date||Number(parts.hour)!==hour||starts.getTime()<=Date.now())return reply({error:'Please choose a future arrival time.'},400);
  const photos=body.photos||[];if(!Array.isArray(photos)||photos.length>5)return reply({error:'Attach no more than 5 photos.'},400);
  const decoded=[];let total=0;
  for(const p of photos){
   if(!['image/jpeg','image/png','image/webp'].includes(p.type)||typeof p.data!=='string'||p.data.length>4200000)return reply({error:'Use JPG, PNG or WebP photos.'},400);
   const bytes=Uint8Array.from(atob(p.data),c=>c.charCodeAt(0));total+=bytes.length;
   if(total>3*1024*1024)return reply({error:'Photos must total no more than 3 MB.'},413);
   const valid=p.type==='image/jpeg'?bytes[0]===255&&bytes[1]===216:p.type==='image/png'?bytes[0]===137&&bytes[1]===80:new TextDecoder().decode(bytes.slice(0,4))==='RIFF';
   if(!valid)return reply({error:'One photo is not a supported image.'},400);
   decoded.push({...p,bytes});
  }
  const paths=[];
  for(let i=0;i<decoded.length;i++){const p=decoded[i],path=body.request_id+'/'+i+'.'+(p.type==='image/jpeg'?'jpg':p.type.split('/')[1]);const {error}=await db.storage.from('pickup-photos').upload(path,p.bytes,{contentType:p.type,upsert:true});if(error)throw Error('Photo upload failed');paths.push(path)}
  body.photo_names=paths;
  const {data,error}=await db.rpc('create_booking',{p:body});
  if(error){if(error.message.includes('TIME_UNAVAILABLE'))return reply({error:'That time was just taken. Please select another time.'},409);console.error('Booking save failed',error.code);throw Error('Save failed')}
  const booking=Array.isArray(data)?data[0]:data;let notification_status='unavailable';
  const url=Deno.env.get('GOOGLE_BOOKING_WEBHOOK_URL');
  if(url){try{
   const links=[];for(const path of paths){const signed=await db.storage.from('pickup-photos').createSignedUrl(path,604800);if(signed.data)links.push(signed.data.signedUrl)}
   const response=await fetch(url,{method:'POST',headers:{'content-type':'application/json'},signal:AbortSignal.timeout(15000),body:JSON.stringify({secret:Deno.env.get('GOOGLE_BOOKING_SECRET'),booking:{...body,...booking,photos:undefined,notes:(body.notes||'')+(links.length?'\nPhotos (links valid 7 days):\n'+links.join('\n'):''),starts_at:starts.toISOString(),ends_at:new Date(starts.getTime()+3600000).toISOString()}})});
   const result=await response.json();notification_status=result.ok?'sent':'pending';
  }catch{notification_status='pending'} }
  return reply({...booking,notification_status},201);
 }catch(e){console.error('Booking request failed',e instanceof Error?e.message:'unknown');return reply({error:'We could not complete this request. Please retry or call 626-386-5623.'},500)}
});

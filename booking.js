'use strict';
(()=>{
 const form=document.querySelector('#booking'),result=document.querySelector('#booking-result'),details=document.querySelector('#booking-details'),confirm=document.querySelector('#confirm-booking');
 const api='https://qcscbkzpfvrbmtvhubtg.supabase.co/functions/v1/create-booking';
 const anonymous='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFjc2Nia3pwZnZyYm10dmh1YnRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkzNTkyNzUsImV4cCI6MjEwNDkzNTI3NX0.N_Hb3jNZ2WvMpCTie3jl3qRdjZNj8suW4NfppOd29lU';
 const headers={apikey:'sb_publishable_qKdJB3Kch41AtT5-AI73Mg_0MJyateY',Authorization:'Bearer '+anonymous,'Content-Type':'application/json'};
 const status=document.createElement('p');status.id='booking-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');document.querySelector('#time-slots').after(status);
 const retry=document.createElement('button');retry.type='button';retry.className='reset';retry.textContent='Retry availability';retry.hidden=true;status.after(retry);
 const pacific=()=>{const parts=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',hourCycle:'h23'}).formatToParts(new Date());const p=Object.fromEntries(parts.map(x=>[x.type,x.value]));return {date:p.year+'-'+p.month+'-'+p.day,hour:Number(p.hour)}};
 let cursor=new Date(pacific().date+'T12:00:00');cursor.setDate(1);
 let selectedDate='',selectedTime='',ready=false,busy=false,pending=null,booked=new Set(),sequence=0;
 const buttons=[...document.querySelectorAll('[data-hour]')],days=document.querySelector('#calendar-days');
 const invalidate=()=>{pending=null;result.hidden=true};
 function paintTimes(){const now=pacific();buttons.forEach(b=>{b.disabled=!ready||booked.has(b.textContent)||(selectedDate===now.date&&Number(b.dataset.hour)<=now.hour);b.classList.toggle('selected',b.textContent===selectedTime);b.setAttribute('aria-pressed',String(b.textContent===selectedTime))})}
 async function availability(){const id=++sequence;ready=false;selectedTime='';invalidate();paintTimes();status.textContent='Checking available times…';retry.hidden=true;
  try{const response=await fetch(api+'?date='+selectedDate,{headers,signal:AbortSignal.timeout(15000)});const data=await response.json();if(!response.ok||!Array.isArray(data.times))throw Error();if(id!==sequence)return;booked=new Set(data.times);ready=true;paintTimes();status.textContent=buttons.some(x=>!x.disabled)?'Choose an available arrival time. All times are Pacific time.':'No times available for this day. Please choose another day.'}
  catch{if(id!==sequence)return;status.textContent='We couldn’t load available times. Please retry or call 626-386-5623.';retry.hidden=false}
 }
 retry.addEventListener('click',availability);
 function render(){document.querySelector('#calendar-month').textContent=new Intl.DateTimeFormat('en-US',{month:'long',year:'numeric'}).format(cursor);days.replaceChildren();const y=cursor.getFullYear(),m=cursor.getMonth();for(let i=0;i<new Date(y,m,1).getDay();i++)days.append(document.createElement('span'));
  for(let n=1;n<=new Date(y,m+1,0).getDate();n++){const b=document.createElement('button');b.type='button';b.textContent=n;b.dataset.date=y+'-'+String(m+1).padStart(2,'0')+'-'+String(n).padStart(2,'0');b.disabled=b.dataset.date<pacific().date;b.classList.toggle('selected',b.dataset.date===selectedDate);b.setAttribute('aria-label',b.dataset.date);b.addEventListener('click',()=>{if(busy)return;selectedDate=b.dataset.date;render();availability()});days.append(b)}
 }
 for(const [selector,delta] of [['[data-calendar-prev]',-1],['[data-calendar-next]',1]])document.querySelector(selector).addEventListener('click',()=>{if(busy)return;cursor.setMonth(cursor.getMonth()+delta);selectedDate='';selectedTime='';ready=false;sequence++;invalidate();render();paintTimes();status.textContent='Choose a day to see available times.';retry.hidden=true});
 buttons.forEach(b=>b.addEventListener('click',()=>{if(b.disabled||busy)return;selectedTime=b.textContent;invalidate();paintTimes()}));
 const params=new URLSearchParams(location.search);let estimate=null;
 if(params.get('city'))form.elements.city.value=params.get('city');
 if(params.get('estimate')==='1'){try{estimate=JSON.parse(sessionStorage.getItem('pickupEstimate'))}catch{}}
 if(estimate)form.elements.items.value=(estimate.quantity?estimate.quantity+' item(s): ':'')+(estimate.description||estimate.otherItem||estimate.itemType||'')+(estimate.notes?'\n'+estimate.notes:'');
 const initialEstimatedItems=estimate?form.elements.items.value:'';
 const row=(label,value)=>{const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value||'Not provided';return [dt,dd]};
 form.addEventListener('input',()=>{if(!busy)invalidate()});
 form.addEventListener('submit',e=>{e.preventDefault();if(busy||!form.reportValidity())return;if(!ready||!selectedDate||!selectedTime){status.textContent='Choose a day and arrival time first.';status.scrollIntoView({block:'center'});return}
  const d=new FormData(form),files=[...form.elements.photos.files];if(files.length>5||files.reduce((n,f)=>n+f.size,0)>3*1024*1024||files.some(f=>!['image/jpeg','image/png','image/webp'].includes(f.type))){status.textContent='Please attach up to 5 JPG, PNG or WebP photos, totaling no more than 3 MB.';status.scrollIntoView({block:'center'});return}
  const changedEstimate=estimate&&d.get('items')!==initialEstimatedItems;
  const labels={city:'City / ZIP',area:'Service area',itemType:'Main service',description:'Item description',quantity:'Approximate count',load:'Amount',bedrooms:'Bedrooms',fullness:'How full',weight:'Weight',access:'Pickup access',flights:'Flights of stairs',elevator:'Elevator available',carry:'Carry distance',disassembly:'Disassembly',tight:'Tight access',material:'Debris material',notes:'Additional details'};
  const notes=estimate?[...Object.entries(estimate).filter(([k])=>!['price','photos'].includes(k)).map(([k,v])=>(labels[k]||k)+': '+v),estimate.price?.amount!=null?'Online estimate: $'+estimate.price.amount+' (subject to approval)'+(changedEstimate?' — pickup details changed; team review needed':''):'Online estimate: team review requested',...(estimate.price?.items||[]),...(estimate.price?.factors||[]),...(estimate.price?.assumptions||[])].join('\n'):'';
  pending={request_id:crypto.randomUUID(),contact_name:d.get('name').trim(),phone:d.get('phone').trim(),email:d.get('email').trim(),address:d.get('address').trim(),city:d.get('city').trim(),area:params.get('area')||estimate?.area||'',pickup_date:selectedDate,pickup_time:selectedTime,items:d.get('items'),payment_preference:d.get('payment'),notes,load_size:estimate?.load||'',heavy_item:estimate?.weight||'',files};
  details.replaceChildren();const dl=document.createElement('dl');for(const [label,value] of [['Date',selectedDate],['Arrival time',selectedTime+' Pacific'],['Name',pending.contact_name],['Phone',pending.phone],['Email',pending.email],['Pickup address',pending.address],['City / ZIP',pending.city],['Area',pending.area],['Items',pending.items],['Payment preference',pending.payment_preference],['Photos',files.length?files.map(f=>f.name).join(', '):'None attached']])dl.append(...row(label,value));
  if(estimate?.price?.low!=null)dl.append(...row(changedEstimate?'Original estimate — items edited; subject to review':'Online estimate','$'+estimate.price.low+(estimate.price.high!==estimate.price.low?'–$'+estimate.price.high:'')));
  if(notes)dl.append(...row('Estimate answers',notes));details.append(dl);result.hidden=false;result.scrollIntoView({behavior:'smooth',block:'center'});
 });
 document.querySelector('#edit-booking').addEventListener('click',()=>{if(!busy){invalidate();form.elements.name.focus()}});
 const readFile=file=>new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve({name:file.name,type:file.type,data:String(reader.result).split(',')[1]});reader.onerror=reject;reader.readAsDataURL(file)});
 confirm.addEventListener('click',async()=>{if(!pending||busy)return;busy=true;confirm.disabled=true;confirm.textContent='Confirming…';const snapshot=pending;form.querySelectorAll('input,textarea,button').forEach(x=>x.disabled=true);
  try{const {files,...payload}=snapshot;payload.photos=await Promise.all(files.map(readFile));const response=await fetch(api,{method:'POST',headers,body:JSON.stringify(payload),signal:AbortSignal.timeout(45000)});const out=await response.json();if(!response.ok)throw Error(out.error||'Please try again.');if(!out.confirmation_number)throw Error('No confirmation received. Please call 626-386-5623 before retrying.');delete payload.photos;try{sessionStorage.setItem('confirmedBooking',JSON.stringify({...payload,photo_names:files.map(f=>f.name),confirmation_number:out.confirmation_number,notification_status:out.notification_status}))}catch{}location.assign('confirmation.html?confirmation='+encodeURIComponent(out.confirmation_number))}
  catch(e){status.textContent=e.name==='TimeoutError'?'Confirmation is taking longer than expected. Retry with the same details, or call 626-386-5623.':e.message;status.scrollIntoView({block:'center'})}
  finally{busy=false;form.querySelectorAll('input,textarea,button').forEach(x=>x.disabled=false);render();paintTimes();confirm.textContent='Confirm details ↗'}
 });render();paintTimes();status.textContent='Choose a day to see available times.';
})();

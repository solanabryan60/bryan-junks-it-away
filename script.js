'use strict';
const header=document.querySelector('header');const nav=document.querySelector('nav');if(header&&nav&&!document.querySelector('#menu-toggle')){const menu=document.createElement('button');menu.id='menu-toggle';menu.className='menu-toggle';menu.type='button';menu.setAttribute('aria-label','Open menu');menu.setAttribute('aria-expanded','false');menu.innerHTML='<span></span><span></span><span></span>';header.insertBefore(menu,nav);menu.addEventListener('click',()=>{const open=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'Close menu':'Open menu')})}
const footerArea=[...document.querySelectorAll('footer span')].find(x=>/Serving SGV/i.test(x.textContent));if(footerArea){footerArea.innerHTML='<a href="san-gabriel-valley.html">SGV</a> · <a href="los-angeles.html">LA</a> · <a href="inland-empire.html">IE</a> · <a href="riverside.html">Riverside</a> · <a href="orange-county.html">OC</a>'}
document.querySelectorAll('.city-toggle').forEach(button=>button.addEventListener('click',()=>{const list=document.getElementById(button.getAttribute('aria-controls'));const open=list.hasAttribute('open');list.toggleAttribute('open',!open);button.setAttribute('aria-expanded',String(!open));if(!open)list.scrollIntoView({behavior:'smooth',block:'nearest'})}));
const calculator=document.querySelector('#calculator');
if(calculator){
 const result=document.querySelector('#price-result');
 calculator.querySelectorAll('#home-size input').forEach(input=>input.disabled=true);
 const otherWrap=document.querySelector('#other-item-wrap');const otherInput=document.querySelector('#other-item');calculator.addEventListener('change',()=>{const show=new FormData(calculator).get('itemType')==='other';if(otherWrap)otherWrap.hidden=!show;if(otherInput){otherInput.disabled=!show;otherInput.required=show}});if(otherInput)otherInput.disabled=true;
 calculator.addEventListener('change',()=>{const home=document.querySelector('#home-size');home.hidden=new FormData(calculator).get('load')!=='home';home.querySelectorAll('input').forEach(input=>input.disabled=home.hidden);result.hidden=true});
 calculator.addEventListener('submit',e=>{
  e.preventDefault();const data=Object.fromEntries(new FormData(calculator));const price=estimatePickup(data);
  document.querySelector('#price-value').textContent=price.low===null?'Let’s review your pickup':price.low===price.high?'$'+price.low:'$'+price.low+'–$'+price.high;
  document.querySelector('#price-note').textContent=price.note;
  const saved={...data,price};delete saved.photos;
  sessionStorage.setItem('pickupEstimate',JSON.stringify(saved));
  const query=new URLSearchParams({city:data.city,area:data.area});document.querySelector('#reserve-estimate').href='schedule.html?'+query;
  result.hidden=false;result.focus();result.scrollIntoView({behavior:'smooth',block:'center'});
 });
 document.querySelector('#edit-estimate').addEventListener('click',()=>{result.hidden=true;calculator.scrollIntoView({behavior:'smooth'})});
}
const booking=document.querySelector('#booking');
let pendingBooking=null;
if(booking){
 const bookingResult=document.querySelector('#booking-result');
 const details=document.querySelector('#booking-details');
 booking.addEventListener('submit',e=>{e.preventDefault();if(!selectedDate||!selectedTime){alert('Choose a day and arrival window first.');return}pendingBooking=new FormData(booking);const d=Object.fromEntries(pendingBooking);details.innerHTML=`<p><strong>${selectedDate} at ${selectedTime}</strong></p><dl><dt>Name</dt><dd>${d.name}</dd><dt>City or ZIP</dt><dd>${d.city}</dd><dt>Phone</dt><dd>${d.phone}</dd><dt>Email</dt><dd>${d.email}</dd><dt>Pickup address</dt><dd>${d.address}</dd><dt>Payment</dt><dd>${d.payment}</dd><dt>Items</dt><dd>${d.items}</dd></dl>`;bookingResult.hidden=false;bookingResult.scrollIntoView({behavior:'smooth',block:'center'});});
 document.querySelector('#edit-booking').addEventListener('click',()=>{bookingResult.hidden=true;booking.scrollIntoView({behavior:'smooth',block:'center'})});
 document.querySelector('#confirm-booking').addEventListener('click',()=>booking.dispatchEvent(new Event('confirmed')));
 render();
}
if(booking){booking.addEventListener('confirmed',async()=>{const d=pendingBooking||new FormData(booking);const payload={contact_name:d.get('name'),phone:d.get('phone'),email:d.get('email'),address:d.get('address'),city:d.get('city'),pickup_date:selectedDate,pickup_time:selectedTime,items:d.get('items'),payment_preference:d.get('payment')};try{const res=await fetch('https://qcscbkzpfvrbmtvhubtg.supabase.co/functions/v1/create-booking',{method:'POST',headers:{'Content-Type':'application/json','apikey':'sb_publishable_qKdJB3Kch41AtT5-AI73Mg_0MJyateY'},body:JSON.stringify(payload)});const out=await res.json();if(res.ok){window.location.href='confirmation.html?confirmation='+encodeURIComponent(out.confirmation_number)}else{alert(out.error||'That time is no longer available.')}}catch(_){/* keep text fallback available */}})}

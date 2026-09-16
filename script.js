'use strict';
const bookingPublicToken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFjc2Nia3pwZnZyYm10dmh1YnRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkzNTkyNzUsImV4cCI6MjEwNDkzNTI3NX0.N_Hb3jNZ2WvMpCTie3jl3qRdjZNj8suW4NfppOd29lU';
const header=document.querySelector('header');const nav=document.querySelector('header nav');if(header&&nav&&!document.querySelector('#menu-toggle')){const menu=document.createElement('button');menu.id='menu-toggle';menu.className='menu-toggle';menu.type='button';menu.setAttribute('aria-label','Open menu');menu.setAttribute('aria-expanded','false');nav.id=nav.id||'primary-nav';menu.setAttribute('aria-controls',nav.id);menu.innerHTML='<span></span><span></span><span></span>';header.insertBefore(menu,nav);const setMenu=open=>{nav.classList.toggle('open',open);menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'Close menu':'Open menu')};menu.addEventListener('click',()=>setMenu(!nav.classList.contains('open')));document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){setMenu(false);menu.focus()}});nav.addEventListener('click',e=>{if(e.target.closest('a'))setMenu(false)})}
const footerArea=[...document.querySelectorAll('footer span')].find(x=>/Serving SGV/i.test(x.textContent));if(footerArea){footerArea.innerHTML='<a href="san-gabriel-valley.html">SGV</a> · <a href="los-angeles.html">LA</a> · <a href="inland-empire.html">IE</a> · <a href="riverside.html">Riverside</a> · <a href="orange-county.html">OC</a>'}
document.querySelectorAll('.city-toggle').forEach(button=>button.addEventListener('click',()=>{const list=document.getElementById(button.getAttribute('aria-controls'));const open=list.hasAttribute('open');list.toggleAttribute('open',!open);button.setAttribute('aria-expanded',String(!open));if(!open)list.scrollIntoView({behavior:'smooth',block:'nearest'})}));
const calculator=document.querySelector('#calculator');
if(calculator){
 const result=document.querySelector('#price-result');
 calculator.addEventListener('change',()=>{const rough=document.querySelector('#rough-size');if(rough){rough.hidden=new FormData(calculator).get('load')!=='unknown';rough.querySelectorAll('input').forEach(x=>x.disabled=rough.hidden)}});
 calculator.querySelectorAll('#home-size input').forEach(input=>input.disabled=true);
 const otherWrap=document.querySelector('#other-item-wrap');const otherInput=document.querySelector('#other-item');calculator.addEventListener('change',()=>{const show=new FormData(calculator).get('itemType')==='other';if(otherWrap)otherWrap.hidden=!show;if(otherInput){otherInput.disabled=!show;otherInput.required=show}});if(otherInput)otherInput.disabled=true;
 calculator.addEventListener('change',()=>{const home=document.querySelector('#home-size');home.hidden=new FormData(calculator).get('load')!=='home';home.querySelectorAll('input').forEach(input=>input.disabled=home.hidden);result.hidden=true});
 calculator.addEventListener('submit',e=>{
  e.preventDefault();const data=Object.fromEntries(new FormData(calculator));const price=estimatePickup(data);
  document.querySelector('#price-value').textContent=price.low===null?'Let’s review your pickup':price.low===price.high?'$'+price.low:'$'+price.low+'–$'+price.high;
  document.querySelector('#price-note').textContent=price.note;
  const saved={...data,price};delete saved.photos;
  sessionStorage.setItem('pickupEstimate',JSON.stringify(saved));
  const query=new URLSearchParams({city:data.city,area:data.area,estimate:'1'});document.querySelector('#reserve-estimate').href='schedule.html?'+query;
  result.hidden=false;result.focus();result.scrollIntoView({behavior:'smooth',block:'center'});
 });
 document.querySelector('#edit-estimate').addEventListener('click',()=>{result.hidden=true;calculator.scrollIntoView({behavior:'smooth'})});
}
if(document.querySelector('#booking')){const script=document.createElement('script');script.src='booking.js';document.head.append(script)}

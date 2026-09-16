'use strict';
const bookingPublicToken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFjc2Nia3pwZnZyYm10dmh1YnRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkzNTkyNzUsImV4cCI6MjEwNDkzNTI3NX0.N_Hb3jNZ2WvMpCTie3jl3qRdjZNj8suW4NfppOd29lU';
const header=document.querySelector('header');const nav=document.querySelector('header nav');if(header&&nav&&!document.querySelector('#menu-toggle')){const menu=document.createElement('button');menu.id='menu-toggle';menu.className='menu-toggle';menu.type='button';menu.setAttribute('aria-label','Open menu');menu.setAttribute('aria-expanded','false');nav.id=nav.id||'primary-nav';menu.setAttribute('aria-controls',nav.id);menu.innerHTML='<span></span><span></span><span></span>';header.insertBefore(menu,nav);const setMenu=open=>{nav.classList.toggle('open',open);menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'Close menu':'Open menu')};menu.addEventListener('click',()=>setMenu(!nav.classList.contains('open')));document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){setMenu(false);menu.focus()}});nav.addEventListener('click',e=>{if(e.target.closest('a'))setMenu(false)})}
const footerArea=[...document.querySelectorAll('footer span')].find(x=>/Serving SGV/i.test(x.textContent));if(footerArea){footerArea.innerHTML='<a href="san-gabriel-valley.html">SGV</a> · <a href="los-angeles.html">LA</a> · <a href="inland-empire.html">IE</a> · <a href="riverside.html">Riverside</a> · <a href="orange-county.html">OC</a>'}
document.querySelectorAll('.city-toggle').forEach(button=>button.addEventListener('click',()=>{const list=document.getElementById(button.getAttribute('aria-controls'));const open=list.hasAttribute('open');list.toggleAttribute('open',!open);button.setAttribute('aria-expanded',String(!open));if(!open)list.scrollIntoView({behavior:'smooth',block:'nearest'})}));
const calculator=document.querySelector('#calculator');
if(calculator){
 const result=document.querySelector('#price-result');
 const conditional=(id,show)=>{const el=document.getElementById(id);if(!el)return;el.hidden=!show;el.querySelectorAll('input,textarea').forEach(x=>x.disabled=!show)};
 const sync=()=>{const d=Object.fromEntries(new FormData(calculator));conditional('home-size',d.load==='home');conditional('fullness-wrap',['quarter','half','threequarters','full','home'].includes(d.load));conditional('stairs-wrap',d.access==='Upstairs');conditional('material-wrap',['yard','construction'].includes(d.itemType));const flights=document.getElementById('flights');flights.required=d.access==='Upstairs'&&d.elevator==='no';flights.disabled=d.access!=='Upstairs'||d.elevator==='yes';result.hidden=true;sessionStorage.removeItem('pickupEstimate');};
 calculator.addEventListener('change',sync);calculator.addEventListener('input',()=>{result.hidden=true;sessionStorage.removeItem('pickupEstimate')});sync();
 calculator.addEventListener('submit',e=>{
  e.preventDefault();const data=Object.fromEntries(new FormData(calculator));const price=estimatePickup(data);
  document.querySelector('#price-value').textContent=price.amount===null?'Let’s fine-tune your quote':'Estimated $'+price.amount;
  document.querySelector('#price-note').textContent=price.note;
  const details=document.querySelector('#price-details');details.replaceChildren();
  for(const [heading,values] of [['Items recognized',price.items],['What shapes your estimate',price.factors],['Please check',price.assumptions]]){if(!values?.length)continue;const h=document.createElement('h3');h.textContent=heading;const ul=document.createElement('ul');values.forEach(value=>{const li=document.createElement('li');li.textContent=value;ul.append(li)});details.append(h,ul)}
  const check=document.createElement('p');check.textContent='Missing an item or a detail? Edit your answers before booking.';details.append(check);
  const saved={...data,price};delete saved.photos;
  sessionStorage.setItem('pickupEstimate',JSON.stringify(saved));
  const query=new URLSearchParams({city:data.city,area:data.area,estimate:'1'});document.querySelector('#reserve-estimate').href='schedule.html?'+query;
  result.hidden=false;result.focus();result.scrollIntoView({behavior:'smooth',block:'center'});
 });
 document.querySelector('#edit-estimate').addEventListener('click',()=>{result.hidden=true;calculator.scrollIntoView({behavior:'smooth'})});
}
if(document.querySelector('#booking')){const script=document.createElement('script');script.src='booking.js';document.head.append(script)}

"use strict";
const contact = window.BRYAN_CONTACT || {};
const phone = /^\+?[\d ()-]{7,22}$/.test(contact.phone || "") ? contact.phone.replace(/[^+\d]/g, "") : "";
const email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact.email || "") ? contact.email : "";
let profile = "";
try { const url = new URL(contact.messageUrl); if(url.protocol === "https:") profile = url.href; } catch {}
const links = document.querySelector("#contact-links");
function link(text, href) { const a=document.createElement("a");a.textContent=text;a.href=href;links.append(a); }
if(phone) {link("Text Bryan: " + contact.phone, "sms:"+phone);link("Call Bryan", "tel:"+phone);}
if(email) link("Email Bryan", "mailto:"+email);
if(profile) link("Message Bryan", profile);
if(phone || email || profile) document.querySelector("#contact-note").textContent="Send your details and photos directly to Bryan, or use the message builder below.";
const form=document.querySelector("#quote-form");
const output=document.querySelector("#message");
const status=document.querySelector("#status");
form.addEventListener("submit",event=>{
 event.preventDefault();const data=new FormData(form);
 const raw=data.get("date");const parts=raw.split("-");const date=parts.length===3 ? `${parts[1]}/${parts[2]}/${parts[0]}` : raw;
 output.value=`Hi Bryan! I'd like a free junk-removal quote.\n\nItems: ${data.get("items").trim()}\nCity / ZIP: ${data.get("city").trim()}\nDesired pickup: ${date}\nAccess: ${data.get("access")}\nNotes: ${data.get("notes").trim() || "None"}\n\nI'll attach photos of everything I want removed. Please confirm the total price and availability.`;
 document.querySelector("#result").hidden=false;
 const send=document.querySelector("#send");send.hidden=!(phone || email || profile);
 if(phone){send.href="sms:"+phone+"?body="+encodeURIComponent(output.value);send.textContent="Open text message";}
 else if(email){send.href="mailto:"+email+"?subject="+encodeURIComponent("Free junk removal quote")+"&body="+encodeURIComponent(output.value);send.textContent="Open email";}
 else if(profile){send.href=profile;send.textContent="Message Bryan";}
 status.textContent="Message prepared, not sent. Copy it or open your message app, attach photos, and send it to Bryan.";output.focus();
});
document.querySelector("#copy").addEventListener("click",async()=>{
 try{await navigator.clipboard.writeText(output.value);status.textContent="Copied! Paste into your conversation with Bryan and attach your photos.";}
 catch{output.focus();output.select();status.textContent="Select and copy the message above, then paste it into your conversation with Bryan.";}
});

document.querySelector("#tire-quote").addEventListener("click",()=>{const items=document.querySelector("#items");if(!items.value.trim()) items.value="Tire pickup — quantity: ";items.focus();});

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
const headers={"content-type":"application/json","Access-Control-Allow-Origin":"https://www.bryanjunksitaway.com","Access-Control-Allow-Headers":"apikey, authorization, content-type","Access-Control-Allow-Methods":"GET, POST, OPTIONS"};
Deno.serve(async (req) => {
  if(req.method === "OPTIONS")return new Response(null,{headers});
  if(req.method === "GET"){
    const date=new URL(req.url).searchParams.get("date");
    if(!/^\d{4}-\d{2}-\d{2}$/.test(date||""))return new Response(JSON.stringify({error:"Invalid date"}),{status:400,headers});
    const db=createClient(Deno.env.get("SUPABASE_URL")!,Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const {data,error}=await db.from("bookings").select("pickup_time").eq("pickup_date",date).in("status",["requested","confirmed"]);
    return new Response(JSON.stringify(error?{error:"Unable to check availability"}:{times:data.map(x=>x.pickup_time)}),{status:error?503:200,headers});
  }
  if (req.method !== "POST") return new Response(JSON.stringify({error:"POST required"}), {status:405,headers});
  try {
    const body = await req.json();
    const required = ["contact_name","phone","email","address","city","pickup_date","pickup_time"];
    if (required.some((k)=>!body[k])) return new Response(JSON.stringify({error:"Please complete all contact and pickup details."}), {status:400,headers});
    const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const {data,error} = await supabase.rpc("create_booking",{p:body});
    if (error) {
      if (error.message.includes("TIME_UNAVAILABLE")) return new Response(JSON.stringify({error:"That time was just taken. Please choose another."}), {status:409,headers});
      throw error;
    }
    const booking = Array.isArray(data) ? data[0] : data;
    const notifyUrl = Deno.env.get("GOOGLE_BOOKING_WEBHOOK_URL");
    if (notifyUrl && booking) {
      const match = String(body.pickup_time).match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
      const hour = match ? (Number(match[1]) % 12) + (match[3].toUpperCase() === "PM" ? 12 : 0) : 9;
      const minute = match ? match[2] : "00";
      const wall= new Date(`${body.pickup_date}T${String(hour).padStart(2,"0")}:${minute}:00Z`);
      const zone=new Intl.DateTimeFormat("en-US",{timeZone:"America/Los_Angeles",timeZoneName:"shortOffset"}).formatToParts(wall).find(p=>p.type==="timeZoneName")!.value;
      const offset=Number(zone.replace("GMT",""));
      const startsAt=new Date(wall.getTime()-offset*3600000).toISOString();
      const endsAt = new Date(new Date(startsAt).getTime() + 60 * 60 * 1000).toISOString();
      const notify = {
        secret:Deno.env.get("GOOGLE_BOOKING_SECRET"),
        booking: {
          id: booking.id,
          confirmation_number: booking.confirmation_number,
          contact_name: body.contact_name,
          phone: body.phone,
          email: body.email,
          address: body.address,
          city: body.city,
          items: body.items,
          notes: body.notes,
          payment_preference: body.payment_preference,
          starts_at: startsAt,
          ends_at: endsAt,
        },
      };
      try { const r=await fetch(notifyUrl,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(notify)});const result=await r.json();if(!result.ok)console.error("Notification delivery failed"); } catch {console.error("Notification delivery unavailable");}
    }
    return new Response(JSON.stringify(data),{status:201,headers});
  } catch (_) { return new Response(JSON.stringify({error:"We couldn't save that booking. Please call Bryan at 626-386-5623."}),{status:500,headers}); }
});

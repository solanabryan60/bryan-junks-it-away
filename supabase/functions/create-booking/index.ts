import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response(JSON.stringify({error:"POST required"}), {status:405,headers:{"content-type":"application/json"}});
  try {
    const body = await req.json();
    const required = ["contact_name","phone","email","address","city","pickup_date","pickup_time"];
    if (required.some((k)=>!body[k])) return new Response(JSON.stringify({error:"Please complete all contact and pickup details."}), {status:400,headers:{"content-type":"application/json"}});
    const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const {data,error} = await supabase.rpc("create_booking",{p:body});
    if (error) {
      if (error.message.includes("TIME_UNAVAILABLE")) return new Response(JSON.stringify({error:"That time was just taken. Please choose another."}), {status:409,headers:{"content-type":"application/json"}});
      throw error;
    }
    const booking = Array.isArray(data) ? data[0] : data;
    const notifyUrl = Deno.env.get("GOOGLE_BOOKING_WEBHOOK_URL");
    if (notifyUrl && booking) {
      const match = String(body.pickup_time).match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
      const hour = match ? (Number(match[1]) % 12) + (match[3].toUpperCase() === "PM" ? 12 : 0) : 9;
      const minute = match ? match[2] : "00";
      const startsAt = `${body.pickup_date}T${String(hour).padStart(2,"0")}:${minute}:00-07:00`;
      const endsAt = new Date(new Date(startsAt).getTime() + 60 * 60 * 1000).toISOString();
      const notify = {
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
      await fetch(notifyUrl, {method:"POST", headers:{"content-type":"application/json"}, body:JSON.stringify(notify)});
    }
    return new Response(JSON.stringify(data),{status:201,headers:{"content-type":"application/json"}});
  } catch (_) { return new Response(JSON.stringify({error:"We couldn't save that booking. Please call Bryan at 626-346-6254."}),{status:500,headers:{"content-type":"application/json"}}); }
});

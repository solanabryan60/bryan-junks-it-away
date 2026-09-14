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
    return new Response(JSON.stringify(data),{status:201,headers:{"content-type":"application/json"}});
  } catch (_) { return new Response(JSON.stringify({error:"We couldn't save that booking. Please call Bryan at 626-346-6254."}),{status:500,headers:{"content-type":"application/json"}}); }
});

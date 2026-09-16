grant select on public.bookings to service_role;
alter table public.bookings add column if not exists request_id uuid unique;
create or replace function public.create_booking(p jsonb) returns jsonb
language plpgsql security definer set search_path=public as $$
declare b public.bookings; request uuid:=(p->>'request_id')::uuid;
begin
 if request is null then raise exception 'REQUEST_ID_REQUIRED'; end if;
 perform pg_advisory_xact_lock(hashtextextended(request::text,0));
 select * into b from bookings where request_id=request;
 if b.id is not null then
   return jsonb_build_object('id',b.id,'confirmation_number',b.confirmation_number,'pickup_date',b.pickup_date,'pickup_time',b.pickup_time);
 end if;
 perform pg_advisory_xact_lock(hashtextextended((p->>'pickup_date')||' '||(p->>'pickup_time'),0));
 if exists(select 1 from bookings where pickup_date=(p->>'pickup_date')::date and pickup_time=p->>'pickup_time' and status in ('requested','confirmed')) then raise exception 'TIME_UNAVAILABLE'; end if;
 insert into bookings(request_id,contact_name,phone,email,address,city,area,pickup_date,pickup_time,items,load_size,heavy_item,notes,payment_preference,photo_names,after_hours_fee)
 values(request,p->>'contact_name',p->>'phone',lower(trim(p->>'email')),p->>'address',p->>'city',p->>'area',(p->>'pickup_date')::date,p->>'pickup_time',p->>'items',p->>'load_size',p->>'heavy_item',p->>'notes',p->>'payment_preference',array(select jsonb_array_elements_text(coalesce(p->'photo_names','[]'::jsonb))),false) returning * into b;
 return jsonb_build_object('id',b.id,'confirmation_number',b.confirmation_number,'pickup_date',b.pickup_date,'pickup_time',b.pickup_time);
end $$;
revoke all on function public.create_booking(jsonb) from public,anon,authenticated;
grant execute on function public.create_booking(jsonb) to service_role;
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
 values('pickup-photos','pickup-photos',false,5242880,array['image/jpeg','image/png','image/webp'])
 on conflict(id) do nothing;

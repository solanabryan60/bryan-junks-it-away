-- Only staff/service-role can record payments, refunds and approved rewards.
create table public.reward_ledger (
 id uuid primary key default gen_random_uuid(),
 customer_email text not null,
 booking_id uuid references public.bookings(id),
 points integer not null,
 reference text not null unique,
 description text not null,
 created_at timestamptz not null default now()
);
create table public.reward_requests (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id),
 tier integer not null check(tier in (25,50,75)),
 cost integer not null check(cost in (10000,25000,40000)),
 status text not null default 'pending' check(status in ('pending','approved','declined')),
 created_at timestamptz not null default now()
);
create unique index one_pending_reward on public.reward_requests(user_id) where status='pending';
alter table public.reward_ledger enable row level security;
alter table public.reward_requests enable row level security;
revoke all on public.reward_ledger,public.reward_requests from anon,authenticated;
grant all on public.reward_ledger,public.reward_requests to service_role;
create function public.customer_dashboard() returns jsonb language plpgsql security definer set search_path=public as $$
declare mail text; uid uuid:=auth.uid();
begin
 select lower(email) into mail from auth.users where id=uid and email_confirmed_at is not null;
 if mail is null then raise exception 'Verify your email first'; end if;
 return jsonb_build_object('balance',coalesce((select sum(points) from reward_ledger where lower(customer_email)=mail),0),
 'bookings',coalesce((select jsonb_agg(x order by x.pickup_date desc) from (select confirmation_number,pickup_date,pickup_time,items,status from bookings where lower(email)=mail) x),'[]'::jsonb),
 'activity',coalesce((select jsonb_agg(x order by x.created_at desc) from (select points,description,created_at from reward_ledger where lower(customer_email)=mail) x),'[]'::jsonb),
 'requests',coalesce((select jsonb_agg(x order by x.created_at desc) from (select tier,status,created_at from reward_requests where user_id=uid) x),'[]'::jsonb));
end $$;
revoke all on function public.customer_dashboard() from public,anon;
grant execute on function public.customer_dashboard() to authenticated;
create function public.request_reward(reward_tier integer) returns void language plpgsql security definer set search_path=public as $$
declare mail text; price integer; balance bigint; uid uuid:=auth.uid();
begin
 select lower(email) into mail from auth.users where id=uid and email_confirmed_at is not null;
 if mail is null then raise exception 'Verify your email first'; end if;
 price:=case reward_tier when 25 then 10000 when 50 then 25000 when 75 then 40000 end;
 if price is null then raise exception 'Invalid reward'; end if;
 perform pg_advisory_xact_lock(hashtextextended(mail,0));
 select coalesce(sum(points),0) into balance from reward_ledger where lower(customer_email)=mail;
 if balance<price then raise exception 'Not enough points'; end if;
 insert into reward_requests(user_id,tier,cost) values(uid,reward_tier,price);
end $$;
revoke all on function public.request_reward(integer) from public,anon;
grant execute on function public.request_reward(integer) to authenticated;
-- Money is recorded in cents; ten points per dollar actually paid, rounded down.
create function public.credit_completed_pickup(job_id uuid, paid_cents integer, payment_reference text) returns void language plpgsql security definer set search_path=public as $$
declare b public.bookings;
begin
 if paid_cents<=0 then raise exception 'Payment must be positive'; end if;
 select * into b from bookings where id=job_id;
 if b.id is null or b.status<>'completed' then raise exception 'Job must be completed'; end if;
 insert into reward_ledger(customer_email,booking_id,points,reference,description)
 values(lower(b.email),b.id,floor(paid_cents/10.0),payment_reference,'Points from completed pickup '||b.confirmation_number);
end $$;
revoke all on function public.credit_completed_pickup(uuid,integer,text) from public,anon,authenticated;
grant execute on function public.credit_completed_pickup(uuid,integer,text) to service_role;
create function public.approve_reward(request_id uuid) returns void language plpgsql security definer set search_path=public as $$
declare r public.reward_requests; mail text; balance bigint;
begin
 select * into r from reward_requests where id=request_id for update;
 if r.id is null or r.status<>'pending' then raise exception 'No pending reward'; end if;
 select lower(email) into mail from auth.users where id=r.user_id;
 perform pg_advisory_xact_lock(hashtextextended(mail,0));
 select coalesce(sum(points),0) into balance from reward_ledger where lower(customer_email)=mail;
 if balance<r.cost then raise exception 'Not enough points'; end if;
 insert into reward_ledger(customer_email,points,reference,description) values(mail,-r.cost,'reward:'||r.id,r.tier||'% reward approved');
 update reward_requests set status='approved' where id=r.id;
end $$;
revoke all on function public.approve_reward(uuid) from public,anon,authenticated;
grant execute on function public.approve_reward(uuid) to service_role;

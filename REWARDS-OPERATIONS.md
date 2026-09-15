# Rewards operations

Customers use the same verified email as their booking. The dashboard only returns that email's pickups, ledger and requests.

10 points per dollar paid; thresholds: 10,000 / 25,000 / 40,000 for 25% / 50% / 75%. Pending requests do not deduct points. Staff must review job size and handling before approving. No automated discount changes an invoice.

## Record points
After confirming payment and marking the booking completed, staff may call `credit_completed_pickup(job_id, paid_cents, payment_reference)` through the Supabase SQL editor. Use the actual paid amount in cents and a unique payment receipt reference. Never include unpaid estimates. Repeating a reference is rejected. Customer credentials cannot call this function.

## Approve a reward
Review the pending row in `reward_requests`. After confirming the eligible job and discount, call `approve_reward(request_id)` in the SQL editor. It rechecks the balance, deducts points, and records approval atomically. To decline, set its status to `declined`; no points were deducted. Customers cannot approve requests.

## Before launch testing
Supabase Auth URL configuration must allow `https://www.bryanjunksitaway.com/account.html`; set Site URL to the production site. Email sign-in must use a configured sender that can deliver to customers. Verify the real email link with the owner before advertising accounts.

No customer payment processor or automatic payment feed is connected. Staff payment recording is required for points. Refunds require a corresponding negative ledger adjustment with a unique refund reference. Merchandise has no products or checkout yet.

# Estimate model — September 16, 2026

Customer results show one planning estimate, not a guaranteed final invoice. Final approval can happen in person, or after the team contacts the customer and sends an invoice for approval. This update changes website copy; it does not automatically create or send invoices.

## Inputs

Main service, written item list, approximate quantity, amount, home size/fullness when relevant, weight, pickup access, elevator/stairs, carry distance, disassembly, tight access, and additional notes. All radio answers start blank. Conditional questions are disabled while hidden. Original descriptions and the estimate breakdown accompany the booking notes.

## Calculation

The existing load bands remain the base reference. Known items use approximate bulky-item equivalents. Those equivalents are interpolated across the owner's load-price anchors; they are planning assumptions rather than measured truck capacity. A selected load establishes a minimum and fullness adjusts the starting point within the band. Common items have planning minimums (for example, couch $150, mattress $95, appliances $135+). Two lightweight chairs with easy access remain $95. Whole studio/one-bedroom cleanouts start at $635, with $90 per additional bedroom and a $175 densely-filled allowance; a larger recognized inventory can increase that amount.

Provisional handling allowances: stairs $25 per flight; indoor or elevator pickup $15; 30–75 foot carry $15; longer carry $35; disassembly $35; tight access $20; heavy item handling $25; light renovation debris $40. These are estimate assumptions introduced with this update, not verified operating costs or guaranteed final charges. Review them against completed jobs and tune `pricing.js` as actual job data becomes available. It is not possible to establish real-world accuracy from software tests alone.

Description recognition is deterministic, not an AI model. It recognizes listed common item names, quantities, and specific handling phrases. Results display recognized items and assumptions for customer review. Unrecognized details remain in the booking notes and require team review. Instructions in text cannot override pricing rules. No customer text is sent to an external AI service.

Dense or hazardous materials, pianos/safes/hot tubs, and items over 200 pounds require review. Small-pickup answers that imply $635+ ask the customer to choose a cleanout size or request team review instead of silently underpricing the job. Large/cleanout selections can produce higher estimates. A typed description alone is not a substitute for photos or a final assessment.

## Checks

Run `node tests/pricing.cjs`, `node tests/estimate-browser.cjs`, and `node tests/expansion-browser.cjs` with the available Node and Playwright runtime. The browser submission is mocked so testing does not create a customer reservation or send email. The build/audit validates all generated site pages.

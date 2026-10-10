---
name: jewelry-research
description: Help someone understand a piece of jewelry or a loose gemstone they own from photos, look at comparable pieces on the market, and save it to their GemstoneAI collection. Use with the GemstoneAI connector when a person shares or describes a specific physical piece and wants to know what it might be, what similar pieces sell for, or wants to keep a record of it.
---

# Jewelry research with GemstoneAI

Use this when a person wants to understand a specific piece they have in hand: an inherited ring, a
pendant from an estate, a loose stone. Do not use it for general jewelry questions, shopping for new
jewelry, or anything that is not about a physical piece the person can photograph.

## 1. Get usable photos

Ask for 1 to 5 photos of the same piece:
- in daylight or by a bright window, no flash
- in focus, with the piece filling most of the frame
- front, side, and a close-up of any stamp inside the band or on the clasp (14K, 585, 750, 925, PT950)

If the person attached photos, pass them to `analyze_jewelry` as `photos`. If they gave public photo
links, pass `image_urls`. If neither works in this app, call `analyze_jewelry` with no photos and share
the `upload_url` it returns; they can open it on their phone and take the photos there.

Each new analysis uses one scan from the person's GemstoneAI plan. Calling again with the same photos
or the same `idempotency_key` returns the same analysis and is not charged twice, so retry freely
after a timeout instead of starting over.

## 2. Run or resume the analysis

If `analyze_jewelry` returns `status: processing` or `awaiting_photos`, call `get_jewelry_analysis`
with the `analysis_id`. It waits up to about 40 seconds per call. Most analyses finish in 20 to 45
seconds.

`not_jewelry` means the photos do not show jewelry or a gemstone. `failed` comes with a message and
`retry_safe`; a plan limit is not retry-safe, so tell the person what the message says.

## 3. Explain it with its uncertainty

Lead with `identification.preliminary`, then say how firm it is. `identification.status` is
`consistent` (repeated reads agreed, which is still not independent confirmation), `unconfirmed`, or
`unsettled` (the reads disagree or the photos could not be read; price is withheld). Use
`identification.basis` for the plain-language reason. Name the `alternatives`. Read out the `unknowns` that matter, and suggest
the `next_evidence` that would settle them, usually better photos, a stamp close-up, or a
gemologist's test.

Never present the result as certain, as an appraisal, or as proof of authenticity, treatment or origin.
GemstoneAI does not give numeric confidence, so do not invent percentages.

## 4. Comparables, only when wanted

Call `find_jewelry_comparables` when the person wants market evidence, for example before deciding
whether to sell, or to sanity-check a value. If it returns `pending` or `partial`, wait
`retry_after_seconds` and call again. `none_found` is missing evidence, not a value of zero.

## 5. Keep price types apart

- `asking_price` is what a seller hopes to get. It is not a sale.
- `realized_sale` is a completed transaction.
- `retail_purchase` is roughly what replacing the piece new would cost.
- `resale_proceeds` is roughly what an owner might be paid. It is usually well below retail and is not an offer.

Read each comparable's `material_differences` before comparing its price to this piece. If
`price_context.status` is `withheld`, say why (the identification is not settled) instead of
guessing a number. For insurance or a sale, recommend an in-person appraisal.

## 6. Save only when asked

Call `save_collection_item` only after the person says they want to keep or save the piece. Then give
them the `reopen_url`. It opens the piece in the GemstoneAI app on their phone when they are signed in
with the same email they used to connect.

# Cross-cutting conventions

> **Reference.** Conventions that apply across endpoints — documented once here instead of repeated per
> endpoint. The pull/polling model (see [overview](../explanation/overview.md#the-pull--polling-model-why-it-matters-everywhere))
> is the reason most of these exist.

## Polling with `changed_since`

The API is consumed by **polling**, not push. List endpoints take a `changed_since` (and on master data,
`changed_until`) timestamp and return items changed in that window.

```
GET /documents?changed_since=2026-01-01T00:00:00Z
GET /realestates?changed_since=2026-01-01T00:00:00Z&changed_until=2026-01-08T00:00:00Z
```

- `changed_since` is **required** on list endpoints; format is RFC 3339 / ISO 8601 date-time.
- Master-data endpoints also require `changed_until` and return items changed in `[changed_since, changed_until)`.
- A poll cycle: store the high-water timestamp, poll with it as `changed_since`, advance it to the
  response's newest change.

## Why no webhooks

There is **no push** from WWImmo to partners — no webhooks, no events. Confirmed with partners (May 2026):
sync happens only via partner-initiated API calls. Design implications below.

## Idempotency

Because partners can re-poll and retry, write operations must be safe to repeat. Treat all calls as
potentially retried; do not build "process exactly once on receipt" logic on the partner side without a
dedup key.

> 🚧 **NEEDS INPUT** — confirm the server's idempotency contract (e.g. an `Idempotency-Key` header on
> `POST /documents`, or natural-key dedup). Not yet in the spec.

## Deletes & tombstones

A hard delete is invisible to a polling partner. The intended pattern is **tombstones**: a deleted record
stays in responses with a `deleted_at` marker until a retention window expires, long enough that even a
partner with a multi-week polling gap sees it.

> 🚧 **NEEDS INPUT** (gap #3) — tombstone fields (`deleted_at`), the retention window, and which entities
> support delete are **not yet in the OpenAPI spec**. Until then, do not assume disappearance = deletion.

## Pagination

> 🚧 **NEEDS INPUT** (gap #4) — list endpoints currently return a bare array with no documented paging.
> Confirm page size, cursor-vs-offset, and the response envelope before integrating against large datasets.

## Rate limits

The token endpoint is limited to **30 req/min per IP**. Data endpoints use rate limiting too.

> 🚧 **NEEDS INPUT** — document the per-endpoint limits and the headers returned on `429` (e.g.
> `Retry-After`, `RateLimit-*`).

## Identifiers & secondary keys

- Primary identifiers are **UUIDs** (`id`, path `{uuid}`).
- Some entities also support a **human-readable secondary key**, e.g.
  `GET /realestates/number:{number}` — inspired by the
  [RESTful secondary key pattern](https://justatheory.com/2022/08/rfc-restful-secondary-key-api/).
- Accounting structures are keyed on **`bookkeepingid`**, not `realestateid` — see
  [domain model](../explanation/domain-model.md#the-anti-corruption-layer-read-this-first).

## Content negotiation

- Request/response bodies are `application/json`.
- Document **file content** (`GET /documents/{uuid}/content`) returns `application/octet-stream`, or a
  `302` redirect when the file is served from a CDN — follow the redirect.

## Errors

All errors use a Problem+JSON body — see [error handling](errors.md).

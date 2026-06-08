# Quick start 🚧

> **Tutorial.** Learning-oriented: the shortest path from zero to "I made the API respond". This is a
> **stub** — it can't be finished until two things are settled (see the blockers at the bottom). The
> skeleton is here so it's ready to fill in.

## What you'll achieve

By the end you'll have: requested a token, polled for documents, and read one document's content.

## 0. What you need

- A `client_id` and `client_secret`. 🚧 **NEEDS INPUT (gap #2):** *how a partner obtains these isn't
  documented yet.*
- The base URL for the environment you're targeting. 🚧 **NEEDS INPUT (gap #1):** *dev/test/prod hosts
  not confirmed* (`erp.wwimmo.ch` in the spec vs `polaris.wwportal-dev.ch` live).

For now, set placeholders:

```bash
BASE_URL="https://<environment-host>/api/v1/dms"   # 🚧 confirm
CLIENT_ID="<your-client-id>"
CLIENT_SECRET="<your-client-secret>"
```

## 1. Get a token

```bash
curl -s -X POST "$BASE_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET"
# → { "access_token": "...", "token_type": "Bearer", "expires_in": ... }
```

Cache the token; the token endpoint is rate-limited to 30 req/min. See
[authentication](../reference/authentication.md).

## 2. Poll for documents

```bash
TOKEN="<access_token from step 1>"
curl -s "$BASE_URL/documents?changed_since=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer $TOKEN"
```

`changed_since` is required. See [conventions](../reference/conventions.md#polling-with-changed_since).

## 3. Read one document's content

```bash
curl -sL "$BASE_URL/documents/<uuid>/content" \
  -H "Authorization: Bearer $TOKEN" -o document.pdf
```

`-L` follows the `302` redirect used when the file is served from a CDN.

## Where to go next

- Pick your flow: [import a document](../how-to/import-a-document.md),
  [import an invoice](../how-to/import-an-invoice.md), or
  [archive a document](../how-to/archive-a-document.md).
- Understand the data: [domain model](../explanation/domain-model.md).

## Blockers to finish this tutorial

1. Confirm the **base URL(s)** per environment (gap #1).
2. Document **credential onboarding** (gap #2).

Once both are known, replace the placeholders above with a real, runnable walkthrough against a sandbox.

# Documentation index

Guided table of contents. New to the API? Read top to bottom. Looking for one thing? Jump to the quadrant.

## 1. Explanation — understand the shape (read first)

- [Overview](explanation/overview.md) — what the API does, who it's for, the three core flows, the pull model.
- [Domain model](explanation/domain-model.md) — entities, relationships, lifecycle, and the anti-corruption layer.
- [Glossary](explanation/glossary.md) — domain vocabulary (German term ↔ English meaning).

## 2. Tutorial — your first success

- [Quick start](tutorials/quickstart.md) 🚧 — get a token and make your first poll. *Needs base URL + credential onboarding.*

## 3. How-to — task-oriented guides

- [Import a document](how-to/import-a-document.md) — DMS → ERP, metadata only.
- [Import an invoice](how-to/import-an-invoice.md) — DMS → ERP → KrediFlow.
- [Archive a document](how-to/archive-a-document.md) — ERP → DMS.

## 4. Reference — the exact contract

- [OpenAPI spec](../openapi/README.md) — the authoritative wire contract.
- [Authentication & authorization](reference/authentication.md) — Cidaas, `client_credentials`, scopes, token endpoint.
- [Cross-cutting conventions](reference/conventions.md) — polling, `changed_since`, tombstones, idempotency, secondary keys.
- [Error handling](reference/errors.md) — Problem+JSON (RFC 9457) response shape and recovery.

## Not yet written (planned)

- **Versioning & changelog** 🚧 — versioning scheme + deprecation policy (gap #6).
- **Webhooks** — *not applicable*: the integration is pull-only. See [conventions](reference/conventions.md#why-no-webhooks).
- **SDKs / code samples** — deferred until base URL + auth onboarding are settled.

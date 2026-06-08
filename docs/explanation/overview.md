# Overview

> **Explanation** — understanding-oriented. Read this before the reference or how-to docs.

## What this API does

The DMS API is a single, unified REST interface that lets an external **Document Management System
(DMS)** exchange documents and the master data around them with a WWImmo-hosted **ERP** (Rimo R5 or
ImmoTop2). The ERP runs in the cloud, so the old database-level integrations (ODBC) no longer work; this
API replaces them.

It is built in the **Polaris stack** (C#, modular monolith, no Hasura) and deliberately implemented as
**REST, not GraphQL** — for a document interface, simple adoption and security matter more than query
flexibility.

## Who it's for

External **partner DMS vendors**. A partner integrates once and then keeps in sync by **polling**. There
is no push from WWImmo to the partner — no webhooks, no events.

## The three core flows

Everything the API does serves one of three flows (the colours match the concept diagram on the wiki):

| Flow | Direction | What moves | Example |
| --- | --- | --- | --- |
| **Import a document** | DMS → ERP | Document is stored in the DMS first; metadata (no file content) is pushed to the ERP, which links it in the E-Dossier. | Scanned creditor invoices/credits, e-bills. |
| **Import an invoice** | DMS → ERP → KrediFlow | Like a document import, plus the ERP processes the invoice through the (adapted) KrediFlow approval workflow. | Supplier invoice that needs visa/approval. |
| **Archive a document** | ERP → DMS | Document is created in the ERP; the DMS pulls metadata (E-Dossier) and the file, archives it, and reports success back. | Booking receipts for manual postings, dunning letters from a dunning run. |

> Opening, viewing and publishing documents in the Portal works as before and is **out of scope** for the
> DMS API.

The step-by-step sequences for each flow are in the [how-to guides](../how-to/). The flows are summarised
here so the reference docs have a shared mental model to point back to.

## The pull / polling model (why it matters everywhere)

Partners consume the API **only by polling** — typically `GET /documents?changed_since=<timestamp>`.
This single architectural fact drives several rules you'll meet again in [conventions](../reference/conventions.md):

- **Deletes need tombstones.** A deleted record must remain visible in responses (e.g. with a
  `deleted_at` marker) until a retention window passes — otherwise a partner that polls infrequently
  never learns it was deleted. 🚧 *Tombstone fields are not yet in the OpenAPI spec — gap #3.*
- **Every mutation needs a timestamp** so `changed_since` can find it.
- **Endpoints must be idempotent.** A partner may re-poll or retry; repeating a call must not double-process.
- **Retention must outlast the worst polling gap.** If a partner can be offline for, say, 30 days,
  tombstones and change history must survive at least that long.

## The anti-corruption layer

The API exposes a **clean, forward-looking domain model** (Portfolio → Bookkeeping → accounts/invoices)
and translates it to the legacy KrediFlow/ERP identifiers internally. The most important example:
at the API surface, `bookkeepingid` replaces the legacy `realestateid` on accounting-related structures,
while the ERP persistence keeps `realestateid` unchanged. Partners code against the new model and are
shielded from ERP internals. Details in the [domain model](domain-model.md).

## Core concepts to hold in your head

- **Document** — a human-readable file (invoice, credit, correspondence, assurance) with metadata,
  storage targets (`DMS`, `ERP`), and links to master-data entities.
- **Master data** — the stable nouns the documents attach to: realestate, house, unit, appliance, tenant,
  tenancy, and (for invoices) creditor, account, bookkeeping.
- **Bookkeeping (`Buchhaltung`)** — the accounting unit that accounting data hangs off in the new model.
- **Portfolio** — groups realestates under an owner; carries the ERP/mandant reference.
- **Storage target** — where a document physically lives: only the DMS, only the ERP, or both.

See the [glossary](glossary.md) for the full vocabulary.

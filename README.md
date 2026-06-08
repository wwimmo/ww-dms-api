# WWImmo DMS API

A unified **REST API** that lets external Document Management Systems (DMS) integrate with WWImmo's
classic ERPs (**Rimo R5** and **ImmoTop2**) once those ERPs are operated ("ghosted") in the cloud.

It replaces the older, database-coupled integrations
([Rimo R5 DMS Schnittstelle](https://github.com/wwimmo/rimor5-dms-schnittstelle),
[ImmoTop2 Schnittstelle](https://github.com/wwimmo/immotop2-dms-schnittstelle)), which relied on direct
ODBC access that is no longer available in the cloud.

> **Status: early / lean.** This repository is the home of the DMS API documentation. The API itself is
> being built in the Polaris stack (C#, modular monolith, REST). The OpenAPI contract is the most mature
> artefact; the hand-written docs below are being filled in. Sections marked **🚧 NEEDS INPUT** are gaps
> we know about — see [What we still need](#what-we-still-need).

## Who this is for

Engineers at **partner DMS vendors** who integrate their product with WWImmo-hosted ERPs. Partners
**poll** this API (pull model) — there are no webhooks or pushes from WWImmo to the partner.

## Three things to understand first

1. **Three core flows.** *Import a document*, *import an invoice*, and *archive a document* — see
   [Use cases](docs/explanation/overview.md#the-three-core-flows).
2. **Pull / polling model.** Partners discover changes by polling with `?changed_since=...`. This shapes
   everything: deletes need tombstones, every mutation needs a timestamp, endpoints must be idempotent.
   See [Conventions](docs/reference/conventions.md).
3. **The API is an anti-corruption layer.** It speaks a clean, forward-looking domain model
   (Portfolio → Bookkeeping → …) and translates to the legacy ERP/KrediFlow IDs internally. See
   [Domain model](docs/explanation/domain-model.md).

## Documentation map (Diátaxis)

This documentation is organised on the [Diátaxis](https://diataxis.fr/) model — four kinds of docs, each
answering a different question:

| Quadrant | Question it answers | Where |
| --- | --- | --- |
| **Tutorial** (learning) | "Get me to my first success" | [docs/tutorials/quickstart.md](docs/tutorials/quickstart.md) 🚧 |
| **How-to** (task) | "How do I do X?" | [docs/how-to/](docs/how-to/) — import document / import invoice / archive |
| **Reference** (information) | "What exactly is the contract?" | [OpenAPI spec](openapi/) + [docs/reference/](docs/reference/) |
| **Explanation** (understanding) | "Why is it shaped this way?" | [docs/explanation/](docs/explanation/) — overview, domain model, glossary |

Start at [docs/index.md](docs/index.md) for the guided table of contents.

## Source material this is built from

- **OpenAPI contract** — generated from the running service. See [openapi/](openapi/README.md).
- **Live Swagger UI** — <https://polaris.wwportal-dev.ch/swagger/index.html> (dev environment).
- **Concept & flows** — ADO Wiki [Konzept DMS-API-Design (1241)](https://dev.azure.com/wwimmo-mobile/mobile/_wiki/wikis/mobile.wiki/1241/Konzept-DMS-API-Design).
- **Domain model** — ADO Wiki [Domänenmodell (1231)](https://dev.azure.com/wwimmo-mobile/mobile/_wiki/wikis/mobile.wiki/1231/Dom%C3%A4nenmodell).
- **Endpoint / data structure** — ADO Wiki [Endpoint-Struktur (2476)](https://dev.azure.com/wwimmo-mobile/mobile/_wiki/wikis/mobile.wiki/2476/Endpoint-Struktur-(Portfolio-Bookkeeping)).
- **Design board** — [Miro](https://miro.com/app/board/uXjVMhPcv8o=/).

## What we still need

These are the critical blocks to make this a usable partner-facing doc set. Tracked inline as
**🚧 NEEDS INPUT** in the relevant files.

| # | Gap | Where it blocks | Who can provide |
| --- | --- | --- | --- |
| 1 | **Base URLs per environment** (dev/test/prod). Spec says `erp.wwimmo.ch/api/v1/dms`; live POC is `polaris.wwportal-dev.ch`. | quickstart, auth | Gabor Raz / DevOps |
| 2 | **How a partner obtains `client_id` / `client_secret`** (onboarding flow, who issues them). | auth, quickstart | Sandro Brunner (Cidaas) |
| 3 | **Tombstone / delete semantics** confirmed in the spec (`deleted_at`, retention window). | conventions, OpenAPI | Andrew Service / Martin Constam |
| 4 | **Pagination & rate-limit contract** (page size, cursor vs offset, limit headers). | conventions, OpenAPI | Backend team |
| 5 | **Error catalogue** — concrete `type` values and recovery advice beyond the Problem shape. | errors | Backend team |
| 6 | **Versioning & deprecation policy** for the API and this doc set. | (new) versioning doc | PO + Backend |
| 7 | **Open domain decisions** that change the contract: `vatcodes` "code for all", `realestatevisas` scope, scope-via-path-vs-payload. | domain-model, OpenAPI | Domain workshops (PSI) |
| 8 | **Invoice / master-data schemas in OpenAPI** (accounts, cost centers, creditors) — currently only in the wiki, not the spec. | OpenAPI, import-an-invoice | Backend team |

## Conventions for editing these docs

- Markdown, one concept per file. Keep the Diátaxis quadrants separate — don't let a how-to become a reference dump.
- The **OpenAPI spec is the single source of truth** for the wire contract. Hand-written docs explain
  *meaning, relationships, lifecycle* — things OpenAPI can't carry well — and link to the spec rather than
  duplicating field tables.
- Mark anything unverified with **🚧 NEEDS INPUT** so gaps stay visible.

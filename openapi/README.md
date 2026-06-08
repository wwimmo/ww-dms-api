# OpenAPI reference (the wire contract)

The **OpenAPI specification is the single source of truth** for the wire contract — paths, methods,
request/response schemas, field types. The hand-written docs in [../docs/](../docs/) explain *meaning,
relationships and lifecycle* and link here rather than duplicating field tables.

## Where the spec lives

- **Live Swagger UI (dev):** <https://polaris.wwportal-dev.ch/swagger/index.html>
- **Generated from:** the running DMS module in the Polaris backend
  (`poc-polaris-backend/backend/DokumentManagementSystem`). The hand-authored draft contract is
  `dms-api.yaml` in that module.

We intentionally **do not vendor a copy here yet** to avoid drift while the spec is changing fast. At the
first stable release, snapshot the spec into this folder as `dms-api.v1.yaml` and version it alongside the
docs (see versioning gap #6).

## What the spec covers today

- `POST /documents`, `GET /documents` (requires `changed_since`), `GET /documents/{uuid}`,
  `PUT /documents/{uuid}`, `GET /documents/{uuid}/content`.
- Master data (`GET`, with `changed_since` + `changed_until`): `/realestates` (+ `/{uuid}`,
  `/number:{number}`), `/houses`, `/units`, `/appliances`, `/tenants`, `/tenancies` (+ `/{uuid}`).
- Schemas: `DocumentEntity`, `DocumentLinkEntity`, `RealestateEntity`, list wrappers, `Problem`.
- Security: `bearerAuth` (JWT). See [authentication](../docs/reference/authentication.md).

## Known gaps in the spec (from the spec's own `info.description` + our review)

- 🚧 **Invoice flow & accounting master data** (accounts, cost centers, creditors, vatcodes, invoices) —
  defined in the [Endpoint-Struktur wiki](https://dev.azure.com/wwimmo-mobile/mobile/_wiki/wikis/mobile.wiki/2476/Endpoint-Struktur-(Portfolio-Bookkeeping)) but **not yet in the spec** (gap #8).
- 🚧 **Delete / replace / file versioning** of documents — open question in the spec.
- 🚧 **Per-entity attribute completeness**, **tombstones** (`deleted_at`), **pagination**, **rate-limit
  responses** — see [conventions](../docs/reference/conventions.md).
- The spec notes barcode/filedate/archiveid/linkid attributes are still under discussion.

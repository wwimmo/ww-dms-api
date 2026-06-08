# Domain model

> **Explanation** — understanding-oriented. This is the conceptual map that the OpenAPI reference can't
> carry: what the entities *mean*, how they *relate*, and how the API translates to the legacy ERP.
>
> Sources: ADO Wiki [Domänenmodell (1231)](https://dev.azure.com/wwimmo-mobile/mobile/_wiki/wikis/mobile.wiki/1231/Dom%C3%A4nenmodell)
> (fachliche Sicht) and [Endpoint-Struktur (2476)](https://dev.azure.com/wwimmo-mobile/mobile/_wiki/wikis/mobile.wiki/2476/Endpoint-Struktur-(Portfolio-Bookkeeping)) (endpoint shape).

## Two layers: domain model vs. data model

- **Domain model** = the business view: concepts and relationships, independent of storage.
- **Data model / schema** = the technical view: tables, columns, types, keys.

This page describes the **domain model** and the parts of the endpoint shape a partner needs. Field-level
types live in the [OpenAPI spec](../openapi/README.md).

## The anti-corruption layer (read this first)

The API does **not** expose the ERP's internal model directly. It translates:

- At the endpoint, **`bookkeepingid` replaces the legacy `realestateid`** on accounting-related
  structures (accounts, vatcodes, accountings_history, invoices). The DMS API maps this back to the
  existing KrediFlow IDs; **KrediFlow persistence keeps `realestateid` unchanged**.
- On `realestates`, the old consolidation logic (`consolidation`, `consolidationid`) is **gone from the
  endpoint** — grouping now runs through `portfolioid`.
- `hash` (internal change-tracking) is **never** sent at the endpoint.
- At the endpoint, `portfolioid` and `bookkeepingid` are **not null**. (The "null allowed" transition
  phase for portals without portfolios is an internal persistence concern, not part of the contract.)

**Why:** the API is long-lived and integrated on the partner side. A later structural change would force
every partner to rewrite. So the domain model leads and the API conforms to it — not the other way round.

## Master-data entities (Stammdaten / `common`)

The stable nouns. One line each — see the wiki for full attribute tables.

| Entity | German | What it is |
| --- | --- | --- |
| **Portfolio** | Portfolio | A managed grouping of realestates owned by one owner. Carries the ERP reference: `Portfolio.number` = IT2 Mandant-Nr. |
| **Owner** | Eigentümer | The party legally responsible for a property; bears income and cost; commissions management. Is-a `Person`. |
| **Management** | Verwaltung | The organisation that operates/manages properties. |
| **RealEstate** | Liegenschaft | A legally/economically delimited property; the basis for all management processes. Belongs to exactly one portfolio. |
| **House** | Haus | A physical building within a realestate; contains units. |
| **Unit** | Mietobjekt / Objekt | The smallest billable rentable unit. Belongs to exactly one realestate (and, if a flat, one house). |
| **Appliance** | Gerät | A serviceable device attached to a realestate/unit. |
| **Tenancy** | Mietverhältnis | A lease relationship linking a unit and a tenant over time. |
| **Tenant** | Mieter | The renting party (is-a `Person` via link). |
| **Person** | Person | A natural/legal person; the contact root behind owners, tenants, etc. |

### Relationships (cardinality)

```
Owner 1 ──< Portfolio 1 ──< RealEstate 1 ──< House 1 ──< Unit
                              RealEstate 1 ──< Unit            (units belong directly to the realestate too)
                              RealEstate ──< Appliance, Tenancy, Maintenance
RealEstate >── 1 Management   (is_managed_by)
Unit 1 ──< Tenancy >── 1 Tenant ──> Person
```

- A **Portfolio** has many **RealEstates**; each RealEstate belongs to exactly one Portfolio and is
  managed by exactly one Management.
- A **RealEstate** consists of one or more **Houses** and one or more **Units**.
- A **Tenancy** links one **Unit** to one **Tenant**; a Tenant resolves to a **Person**.

## Accounting entities (`cred`)

Used by the invoice-import flow. At the endpoint these hang off **`bookkeepingid`**, not `realestateid`.

| Entity | What it is | Key change at endpoint |
| --- | --- | --- |
| **Bookkeeping** (`Buchhaltung`) | The accounting unit; links to a Portfolio. | New entity; the anchor for accounting data. |
| **Creditor** (`Kreditor`) | A supplier. | Unchanged — portfolio/bookkeeping-independent. |
| **PaymentAccount** | A creditor's pay-to connection (IBAN). | Unchanged. |
| **PayoutBankAccount** (+ bridge) | Pay-from connection per bookkeeping. | **Replaces** the old `payoutaccounts`. |
| **Account** (`Konto`) | A bookkeeping account. | `realestateid` → `bookkeepingid`. |
| **CostCenter** (`Kostenstelle`) | Cost center (IT2 only). | Unchanged. |
| **VatCode** (`MWST-Code`) | VAT code. | `realestateid` → `bookkeepingid` (see open point below). |
| **Invoice** (`Rechnung`) | An invoice or credit note flowing through KrediFlow. | `realestateid` → `bookkeepingid`; `payoutaccountid` → `payoutbankaccountid`. |
| **Accounting** (`Kontierung`) | A posting line on an invoice. | No `bookkeepingid` needed — derivable via `invoiceid` / `accountid`. |
| **RealestateVisa** (`Visumspfad`) | Approval/visa path. | **Open**: stays `realestateid`, or moves to `bookkeepingid`/`portfolioid`? |

> 🚧 **NEEDS INPUT — accounting schemas are not in the OpenAPI spec yet** (gap #8). Today only documents
> and the `common` master data (realestates, units, etc.) are in the spec; the `cred` entities above live
> only in the wiki. The invoice-import flow can't be fully documented as reference until they land.

## Document model

A **Document** (`DocumentEntity`) is "a human-readable file". Key fields:

- `id` (uuid), `name`, `filedate`, `mime-type`, `extention`, `url`, `barcode`.
- `type` — enum: `invoice` | `credit` | `correspondence` | `assurance`.
- `storageTargets` — array of `DMS` | `ERP`: where the file physically lives.
- `dmsReference` — `{ archive, documentId }`: the back-reference written once the DMS has archived it.
- `links` — array of `DocumentLinkEntity` `{ id, entity-type }` connecting the document to master data
  (`realestate`, `house`, `unit`, `appliance`, `tenant`, `tenancy`).

### Document lifecycle (state, informal)

The spec doesn't yet model an explicit `state` enum on documents, but the flows imply a lifecycle:

```
(import)   created in DMS → metadata POSTed to ERP → linked in E-Dossier
(archive)  created in ERP → pulled by DMS → archived in DMS → dmsReference written back (PUT) → optionally removed from ERP
```

> 🚧 **NEEDS INPUT** — confirm whether documents carry an explicit status, and whether delete/replace/
> versioning is supported (the spec's own `info.description` lists these as open: *"Delete document and/or
> replace document and/or file versioning?"*).

## Open domain decisions that affect the contract

These are gating decisions — they change field shapes or endpoint structure, so partners should not hard-code around them yet:

- **`vatcodes` "code for all"** — legacy `realestateid` was nullable (null = applies to all). The endpoint
  forbids null `bookkeepingid`, so how "applies to all bookkeepings" is expressed is open.
- **`realestatevisas` scope** — per realestate today; may move to `bookkeepingid` or `portfolioid`.
- **Scope via path vs. payload** — whether `bookkeepingid`/`portfolioid` are payload fields or path
  parameters (e.g. `GET /bookkeepings/{id}/accounts`). The wiki currently shows them as fields.

See the [glossary](glossary.md) for term definitions.

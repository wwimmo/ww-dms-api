# Glossary

Domain vocabulary, German ↔ English. The codebase and ERPs are German; partner-facing docs are English.
Where our usage differs from the obvious meaning, that's called out.

| Term (DE) | Term (EN) | Meaning |
| --- | --- | --- |
| Liegenschaft | RealEstate | A legally/economically delimited property; basis for all management processes. |
| Haus | House | A physical building within a realestate. |
| Mietobjekt / Objekt | Unit | Smallest billable rentable unit (flat, commercial space, …). |
| Gerät | Appliance | A serviceable device attached to a realestate/unit. |
| Mietverhältnis | Tenancy | Lease relationship linking a unit and a tenant over time. |
| Mieter | Tenant | The renting party. |
| Eigentümer | Owner | Party legally responsible for a property; bears income/cost. |
| Verwaltung | Management | Organisation that operates/manages properties. |
| Portfolio | Portfolio | Grouping of realestates under one owner; carries the ERP/mandant reference. |
| Mandant | (Owner, Portfolio) tuple | The IT2 "client". Not a separate model construct — `Portfolio.number` carries the IT2 Mandant-Nr. |
| Buchhaltung | Bookkeeping | The accounting unit; anchor for accounting data at the endpoint (`bookkeepingid`). |
| Kreditor | Creditor | A supplier. Portfolio/bookkeeping-independent. |
| Zahlstelle / Zahlverbindung | PaymentAccount / PayoutBankAccount | Pay-to (creditor) and pay-from (bookkeeping) bank connections. |
| Konto | Account | A bookkeeping account. |
| Kostenstelle | CostCenter | Cost center (IT2 only). |
| MWST-Code | VatCode | VAT code. |
| Rechnung | Invoice | An invoice or credit note processed via KrediFlow. |
| Gutschrift | Credit (note) | A credit; a document `type` value. |
| Kontierung | Accounting | A posting line on an invoice. |
| Visum / Visumspfad | Visa / RealestateVisa | Approval step / approval path in the invoice workflow. |
| E-Dossier | E-Dossier | The ERP's per-object electronic document file where documents are linked. |
| KrediFlow | KrediFlow | WWImmo's invoice-approval workflow engine; the invoice-import flow feeds an adapted KrediFlow. |
| Stammdaten | Master data | Stable, long-lived reference data (the nouns documents attach to). |
| DMS | DMS | The external Document Management System (the partner's product). |
| ERP | ERP | Rimo R5 or ImmoTop2, operated in the cloud. |

## Cross-cutting terms

- **Ghosting** — running a classic on-prem ERP in the cloud so it can be reached via API.
- **Anti-corruption layer (ACL)** — the API's translation between its clean domain model and legacy ERP IDs.
- **Tombstone** — a record kept visible after deletion (e.g. `deleted_at`) so polling partners learn of the delete.
- **Storage target** — where a document physically lives: `DMS`, `ERP`, or both.
- **`changed_since`** — the polling cursor: "give me everything changed at/after this timestamp".
- **Secondary key** — a human-readable lookup key (e.g. realestate `number`) usable in place of the uuid.

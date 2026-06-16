# OpenAPI-Referenz (der Wire-Vertrag)

Die **OpenAPI-Spezifikation ist die einzige Quelle der Wahrheit** für den Wire-Vertrag – Pfade, Methoden,
Request-/Response-Schemas, Feldtypen. Die handgeschriebene Doku unter [../docs/](../docs/) erklärt
*Bedeutung, Beziehungen und Lebenszyklus* und verweist hierher, statt Feldtabellen zu duplizieren.

Die Spezifikation liegt als [`dms-api.v1.yaml`](dms-api.v1.yaml) vor und wird aus dem laufenden Dienst
generiert.

## Anzeigen

- **Online (Swagger UI):** <https://wwimmo.github.io/ww-dms-api/> – wird per GitHub Pages aus dieser
  Spezifikation veröffentlicht (siehe `.github/workflows/pages.yml`), **sobald das Repository öffentlich
  und Pages aktiviert ist**.
- In VS Code mit einer OpenAPI-/Swagger-Vorschau-Erweiterung.
- Lokal als HTML, z. B. `npx @redocly/cli preview-docs openapi/dms-api.v1.yaml`.

## Was die Spezifikation abdeckt

- **Dokumente:** `POST /documents`, `GET /documents` (erfordert `changed_since`),
  `GET /documents/{uuid}`, `PUT /documents/{uuid}`, `DELETE /documents/{uuid}`,
  `GET /documents/{uuid}/content`.
- **Stammdaten** (`GET`, mit `changed_since` + `changed_until`, paginiert): `/realestates`
  (+ `/{uuid}`, `/number:{number}`), `/portfolios` (+ `/{uuid}`), `/houses`, `/units`, `/appliances`,
  `/tenants`, `/tenancies` (+ `/{uuid}`), `/persons`, `/users`, `/realestate-persons`,
  `/realestate-users`, `/tenancy-persons`.
- **Buchhaltung & Rechnungen (Kreditorenprozess):** `/bookkeepings` (+ `/{uuid}`), `/creditors`
  (GET/POST, + `/{uuid}`), `/accounts` (GET/POST), `/payment-accounts`, `/payoutbankaccounts`,
  `/payoutbankaccountbookkeepings`, `/cost-centers`, `/account-cost-centers`, `/vat-codes`,
  `/accountings-history`, `/realestate-visas`, `/orders` (+ `/{uuid}`), `/invoices`
  (GET/POST, + `/{uuid}` GET/DELETE).
- **Betrieb:** `GET /health`, `GET /info`, `POST /token` (Authentifizierung).
- **Querschnitt:** Paginierung (`page`, `page_size`, `Link`-Header), Rate-Limit-Header
  (`X-RateLimit-*`, `Retry-After`), `bearerAuth` (JWT). Siehe
  [Authentifizierung](../docs/3-referenz/1-authentifizierung.md) und
  [Konventionen](../docs/3-referenz/2-konventionen.md).

## Noch nicht im Vertrag modelliert

- **Fehler-Body als eigenes Schema.** Fehler werden heute über Statuscodes beschrieben; das
  Antwortformat ist in [Fehlerbehandlung](../docs/3-referenz/3-fehler.md) dokumentiert, aber noch nicht
  als `Problem`-Schema in der Spezifikation hinterlegt.
- **Löschungen / Aufbewahrung.** `DELETE` ist als Soft-Delete umgesetzt (204). Wie gelöschte Datensätze
  über das Polling sichtbar werden (Markierung, Aufbewahrung), wird derzeit erarbeitet – siehe
  [Konventionen](../docs/3-referenz/2-konventionen.md#löschungen).

> `enum`-Werte einzelner String-Felder (z. B. Dokument-`type`, Verknüpfungs-`entity-type`,
> `storageTargets`) sind in der Spezifikation als `string` typisiert; die gültigen Werte stehen im
> [Domänenmodell](../docs/4-konzepte/1-domaenenmodell.md) und in den
> [Anleitungen](../docs/2-anleitungen/).

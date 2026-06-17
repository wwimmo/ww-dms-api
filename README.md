# W&W Immo DMS-API

Eine einheitliche **REST-API**, über die Dokumentenmanagement-Systeme (DMS) mit den in der Cloud
betriebenen ERP-Systemen **Rimo R5** und **ImmoTop2** von W&W Immo Informatik AG zusammenarbeiten.

## Geltungsbereich

Diese API gilt für Kunden, deren ERP **in der Cloud betrieben** wird. Sie ersetzt die bestehenden
Schnittstellen **nicht**: Kunden mit einer **On-Premise-Installation** nutzen weiterhin die bisherigen
DMS-Schnittstellen, da diese auf direktem Datenbankzugriff beruhen, der in der Cloud nicht zur Verfügung
steht.

## Für wen ist diese Dokumentation?

Für **DMS-Anbieter**, die ihr Produkt an ein cloud-betriebenes W&W-Immo-ERP anbinden. Die Anbindung
erfolgt über **Polling**: Ihr System ruft die API aktiv ab (Pull). Es gibt keine Webhooks oder Pushes.

## Drei Dinge, die man zuerst verstehen sollte

1. **Drei Kernabläufe** – *Dokument importieren*, *Rechnung importieren* und *Dokument archivieren*.
   Siehe [Übersicht](docs/1-einstieg/1-uebersicht.md).
2. **Pull-/Polling-Modell** – Änderungen werden über `?changed_since=...` abgerufen. Siehe
   [Konventionen](docs/3-referenz/2-konventionen.md).
3. **Klares Domänenmodell** – die API spricht ein eigenständiges Fachmodell (Portfolio → Buchhaltung → …)
   und ist von ERP-Interna entkoppelt. Siehe [Domänenmodell](docs/4-konzepte/1-domaenenmodell.md).

## Inhalt

**1 – Einstieg**
- [Übersicht](docs/1-einstieg/1-uebersicht.md) – was die API tut, die drei Kernabläufe, das Pull-Modell.
- [Schnellstart](docs/1-einstieg/2-schnellstart.md) – Token holen und erste Abfrage. *(in Arbeit)*

**2 – Anleitungen**
- [Dokument importieren](docs/2-anleitungen/1-dokument-importieren.md) – DMS → ERP.
- [Rechnung importieren](docs/2-anleitungen/2-rechnung-importieren.md) – DMS → ERP → Freigabe.
- [Dokument archivieren](docs/2-anleitungen/3-dokument-archivieren.md) – ERP → DMS.

**3 – Referenz**
- [OpenAPI-Referenz](#openapi-referenz) – Spezifikation, Abdeckung, Anzeige.
- [Authentifizierung](docs/3-referenz/1-authentifizierung.md) – OAuth 2.0, Token, Scope.
- [Konventionen](docs/3-referenz/2-konventionen.md) – Polling, `changed_since`, Idempotenz, Schlüssel.
- [Fehlerbehandlung](docs/3-referenz/3-fehler.md) – Problem+JSON.

**4 – Konzepte**
- [Domänenmodell](docs/4-konzepte/1-domaenenmodell.md) – Entitäten, Beziehungen, Lebenszyklus.
- [Glossar](docs/4-konzepte/2-glossar.md) – Fachbegriffe.

**Ausprobieren**
- [Bruno-Collection](bruno/README.md) – einsatzbereite Beispiel-Requests für alle Endpunkte
  (Token holen, Stammdaten, Finanzstammdaten, Buchungskreise, Rechnungen) zum direkten Testen.

## OpenAPI-Referenz

Die **OpenAPI-Spezifikation ist die einzige Quelle der Wahrheit** – Pfade, Methoden, Request-/Response-Schemas,
Feldtypen. Die handgeschriebene Doku unter [docs/](docs/) erklärt Bedeutung, Beziehungen und Lebenszyklus und
verweist hierher, statt Feldtabellen zu duplizieren.

Die Spezifikation liegt als [`openapi/dms-api.v1.yaml`](openapi/dms-api.v1.yaml) vor und wird aus dem
laufenden Dienst generiert.

### Anzeigen

- **Online (Swagger UI):** <https://wwimmo.github.io/ww-dms-api/> – wird per GitHub Pages aus dieser
  Spezifikation veröffentlicht (siehe `.github/workflows/pages.yml`), sobald das Repository öffentlich und
  Pages aktiviert ist.
- In VS Code mit einer OpenAPI-/Swagger-Vorschau-Erweiterung.
- Lokal als HTML, z. B. `npx @redocly/cli preview-docs openapi/dms-api.v1.yaml`.

### Was die Spezifikation abdeckt

- **Dokumente:** `POST /documents`, `GET /documents` (erfordert `changed_since`), `GET /documents/{uuid}`,
  `PUT /documents/{uuid}`, `DELETE /documents/{uuid}`, `GET /documents/{uuid}/content`.
- **Stammdaten** (`GET`, mit `changed_since` + `changed_until`, paginiert): `/realestates`
  (+ `/{uuid}`, `/number:{number}`), `/portfolios` (+ `/{uuid}`), `/houses`, `/units`, `/appliances`,
  `/tenants`, `/tenancies` (+ `/{uuid}`), `/persons`, `/users`, `/realestate-persons`,
  `/realestate-users`, `/tenancy-persons`.
- **Buchhaltung & Rechnungen (Kreditorenprozess):** `/bookkeepings` (+ `/{uuid}`), `/creditors`
  (GET/POST, + `/{uuid}`), `/accounts` (GET/POST), `/payment-accounts`, `/payoutbankaccounts`,
  `/payoutbankaccountbookkeepings`, `/cost-centers`, `/account-cost-centers`, `/vat-codes`,
  `/accountings-history`, `/orders` (+ `/{uuid}`), `/invoices` (GET/POST, + `/{uuid}` GET/DELETE).
- **Betrieb:** `GET /health`, `GET /info`, `POST /token` (Authentifizierung).
- **Querschnitt:** Paginierung (`page`, `page_size`, `Link`-Header), Rate-Limit-Header
  (`X-RateLimit-*`, `Retry-After`), `bearerAuth` (JWT). Siehe
  [Authentifizierung](docs/3-referenz/1-authentifizierung.md) und
  [Konventionen](docs/3-referenz/2-konventionen.md).

### Noch nicht im Vertrag modelliert

- **Löschungen / Aufbewahrung.** `DELETE` ist als Soft-Delete umgesetzt (204). Wie gelöschte Datensätze
  über das Polling sichtbar werden (Markierung, Aufbewahrung), wird derzeit erarbeitet – siehe
  [Konventionen](docs/3-referenz/2-konventionen.md#löschungen).

> `enum`-Werte einzelner String-Felder (z. B. Dokument-`type`, Verknüpfungs-`entity-type`,
> `storageTargets`) sind in der Spezifikation als `string` typisiert; die gültigen Werte stehen im
> [Domänenmodell](docs/4-konzepte/1-domaenenmodell.md) und in den [Anleitungen](docs/2-anleitungen/).

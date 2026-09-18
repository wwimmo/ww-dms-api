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
- [Schnellstart](docs/1-einstieg/2-schnellstart.md) – Erreichbarkeit, Token, erste Abfragen.

**2 – Anleitungen**
- [Dokument importieren](docs/2-anleitungen/1-dokument-importieren.md) – DMS → ERP.
- [Rechnung importieren](docs/2-anleitungen/2-rechnung-importieren.md) – DMS → ERP zur Verbuchung.
- [Dokument archivieren](docs/2-anleitungen/3-dokument-archivieren.md) – ERP → DMS.

**3 – Referenz**
- [OpenAPI-Referenz](#openapi-referenz) – Spezifikation, Abdeckung, Anzeige, Version.
- [Authentifizierung](docs/3-referenz/1-authentifizierung.md) – OAuth 2.0, Token, Scope, Zugangsdaten.
- [Konventionen](docs/3-referenz/2-konventionen.md) – Polling, `changed_since`, PATCH/PUT, Idempotenz, Löschungen.
- [Fehlerbehandlung](docs/3-referenz/3-fehler.md) – Problem+JSON und die Ausnahmen.

**4 – Konzepte**
- [Domänenmodell](docs/4-konzepte/1-domaenenmodell.md) – Entitäten, Beziehungen, Lebenszyklus.
- [Glossar](docs/4-konzepte/2-glossar.md) – Fachbegriffe.

**Änderungen**
- [CHANGELOG](CHANGELOG.md) – was sich wann am Vertrag geändert hat, inkl. Deprecation-Regel.

## Ausprobieren

- **Sandbox = Test-Umgebung** (`https://erp-test.wwimmo.net`): Sie erhalten einen eigenen Test-Mandanten
  und eigene Zugangsdaten (siehe [Zugangsdaten erhalten](docs/3-referenz/1-authentifizierung.md#zugangsdaten-erhalten-kontakt-aufnehmen))
  und arbeiten gegen echte Endpunkte. Auf Produktion gibt es bewusst keine Swagger UI.
- **Swagger UI** auf GitHub Pages, zeigt auf Test – siehe [Anzeigen](#anzeigen).
- **[Bruno-Collection](bruno/README.md)** – einsatzbereite Beispiel-Requests für Token, Stammdaten,
  Finanzstammdaten, Buchhaltungen (Buchungskreise), Rechnungen und Dokumente; die Umgebung `Vorlage` zeigt
  bereits auf Test.

## OpenAPI-Referenz

Die **OpenAPI-Spezifikation ist die einzige Quelle der Wahrheit** – Pfade, Methoden, Request-/Response-Schemas,
Feldtypen. Die handgeschriebene Doku unter [docs/](docs/) erklärt Bedeutung, Beziehungen und Lebenszyklus und
verweist hierher, statt Feldtabellen zu duplizieren.

Die Spezifikation liegt als [`openapi/dms-api.v1.yaml`](openapi/dms-api.v1.yaml) vor (daneben das
Roh-JSON [`openapi/dms-api.v1.json`](openapi/dms-api.v1.json)). Sie wird **aus dem Build des Dienstes
generiert** – Beschreibungen und Statuscodes stammen aus dem Code – und bei jeder Vertragsänderung von der
Build-Pipeline als Review-PR in dieses Repository gespielt (siehe `.github/workflows/openapi-sync.yml`).
Niemand pflegt sie von Hand.

### Anzeigen

1. **Online – Swagger UI auf GitHub Pages:** <https://wwimmo.github.io/ww-dms-api/>. Im **Servers**-Dropdown
   oben ist die **Test-Umgebung** vorausgewählt; der zweite Eintrag «Eigener Host» hat ein Textfeld, in das
   Sie einen anderen Host eintragen (z. B. die beim Onboarding erhaltene Produktions-URL oder einen
   eigenen Proxy). Token über `POST /token` holen, auf **Authorize** klicken, das Token eintragen – danach
   funktioniert **Try it out** gegen Ihren Test-Mandanten. Gegen andere Hosts geht *Try it out* nur, wenn
   dieser Host Aufrufe aus dem Browser von `wwimmo.github.io` erlaubt (CORS); Produktion tut das bewusst
   nicht, dort bleibt die UI eine Referenz zum Lesen.
2. **Offline:** dieselbe Site liefert
   [`dms-api-swagger.html`](https://wwimmo.github.io/ww-dms-api/dms-api-swagger.html) – Swagger UI und
   Spezifikation in einer Datei, läuft per Doppelklick ohne Netzzugang. *Try it out* ist aus einer lokalen
   Datei nicht möglich (Browser-Sicherheitsregeln); dafür die Bruno-Collection verwenden.
3. Lokal: in VS Code mit einer OpenAPI-/Swagger-Vorschau-Erweiterung oder
   `npx @redocly/cli preview-docs openapi/dms-api.v1.yaml`.
4. Für Reviewer: jeder Pull Request, der die Spezifikation berührt, hängt die Offline-Datei als Artefakt
   `dms-api-swagger` an.

### Version und Herkunft

Die Datei heisst `dms-api.v1.yaml`: `v1` ist die Vertragsversion und entspricht dem Pfadpräfix
`/api/v1/dms`. Welcher Build sie erzeugt hat, steht im `info`-Block: `x-build-sha` (Commit des Dienstes)
und `x-build-number` (Lauf der Build-Pipeline). In der Swagger UI ist beides im Kopfbereich sichtbar.
Geben Sie diese Werte bei Rückfragen oder Abweichungsmeldungen an. Was sich zwischen zwei Ständen geändert
hat, steht im [CHANGELOG](CHANGELOG.md).

### Was die Spezifikation abdeckt

- **Dokumente:** `GET /documents` (paginiert, Zeitfenster, Filter `requires_dms_archiving` und
  `archive_uuid`), `POST /documents`, `GET /documents/{uuid}` (mit `ETag`), `PATCH /documents/{uuid}`
  (Teilaktualisierung), `PUT /documents/{uuid}` (Vollersatz), `DELETE /documents/{uuid}`,
  `GET /documents/{uuid}/content`.
- **Stammdaten** (`GET`, mit `changed_since` + `changed_until`, paginiert, je Ressource ein
  Einzelabruf `/{uuid}` mit `ETag`): `/realestates` (+ `/number:{number}`), `/portfolios`, `/houses`,
  `/units`, `/appliances`, `/tenants`, `/tenancies`, `/persons`, `/realestate-persons`,
  `/tenancy-persons`.
- **Buchhaltung & Rechnungen (Kreditorenprozess):** `/bookkeepings` (+ `/{uuid}`), `/creditors`
  (GET/POST, + `/{uuid}`), `/accounts` (+ `/{uuid}`), `/payment-accounts` (+ `/{uuid}`),
  `/payout-bank-accounts` (+ `/{uuid}`), `/payout-bank-account-bookkeepings`, `/cost-centers`
  (+ `/{uuid}`), `/account-cost-centers`, `/vat-codes` (+ `/{uuid}`), `/accountings-history`
  (+ `/{uuid}`), `/orders` (+ `/{uuid}`), `/invoices` (GET/POST, + `/{uuid}` GET).
- **Betrieb:** `GET /health` (anonym), `GET /info`, `POST /token` (Authentifizierung).
- **Querschnitt:** Paginierung (`page`, `page_size`, `Link`-Header), Rate-Limit-Budget auf jeder Antwort
  (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) und `Retry-After` bei `429`, `If-Match`/`ETag`, `Idempotency-Key`/`Idempotency-Replayed` (nur `POST /invoices`), `bearerAuth` (JWT). Siehe
  [Authentifizierung](docs/3-referenz/1-authentifizierung.md) und
  [Konventionen](docs/3-referenz/2-konventionen.md).

### Noch nicht im Vertrag modelliert

- **Lösch-Signal.** `DELETE /documents/{uuid}` löscht physisch (204). Gelöschte Dokumente verschwinden aus
  dem Polling ohne Tombstone; ein explizites Signal ist ein bekannter offener Punkt – siehe
  [Konventionen](docs/3-referenz/2-konventionen.md#löschungen).
- **Storno einer Rechnung.** Es gibt keinen Endpunkt dafür (`DELETE /invoices/{uuid}` → `405`); eine
  übergebene Rechnung lässt sich über die API nicht zurücknehmen.
- **Idempotenz-Schlüssel für `POST /documents`.** `POST /invoices` hat ihn (`Idempotency-Key`, siehe
  [Konventionen](docs/3-referenz/2-konventionen.md#idempotenz)); für Dokumente folgt er, sobald deren
  Ablage dauerhaft ist.

> `enum`-Werte einzelner String-Felder (z. B. Dokument-`type`, Verknüpfungs-`entity-type`,
> `storageTargets`) sind in der Spezifikation als `string` typisiert; die gültigen Werte stehen im
> [Domänenmodell](docs/4-konzepte/1-domaenenmodell.md) und in den [Anleitungen](docs/2-anleitungen/).
> Die Eingabe ist Gross-/Kleinschreibungs-unabhängig.

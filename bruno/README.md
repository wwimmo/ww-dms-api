# W&W Immo DMS-API – Bruno-Collection

Einsatzbereite Bruno-Collection für die DMS-API der W&W Immo Informatik AG, gerichtet an DMS-Anbieter.
Die Collection enthält ausschliesslich Endpunkte, die produktiv gegen echte Systeme (ImmoTop2, Rimo R5)
laufen: Token, Stammdaten, Finanzstammdaten, Buchhaltungen (hier «Buchungskreise»), Rechnungen und
Dokumente – also die drei Kernabläufe *Dokument importieren*, *Rechnung importieren* und *Dokument
archivieren*.

Die Request-Bodies werden bei jedem Pull Request automatisch gegen das Request-Schema der
OpenAPI-Spezifikation geprüft (`scripts/check-docs-against-spec.py`) – sie sind deshalb die verlässlichen
Beispiele für den Vertrag.

## Nutzung

1. Collection in Bruno importieren (Ordner `bruno` öffnen).
2. Umgebung **Vorlage** auswählen. `baseUrl` ist für die Test-Umgebung vorbelegt
   (`https://erp-test.wwimmo.net/api/v1/dms`); für Produktion die beim Onboarding erhaltene URL eintragen.
3. `clientId`, `clientSecret` (als Secret-Variable, wird nicht committet) und `archiveId` (die Archiv-UUID
   Ihrer DMS-Anbindung) in der Umgebung eintragen.
4. Zuerst **1. Token / Token holen** ausführen. Das Zugriffstoken wird automatisch als `{{token}}`
   gespeichert und für alle weiteren Anfragen verwendet.
5. Anschliessend beliebige Anfrage ausführen. Die `… synchronisieren`-Anfragen speichern die erste ID der
   Antwort (z. B. `{{realestateId}}`, `{{bookkeepingId}}`, `{{documentId}}`) für die Folge-Anfragen.

## Delta-Sync-Konvention

Die Synchronisations-Endpunkte liefern Änderungen über ein Zeitfenster:

- `changed_since` und `changed_until` als Query-Parameter, **beide optional**: ohne `changed_since` den
  Vollbestand, ohne `changed_until` ein offenes Ende. Das Fenster ist halboffen
  `[changed_since, changed_until)`. Die Beispiele setzen `changed_until` nur zur Illustration.
- Zeitstempel im Format ISO 8601 in UTC (z. B. `2026-01-15T00:00:00Z`).
- Die Antwort ist paginiert (`page`, `page_size` bis 1000, `Link`-Header) und hat die Form
  `{ items: [...], totalCount, pageCount, page, pageSize }`.
- `GET /documents` kennt zusätzlich das Flag `requires_dms_archiving` (ohne Wert): nur die Dokumente, die
  Ihr DMS archivieren soll.
- Einige Finanzlisten (Konten, Kostenstellen, MwSt-Codes, Zahlkonten, Auszahlungs-Bankkonten,
  Buchungshistorie) nehmen das Fenster an, wenden es aber nicht an und liefern immer den vollen Bestand.

## Mandanten-Scoping

Die Sichtbarkeit der Daten wird automatisch über das Zugriffstoken (`customerid`-Claim) auf Ihren
Mandanten eingeschränkt. Es ist keine zusätzliche Filterung notwendig; fehlt der Claim, antwortet die API
mit `403`.

## Begriffe

«Buchungskreis» in dieser Collection entspricht «Buchhaltung» (`bookkeeping`) in der Dokumentation.

## Weiterführende Dokumentation

Der verbindliche Vertrag sowie die ausführliche Dokumentation zu Authentifizierung, Konventionen und
Fehlerbehandlung befinden sich in der Repo-Dokumentation:
[Authentifizierung](../docs/3-referenz/1-authentifizierung.md),
[Konventionen](../docs/3-referenz/2-konventionen.md),
[Fehlerbehandlung](../docs/3-referenz/3-fehler.md) und
[OpenAPI-Spezifikation](../openapi/).

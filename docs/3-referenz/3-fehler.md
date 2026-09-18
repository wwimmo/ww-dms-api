# Fehlerbehandlung

Das Format der Fehlerantworten und wie Sie darauf reagieren.

## Format – Problem (nach RFC 9457)

Fachliche und Validierungsfehler werden als `application/problem+json` zurückgegeben:

```json
{
  "type": "/some/uri-reference",
  "title": "some title for the error situation",
  "status": 400,
  "detail": "a human-readable explanation specific to this occurrence",
  "instance": "/some/uri-reference#specific-occurrence-context",
  "traceId": "00-…"
}
```

| Feld | Bedeutung |
| --- | --- |
| `type` | URI-Referenz, die den **Fehlertyp** API-intern identifiziert. Anders als in RFC 9457 nicht zwingend auflösbar oder global eindeutig – als undurchsichtige, API-lokale Kategorie behandeln. |
| `title` | Kurze, englische Zusammenfassung für Entwickler. Nicht lokalisiert, nicht für Endnutzer. |
| `status` | Der HTTP-Statuscode, im Body wiederholt. |
| `detail` | Vorfallspezifische, englische Erklärung zur Eingrenzung des Problems. |
| `instance` | URI-Referenz, die diesen konkreten Vorfall identifiziert. |
| `traceId` | Korrelations-ID des Aufrufs – bei Support-Anfragen mitgeben. |
| `errors` | Nur bei Eingabefehlern: Feld → Liste der Meldungen. |

`title` und `detail` sind für Entwickler gedacht und **nicht** geeignet, um sie Endnutzern unverändert
anzuzeigen.

## Drei Ausnahmen vom Problem-Format

Prüfen Sie den `Content-Type` der Antwort, bevor Sie parsen:

1. **`429 Too Many Requests`** (`application/json`):
   `{ "error": "Too many requests", "message": "Rate limit exceeded. Please try again later.", "retryAfter": <sekunden|null> }`
   mit den Headern `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining: 0`, `X-RateLimit-Reset`
   (die drei `X-RateLimit-*`-Header kommen auf jeder Antwort, siehe
   [Konventionen → Rate-Limits](2-konventionen.md#rate-limits)).
2. **Token-Endpunkt** `POST /token` (`application/json`): `401` `{ "error": "invalid_client", "message": … }`,
   `502` `{ "error": "service_unavailable", "message": … }`.
3. **`POST /invoices` – fachliche Validierung** (`application/json`):

   ```json
   {
     "isValid": false,
     "errors": [
       { "field": "Accountings", "code": "AMOUNT_MISMATCH", "message": "…" },
       { "field": "Accountings[0].Text", "code": "REQUIRED", "message": "…" }
     ]
   }
   ```

   Die `code`-Werte (z. B. `REQUIRED`, `AMOUNT_MISMATCH`, `QR_IBAN_REQUIRES_REFERENCE`, `INVALID_IBAN`,
   `DUE_DATE_BEFORE_DATE`, `COST_CENTER_REQUIRED`) sind der Vertrag des ERP-Rechnungsworkflows und stabil –
   Ihr System kann darauf verzweigen und dem Sachbearbeiter eine Korrektur anbieten. Ein fehlendes Feld
   und ein Feld mit `null` antworten beide `REQUIRED`; ein nicht lesbarer Wert (falscher Typ, keine UUID)
   antwortet `INVALID_FORMAT` auf diesem Feld. Mehrere Fehler kommen gesammelt zurück.

   Daneben gibt es am selben Endpunkt ein **strukturelles `400` im Problem-Format**, etwa bei leerem
   `invoices`-Array (`detail: "At least one invoice is required."`).

## Reaktion auf Fehler

| Status | Wahrscheinliche Ursache | Was tun |
| --- | --- | --- |
| `400` | Validierungsproblem in der Anfrage: ungültiges Zeitfenster (`Invalid time range`), ungültige Paginierung (`Invalid pagination parameter`), ungültiger `type`/`entity-type`/`storageTargets`-Wert, `links` mit unbekannter ID, `dmsReference` ohne `documentId` oder mit falschem `archive`; bei `POST /invoices` zusätzlich die Validierungsliste (oben). | `detail` bzw. `errors` prüfen, Anfrage korrigieren; nicht unverändert wiederholen. |
| `401` | Token fehlt oder ist abgelaufen; am Token-Endpunkt: falsche Zugangsdaten (`invalid_client`). | Neues Token anfordern (siehe [Authentifizierung](1-authentifizierung.md)) und einmal wiederholen; bei `invalid_client` Zugangsdaten prüfen, nicht wiederholen. |
| `403` | Token hat den Scope `wwimmo:dms:api` nicht oder trägt keinen `customerid`. | Zugangsdaten/Scope prüfen – nicht blind wiederholen. |
| `404` | Unbekannte ID / unbekannter Schlüssel. | Als «nicht vorhanden» behandeln; nicht wiederholen. |
| `405` | `DELETE /invoices/{uuid}` – ein Storno ist nicht verfügbar. | Korrektur im ERP; siehe [Konventionen → Löschungen](2-konventionen.md#löschungen). |
| `409` | `POST /invoices` mit einem `Idempotency-Key`, dessen erster Aufruf noch läuft. | `Retry-After` (1 s) abwarten und denselben Aufruf unverändert wiederholen; dann kommt die gespeicherte Antwort. Siehe [Konventionen → Idempotenz](2-konventionen.md#idempotenz). |
| `412` | Mitgesendetes `If-Match` benennt nicht den aktuellen Stand – das Dokument wurde zwischenzeitlich geändert. | Neu lesen, Änderung erneut anwenden, mit dem aktuellen `ETag` wiederholen. Siehe [Konventionen](2-konventionen.md#schreiben-mit-if-match). |
| `422` | `POST /invoices` mit einem bereits verwendeten `Idempotency-Key`, aber anderem Body. | Für einen neuen Vorgang einen neuen Schlüssel verwenden; nicht denselben Schlüssel mit geändertem Body wiederholen. |
| `428` | `PUT`/`PATCH`/`DELETE /documents/{uuid}` ohne `If-Match` in einer Umgebung, in der der Header Pflicht ist. | Dokument per `GET` lesen und den Aufruf mit `If-Match: "<etag>"` wiederholen. Siehe [Konventionen](2-konventionen.md#schreiben-mit-if-match). |
| `429` | Rate-Limit. | Zurückhalten; `Retry-After` beachten. Siehe [Konventionen](2-konventionen.md#rate-limits). |
| `502` | Vorgelagerter Dienst nicht erreichbar (z. B. beim Token-Bezug). | Mit Backoff wiederholen. |
| `503` | `GET /health` bei ungesundem Dienst (Body mit `status` und `details`). | Wie `5xx` behandeln. |
| `5xx` | Serverseitig. | Mit Backoff wiederholen. `POST /invoices` dabei mit demselben `Idempotency-Key` – so entsteht höchstens eine Rechnung. **Achtung bei `POST /documents`:** kein Schlüssel; nach einem Timeout erst per `GET` prüfen, ob der erste Versuch angekommen ist (siehe [Konventionen](2-konventionen.md#idempotenz)). |

## Retry-Strategie

Bei `429` und `5xx`: exponentielles Backoff mit Jitter – zuerst `Retry-After` Sekunden (bzw. 1 s) warten,
bei wiederholten Fehlern die Wartezeit verdoppeln (1 s → 2 s → 4 s → 8 s), ±25 % Jitter, nach ~5 Versuchen
abbrechen.

## Stand

Ein **Katalog konkreter `type`-Werte** (je mit Bedeutung, Status und Recovery-Hinweis) wird noch ergänzt.
Die je Endpunkt möglichen Statuscodes stehen in der [OpenAPI-Spezifikation](../../openapi/dms-api.v1.yaml).

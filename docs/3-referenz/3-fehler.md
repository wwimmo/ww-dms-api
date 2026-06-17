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
  "instance": "/some/uri-reference#specific-occurrence-context"
}
```

Zwei Sonderfälle weichen vom Problem-Format ab und liefern ein einfacheres JSON-Objekt:

- **`429 Too Many Requests`** (Rate-Limit): `{ "error": "...", "message": "...", "retryAfter": <sek> }`.
- **Token-Endpunkt** (`/token`) bei Fehlern: `{ "error": "...", "message": "..." }`.

| Feld | Bedeutung |
| --- | --- |
| `type` | URI-Referenz, die den **Fehlertyp** API-intern identifiziert. Anders als in RFC 9457 nicht zwingend auflösbar oder global eindeutig – als undurchsichtige, API-lokale Kategorie behandeln. |
| `title` | Kurze, englische Zusammenfassung für Entwickler. Nicht lokalisiert, nicht für Endnutzer. |
| `status` | Der HTTP-Statuscode, im Body wiederholt. |
| `detail` | Vorfallspezifische, englische Erklärung zur Eingrenzung des Problems. |
| `instance` | URI-Referenz, die diesen konkreten Vorfall identifiziert. |

`title` und `detail` sind für Entwickler gedacht und **nicht** geeignet, um sie Endnutzern unverändert
anzuzeigen.

## Reaktion auf Fehler

| Status | Wahrscheinliche Ursache | Was tun |
| --- | --- | --- |
| `400` | Validierungsproblem in der Anfrage (z. B. fehlender/ungültiger `changed_since`, ungültiger `type`/`entity-type`, ungültige Seitengrösse). | `detail` prüfen, Anfrage korrigieren; nicht unverändert wiederholen. |
| `401` | Token fehlt/abgelaufen. | Neues Token anfordern (siehe [Authentifizierung](1-authentifizierung.md)); einmal wiederholen. |
| `403` | Token hat den Scope `wwimmo:dms:api` nicht bzw. keinen `customerid`-Bezug. | Zugangsdaten/Scope prüfen – nicht blind wiederholen. |
| `404` | Unbekannte ID / unbekannter Schlüssel. | Als „nicht vorhanden" behandeln; nicht wiederholen. |
| `409` | Konflikt mit dem aktuellen Zustand (z. B. eine bereits verbuchte Rechnung löschen). | Nicht wiederholen; fachlich klären. |
| `429` | Rate-Limit. | Zurückhalten; `Retry-After` beachten. Siehe [Konventionen](2-konventionen.md#rate-limits). |
| `502` | Vorgelagerter Dienst nicht erreichbar (z. B. beim Token-Bezug). | Mit Backoff wiederholen. |
| `5xx` | Serverseitig. | Mit Backoff wiederholen; dank Idempotenz unbedenklich. |

## Retry-Strategie

Bei `429` und `5xx`: exponentielles Backoff mit Jitter – zuerst `Retry-After` Sekunden (bzw. 1 s) warten,
bei wiederholten Fehlern die Wartezeit verdoppeln (1 s → 2 s → 4 s → 8 s), ±25 % Jitter, nach ~5 Versuchen
abbrechen.

## Stand

Ein **Katalog konkreter `type`-Werte** (je mit Bedeutung, Status und Recovery-Hinweis) wird noch ergänzt.
Die je Endpunkt möglichen Statuscodes stehen in der [OpenAPI-Spezifikation](../../openapi/dms-api.v1.yaml).

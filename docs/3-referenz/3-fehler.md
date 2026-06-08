# Fehlerbehandlung

Das Format der Fehlerantworten und wie Sie darauf reagieren.

## Format – Problem (nach RFC 9457)

Fehler werden als `application/problem+json` zurückgegeben (Schema `Problem` aus der
[OpenAPI-Spezifikation](../../openapi/README.md)):

```json
{
  "type": "/some/uri-reference",
  "title": "some title for the error situation",
  "status": 422,
  "detail": "a human-readable explanation specific to this occurrence",
  "instance": "/some/uri-reference#specific-occurrence-context"
}
```

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
| `401` | Token fehlt/abgelaufen. | Neues Token anfordern (siehe [Authentifizierung](1-authentifizierung.md)); einmal wiederholen. |
| `403` | Token hat den Scope `wwimmo:dms:api` nicht. | Zugangsdaten/Scope prüfen – nicht blind wiederholen. |
| `404` | Unbekannte ID / unbekannter Schlüssel. | Als „nicht vorhanden" behandeln; nicht wiederholen. |
| `422` | Validierungsproblem in der Anfrage. | `detail` prüfen, Anfrage korrigieren; nicht unverändert wiederholen. |
| `429` | Rate-Limit. | Zurückhalten; falls vorhanden `Retry-After` beachten. |
| `5xx` | Serverseitig. | Mit Backoff wiederholen; dank Idempotenz unbedenklich. |

## Stand

Der **Katalog konkreter `type`-Werte** (je mit Bedeutung, zugehörigem Status und Recovery-Hinweis) sowie
die je Endpunkt möglichen Statuscodes werden noch ergänzt.

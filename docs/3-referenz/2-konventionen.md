# Konventionen

Regeln, die über alle Endpunkte hinweg gelten – einmal hier beschrieben statt pro Endpunkt wiederholt.

## Polling mit `changed_since`

Die API wird durch **Abrufen** konsumiert, nicht durch Push. Listen-Endpunkte erwarten einen
`changed_since`- (bei Stammdaten zusätzlich `changed_until`-) Zeitstempel und liefern die im Zeitfenster
geänderten Datensätze.

```
GET /documents?changed_since=2026-01-01T00:00:00Z
GET /realestates?changed_since=2026-01-01T00:00:00Z&changed_until=2026-01-08T00:00:00Z
```

- `changed_since` ist auf Listen-Endpunkten **erforderlich**; Format: RFC 3339 / ISO 8601.
- Stammdaten-Endpunkte erwarten zusätzlich `changed_until` und liefern Änderungen im Intervall
  `[changed_since, changed_until)`.
- Ablauf eines Polling-Zyklus: höchsten Zeitstempel merken, mit ihm als `changed_since` abfragen, danach
  auf die neueste Änderung der Antwort weiterschalten.

## Kein Push / keine Webhooks

Die Synchronisation erfolgt ausschliesslich über von Ihnen ausgelöste Abrufe (Pull). Es gibt keine
Webhooks und keine Events.

## Idempotenz

Da Abrufe wiederholt werden können, sind schreibende Operationen wiederholungssicher. Behandeln Sie
Aufrufe als potenziell mehrfach gesendet und bauen Sie auf Ihrer Seite keine „genau-einmal-bei-Empfang"-
Logik ohne Dedup-Schlüssel.

## Löschungen

`DELETE`-Endpunkte (z. B. `DELETE /documents/{uuid}`, `DELETE /invoices/{uuid}`) antworten mit
`204 No Content`. Löschungen sind als **Soft-Delete** umgesetzt: der Datensatz wird als gelöscht
markiert, nicht physisch entfernt.

> Wie gelöschte Datensätze über das Polling sichtbar gemacht werden (Markierung, Aufbewahrung), wird
> derzeit erarbeitet und hier ergänzt, sobald es feststeht.

## Paginierung

Listen-Endpunkte für Stammdaten und Buchhaltung sind seitenweise abrufbar:

- Query-Parameter: `page` (Standard `1`) und `page_size` (Standard `100`, Maximum `1000`).
- Die Antwort ist eine Hülle:

  ```json
  {
    "items": [ /* … */ ],
    "totalCount": 1234,
    "pageCount": 13,
    "page": 1,
    "pageSize": 100
  }
  ```

- Zusätzlich wird ein `Link`-Header (RFC 5988) mit den Relationen `first`, `last`, `prev`, `next`
  geliefert. Folgen Sie `next`, bis kein `next` mehr vorhanden ist.

## Rate-Limits

Alle Endpunkte sind rate-limitiert (Konfiguration über `RateLimiting:Dms`):

| Bereich | Verfahren | Standard-Grenze |
| --- | --- | --- |
| Anonyme Endpunkte (`/token`, `/health`) | Fixed Window pro IP | 30 Anfragen/Minute |
| Authentifizierte Daten-Endpunkte | Token-Bucket pro Client | 100 Burst, 50 Anfragen/Minute |

Antworten tragen die Header `X-RateLimit-Limit`, `X-RateLimit-Remaining` und `X-RateLimit-Reset`
(Unix-Zeitstempel). Bei Überschreitung antwortet die API mit `429 Too Many Requests` und einem
`Retry-After`-Header (Sekunden). Empfohlen: exponentielles Backoff mit Jitter (siehe
[Fehlerbehandlung](3-fehler.md)).

## Bedingte Abfragen (ETag)

Einzel-GETs einiger Stammdaten (z. B. `GET /realestates/{uuid}`, `GET /portfolios/{uuid}`,
`GET /bookkeepings/{uuid}`) liefern einen `ETag`-Header. Senden Sie ihn bei der nächsten Abfrage als
`If-None-Match` mit; bei unveränderten Daten antwortet die API mit `304 Not Modified` (ohne Body).

## Bezeichner & sprechende Schlüssel

- Primäre Bezeichner sind **UUIDs** (`id`, Pfad `{uuid}`).
- Einige Entitäten unterstützen zusätzlich einen **sprechenden Sekundärschlüssel**, z. B.
  `GET /realestates/number:{number}`.
- Buchhaltungsbezogene Strukturen sind über **`bookkeepingid`** verschlüsselt, nicht über `realestateid` –
  siehe [Domänenmodell](../4-konzepte/1-domaenenmodell.md).

## Inhaltstypen

- Anfragen/Antworten verwenden `application/json`.
- Der **Dateiinhalt** (`GET /documents/{uuid}/content`) liefert `application/octet-stream` oder eine
  `302`-Weiterleitung, wenn die Datei über ein CDN ausgeliefert wird – der Weiterleitung folgen.

## Fehler

Fachliche und Validierungsfehler verwenden einen Problem+JSON-Body (mit Ausnahmen bei `429` und am
Token-Endpunkt) – siehe [Fehlerbehandlung](3-fehler.md).

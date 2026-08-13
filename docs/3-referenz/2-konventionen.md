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

- Format: RFC 3339 / ISO 8601, mit Zeitzonen-Angabe (`Z` oder Offset).
- `changed_since` ist technisch optional: ohne Angabe liefert der Endpunkt den **Vollbestand**. Für den
  laufenden Abgleich immer mitsenden – ein Vollabruf kostet Sie Rate-Limit-Budget.
- `changed_until` ist ebenfalls optional (offenes Ende). Beide Grenzen ergeben das Intervall
  `[changed_since, changed_until)`.
- Ablauf eines Polling-Zyklus: höchsten Zeitstempel merken, mit ihm als `changed_since` abfragen, danach
  auf die neueste Änderung der Antwort weiterschalten.
- Das Zeitfenster wird bis zum ERP durchgereicht und dort gefiltert. Randfall: Das ERP vergleicht die
  Wand-Uhr-Zeit gegen seine lokal (Europe/Zurich) gespeicherten Änderungsstempel. Ein UTC-Zeitstempel kann
  deshalb ein 1–2 Stunden **grösseres** Fenster liefern als erwartet – Sie erhalten also eher zu viele als
  zu wenige Datensätze. Verarbeiten Sie Wiederholungen idempotent (siehe unten).

## Kein Push / keine Webhooks

Die Synchronisation erfolgt ausschliesslich über von Ihnen ausgelöste Abrufe (Pull). Es gibt keine
Webhooks und keine Events.

## Teilaktualisierung: `PATCH` statt `PUT`

Für Dokumente gibt es zwei schreibende Aktualisierungen mit unterschiedlicher Semantik:

| Methode | Semantik |
| --- | --- |
| `PATCH /documents/{uuid}` | **Teilaktualisierung.** Nicht mitgesendete Eigenschaften behalten ihren gespeicherten Wert. |
| `PUT /documents/{uuid}` | **Vollersatz.** Nicht mitgesendete Eigenschaften werden geleert – auch `links` und `storageTargets`. |

Wollen Sie einzelne Eigenschaften ändern – der Regelfall, insbesondere das Zurückschreiben der
Archiv-Referenz –, verwenden Sie `PATCH`:

```
PATCH /documents/{uuid}
{ "dmsReference": { "archive": "…", "documentId": "…" } }
```

Abweichung von RFC 7396, die Sie kennen sollten: ein explizites `null` bedeutet bei `PATCH` ebenfalls
„unverändert", es leert das Feld **nicht**. Das Leeren von `links`, `storageTargets`, `url` oder `barcode`
bleibt Aufgabe von `PUT`. So bleibt die gefährliche Operation explizit.

## Schreiben mit `If-Match`

`PUT`, `PATCH` und `DELETE` auf Dokumente werten den `If-Match`-Header aus. Damit überschreiben Sie keinen
Stand, den Sie nicht gesehen haben:

1. `ETag` aus `GET /documents/{uuid}` merken.
2. Beim Schreiben als `If-Match: "<etag>"` mitsenden.
3. Wurde das Dokument zwischenzeitlich geändert, antwortet die API mit `412 Precondition Failed` und
   schreibt nicht. Neu lesen, Änderung erneut anwenden, mit dem aktuellen `ETag` wiederholen.

Der Header ist **optional**: ohne `If-Match` wird wie bisher geschrieben. `If-Match: *` verlangt nur, dass
das Dokument existiert.

## Verknüpfungen (`links`) müssen auflösbar sein

`links` verweist auf Stammdaten Ihres Mandanten (`realestate`, `house`, `unit`, `appliance`, `tenant`,
`tenancy`). Beim Schreiben wird geprüft, ob die IDs existieren; eine unbekannte ID wird mit `400` und der
betroffenen ID im `detail` abgewiesen. IDs eines anderen Mandanten gelten als unbekannt.

## Idempotenz

Lesende Abrufe können beliebig wiederholt werden.

> **Schreibende Operationen sind derzeit nicht wiederholungssicher.** Es gibt noch keinen
> Idempotenz-Schlüssel: eine Wiederholung von `POST /documents` oder `POST /invoices` nach einem Timeout
> erzeugt einen **zweiten** Datensatz. Führen Sie auf Ihrer Seite einen eigenen Dedup-Schlüssel und prüfen
> Sie nach einem Timeout per `GET` mit `changed_since`, ob der erste Versuch angekommen ist, bevor Sie
> erneut senden.

## Löschungen

`DELETE /documents/{uuid}` antwortet mit `204 No Content`.

> Ob Löschungen als Soft-Delete (Markierung) oder physisch umgesetzt werden, ist noch nicht festgelegt.

> **Rechnungen lassen sich nicht stornieren.** Es gibt keinen `DELETE`-Endpunkt für `/invoices/{uuid}`;
> die Route beantwortet `DELETE` mit `405 Method Not Allowed`. Der Storno müsste im Visums-Workflow des
> ERP greifen, und dafür existiert noch keine Schnittstelle. Prüfen Sie eine Rechnung deshalb vor dem
> `POST` – eine Korrektur ist danach nur im ERP möglich.

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
`GET /bookkeepings/{uuid}`) sowie `GET /documents/{uuid}` liefern einen `ETag`-Header. Senden Sie ihn bei
der nächsten Abfrage als `If-None-Match` mit; bei unveränderten Daten antwortet die API mit
`304 Not Modified` (ohne Body).

Beim **Schreiben** dient derselbe `ETag` als `If-Match` – siehe
[Schreiben mit If-Match](#schreiben-mit-if-match).

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

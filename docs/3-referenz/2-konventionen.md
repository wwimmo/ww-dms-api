# Konventionen

Regeln, die über alle Endpunkte hinweg gelten – einmal hier beschrieben statt pro Endpunkt wiederholt.

## Polling mit `changed_since`

Die API wird durch **Abrufen** konsumiert, nicht durch Push. Alle Listen-Endpunkte – Stammdaten,
Buchhaltung, Rechnungen **und Dokumente** – akzeptieren ein Zeitfenster aus `changed_since` und
`changed_until` und liefern die darin geänderten Datensätze:

```
GET /documents?changed_since=2026-01-01T00:00:00Z
GET /documents?changed_since=2026-01-01T00:00:00Z&requires_dms_archiving
GET /realestates?changed_since=2026-01-01T00:00:00Z&changed_until=2026-01-08T00:00:00Z
```

- Format: RFC 3339 / ISO 8601, mit Zeitzonen-Angabe (`Z` oder Offset).
- **Beide Grenzen sind optional.** Ohne `changed_since` liefert der Endpunkt den **Vollbestand**, ohne
  `changed_until` gilt ein offenes Ende. Für den laufenden Abgleich `changed_since` immer mitsenden – ein
  Vollabruf kostet Rate-Limit-Budget.
- Das Fenster ist **halboffen**: `[changed_since, changed_until)`. Liegt `changed_since` nicht vor
  `changed_until`, antwortet die API mit `400` (`title: "Invalid time range"`).
- Ablauf eines Polling-Zyklus: höchsten Zeitstempel merken, mit ihm als `changed_since` abfragen, danach
  auf die neueste Änderung der Antwort weiterschalten.
- Das Zeitfenster wird bis zum ERP durchgereicht und dort gefiltert. Randfall: Das ERP vergleicht die
  Wand-Uhr-Zeit gegen seine lokal (Europe/Zurich) gespeicherten Änderungsstempel. Ein UTC-Zeitstempel kann
  deshalb ein 1–2 Stunden **grösseres** Fenster liefern als erwartet – Sie erhalten also eher zu viele als
  zu wenige Datensätze. Verarbeiten Sie Wiederholungen idempotent (siehe unten).
- Einige Buchhaltungslisten (`accounts`, `account-cost-centers`, `cost-centers`, `vat-codes`,
  `payment-accounts`, `payout-bank-accounts`, `accountings-history`) nehmen das Fenster an, wenden es aber
  nicht an – ihre ERP-Quelle kennt keine Änderungsstempel. Sie liefern immer den vollen Bestand: seltener
  abrufen und lokal vergleichen.
- `requires_dms_archiving` (nur `GET /documents`) ist ein Flag ohne Wert: nur Dokumente, deren
  `storageTargets` `DMS` enthält und deren `dmsReference` noch leer ist – also die Archivierungsaufträge.

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
{ "dmsReference": { "archive": "<archiv-uuid>", "documentId": "<dms-dokument-id>" } }
```

Abweichung von RFC 7396, die Sie kennen sollten: ein explizites `null` bedeutet bei `PATCH` ebenfalls
«unverändert», es leert das Feld **nicht**. Das Leeren von `links`, `storageTargets`, `url` oder `barcode`
bleibt Aufgabe von `PUT`. So bleibt die gefährliche Operation explizit.

Regeln für `dmsReference` (bei `POST`, `PUT`, `PATCH` und bei Rechnungen gleich): ist das Objekt gesetzt,
ist `documentId` Pflicht, und `archive` muss die **Archiv-ID Ihrer DMS-Anbindung** sein – eine von W&W Immo
beim Onboarding vergebene UUID. Andere Werte weist die API mit `400` ab.

## Schreiben mit `If-Match`

`PUT`, `PATCH` und `DELETE` auf Dokumente werten den `If-Match`-Header aus. Damit überschreiben Sie keinen
Stand, den Sie nicht gesehen haben:

1. `ETag` aus `GET /documents/{uuid}` merken.
2. Beim Schreiben als `If-Match: "<etag>"` mitsenden.
3. Wurde das Dokument zwischenzeitlich geändert, antwortet die API mit `412 Precondition Failed` und
   schreibt nicht. Neu lesen, Änderung erneut anwenden, mit dem aktuellen `ETag` wiederholen.

Der Header ist **heute optional**: ohne `If-Match` wird wie bisher geschrieben. `If-Match: *` verlangt nur,
dass das Dokument existiert.

**Ausblick:** Der Header wird Pflicht. Schreibzugriffe ohne `If-Match` werden bereits serverseitig
protokolliert; sobald alle angebundenen Partner ihn senden, schaltet W&W Immo die Pflicht pro Umgebung
ein. Danach antwortet die API auf `PUT`, `PATCH` und `DELETE` ohne `If-Match` mit
`428 Precondition Required` und schreibt nicht. Senden Sie den Header deshalb schon jetzt bei jedem
Schreibzugriff; der Termin wird im [Changelog](../../CHANGELOG.md) angekündigt.

Der `ETag` ist ein Hash über den sichtbaren Inhalt des Dokuments (Name, Verknüpfungen, Archiv-Referenz,
…). Er ändert sich mit jeder sichtbaren Änderung, egal ob sie vom DMS oder aus dem ERP kommt, und bleibt
gleich, solange sich nichts ändert.

## Verknüpfungen (`links`) müssen auflösbar sein

`links` verweist auf Stammdaten Ihres Mandanten (`realestate`, `house`, `unit`, `appliance`, `tenant`,
`tenancy`; Gross-/Kleinschreibung egal). Beim Schreiben wird geprüft, ob die IDs existieren; eine
unbekannte ID wird mit `400` abgewiesen (`title: "Invalid request"`,
`detail: "Unknown <entity-type> link target(s): <ids>"`). IDs eines anderen Mandanten gelten als unbekannt.

## Idempotenz

Lesende Abrufe können beliebig wiederholt werden.

### `Idempotency-Key` auf `POST /invoices`

Bricht die Verbindung nach dem Senden einer Rechnung ab, wissen Sie nicht, ob sie angelegt wurde. Damit
Sie gefahrlos wiederholen können, akzeptiert `POST /invoices` den optionalen Header `Idempotency-Key`:

- **Schlüssel:** ein von Ihnen erzeugter, pro Vorgang eindeutiger Wert (z. B. eine UUID), höchstens
  255 Zeichen. Leer oder länger → `400`.
- **Geltungsbereich:** pro Mandant, pro Client (`client_id` des Tokens) und pro Operation. Ein Schlüssel,
  den ein anderer Mandant verwendet, kollidiert nicht mit Ihrem.
- **Fenster:** 24 Stunden ab dem ersten Aufruf.
- **Wiederholung mit gleichem Schlüssel und byteidentischem Body:** Sie erhalten die Antwort des ersten
  Aufrufs zurück (gleicher Status, gleicher Body, gleiche `Location`), gekennzeichnet mit dem Header
  `Idempotency-Replayed: true`. Es entsteht keine zweite Rechnung. Senden Sie den Body unverändert –
  auch Leerzeichen und Feldreihenfolge zählen.
- **Gleicher Schlüssel, anderer Body:** `422 Unprocessable Content` (Problem-Format). Ein neuer Vorgang
  braucht einen neuen Schlüssel.
- **Wiederholung, während der erste Aufruf noch läuft:** `409 Conflict` mit `Retry-After: 1`. Kurz warten
  und denselben Aufruf wiederholen; dann kommt die gespeicherte Antwort.
- **Gespeichert werden auch Ablehnungen (`400`)**: Wer eine Validierungsmeldung erhält, den Fehler
  korrigiert und erneut sendet, verwendet dafür einen **neuen** Schlüssel – der alte antwortet mit `422`,
  weil sich der Body geändert hat.
- **Nicht gespeichert werden `5xx`-Antworten**: nach einem Serverfehler oder Timeout ist der Schlüssel
  frei, die Wiederholung mit demselben Schlüssel legt die Rechnung genau einmal an.

Ohne Header verhält sich `POST /invoices` wie bisher: jede Wiederholung erzeugt eine weitere Rechnung.

> **`POST /documents` kennt den Schlüssel noch nicht.** Eine Wiederholung nach einem Timeout erzeugt dort
> ein **zweites** Dokument. Prüfen Sie vor dem erneuten Senden per `GET /documents?changed_since=…`, ob
> der erste Versuch angekommen ist. Der Header wird für Dokumente nachgezogen, sobald deren Ablage
> dauerhaft ist.

## Löschungen

`DELETE /documents/{uuid}` löscht den Datensatz heute **physisch** und antwortet mit `204 No Content`.
Danach erscheint das Dokument in keinem Abruf mehr – auch nicht mit `changed_since`; es gibt **keinen
Tombstone** und kein `deleted_at`. Ein DMS erkennt Löschungen deshalb nur durch Abgleich des eigenen
Bestands mit dem Vollbestand der API.

> Die endgültige Löschsemantik (Markierung, Aufbewahrung, ein Lösch-Signal im Polling) wird mit dem
> Feedback der ersten Partner festgelegt und im [CHANGELOG](../../CHANGELOG.md) angekündigt. Bauen Sie
> nicht darauf, dass gelöschte Datensätze sichtbar bleiben.

> **Rechnungen lassen sich nicht stornieren.** Es gibt keinen `DELETE`-Endpunkt für `/invoices/{uuid}`;
> die Route beantwortet `DELETE` mit `405 Method Not Allowed`. Der Storno müsste im Visums-Workflow des
> ERP greifen, und dafür existiert noch keine Schnittstelle. Prüfen Sie eine Rechnung deshalb vor dem
> `POST` – eine Korrektur ist danach nur im ERP möglich.

## Paginierung

Alle Listen-Endpunkte (inkl. `GET /documents` und `GET /invoices`) sind seitenweise abrufbar:

- Query-Parameter: `page` (Standard `1`) und `page_size` (Standard `100`, Maximum `1000`). Werte ausserhalb
  antworten mit `400` (`page must be >= 1 and page_size between 1 and 1000.`).
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

Alle Endpunkte sind rate-limitiert:

| Bereich | Verfahren | Standard-Grenze |
| --- | --- | --- |
| Anonyme Endpunkte (`/token`, `/health`) | Fixed Window pro IP | 30 Anfragen/Minute |
| Authentifizierte Daten-Endpunkte | Token-Bucket pro `client_id` | 100 Burst, 50 Anfragen/Minute |

Jede rate-limitierte Antwort, erfolgreich oder `429`, meldet Ihr Budget in drei Headern:

| Header | Bedeutung |
| --- | --- |
| `X-RateLimit-Limit` | Anfragen pro Fenster (anonym) bzw. Kapazität des Token-Buckets (authentifiziert) |
| `X-RateLimit-Remaining` | Nach dieser Anfrage verbleibende Anfragen im Fenster bzw. Tokens im Bucket |
| `X-RateLimit-Reset` | Unix-Sekunden, zu denen das Fenster endet bzw. der Bucket das nächste Mal aufgefüllt wird |

Richten Sie Ihr Polling an `X-RateLimit-Remaining` aus, statt in den `429` zu laufen. Bei Überschreitung
antwortet die API mit `429 Too Many Requests`, zusätzlich `Retry-After` (Sekunden), `X-RateLimit-Remaining: 0`
und `X-RateLimit-Reset` als Zeitpunkt des nächsten Versuchs, sowie dem Body
`{ "error": "Too many requests", "message": "Rate limit exceeded. Please try again later.", "retryAfter": <sekunden|null> }`
(`application/json`, kein Problem-Format). Empfohlen: exponentielles Backoff mit Jitter (siehe
[Fehlerbehandlung](3-fehler.md)).

## Bedingte Abfragen (ETag)

`GET /realestates/{uuid}`, `GET /portfolios/{uuid}` und `GET /documents/{uuid}` liefern einen
`ETag`-Header. Senden Sie ihn bei der nächsten Abfrage als `If-None-Match` mit; bei unveränderten Daten
antwortet die API mit `304 Not Modified` (ohne Body). Andere Einzel-GETs (z. B. `/bookkeepings/{uuid}`,
`/realestates/number:{number}`, `/invoices/{uuid}`) liefern keinen `ETag`.

Beim **Schreiben** dient derselbe `ETag` als `If-Match` – siehe
[Schreiben mit If-Match](#schreiben-mit-if-match).

## Bezeichner & sprechende Schlüssel

- Primäre Bezeichner sind **UUIDs** (`id`, Pfad `{uuid}`).
- Einige Entitäten unterstützen zusätzlich einen **sprechenden Sekundärschlüssel**, z. B.
  `GET /realestates/number:{number}`.
- Buchhaltungsbezogene Strukturen sind über **`bookkeepingid`** verschlüsselt, nicht über `realestateid` –
  siehe [Domänenmodell](../4-konzepte/1-domaenenmodell.md).

## Inhaltstypen und Caching

- Anfragen und Antworten verwenden `application/json`; Fehler `application/problem+json` (Ausnahmen siehe
  [Fehlerbehandlung](3-fehler.md)).
- `GET /documents/{uuid}/content` streamt die Datei mit `200`, `Content-Type` = gespeicherter MIME-Typ des
  Dokuments (z. B. `application/pdf`) und `Content-Disposition: attachment; filename="…"`. Es gibt keine
  Weiterleitung und kein CDN.
- Alle Antworten tragen `Cache-Control: private, max-age=60` und `Vary: Authorization` – sie dürfen nicht in
  geteilten Caches landen.

## Fehler

Fachliche und Validierungsfehler verwenden einen Problem+JSON-Body – mit den in
[Fehlerbehandlung](3-fehler.md) beschriebenen Ausnahmen (`429`, Token-Endpunkt, Rechnungsvalidierung).

# Änderungen an der DMS-API

Neueste zuerst. Ab dem ersten automatischen Spec-Sync schreibt der Workflow *OpenAPI sync PR* die
Einträge selbst (`oasdiff` gegen den vorherigen Stand der Spezifikation, Build-Nummer und Commit
aus `info.x-build-*`). Die Einträge davor sind von Hand nachgetragen und tragen deshalb nur den
Monat.

**Deprecation-Regel:** Ein Endpunkt oder Feld, das entfällt, wird hier mindestens einen Release
vorher als *deprecated* angekündigt, bevor er aus der Spezifikation verschwindet. Breaking
Changes tragen im Sync-PR das Label `breaking`.

## 2026-09-17 · angekündigt mit Polaris-PR 9324 (Bug #23979)

- **Neu: Rate-Limit-Budget auf jeder Antwort.** `X-RateLimit-Limit`, `X-RateLimit-Remaining` und
  `X-RateLimit-Reset` kommen auf jeder rate-limitierten Antwort, nicht mehr nur beim `429`; der `429`
  trägt zusätzlich neu `X-RateLimit-Limit`. `Limit` ist die Zahl der Anfragen pro Fenster (anonym) bzw.
  die Kapazität des Token-Buckets (authentifiziert), `Remaining` der Rest nach dieser Anfrage, `Reset`
  die Unix-Sekunde des Fensterendes bzw. der nächsten Auffüllung. Bisher stand hier, erfolgreiche
  Antworten trügen keine Rate-Limit-Header; das beschrieb den damaligen Stand der API, nicht die Zusage.
  Wirksam auf Test und Prod mit dem nächsten Polaris-Release nach dem Merge. Siehe
  [Konventionen → Rate-Limits](docs/3-referenz/2-konventionen.md#rate-limits).

## 2026-09-16 · Polaris-Build 20260916.3 (`04a7f940a806`)

**Breaking – `POST /invoices` antwortet auf `400` in einem anderen Schema.** Bisher kamen
Validierungsfehler als Problem Details (`type`, `title`, `status`, `detail`, `instance`), neu
immer als `{ "isValid": false, "errors": [{ "field", "code", "message" }] }` – dieselbe Liste,
die fachliche Fehler schon vorher benutzten. Clients, die auf `title`/`status` im Fehlerkörper
zugreifen, müssen angepasst werden. Einzige Ausnahme: ein fehlerhafter `Idempotency-Key` wird
vor dem Rumpf abgewiesen und bleibt Problem Details.

- **Neu: `Idempotency-Key` auf `POST /invoices`** (optional, max. 255 Zeichen, eindeutig pro
  Mandant, Aufrufer und Operation). Eine Wiederholung mit demselben Schlüssel und demselben
  Rumpf liefert 24 h lang die gespeicherte Antwort mit `Idempotency-Replayed: true`, statt eine
  zweite Rechnung anzulegen. Derselbe Schlüssel mit abweichendem Rumpf: `422`. Wiederholung,
  während die erste Anfrage noch läuft: `409` mit `Retry-After`. Ohne den Header erzeugt eine
  Wiederholung weiterhin eine zweite Rechnung.
- **Neu: `If-Match` steht jetzt in der Spezifikation** – auf `PUT`, `PATCH` und
  `DELETE /documents/{uuid}`, zusammen mit der neuen Antwort `428 Precondition Required`. Der
  Header ist **heute optional**; `428` kommt erst, wenn die Pflicht pro Umgebung eingeschaltet
  wird. Bis dahin sind Schreibzugriffe ohne Header weiterhin erlaubt und werden serverseitig
  protokolliert. Der Termin der Umstellung wird hier im Changelog angekündigt – siehe
  [Konventionen → Schreiben mit If-Match](docs/3-referenz/2-konventionen.md#schreiben-mit-if-match).
- **Neu: `If-None-Match` und `ETag` stehen in der Spezifikation** – auf
  `GET /documents/{uuid}`, `GET /portfolios/{uuid}` und `GET /realestates/{uuid}`. Verhalten
  unverändert, bisher war beides nur in der Prosa beschrieben; generierte Clients sahen es nicht.
- **Geändert: der `ETag` eines Dokuments ist neu ein Hash über den sichtbaren Inhalt** statt über
  den `Updated`-Stempel. Er bewegt sich damit bei jeder sichtbaren Änderung, auch wenn sie aus
  dem ERP kommt. Einmalige Folge: **gespeicherte ETags aus der Zeit davor passen nicht mehr** und
  führen bei `If-Match` zu einem `412`. Einmal neu lesen genügt.
- **Unverändert: `POST /documents` nimmt noch keinen `Idempotency-Key`.** Die Ablage ist dort
  heute flüchtig; der Schlüssel folgt zusammen mit der dauerhaften Dokumentablage.
- **Geändert: Rumpffelder von `POST /invoices` sind im Schema nullable** (`amount`, `date`,
  `bookkeepingid`, `fileId`, `creditor.legal` sowie `id`, `sort`, `amount` je Buchungszeile). Ein
  ausdrückliches `null` wird dadurch als Validierungsfehler mit Feld und Code beantwortet statt
  als nicht lesbarer Rumpf. Pflicht bleiben die Felder trotzdem.

<details>
<summary>Maschinell erzeugter Vertragsdiff (oasdiff)</summary>

### API Changelog v1 vs. v1


#### API Changes

##### DELETE /api/v1/dms/documents/{uuid}
-  added the new optional `header` request parameter `if-match`
-  added the non-success response with the status `428`


##### GET /api/v1/dms/documents/{uuid}
-  added the new optional `header` request parameter `if-none-match`
-  the response header `etag` was added for the status `200`


##### PATCH /api/v1/dms/documents/{uuid}
-  added the new optional `header` request parameter `if-match`
-  added the non-success response with the status `428`


##### PUT /api/v1/dms/documents/{uuid}
-  added the new optional `header` request parameter `if-match`
-  added the non-success response with the status `428`


##### POST /api/v1/dms/invoices
-  added the new optional `header` request parameter `idempotency-key`
-  the request property `invoices/items/invoice/accountings/items/amount` became nullable (media type: text/json)
-  the request property `invoices/items/invoice/accountings/items/amount` became nullable (media type: application/json)
-  the request property `invoices/items/invoice/accountings/items/amount` became nullable (media type: application/*+json)
-  the request property `invoices/items/invoice/accountings/items/id` became nullable (media type: application/*+json)
-  the request property `invoices/items/invoice/accountings/items/id` became nullable (media type: application/json)
-  the request property `invoices/items/invoice/accountings/items/id` became nullable (media type: text/json)
-  the request property `invoices/items/invoice/accountings/items/sort` became nullable (media type: application/json)
-  the request property `invoices/items/invoice/accountings/items/sort` became nullable (media type: text/json)
-  the request property `invoices/items/invoice/accountings/items/sort` became nullable (media type: application/*+json)
-  the request property `invoices/items/invoice/amount` became nullable (media type: text/json)
-  the request property `invoices/items/invoice/amount` became nullable (media type: application/json)
-  the request property `invoices/items/invoice/amount` became nullable (media type: application/*+json)
-  the request property `invoices/items/invoice/bookkeepingid` became nullable (media type: text/json)
-  the request property `invoices/items/invoice/bookkeepingid` became nullable (media type: application/*+json)
-  the request property `invoices/items/invoice/bookkeepingid` became nullable (media type: application/json)
-  the request property `invoices/items/invoice/creditor/legal` became nullable (media type: application/*+json)
-  the request property `invoices/items/invoice/creditor/legal` became nullable (media type: application/json)
-  the request property `invoices/items/invoice/creditor/legal` became nullable (media type: text/json)
-  the request property `invoices/items/invoice/date` became nullable (media type: text/json)
-  the request property `invoices/items/invoice/date` became nullable (media type: application/*+json)
-  the request property `invoices/items/invoice/date` became nullable (media type: application/json)
-  the request property `invoices/items/invoice/fileId` became nullable (media type: application/json)
-  the request property `invoices/items/invoice/fileId` became nullable (media type: application/*+json)
-  the request property `invoices/items/invoice/fileId` became nullable (media type: text/json)
-  the response header `idempotency-replayed` was added for the status `201`
-  added the non-success response with the status `409`
-  added the non-success response with the status `422`
-  added the optional property `errors` to the response with the `400` status (media type: text/plain)
-  added the optional property `errors` to the response with the `400` status (media type: text/json)
-  added the optional property `errors` to the response with the `400` status (media type: application/json)
-  added the optional property `isValid` to the response with the `400` status (media type: application/json)
-  added the optional property `isValid` to the response with the `400` status (media type: text/plain)
-  added the optional property `isValid` to the response with the `400` status (media type: text/json)
-  removed the optional property `detail` from the response with the `400` status (media type: text/json)
-  removed the optional property `detail` from the response with the `400` status (media type: text/plain)
-  removed the optional property `detail` from the response with the `400` status (media type: application/json)
-  removed the optional property `instance` from the response with the `400` status (media type: text/json)
-  removed the optional property `instance` from the response with the `400` status (media type: application/json)
-  removed the optional property `instance` from the response with the `400` status (media type: text/plain)
-  removed the optional property `status` from the response with the `400` status (media type: text/json)
-  removed the optional property `status` from the response with the `400` status (media type: text/plain)
-  removed the optional property `status` from the response with the `400` status (media type: application/json)
-  removed the optional property `title` from the response with the `400` status (media type: text/plain)
-  removed the optional property `title` from the response with the `400` status (media type: text/json)
-  removed the optional property `title` from the response with the `400` status (media type: application/json)
-  removed the optional property `type` from the response with the `400` status (media type: text/json)
-  removed the optional property `type` from the response with the `400` status (media type: text/plain)
-  removed the optional property `type` from the response with the `400` status (media type: application/json)


##### GET /api/v1/dms/portfolios/{uuid}
-  added the new optional `header` request parameter `if-none-match`
-  the response header `etag` was added for the status `200`


##### GET /api/v1/dms/realestates/{uuid}
-  added the new optional `header` request parameter `if-none-match`
-  the response header `etag` was added for the status `200`

</details>

## 2026-08-26 · Breaking: Benutzer- und Visa-Endpunkte entfernt (#22159)

- Entfernt: `GET /users`, `GET /realestate-users`, `GET /realestate-visas` – antworten mit `404`.
  `GET /persons`, `GET /realestate-persons` und `GET /tenancy-persons` bleiben unverändert.

## 2026-08 · Vertrag an das Verhalten angeglichen

- Entfernt: `DELETE /invoices/{uuid}` – Storno gibt es nicht; die Route antwortet mit `405`.
- Neu: `PATCH /documents/{uuid}` (Teilaktualisierung, Weg für die Archiv-Rückmeldung); `PUT` bleibt
  Vollersatz.
- Neu: `If-Match` auf `PUT`/`PATCH`/`DELETE /documents/{uuid}` → `412` bei veraltetem `ETag` (opt-in).
- Neu: `GET /documents` ist paginiert (`items`, `page`, `pageSize`, `totalCount`, `pageCount`) und
  akzeptiert das Flag `requires_dms_archiving`.
- Geändert: `changed_since`/`changed_until` werden bei den ERP-Listen bis ins ERP durchgereicht statt
  verworfen; `links[].id` wird gegen die Stammdaten des Mandanten geprüft (`400` bei unbekannter ID).
- Neu: `dmsReference` auf `POST /invoices` (#23154); Antwort von `POST /invoices` ist `201 { id, number }`
  mit `Location`-Header.

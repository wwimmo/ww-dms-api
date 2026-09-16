# Änderungen an der DMS-API

Neueste zuerst. Ab dem ersten automatischen Spec-Sync schreibt der Workflow *OpenAPI sync PR* die
Einträge selbst (`oasdiff` gegen den vorherigen Stand der Spezifikation, Build-Nummer und Commit
aus `info.x-build-*`). Die Einträge davor sind von Hand nachgetragen und tragen deshalb nur den
Monat.

**Deprecation-Regel:** Ein Endpunkt oder Feld, das entfällt, wird hier mindestens einen Release
vorher als *deprecated* angekündigt, bevor er aus der Spezifikation verschwindet. Breaking
Changes tragen im Sync-PR das Label `breaking`.

## 2026-09-16 · Polaris-Build 20260916.3 (`04a7f940a806`)

# API Changelog v1 vs. v1


## API Changes

### DELETE /api/v1/dms/documents/{uuid}
-  added the new optional `header` request parameter `if-match`
-  added the non-success response with the status `428`


### GET /api/v1/dms/documents/{uuid}
-  added the new optional `header` request parameter `if-none-match`
-  the response header `etag` was added for the status `200`


### PATCH /api/v1/dms/documents/{uuid}
-  added the new optional `header` request parameter `if-match`
-  added the non-success response with the status `428`


### PUT /api/v1/dms/documents/{uuid}
-  added the new optional `header` request parameter `if-match`
-  added the non-success response with the status `428`


### POST /api/v1/dms/invoices
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


### GET /api/v1/dms/portfolios/{uuid}
-  added the new optional `header` request parameter `if-none-match`
-  the response header `etag` was added for the status `200`


### GET /api/v1/dms/realestates/{uuid}
-  added the new optional `header` request parameter `if-none-match`
-  the response header `etag` was added for the status `200`


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

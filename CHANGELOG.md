# Änderungen an der DMS-API

Neueste zuerst. Ab dem ersten automatischen Spec-Sync schreibt der Workflow *OpenAPI sync PR* die
Einträge selbst (`oasdiff` gegen den vorherigen Stand der Spezifikation, Build-Nummer und Commit
aus `info.x-build-*`). Die Einträge davor sind von Hand nachgetragen und tragen deshalb nur den
Monat.

**Deprecation-Regel:** Ein Endpunkt oder Feld, das entfällt, wird hier mindestens einen Release
vorher als *deprecated* angekündigt, bevor er aus der Spezifikation verschwindet. Breaking
Changes tragen im Sync-PR das Label `breaking`.

## 2026-09 · `If-Match` im Vertrag, Pflicht angekündigt (#23151)

- Neu in der Spezifikation: `If-None-Match` und der Response-Header `ETag` auf den Einzelabfragen
  (`GET /documents/{uuid}`, `GET /realestates/{uuid}`, `GET /portfolios/{uuid}`), `If-Match` auf `PUT`,
  `PATCH` und `DELETE /documents/{uuid}`. Verhalten unverändert – die Header waren bisher nur in der Prosa
  beschrieben.
- Geändert: der `ETag` eines Dokuments ist ein Hash über den sichtbaren Inhalt statt eines Zeitstempels.
  Gespeicherte ETags aus früheren Abfragen passen einmal nicht mehr (`412`): neu lesen und wiederholen.
- **Angekündigt:** `If-Match` wird auf den Dokument-Schreibzugriffen Pflicht. Bis dahin sind Aufrufe ohne
  Header weiterhin erlaubt und werden protokolliert. Nach der Umstellung antwortet die API ohne Header mit
  `428 Precondition Required`; der Termin steht hier im Changelog. Siehe
  [Konventionen → Schreiben mit If-Match](docs/3-referenz/2-konventionen.md#schreiben-mit-if-match).

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

# OpenAPI-Referenz (der Wire-Vertrag)

Die **OpenAPI-Spezifikation ist die einzige Quelle der Wahrheit** für den Wire-Vertrag – Pfade, Methoden,
Request-/Response-Schemas, Feldtypen. Die handgeschriebene Doku unter [../docs/](../docs/) erklärt
*Bedeutung, Beziehungen und Lebenszyklus* und verweist hierher, statt Feldtabellen zu duplizieren.

## Was die Spezifikation heute abdeckt

- `POST /documents`, `GET /documents` (erfordert `changed_since`), `GET /documents/{uuid}`,
  `PUT /documents/{uuid}`, `GET /documents/{uuid}/content`.
- Stammdaten (`GET`, mit `changed_since` + `changed_until`): `/realestates` (+ `/{uuid}`,
  `/number:{number}`), `/houses`, `/units`, `/appliances`, `/tenants`, `/tenancies` (+ `/{uuid}`).
- Schemas: `DocumentEntity`, `DocumentLinkEntity`, `RealestateEntity`, Listen-Hüllen, `Problem`.
- Sicherheit: `bearerAuth` (JWT). Siehe [Authentifizierung](../docs/3-referenz/1-authentifizierung.md).

## Noch nicht enthalten

- **Rechnungs- & Buchhaltungs-Stammdaten** (Konten, Kostenstellen, Kreditoren, MWST-Codes, Rechnungen) –
  fachlich im Wiki definiert, aber noch nicht in der Spezifikation.
- **Löschen / Ersetzen / Versionierung** von Dokumenten.
- **Tombstones** (`deleted_at`), **Paginierung** und **Rate-Limit-Antworten** – siehe
  [Konventionen](../docs/3-referenz/2-konventionen.md).

> Eine versionierte Momentaufnahme der Spezifikation wird zum ersten stabilen Release in diesem Ordner
> abgelegt (`dms-api.v1.yaml`). Bis dahin ist der generierte Vertrag aus dem laufenden Dienst massgeblich.

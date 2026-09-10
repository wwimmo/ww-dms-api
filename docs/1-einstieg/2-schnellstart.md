# Schnellstart

> Der kürzeste Weg von null zu «die API antwortet». Zugangsdaten für die Test-Umgebung erhalten Sie von
> W&W Immo – siehe [Authentifizierung → Zugangsdaten erhalten](../3-referenz/1-authentifizierung.md#zugangsdaten-erhalten-kontakt-aufnehmen).

## Ziel

Am Ende haben Sie die Erreichbarkeit geprüft, ein Token angefordert und geprüft, Dokumente abgefragt und
den Inhalt eines Dokuments gelesen.

## 0. Voraussetzungen

- Eine `client_id` und ein `client_secret` für die Test-Umgebung.
- `curl` (oder ein beliebiger HTTP-Client; für die Collection siehe [Bruno](../../bruno/README.md)).
- Die Basis-URL der Test-Umgebung: `https://erp-test.wwimmo.net`. Die Produktions-URL erhalten Sie beim
  Onboarding.

Platzhalter setzen (hier: Test):

```bash
BASE_URL="https://erp-test.wwimmo.net/api/v1/dms"
CLIENT_ID="<ihre-client-id>"
CLIENT_SECRET="<ihr-client-secret>"
```

## 1. Erreichbarkeit prüfen (ohne Token)

```bash
curl -s "$BASE_URL/health"
# → { "status": "Healthy", "version": "…", "details": { "service": "DokumentManagementSystem", … } }
```

Antwortet `200`, ist die API erreichbar. Der Endpunkt ist anonym und auf 30 Anfragen/Minute pro IP begrenzt.

## 2. Token holen

```bash
curl -s -X POST "$BASE_URL/token" \
  -H "Content-Type: application/json" \
  -d "{\"client_id\":\"$CLIENT_ID\",\"client_secret\":\"$CLIENT_SECRET\"}"
# → { "token": "<jwt>", "tokenType": "Bearer", "expiresIn": <sekunden>, "expiresAt": "<utc>" }
```

Das Token bis kurz vor `expiresAt` wiederverwenden – die Gültigkeit kommt vom Identity-Provider, nehmen Sie
keine feste Laufzeit an. Der Token-Endpunkt ist auf 30 Anfragen/Minute pro IP begrenzt.

Fehler: `401` mit `{ "error": "invalid_client", … }` bei falschen Zugangsdaten (nicht wiederholen,
Zugangsdaten prüfen), `502` mit `{ "error": "service_unavailable", … }`, wenn der Identity-Provider nicht
erreichbar ist (mit Backoff wiederholen). Details: [Authentifizierung](../3-referenz/1-authentifizierung.md).

## 3. Token prüfen

```bash
TOKEN="<token aus Schritt 2>"
curl -s "$BASE_URL/info" -H "Authorization: Bearer $TOKEN"
# → { "service": "DokumentManagementSystem", "apiVersion": "1.0", "caller": { "type": "M2M", "clientId": "…", "customerId": "…" } }
```

`caller.customerId` ist Ihr Mandant – stimmt er nicht, sind die Zugangsdaten falsch zugeordnet. `/info`
ist der einzige Daten-Endpunkt, der ohne `customerid` antwortet; alle anderen liefern ohne diesen Claim `403`.

## 4. Dokumente abfragen

```bash
curl -s "$BASE_URL/documents?changed_since=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer $TOKEN"
# → { "items": [ … ], "page": 1, "pageSize": 100, "totalCount": 3, "pageCount": 1 }
```

Die Antwort ist paginiert (`page`, `page_size`, dazu ein `Link`-Header mit `next`). Ohne `changed_since`
liefert der Endpunkt den Vollbestand – für den laufenden Abgleich immer mitsenden. Siehe
[Konventionen](../3-referenz/2-konventionen.md#polling-mit-changed_since).

## 5. Dokumentinhalt lesen

```bash
curl -s -OJ "$BASE_URL/documents/<uuid>/content" -H "Authorization: Bearer $TOKEN"
```

Antwort `200` mit dem gespeicherten MIME-Typ (z. B. `application/pdf`) und dem Dateinamen im
`Content-Disposition`-Header; `-OJ` speichert die Datei unter diesem Namen. Es gibt keine Weiterleitung.

## 6. Stammdaten nach demselben Muster

```bash
curl -s "$BASE_URL/realestates?changed_since=2026-01-01T00:00:00Z&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

Alle Listen-Endpunkte (Liegenschaften, Objekte, Mieter, Kreditoren, Konten, …) funktionieren gleich:
Zeitfenster, Paginierung, `Link`-Header.

## Wie weiter

- Ihren Ablauf wählen: [Dokument importieren](../2-anleitungen/1-dokument-importieren.md),
  [Rechnung importieren](../2-anleitungen/2-rechnung-importieren.md) oder
  [Dokument archivieren](../2-anleitungen/3-dokument-archivieren.md).
- Die Daten verstehen: [Domänenmodell](../4-konzepte/1-domaenenmodell.md).
- Ausprobieren ohne Skripte: [Bruno-Collection](../../bruno/README.md) oder die Swagger UI (siehe
  [README → Anzeigen](../../README.md#anzeigen)).

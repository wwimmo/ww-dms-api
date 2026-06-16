# Schnellstart

> Der kürzeste Weg von null zu „die API antwortet". *Das Verfahren zur Ausgabe der Zugangsdaten
> (`client_id`/`client_secret`) wird noch ergänzt.*

## Ziel

Am Ende haben Sie ein Token angefordert, nach Dokumenten abgefragt und den Inhalt eines Dokuments gelesen.

## 0. Voraussetzungen

- Eine `client_id` und ein `client_secret` (werden Ihnen bereitgestellt).
- Die Basis-URL der Test-Umgebung: `https://erp-test.wwimmo.ch` (die Produktions-URL erhalten Sie beim Onboarding).

Platzhalter setzen (hier: Test):

```bash
BASE_URL="https://erp-test.wwimmo.ch/api/v1/dms"
CLIENT_ID="<ihre-client-id>"
CLIENT_SECRET="<ihr-client-secret>"
```

## 1. Token holen

```bash
curl -s -X POST "$BASE_URL/token" \
  -H "Content-Type: application/json" \
  -d "{\"client_id\":\"$CLIENT_ID\",\"client_secret\":\"$CLIENT_SECRET\"}"
# → { "token": "...", "tokenType": "Bearer", "expiresIn": 3600, "expiresAt": "..." }
```

Token zwischenspeichern und wiederverwenden – der Token-Endpunkt ist auf 30 Anfragen/Minute begrenzt.
Siehe [Authentifizierung](../3-referenz/1-authentifizierung.md).

## 2. Dokumente abfragen

```bash
TOKEN="<token aus Schritt 1>"
curl -s "$BASE_URL/documents?changed_since=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer $TOKEN"
```

`changed_since` ist erforderlich. Siehe
[Konventionen](../3-referenz/2-konventionen.md#polling-mit-changed_since).

## 3. Dokumentinhalt lesen

```bash
curl -sL "$BASE_URL/documents/<uuid>/content" \
  -H "Authorization: Bearer $TOKEN" -o dokument.pdf
```

`-L` folgt der `302`-Weiterleitung, wenn die Datei über ein CDN ausgeliefert wird.

## Wie weiter

- Ihren Ablauf wählen: [Dokument importieren](../2-anleitungen/1-dokument-importieren.md),
  [Rechnung importieren](../2-anleitungen/2-rechnung-importieren.md) oder
  [Dokument archivieren](../2-anleitungen/3-dokument-archivieren.md).
- Die Daten verstehen: [Domänenmodell](../4-konzepte/1-domaenenmodell.md).

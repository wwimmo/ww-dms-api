# Authentifizierung

So erhalten und verwenden Sie Zugangsdaten.

## Modell

- **Protokoll:** OAuth 2.0 **Client Credentials** (Maschine-zu-Maschine). Kein interaktiver Login.
- **Token:** JWT, gesendet als `Authorization: Bearer <token>`.
- **Erforderlicher Scope:** `wwimmo:dms:api`. Tokens ohne diesen Scope werden mit `403` abgewiesen.

## Token holen

Sie fragen das Token an einem Endpunkt der API an. Der Endpunkt nimmt einen **JSON-Body** mit
`client_id` und `client_secret` entgegen (kein Formular, kein `grant_type`-Feld – das ergänzt die API
selbst):

```
POST {basis-url}/api/v1/dms/token
Content-Type: application/json

{
  "client_id": "<ihre client id>",
  "client_secret": "<ihr client secret>"
}
```

Die Antwort ist ein JSON-Objekt mit dem Token und seiner Gültigkeit:

```json
{
  "token": "<jwt>",
  "tokenType": "Bearer",
  "expiresIn": 3600,
  "expiresAt": "2026-01-01T01:00:00Z"
}
```

`expiresIn` (Sekunden) und `expiresAt` (UTC) stammen vom Identity-Provider. Verwenden Sie diese Werte,
statt eine feste Gültigkeit anzunehmen, und erneuern Sie das Token kurz vor `expiresAt`. Der Endpunkt ist
auf **30 Anfragen/Minute pro IP** begrenzt – ein Token pro Ablaufzeitraum genügt.

### Fehler am Token-Endpunkt

Der Token-Endpunkt antwortet nicht im Problem-Format, sondern mit einem einfachen Objekt
(`application/json`):

| Status | Body | Was tun |
| --- | --- | --- |
| `401` | `{ "error": "invalid_client", "message": "Authentication failed. Verify your client_id and client_secret." }` | Zugangsdaten prüfen; nicht wiederholen. |
| `502` | `{ "error": "service_unavailable", "message": "Authentication service is temporarily unavailable. Please try again later." }` | Mit Backoff wiederholen. |
| `429` | siehe [Konventionen → Rate-Limits](2-konventionen.md#rate-limits) | `Retry-After` abwarten. |

## Was das Token enthält

| Claim | Bedeutung |
| --- | --- |
| `scopes` | Muss `wwimmo:dms:api` enthalten, sonst `403` auf allen Endpunkten. |
| `customerid` | Ihr Mandant. Alle Daten-Endpunkte verlangen ihn (`403` ohne); die Daten sind darüber automatisch auf Ihren Mandanten eingeschränkt. Einzige Ausnahme ist `GET /info`, das ohne `customerid` antwortet und sich deshalb als Token-Test eignet. |
| `erp` | Optional, `it2` oder `rimo`. Wirkt nur auf `POST /invoices`: welche Kontierungsregeln gelten. Ohne Claim gelten die ImmoTop2-Regeln. |

Das Rate-Limit authentifizierter Aufrufe wird pro `client_id` gezählt – ein anderer Partner kann Ihr
Kontingent nicht aufbrauchen.

## Token verwenden

Bei jeder Anfrage mitsenden – das `token`-Feld aus der Antwort als Bearer-Token:

```
GET {basis-url}/api/v1/dms/documents?changed_since=2026-01-01T00:00:00Z
Authorization: Bearer <token>
```

## Basis-URLs

| Umgebung | Basis-URL | Zweck |
| --- | --- | --- |
| Test | `https://erp-test.wwimmo.net` | Sandbox für die Integration: eigener Test-Mandant, eigene Zugangsdaten, echte Endpunkte. |

Alle Pfade beginnen mit `/api/v1/dms`, z. B. `https://erp-test.wwimmo.net/api/v1/dms/token`. Die
**Produktions-URL** erhalten Sie beim Onboarding. Die Swagger UI auf GitHub Pages zeigt ebenfalls auf
Test (siehe [README → Anzeigen](../../README.md#anzeigen)).

## Zugangsdaten erhalten (Kontakt aufnehmen)

`client_id` und `client_secret` werden **pro DMS-Anbieter und Kunde (Mandant)** von W&W Immo ausgestellt.
Sie sind an den Mandanten (`customerid`) und an den Scope gebunden und gelten je Umgebung getrennt.

Wenden Sie sich an **`<Kontaktadresse folgt>`** und nennen Sie:

- Ihr Produkt und Ihren Ansprechpartner,
- den Kunden bzw. Mandanten, den Sie anbinden,
- die Umgebung (Test oder Produktion).

Sie erhalten die Zugangsdaten über einen sicheren Kanal, die Produktions-URL sowie die Archiv-ID Ihrer
DMS-Anbindung (`dmsReference.archive`, siehe [Konventionen](2-konventionen.md#teilaktualisierung-patch-statt-put)).

> **Follow-up:** Das Verfahren zur Ausgabe und Rotation der Zugangsdaten wird hier beschrieben, sobald es
> festgelegt ist. Bis dahin gilt der Kontaktweg.

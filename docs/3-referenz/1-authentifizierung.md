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

Der Endpunkt ist auf **30 Anfragen/Minute pro IP** begrenzt – speichern Sie das Token zwischen und
verwenden Sie es bis `expiresAt` wieder.

## Token verwenden

Bei jeder Anfrage mitsenden – das `token`-Feld aus der Antwort als Bearer-Token:

```
GET {basis-url}/api/v1/dms/documents?changed_since=2026-01-01T00:00:00Z
Authorization: Bearer <token>
```

## Offen

- Die **Basis-URL je Umgebung** (Dev/Test/Prod) wird noch festgelegt und hier ergänzt.
- Das **Verfahren zur Ausgabe von `client_id`/`client_secret`** (Onboarding, Rotation) wird noch
  beschrieben.

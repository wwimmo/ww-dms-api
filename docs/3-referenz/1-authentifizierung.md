# Authentifizierung

So erhalten und verwenden Sie Zugangsdaten.

## Modell

- **Protokoll:** OAuth 2.0 **Client Credentials** (Maschine-zu-Maschine). Kein interaktiver Login.
- **Token:** JWT, gesendet als `Authorization: Bearer <token>`.
- **Erforderlicher Scope:** `wwimmo:dms:api`. Tokens ohne diesen Scope werden mit `403` abgewiesen.

## Token holen

Sie fragen das Token an einem Endpunkt der API an:

```
POST {basis-url}/api/v1/dms/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
client_id=<ihre client id>
client_secret=<ihr client secret>
```

Die Antwort ist eine Standard-OAuth-Token-Antwort (`access_token`, `token_type=Bearer`, `expires_in`, …).

Der Endpunkt ist auf **30 Anfragen/Minute pro IP** begrenzt – speichern Sie das Token zwischen und
verwenden Sie es bis zum Ablauf wieder.

## Token verwenden

Bei jeder Anfrage mitsenden:

```
GET {basis-url}/api/v1/dms/documents?changed_since=2026-01-01T00:00:00Z
Authorization: Bearer <access_token>
```

## Offen

- Die **Basis-URL je Umgebung** (Dev/Test/Prod) wird noch festgelegt und hier ergänzt.
- Das **Verfahren zur Ausgabe von `client_id`/`client_secret`** (Onboarding, Rotation) wird noch
  beschrieben.

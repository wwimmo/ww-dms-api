# W&W Immo DMS-API – Bruno-Collection

Einsatzbereite Bruno-Collection für die DMS-API der W&W Immo Informatik AG, gerichtet
an DMS-Anbieter. Die Collection enthält ausschließlich Endpunkte, die produktiv gegen
echte Systeme (ImmoTop2, Rimo R5) laufen.

## Nutzung

1. Collection in Bruno importieren (Ordner `bruno` öffnen).
2. Umgebung **Vorlage** auswählen.
3. Die Variablen `baseUrl`, `clientId` und `clientSecret` in der Umgebung eintragen.
4. Zuerst **1. Token / Token holen** ausführen. Das Zugriffstoken wird automatisch als
   `{{token}}` gespeichert und für alle weiteren Anfragen verwendet.
5. Anschließend beliebige Anfrage ausführen.

## Delta-Sync-Konvention

Die Synchronisations-Endpunkte liefern Änderungen über ein Zeitfenster:

- `changed_since` und `changed_until` als Query-Parameter, beide erforderlich.
- Zeitstempel im Format ISO 8601 in UTC (z. B. `2026-01-15T00:00:00Z`).
- Die Antwort ist paginiert und hat die Form `{ items: [...], totalCount, pageCount, page, pageSize }`.

## Mandanten-Scoping

Die Sichtbarkeit der Daten wird automatisch über das Zugriffstoken auf Ihren Mandanten
eingeschränkt. Es ist keine zusätzliche Filterung notwendig.

## Weiterführende Dokumentation

Der verbindliche Vertrag sowie die ausführliche Dokumentation zu Authentifizierung,
Konventionen und Fehlerbehandlung befinden sich in der Repo-Dokumentation:
[Authentifizierung](../docs/3-referenz/1-authentifizierung.md),
[Konventionen](../docs/3-referenz/2-konventionen.md) und
[OpenAPI-Spezifikation](../openapi/).

# Dokument importieren (DMS → ERP)

Ziel: Ein Dokument, das in Ihrem DMS liegt, wird im E-Dossier des ERP verlinkt. Es werden nur Metadaten
übertragen – nicht der Dateiinhalt. Beispiel: eine eingescannte Kreditorenrechnung oder -gutschrift, eine
E-Rechnung.

## Voraussetzungen

- Ein gültiges Token mit Scope `wwimmo:dms:api` – siehe
  [Authentifizierung](../3-referenz/1-authentifizierung.md).
- Das Dokument ist bereits in Ihrem DMS abgelegt und indexiert.

## Schritte

1. **Benötigte Stammdaten aktualisieren** (abrufen, nicht annehmen, dass sie aktuell sind):

   ```
   GET /realestates?changed_since=<letzter-abgleich>&changed_until=<jetzt>
   GET /units?changed_since=<letzter-abgleich>&changed_until=<jetzt>
   ```

2. **Dokument im ERP anlegen** – mit Metadaten und Verknüpfungen, ohne Dateiinhalt:

   ```
   POST /documents
   Content-Type: application/json

   {
     "name": "EKZ Stromrechnung Winter 2026",
     "type": "invoice",
     "mime-type": "application/pdf",
     "extention": ".pdf",
     "filedate": "2026-01-15T10:00:00Z",
     "storageTargets": ["DMS"],
     "links": [
       { "id": "<liegenschaft-uuid>", "entity-type": "realestate" },
       { "id": "<objekt-uuid>", "entity-type": "unit" }
     ]
   }
   ```
   Die Antwort enthält das angelegte Dokument inkl. `id`. Das ERP verlinkt es im E-Dossier.

3. **Dokument aktualisieren**, falls sich etwas ändert (z. B. weitere Verknüpfungen, neuer Name):

   ```
   PUT /documents/{id}
   ```

   Ein nicht mehr benötigtes Dokument lässt sich mit `DELETE /documents/{id}` löschen (Soft-Delete,
   Antwort `204`).

## Ablauf

```mermaid
sequenceDiagram
  participant DMS
  participant API as DMS-API
  participant ERP
  DMS->>API: GET /realestates?changed_since=...
  DMS->>API: GET /units?changed_since=...
  DMS->>DMS: Dokument neu (abgelegt & indexiert)
  DMS->>+API: POST /documents
  API->>ERP: Datei anlegen
  API-->>-DMS: { id: "..." }
  DMS->>+API: PUT /documents/{id}
  API->>ERP: Datei aktualisieren
  API-->>-DMS: 200
```

## Hinweise

- `links[].entity-type` (gültige Werte, Gross-/Kleinschreibung egal): `realestate`, `house`, `unit`,
  `appliance`, `tenant`, `tenancy`.
- `type` (gültige Werte): `invoice`, `credit`, `correspondence`, `assurance`.
- `storageTargets` (gültige Werte): `DMS`, `ERP`.
- Für Rechnungen mit Freigabeprozess verwenden Sie stattdessen
  [Rechnung importieren](2-rechnung-importieren.md).

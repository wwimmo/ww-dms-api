# Dokument archivieren (ERP → DMS)

Ziel: Ein im ERP erzeugtes Dokument wird in Ihr DMS geholt, archiviert und die Archiv-Referenz
zurückgeschrieben. Beispiel: Buchungsbelege zu manuellen Buchungen, Mahnbriefe aus dem Mahnlauf.

## Voraussetzungen

- Ein gültiges Token mit Scope `wwimmo:dms:api` – siehe
  [Authentifizierung](../3-referenz/1-authentifizierung.md).

## Schritte

1. **Dokumente finden, die das ERP zur Archivierung vorsieht:**

   ```
   GET /documents?changed_since=<letzter-abgleich>&requires_dms_archiving
   ```
   `requires_dms_archiving` ist ein Flag-Filter: nur Dokumente, die durch das DMS archiviert werden sollen.

2. **Dateiinhalt je Dokument abrufen:**

   ```
   GET /documents/{id}/content
   ```
   Liefert den Binärstrom (`application/octet-stream`) oder eine `302`-Weiterleitung, wenn die Datei auf
   einem CDN liegt – der Weiterleitung folgen.

3. **Benötigte Stammdaten abrufen**, um korrekt abzulegen, z. B.:

   ```
   GET /realestates/{id}
   GET /tenancies/{id}
   ```

4. **In Ihrem DMS archivieren**, dann die **Archiv-Referenz zurückschreiben**, damit das ERP die
   Archivierung kennt:

   ```
   PATCH /documents/{id}
   Content-Type: application/json

   {
     "dmsReference": { "archive": "<archiv-id>", "documentId": "<dms-dokument-id>" },
     "storageTargets": ["DMS", "ERP"]
   }
   ```
   `PATCH` ist eine **Teilaktualisierung**: nicht mitgesendete Eigenschaften bleiben unverändert.

   > **Nicht `PUT` verwenden.** `PUT` ersetzt das Dokument vollständig, nicht mitgesendete Eigenschaften
   > werden geleert. Ein `PUT` mit nur `dmsReference` löscht damit die `links` des Dokuments
   > (Liegenschaft, Mietverhältnis …). Siehe
   > [Konventionen → Teilaktualisierung](../3-referenz/2-konventionen.md#teilaktualisierung-patch-statt-put).

   Das ERP kann seine E-Dossier-Kopie anschliessend optional entfernen (das Dokument liegt dann nur im DMS
   oder in beiden Systemen).

## Ablauf

```mermaid
sequenceDiagram
  participant DMS
  participant API as DMS-API
  participant ERP
  DMS->>+API: GET /documents?requires_dms_archiving
  API->>ERP: zu archivierende Dateien
  API-->>-DMS: Liste
  DMS->>DMS: Dokument anlegen
  DMS->>+API: GET /documents/{id}/content
  API->>ERP: Inhalt holen
  API-->>-DMS: Binär / 302
  DMS->>+API: GET /realestates/{id}
  API-->>-DMS: Liegenschaft
  DMS->>+API: GET /tenancies/{id}
  API-->>-DMS: Mietverhältnis
  DMS->>+API: PATCH /documents/{id} { dmsReference: {...} }
  API->>ERP: Datei aktualisieren
  ERP->>ERP: optional E-Dossier-Version löschen
  API-->>-DMS: 200
```

## Hinweise

- `storageTargets` drückt nach der Archivierung aus, wo die Datei liegt: `["DMS"]` (nur DMS) oder
  `["DMS","ERP"]` (beide).
- Ob das ERP seine E-Dossier-Kopie löscht, ist optional.
- Wollen Sie ausschliessen, dass Ihr Rückschreiben eine zwischenzeitliche Änderung des ERP überschreibt:
  den `ETag` aus Schritt 1/2 als `If-Match` mitsenden. Bei veralteter Version antwortet die API mit
  `412 Precondition Failed` statt zu schreiben – siehe
  [Konventionen → Schreiben mit If-Match](../3-referenz/2-konventionen.md#schreiben-mit-if-match).

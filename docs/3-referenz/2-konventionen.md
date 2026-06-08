# Konventionen

Regeln, die über alle Endpunkte hinweg gelten – einmal hier beschrieben statt pro Endpunkt wiederholt.

## Polling mit `changed_since`

Die API wird durch **Abrufen** konsumiert, nicht durch Push. Listen-Endpunkte erwarten einen
`changed_since`- (bei Stammdaten zusätzlich `changed_until`-) Zeitstempel und liefern die im Zeitfenster
geänderten Datensätze.

```
GET /documents?changed_since=2026-01-01T00:00:00Z
GET /realestates?changed_since=2026-01-01T00:00:00Z&changed_until=2026-01-08T00:00:00Z
```

- `changed_since` ist auf Listen-Endpunkten **erforderlich**; Format: RFC 3339 / ISO 8601.
- Stammdaten-Endpunkte erwarten zusätzlich `changed_until` und liefern Änderungen im Intervall
  `[changed_since, changed_until)`.
- Ablauf eines Polling-Zyklus: höchsten Zeitstempel merken, mit ihm als `changed_since` abfragen, danach
  auf die neueste Änderung der Antwort weiterschalten.

## Kein Push / keine Webhooks

Die Synchronisation erfolgt ausschliesslich über von Ihnen ausgelöste Abrufe (Pull). Es gibt keine
Webhooks und keine Events.

## Idempotenz

Da Abrufe wiederholt werden können, sind schreibende Operationen wiederholungssicher. Behandeln Sie
Aufrufe als potenziell mehrfach gesendet und bauen Sie auf Ihrer Seite keine „genau-einmal-bei-Empfang"-
Logik ohne Dedup-Schlüssel.

## Löschungen

Eine harte Löschung wäre für ein abrufendes System unsichtbar. Daher werden Löschungen über **Tombstones**
abgebildet: Ein gelöschter Datensatz bleibt mit einer Lösch-Markierung in den Antworten sichtbar, bis eine
Aufbewahrungsfrist abläuft – lange genug, dass auch ein System mit mehrwöchiger Polling-Lücke die Löschung
mitbekommt.

> Die konkreten Felder (`deleted_at`) und die Aufbewahrungsfrist werden noch festgelegt und ergänzt. Bis
> dahin gilt: Verschwinden ≠ Löschung.

## Paginierung

> Wird noch festgelegt (Seitengrösse, Cursor/Offset, Antwort-Hülle) und hier ergänzt. Prüfen Sie dies vor
> der Anbindung grosser Datenmengen.

## Rate-Limits

Der Token-Endpunkt ist auf **30 Anfragen/Minute pro IP** begrenzt. Auch Daten-Endpunkte sind
rate-limitiert; die genauen Grenzen und die `429`-Header werden ergänzt.

## Bezeichner & sprechende Schlüssel

- Primäre Bezeichner sind **UUIDs** (`id`, Pfad `{uuid}`).
- Einige Entitäten unterstützen zusätzlich einen **sprechenden Sekundärschlüssel**, z. B.
  `GET /realestates/number:{number}`.
- Buchhaltungsbezogene Strukturen sind über **`bookkeepingid`** verschlüsselt, nicht über `realestateid` –
  siehe [Domänenmodell](../4-konzepte/1-domaenenmodell.md).

## Inhaltstypen

- Anfragen/Antworten verwenden `application/json`.
- Der **Dateiinhalt** (`GET /documents/{uuid}/content`) liefert `application/octet-stream` oder eine
  `302`-Weiterleitung, wenn die Datei über ein CDN ausgeliefert wird – der Weiterleitung folgen.

## Fehler

Alle Fehler verwenden einen Problem+JSON-Body – siehe [Fehlerbehandlung](3-fehler.md).

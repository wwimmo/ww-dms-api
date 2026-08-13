# Übersicht

Eine einheitliche REST-API, über die ein **Dokumentenmanagement-System (DMS)** Dokumente und die
zugehörigen Stammdaten mit einem in der Cloud betriebenen W&W-Immo-ERP (Rimo R5 oder ImmoTop2)
austauscht.

## Geltungsbereich

Die API gilt für Kunden, deren ERP in der Cloud betrieben wird. **On-Premise-Installationen** nutzen
weiterhin die bestehenden DMS-Schnittstellen – diese API ersetzt sie nicht.

## Für wen

Für **DMS-Anbieter**, die ihr Produkt anbinden. Die Anbindung erfolgt über **Polling**: Ihr System ruft
die API aktiv ab und hält sich so synchron. Es gibt keine Webhooks oder Pushes.

## Die drei Kernabläufe

Alles, was die API tut, dient einem dieser drei Abläufe:

| Ablauf | Richtung | Was übertragen wird | Beispiel |
| --- | --- | --- | --- |
| **Dokument importieren** | DMS → ERP | Dokument liegt zuerst im DMS; die Metadaten (ohne Dateiinhalt) gehen ans ERP, das sie im E-Dossier verlinkt. | Eingescannte Kreditorenrechnungen/-gutschriften, E-Rechnungen. |
| **Rechnung importieren** | DMS → ERP | Wie ein Dokumentimport, zusätzlich wird die im DMS freigegebene Rechnung ins ERP zur Verbuchung importiert. | Lieferantenrechnung (Kreditorenbeleg). |
| **Dokument archivieren** | ERP → DMS | Dokument entsteht im ERP; das DMS holt Metadaten und Datei, archiviert sie und meldet den Erfolg zurück. | Buchungsbelege zu manuellen Buchungen, Mahnbriefe aus dem Mahnlauf. |

> Öffnen, Anzeigen und Publizieren von Dokumenten im Portal funktioniert wie bisher und ist **nicht Teil**
> dieser API.

Die schrittweisen Abläufe finden Sie in den [Anleitungen](../2-anleitungen/).

## Das Pull-/Polling-Modell

Sie konsumieren die API ausschliesslich durch **Abrufen** – typischerweise
`GET /documents?changed_since=<Zeitstempel>`. Daraus ergeben sich einige Regeln, die in den
[Konventionen](../3-referenz/2-konventionen.md) beschrieben sind:

- Jede Änderung trägt einen Zeitstempel, damit `changed_since` sie findet.
- Wie Löschungen über das Polling sichtbar werden, wird derzeit erarbeitet – siehe
  [Konventionen](../3-referenz/2-konventionen.md#löschungen).
- **Lesende** Abrufe sind beliebig wiederholbar. **Schreibende** Aufrufe sind es nicht: es gibt noch keinen
  Idempotenz-Schlüssel, eine Wiederholung nach einem Timeout legt einen zweiten Datensatz an – siehe
  [Konventionen](../3-referenz/2-konventionen.md#idempotenz).

## Das Domänenmodell

Die API spricht ein **eigenständiges Fachmodell** (Portfolio → Buchhaltung → Konten/Rechnungen) und ist
von ERP-Interna entkoppelt. So programmieren Sie gegen ein stabiles Modell. Details im
[Domänenmodell](../4-konzepte/1-domaenenmodell.md).

## Begriffe, die man im Kopf haben sollte

- **Dokument** – eine lesbare Datei (Rechnung, Gutschrift, Korrespondenz, Versicherung) mit Metadaten,
  Ablagezielen (`DMS`, `ERP`) und Verknüpfungen zu Stammdaten.
- **Stammdaten** – die stabilen Bezugsobjekte: Liegenschaft, Haus, Objekt, Gerät, Mieter, Mietverhältnis
  und (für Rechnungen) Kreditor, Konto, Buchhaltung.
- **Buchhaltung** – die Abrechnungseinheit, an der Rechnungsdaten hängen.
- **Portfolio** – fasst Liegenschaften eines Eigentümers zusammen.
- **Ablageziel** – wo ein Dokument physisch liegt: nur DMS, nur ERP oder beides.

Das vollständige Vokabular steht im [Glossar](../4-konzepte/2-glossar.md).

# W&W Immo DMS-API

Eine einheitliche **REST-API**, über die Dokumentenmanagement-Systeme (DMS) mit den in der Cloud
betriebenen ERP-Systemen **Rimo R5** und **ImmoTop2** von W&W Immo Informatik AG zusammenarbeiten.

## Geltungsbereich

Diese API gilt für Kunden, deren ERP **in der Cloud betrieben** wird. Sie ersetzt die bestehenden
Schnittstellen **nicht**: Kunden mit einer **On-Premise-Installation** nutzen weiterhin die bisherigen
DMS-Schnittstellen, da diese auf direktem Datenbankzugriff beruhen, der in der Cloud nicht zur Verfügung
steht.

## Für wen ist diese Dokumentation?

Für **DMS-Anbieter**, die ihr Produkt an ein cloud-betriebenes W&W-Immo-ERP anbinden. Die Anbindung
erfolgt über **Polling**: Ihr System ruft die API aktiv ab (Pull). Es gibt keine Webhooks oder Pushes.

## Drei Dinge, die man zuerst verstehen sollte

1. **Drei Kernabläufe** – *Dokument importieren*, *Rechnung importieren* und *Dokument archivieren*.
   Siehe [Übersicht](docs/1-einstieg/1-uebersicht.md).
2. **Pull-/Polling-Modell** – Änderungen werden über `?changed_since=...` abgerufen. Siehe
   [Konventionen](docs/3-referenz/2-konventionen.md).
3. **Klares Domänenmodell** – die API spricht ein eigenständiges Fachmodell (Portfolio → Buchhaltung → …)
   und ist von ERP-Interna entkoppelt. Siehe [Domänenmodell](docs/4-konzepte/1-domaenenmodell.md).

## Inhalt

**1 – Einstieg**
- [Übersicht](docs/1-einstieg/1-uebersicht.md) – was die API tut, die drei Kernabläufe, das Pull-Modell.
- [Schnellstart](docs/1-einstieg/2-schnellstart.md) – Token holen und erste Abfrage. *(in Arbeit)*

**2 – Anleitungen**
- [Dokument importieren](docs/2-anleitungen/1-dokument-importieren.md) – DMS → ERP.
- [Rechnung importieren](docs/2-anleitungen/2-rechnung-importieren.md) – DMS → ERP → Freigabe.
- [Dokument archivieren](docs/2-anleitungen/3-dokument-archivieren.md) – ERP → DMS.

**3 – Referenz**
- [OpenAPI-Spezifikation](openapi/README.md) – der verbindliche Vertrag.
- [Authentifizierung](docs/3-referenz/1-authentifizierung.md) – OAuth 2.0, Token, Scope.
- [Konventionen](docs/3-referenz/2-konventionen.md) – Polling, `changed_since`, Idempotenz, Schlüssel.
- [Fehlerbehandlung](docs/3-referenz/3-fehler.md) – Problem+JSON.

**4 – Konzepte**
- [Domänenmodell](docs/4-konzepte/1-domaenenmodell.md) – Entitäten, Beziehungen, Lebenszyklus.
- [Glossar](docs/4-konzepte/2-glossar.md) – Fachbegriffe.

---

> Die Dokumentation befindet sich im Aufbau. Hinweise für Mitwirkende sowie der Stand offener Punkte
> stehen in [CONTRIBUTING.md](CONTRIBUTING.md).

# Mitwirken & interne Hinweise

> **Nicht kundengerichtet.** Diese Datei bündelt Quellen, offene Punkte und Redaktionsregeln für das
> Team. Die Inhalte unter `README.md`, `docs/` und `openapi/` sind kundengerichtet und sollen frei von
> internen Verweisen, Tool-Namen und WIP-Markern bleiben.

## Aufbau der Dokumentation (Diátaxis)

Die Doku folgt dem [Diátaxis](https://diataxis.fr/)-Modell – vier Arten von Inhalten, jede beantwortet
eine andere Frage:

| Ordner | Diátaxis | Frage |
| --- | --- | --- |
| `docs/1-einstieg` | Tutorial / Übersicht | „Bring mich zum ersten Erfolg" |
| `docs/2-anleitungen` | How-to | „Wie mache ich X?" |
| `docs/3-referenz` + `openapi/` | Reference | „Was ist der genaue Vertrag?" |
| `docs/4-konzepte` | Explanation | „Warum ist es so gebaut?" |

Die Reihenfolge wird über **Zahlenpräfixe** an Ordnern und Dateien erzwungen (`1-`, `2-`, …), damit die
Navigation in VS Code, GitHub und späteren Static-Site-Generatoren stimmt.

## Quellenmaterial (intern)

- **OpenAPI-Vertrag** – generiert aus dem laufenden DMS-Modul im Cloud-Backend
  (Repo-Pfad `…/DokumentManagementSystem`, Entwurf `dms-api.yaml`).
- **Live Swagger UI (Dev):** <https://polaris.wwportal-dev.ch/swagger/index.html>
- **Konzept & Abläufe:** ADO-Wiki [Konzept DMS-API-Design (1241)](https://dev.azure.com/wwimmo-mobile/mobile/_wiki/wikis/mobile.wiki/1241/Konzept-DMS-API-Design).
- **Domänenmodell:** ADO-Wiki [Domänenmodell (1231)](https://dev.azure.com/wwimmo-mobile/mobile/_wiki/wikis/mobile.wiki/1231/Dom%C3%A4nenmodell).
- **Endpoint-/Datenstruktur:** ADO-Wiki [Endpoint-Struktur (2476)](https://dev.azure.com/wwimmo-mobile/mobile/_wiki/wikis/mobile.wiki/2476/Endpoint-Struktur-(Portfolio-Bookkeeping)).
- **Design-Board:** [Miro](https://miro.com/app/board/uXjVMhPcv8o=/).

## Offene Punkte / „was wir noch brauchen"

Kritische Blöcke, bevor die Doku partnertauglich ist. Im kundengerichteten Text bewusst **nicht** als
nummerierte Lücken sichtbar – dort höchstens neutral „wird ergänzt".

| # | Lücke | Blockiert | Wer liefert |
| --- | --- | --- | --- |
| 1 | **Basis-URLs je Umgebung** (Dev/Test/Prod). Spec nennt `erp.wwimmo.ch/api/v1/dms`, Live-Dev ist `polaris.wwportal-dev.ch`. | Schnellstart, Auth | Gabor Raz / DevOps |
| 2 | **Wie ein Anbieter `client_id`/`client_secret` erhält** (Onboarding, Rotation). | Auth, Schnellstart | Sandro Brunner |
| 3 | **Tombstone-/Delete-Semantik** im Vertrag (`deleted_at`, Aufbewahrung). | Konventionen, OpenAPI | Andrew Service / Martin Constam |
| 4 | **Paginierung & Rate-Limit-Vertrag** (Seitengrösse, Cursor/Offset, Header). | Konventionen, OpenAPI | Backend |
| 5 | **Fehlerkatalog** – konkrete `type`-Werte + Recovery. | Fehler | Backend |
| 6 | **Versionierungs- & Deprecation-Policy** für API und Doku. | (neue Seite) | PO + Backend |
| 7 | **Offene Domänenentscheide** mit Vertragswirkung: `vatcodes` „für alle", `realestatevisas`-Scope, Scope via Pfad vs. Payload. | Domänenmodell, OpenAPI | Domänen-Workshops (PSI) |
| 8 | **Rechnungs-/Stammdaten-Schemas in OpenAPI** (accounts, costcenters, creditors, invoices) – heute nur im Wiki. | OpenAPI, Rechnung importieren | Backend |

## Redaktionsregeln

- **Firmenname:** „W&W Immo Informatik AG" (kurz „W&W Immo"), nicht „WWImmo".
- **Sprache:** Deutsch (analog Bestandsdoku).
- **Zielgruppe:** „DMS-Anbieter". Nicht „extern" – aus deren Sicht sind sie es nicht.
- **Interne Begriffe vermeiden** in kundengerichteten Texten (z. B. Produkt-/Plattform-Codenamen,
  interne Workflow-Namen). On-Premise-Bestand neutral als „On-Premise", nicht „alt/legacy".
- **OpenAPI ist die einzige Quelle der Wahrheit** für den Wire-Vertrag. Handgeschriebene Doku erklärt
  Bedeutung, Beziehungen und Lebenszyklus und verlinkt die Spec, statt Feldtabellen zu duplizieren.
- **Keine TMI:** keine internen Begründungen, Datumsstempel von Absprachen oder Verantwortlichen in
  kundengerichteten Seiten. Solche Punkte hierher.

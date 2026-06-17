# Domänenmodell

Die fachliche Landkarte: was die Entitäten *bedeuten*, wie sie *zusammenhängen* und welchen Lebenszyklus
sie haben. Feldtypen stehen in der [OpenAPI-Spezifikation](../../openapi/dms-api.v1.yaml).

## Fachmodell statt ERP-Interna

Die API stellt ein **eigenständiges Fachmodell** bereit und ist von den Interna der ERP-Systeme
entkoppelt. Wichtigste Konsequenzen für Sie:

- Buchhaltungsbezogene Strukturen (Konten, MWST-Codes, Buchungshistorie, Rechnungen) hängen an der
  **Buchhaltung** (`bookkeepingid`).
- Liegenschaften werden über **`portfolioid`** gruppiert.
- Am Endpunkt sind `portfolioid` und `bookkeepingid` **nicht null**.

So programmieren Sie gegen ein stabiles Modell, unabhängig davon, ob im Hintergrund Rimo R5 oder ImmoTop2
läuft.

Die **Buchhaltung** kennt drei Ausprägungen, die implizit über die gesetzten Fremdschlüssel erkennbar
sind: *Portfolio-Modus* (`portfolioid` gesetzt), *Liegenschafts-Modus* (`realestateid` gesetzt) und
*Standalone* (beide leer). Für ImmoTop2 kommt nur der Portfolio-Modus zum Tragen. 

## Stammdaten

Die stabilen Bezugsobjekte. Eine Zeile je Entität – vollständige Attribute in der Spezifikation und im
Wiki.

| Entität | Bedeutung |
| --- | --- |
| **Portfolio** | Verwaltete Zusammenfassung mehrerer Liegenschaften eines Eigentümers. |
| **Eigentümer** (Owner) | Rechtlich verantwortliche Partei; trägt Ertrag und Kosten; erteilt den Bewirtschaftungsauftrag. |
| **Verwaltung** (Management) | Organisation, die die Liegenschaften bewirtschaftet. |
| **Liegenschaft** (RealEstate) | Rechtlich/wirtschaftlich abgegrenzte Immobilieneinheit; Basis aller Bewirtschaftungsprozesse. Gehört zu genau einem Portfolio. |
| **Haus** (House) | Physisches Gebäude innerhalb einer Liegenschaft; enthält Objekte. |
| **Objekt** (Unit) | Kleinste abrechenbare Mieteinheit. Gehört zu genau einer Liegenschaft (bei Wohnungen zusätzlich zu einem Haus). |
| **Gerät** (Appliance) | Wartbares Gerät, einer Liegenschaft/einem Objekt zugeordnet. |
| **Mietverhältnis** (Tenancy) | Verbindet ein Objekt mit einem Mieter über die Zeit. |
| **Mieter** (Tenant) | Mietende Partei (verweist auf eine Person). |
| **Person** (Person) | Natürliche/juristische Person; Kontakt-Wurzel hinter Eigentümern, Mietern usw. |

### Beziehungen

```mermaid
erDiagram
  Owner       ||--o{ Portfolio  : besitzt
  Portfolio   ||--o{ RealEstate : enthaelt
  Management  ||--o{ RealEstate : verwaltet
  RealEstate  ||--o{ House      : "besteht aus"
  RealEstate  ||--o{ Unit       : hat
  House        ||--o{ Unit      : enthaelt
  Unit        ||--o{ Tenancy    : hat
  Tenancy     }o--|| Tenant     : betrifft
  Tenant      }o--|| Person     : ist
```

- Ein **Portfolio** hat mehrere **Liegenschaften**; jede Liegenschaft gehört zu genau einem Portfolio und
  wird von genau einer **Verwaltung** bewirtschaftet.
- Eine **Liegenschaft** besteht aus einem oder mehreren **Häusern** und **Objekten**.
- Ein **Mietverhältnis** verbindet ein **Objekt** mit einem **Mieter**; ein Mieter verweist auf eine
  **Person**.

## Buchhaltungs-Entitäten

Werden vom Rechnungsimport genutzt. Am Endpunkt hängen sie an der **Buchhaltung** (`bookkeepingid`).

| Entität | Bedeutung |
| --- | --- |
| **Buchhaltung** (Bookkeeping) | Abrechnungseinheit; Anker für Rechnungsdaten. Drei Modi (Portfolio/Liegenschaft/Standalone, siehe oben). |
| **Kreditor** (Creditor) | Ein Lieferant. Portfolio-/buchhaltungsunabhängig. |
| **Zahlstelle** (PaymentAccount) | Zahlverbindung eines Kreditors (IBAN). |
| **Auszahlverbindung** (PayoutBankAccount) | Auszahlende Bankverbindung ohne Liegenschaftsbezug. |
| **Auszahlverbindung↔Buchhaltung** (PayoutBankAccountBookkeeping) | M:N-Verknüpfung; ein `default`-Flag je Verknüpfung markiert die Standard-Verbindung der Buchhaltung. |
| **Konto** (Account) | Ein Buchhaltungskonto. |
| **Kostenstelle** (CostCenter) | Kostenstelle (nur ImmoTop2). |
| **Konto-Kostenstelle** (AccountCostCenter) | Zuweisung von Konten zu Kostenstellen. |
| **Buchungshistorie** (AccountingHistory) | Kontierungshistorie (frühere Buchungszeilen). |
| **MWST-Code** (VatCode) | Mehrwertsteuercode. |
| **Rechnung** (Invoice) | Kreditorenrechnung oder Gutschrift. |
| **Kontierung** (Accounting) | Buchungszeile zu einer Rechnung. |

Diese Entitäten sind in der [OpenAPI-Spezifikation](../../openapi/dms-api.v1.yaml) als `GET`-Endpunkte
abgebildet (paginiert, mit `changed_since` + `changed_until`); `creditors`, `accounts` und `invoices`
bieten zusätzlich `POST`. Feldtypen und die genauen Schemas stehen in der Spezifikation.

## Personen, Benutzer & Rollen

Wer mit Liegenschaften zu tun hat. Alle als paginierte `GET`-Endpunkte.

| Entität | Bedeutung |
| --- | --- |
| **Person** (Person) | Natürliche/juristische Person; Kontakt-Wurzel hinter Mietern, Kreditoren usw. Adressfelder spiegeln die jüngste Adresse. |
| **Benutzer** (User) | ERP-Benutzer. |
| **Liegenschaftsperson** (RealestatePerson) | Person ↔ Liegenschaft mit Rolle. |
| **Liegenschafts-Benutzer** (RealestateUser) | Benutzer ↔ Liegenschaft mit Rolle. Rollen: 10 = Bewirtschafter (Manager), 11 = Buchhalter (Accountant). |
| **Mietverhältnisperson** (TenancyPerson) | Person ↔ Mietverhältnis mit Rolle. |

## Aufträge

| Entität | Bedeutung |
| --- | --- |
| **Auftrag** (Order) | Arbeitsauftrag aus dem Portal; trägt u. a. Status, Kontakt/Auftragnehmer, Liegenschaftsbezug und mehrsprachige Titel/Anweisungen (`mls`). |

## Dokumentmodell

Ein **Dokument** (`DocumentEntity`) ist „eine lesbare Datei". Wichtige Felder:

- `id` (uuid), `name`, `filedate`, `mime-type`, `extention`, `url`, `barcode`.
- `type` – einer von `invoice` | `credit` | `correspondence` | `assurance`.
- `storageTargets` – Liste aus `DMS` | `ERP`: wo die Datei physisch liegt.
- `dmsReference` – `{ archive, documentId }`: die Rück-Referenz, sobald das DMS archiviert hat.
- `links` – Liste von `DocumentLinkEntity` `{ id, entity-type }` zur Verknüpfung mit Stammdaten
  (`realestate`, `house`, `unit`, `appliance`, `tenant`, `tenancy`).

### Lebenszyklus (informell)

```
Import:      im DMS erstellt → Metadaten an ERP (POST) → im E-Dossier verlinkt
Archivierung: im ERP erstellt → vom DMS geholt → im DMS archiviert
              → dmsReference zurückgeschrieben (PUT) → optional aus ERP entfernt
Löschung:    DELETE /documents/{uuid} → Soft-Delete (204)
```

> Löschen wird über `DELETE` als **Soft-Delete** umgesetzt (siehe
> [Konventionen](../3-referenz/2-konventionen.md#löschungen)). Ob Dokumente einen expliziten Status tragen
> und ob Ersetzen/Versionierung unterstützt wird, ist noch offen und wird ergänzt.

Begriffsdefinitionen im [Glossar](2-glossar.md).

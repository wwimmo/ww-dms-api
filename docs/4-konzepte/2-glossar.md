# Glossar

Fachbegriffe. Die ERP-Systeme und die Bestandsdoku sind deutsch; englische Entsprechungen entsprechen den
Bezeichnern in der API.

| Begriff (DE) | API / EN | Bedeutung |
| --- | --- | --- |
| Liegenschaft | RealEstate | Rechtlich/wirtschaftlich abgegrenzte Immobilieneinheit; Basis aller Bewirtschaftungsprozesse. |
| Haus | House | Physisches Gebäude innerhalb einer Liegenschaft. |
| Objekt / Mietobjekt | Unit | Kleinste abrechenbare Mieteinheit (Wohnung, Gewerbe …). |
| Gerät | Appliance | Wartbares Gerät, einer Liegenschaft/einem Objekt zugeordnet. |
| Mietverhältnis | Tenancy | Verbindet ein Objekt mit einem Mieter über die Zeit. |
| Mieter | Tenant | Mietende Partei. |
| Eigentümer | Owner | Rechtlich verantwortliche Partei; trägt Ertrag/Kosten. |
| Verwaltung | Management | Organisation, die Liegenschaften bewirtschaftet. |
| Portfolio | Portfolio | Zusammenfassung von Liegenschaften eines Eigentümers. |
| Mandant | (Eigentümer, Portfolio) | In ImmoTop2 der «Mandant»; kein eigenes Modellkonstrukt – `Portfolio.number` trägt die Mandant-Nr. In der API ist «Mandant» zugleich der `customerid`-Claim des Tokens, der die sichtbaren Daten eingrenzt. |
| Buchhaltung / Buchungskreis | Bookkeeping | Abrechnungseinheit; Anker der Rechnungsdaten am Endpunkt (`bookkeepingid`). «Buchungskreis» ist das Synonym in der Bruno-Collection. |
| Kreditor | Creditor | Ein Lieferant. Portfolio-/buchhaltungsunabhängig. |
| Zahlstelle / Zahlverbindung | PaymentAccount / PayoutBankAccount | Zahlverbindung des Kreditors bzw. auszahlende Verbindung je Buchhaltung. |
| Konto | Account | Ein Buchhaltungskonto. |
| Kostenstelle | CostCenter | Kostenstelle (nur ImmoTop2). |
| MWST-Code | VatCode | Mehrwertsteuercode. |
| Rechnung | Invoice | Kreditorenrechnung oder Gutschrift. |
| Gutschrift | Credit | Eine Gutschrift; ein Wert des Dokument-`type` und des Rechnungs-`type`. |
| Kontierung | Accounting | Buchungszeile zu einer Rechnung. |
| Auftrag | Order | Arbeitsauftrag aus dem Portal (mit Status und mehrsprachigen Texten). |
| Archiv-ID | `dmsReference.archive` | Die von W&W Immo beim Onboarding vergebene UUID Ihrer DMS-Anbindung; Pflicht in jeder `dmsReference`. |
| E-Dossier | E-Dossier | Die elektronische Dokumentenakte des ERP je Objekt, in der Dokumente verlinkt werden. |
| Stammdaten | Master data | Stabile, langlebige Bezugsdaten (die Objekte, an die Dokumente hängen). |
| DMS | DMS | Das Dokumentenmanagement-System des Anbieters. |
| ERP | ERP | Rimo R5 oder ImmoTop2, in der Cloud betrieben. |

## Übergreifende Begriffe

- **Anti-Corruption-Layer (ACL)** – die Übersetzungsschicht der API zwischen ihrem Fachmodell und den
  ERP-Bezeichnern.
- **Tombstone** – ein nach der Löschung sichtbar gehaltener Datensatz (z. B. `deleted_at`), damit
  abrufende Systeme die Löschung erkennen. Von dieser API derzeit **nicht** geliefert: Löschungen sind
  physisch.
- **Ablageziel** – wo ein Dokument physisch liegt: `DMS`, `ERP` oder beides.
- **`changed_since`** – der Polling-Cursor: «liefere alles, was sich ab diesem Zeitstempel geändert hat».
- **Sprechender Schlüssel** – ein lesbarer Such-Schlüssel (z. B. Liegenschafts-`number`) anstelle der
  UUID.

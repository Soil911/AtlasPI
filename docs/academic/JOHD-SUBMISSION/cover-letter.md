# Cover letter — JOHD submission

> Da incollare nel campo **"Comments to the Editor"** del wizard di submission.
> ⚠️ La richiesta di esenzione va fatta **contestualmente all'invio**, non dopo.

---

Dear Editors,

I am submitting a Data Paper describing **AtlasPI**, an open dataset of 1,015
historical geopolitical entities spanning 4500 BCE to 2024 CE, with GeoJSON boundary
geometry, endonymic naming, per-record source citations and explicit confidence
scores.

The dataset is already deposited with a persistent identifier
(DOI: 10.5281/zenodo.19581784), released under Apache-2.0, and openly accessible
without authentication at https://atlaspi.it, with the source repository at
https://github.com/Soil911/AtlasPI.

I believe the paper fits JOHD's scope for three reasons. First, the object is a
humanities research dataset with demonstrable reuse potential in historical GIS,
teaching and methodological research. Second, provenance is documented at record
level rather than asserted in prose: every entity carries its citations, its boundary
source tier and an auditable confidence value. Third, the dataset treats uncertainty
and contested interpretation as machine-readable fields — a design choice I argue is
increasingly consequential as historical data is consumed by automated systems that
otherwise flatten it.

**Request for APC waiver.** I would like to request a waiver of the Article Processing
Charge. AtlasPI is an independent project developed without institutional or grant
funding, and the dataset is released openly at no cost to users. I have no research
budget from which to cover the charge. I understand this request is assessed
separately from the editorial decision, and I am of course happy to provide any
further information the journal requires.

**Competing interests.** In the interest of full transparency: I am the founder of
CRA S.r.l., the company that develops and hosts AtlasPI. The dataset and API described
in the paper are openly licensed and freely accessible; the project follows an
open-core model under which commercial services may be offered in future, though none
exists at present. This is stated in the manuscript's competing-interests section.

Thank you for considering the submission.

Kind regards,
Clirim Ramadani
CRA S.r.l., Italy
clirim.ramadani1@gmail.com

---

## Revisori suggeriti — DA DECIDERE con Clirim

Il portale permette (facoltativo) di suggerire fino a 3 revisori. **Non ho inserito
nomi**: proporre revisori è una scelta che deve fare l'autore, e suggerire persone a
caso o con cui non si ha alcun rapporto può essere controproducente.

Profili che avrebbero senso (da valutare tu, verificando che non ci siano conflitti):
- specialisti di **historical GIS / gazetteer** (es. l'ambito Pleiades, Recogito,
  World Historical Gazetteer);
- ricercatori di **digital history** che lavorano su confini e cartografia storica;
- il maintainer di un dataset upstream — **ma NON André Ourednik**: essendo AtlasPI
  costruito sui suoi dati, sarebbe in conflitto d'interessi.

Se preferisci, si può lasciare il campo vuoto: è facoltativo e l'assenza non penalizza.

---

## Checklist finale prima dell'invio

- [ ] Scaricare il **template Data Paper** (Word/LaTeX) dal portale e travasarci il
      testo di `manuscript.md` — il markdown non è un formato accettato
- [ ] Inserire il proprio **ORCID** (se non ce l'hai: registrazione gratuita su
      orcid.org, 2 minuti — le riviste lo chiedono quasi sempre)
- [ ] Manoscritto in **.docx** (NON PDF) se usi Word
- [ ] Incollare questa lettera nel campo *Comments to the Editor*
- [ ] Scrivere anche a **patrick.higgins@ubiquitypress.com** per l'esenzione APC,
      contestualmente all'invio
- [ ] Verificare un'ultima volta i numeri: `curl https://atlaspi.it/v1/stats`
      (usare **1.015 entità**, la cifra interrogabile, non 1.061 che include i
      record deprecati)

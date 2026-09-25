# API inPA — Documentazione non ufficiale

L'API del Portale inPA (Portale del Reclutamento PA) non è documentata ufficialmente.
Questa pagina raccoglie quanto appreso durante lo sviluppo del dataset.

## Base URL

```
https://portale.inpa.gov.it/concorsi-smart/api
```

## Link ai bandi

Il link diretto al bando su inPA si costruisce dall'ID:

```
https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id={id}
```

Non serve chiamare l'endpoint detail per ottenere il link — basta concatenare con l'ID dal search.

## Endpoint

### 1. Ricerca bandi

```
POST /concorso-public-area/search-better?page={page}&size={size}
```

**Body (JSON):**
```json
{
  "text": "",
  "categoriaId": null,
  "regioneId": null,
  "status": ["OPEN"],
  "settoreId": null,
  "provinciaCodice": null,
  "dateFrom": "2026-01-01",
  "dateTo": null,
  "livelliAnzianitaIds": null,
  "tipoImpiegoId": null,
  "salaryMin": null,
  "salaryMax": null,
  "enteRiferimentoName": ""
}
```

**Risposta (paginazione Spring):**
```json
{
  "content": [ { ... }, ... ],
  "totalElements": 1622,
  "totalPages": 4,
  "size": 500,
  "number": 0
}
```

**Campi nel record (lista completa):**

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | string | UUID del bando |
| `codice` | string | Codice identificativo |
| `titolo` | string | Titolo del bando |
| `descrizioneBreve` | string | Descrizione breve (HTML) |
| `descrizione` | string | Descrizione completa (HTML) |
| `figuraRicercata` | string | Figura professionale |
| `dataPubblicazione` | string | Data pubblicazione (ISO) |
| `dataScadenza` | string | Scadenza candidature (ISO) |
| `dataVisibilita` | string | Fine visibilità (ISO) |
| `tipoProcedura` | string | ESAMI, TITOLI_ESAMI, COLLOQUIO, ecc. |
| `numPosti` | int | Numero posti |
| `calculatedStatus` | string | OPEN / CLOSED |
| `statusLabel` | string | Etichetta testuale stato |
| `categorie` | list | Categorie del bando |
| `settori` | list | Settori (oggetti con .name) |
| `sedi` | list | Sedi (oggetti con regioneDenominazione, provinciaDenominazione) |
| `entiRiferimento` | list | Enti di riferimento |

| `salaryMin` | float | Stipendio minimo annuo (dal search, non dal detail) |
| `salaryMax` | float | Stipendio massimo annuo (dal search, non dal detail) |
| `linkReindirizzamento` | string | URL generico dell'ente (non al bando specifico) |

### 2. Ricerca comunicazioni

```
POST /communication/user/public-area/search?page={page}&size={size}
```

**Body (JSON):**
```json
{
  "subject": "",
  "concorsoId": null,
  "categoryId": null,
  "publishDateFrom": null,
  "publishDateTo": null,
  "effectiveDateFrom": null,
  "effectiveDateTo": null,
  "companyName": ""
}
```

**Campi nel record:**

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | string | UUID comunicazione |
| `concorsoId` | string | ID bando collegato |
| `concorsoTitle` | string | Titolo bando |
| `subject` | string | Oggetto comunicazione |
| `body` | string | Corpo (HTML) |
| `categoryName` | string | Tipo: Graduatoria, Calendario, ecc. |
| `dateFirstPublish` | string | Data pubblicazione (ISO) |
| `companyName` | string | Ente |

## Limiti noti

- **Nessuna documentazione ufficiale** — endpoint e campi possono cambiare senza preavviso
- **Rate limiting** non rilevato, ma consigliata pausa ≥ 0.3s tra richieste
- **Paginazione Spring**: `content` + `totalPages` + `totalElements`
- **Filtro per data**: non supportato — `dateFrom`/`dateTo` nel body vengono ignorati o rompono la query
- **Filtro per status**: funziona (OPEN / CLOSED)
- **Link ai bandi**: costruibile dall'ID (`https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id={id}`)
- **API timeout**: variabile, 30-60s consigliati per le ricerche

## User-Agent

Lo script usa:
```
Mozilla/5.0 (DataCivicLab dataset-incubator)
```

## Fonte dei dati

- Portale: https://www.inpa.gov.it/
- API: https://portale.inpa.gov.it/concorsi-smart/api/
- Ultimo aggiornamento documentazione: 2026-09-25

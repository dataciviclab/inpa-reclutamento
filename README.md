# inPA Reclutamento

Dati aperti sul reclutamento della Pubblica Amministrazione italiana dal Portale inPA.

## Perché questi dati

[inPA](https://www.inpa.gov.it/) è il portale ufficiale del reclutamento della PA, obbligatorio per tutti gli enti dal 2023. Questo dataset rende interrogabili i bandi di concorso, le comunicazioni di procedura e i tempi di assunzione di tutta la PA italiana — dati che finora restavano chiusi nella piattaforma.

## Cosa contengono

| Dataset | Contenuto | Aggiornamento |
|---------|-----------|---------------|
| `inpa_bandi_open` | Bandi aperti (attivi) — ~1.8k bandi | Giornaliero |
| `inpa_bandi_closed` | Bandi chiusi (archivio storico) — ~74k bandi | Mensile (1° del mese) |
| `inpa_comunicazioni` | Comunicazioni di procedura (graduatorie, calendari, esiti) | Giornaliero |
| `inpa_insight` | Analisi cross-dataset: tempi per ente, trasparenza, procedure | Giornaliero |

Copertura: **tutti gli enti PA italiani**, dal 2026. Dati harvestati dall'API pubblica inPA.

## Domande che puoi porre

- Quali enti assumono di più e in quali aree?
- Quali sono i profili professionali più ricercati dalla PA?
- Quanto tempo passa tra la pubblicazione di un bando e la comunicazione dell'esito?
- Quali regioni hanno più bandi aperti e quali meno?
- Qual è lo stipendio medio offerto nei concorsi PA?

## Come accedere

**Parquet (raw)** — scarica i file puliti da GCS:
```
gs://dataciviclab-clean/inpa-reclutamento/inpa_bandi_open/2026/
gs://dataciviclab-clean/inpa-reclutamento/inpa_comunicazioni/2026/
```

**DuckDB** — query dirette sui dati:
```sql
SELECT ente, COUNT(*) AS n_bandi, SUM(num_posti) AS posti
FROM read_parquet('gs://dataciviclab-mart/inpa-reclutamento/inpa_bandi_open/*/mart_efficienza_ente.parquet')
GROUP BY ente ORDER BY posti DESC LIMIT 10;
```

**Dashboard interattiva** — esplora i dati senza codice:
[dataciviclab-inpa-reclutamento.streamlit.app](https://dataciviclab-inpa-reclutamento.streamlit.app/)

## Struttura

```
datasets/
  inpa-bandi-open/       bandi aperti (harvest → clean → mart)
  inpa-bandi-closed/     bandi chiusi (harvest → clean, no mart)
  inpa-comunicazioni/    comunicazioni di procedura
compose/
  inpa-insight/          analisi cross-dataset bandi × comunicazioni
dashboard/               app Streamlit
registry/                catalogo pubblicato
tests/                   test suite
```

## Dashboard

La dashboard è disponibile su [Streamlit Community Cloud](https://dataciviclab-inpa-reclutamento.streamlit.app/).

## Setup locale

```bash
# Installa dipendenze
pip install -e ".[pipeline,dashboard]"

# Harvest completo (open + closed)
make run-bandi

# Solo open (daily)
make run-bandi-open

# Esegui pipeline completa
make run

# Avvia dashboard
make dashboard
```

## Aggiornamenti

- **Giornaliero** (06:00 UTC): harvest bandi aperti + comunicazioni
- **Mensile** (1° del mese): harvest bandi chiusi (archivio storico)

## Partecipa

Hai trovato un problema o vuoi contribuire?

- **Discussioni**: [Apri una Discussion](https://github.com/dataciviclab/inpa-reclutamento/discussions) per domande, suggerimenti, analisi
- **Bug**: [Segnala un Issue](https://github.com/dataciviclab/inpa-reclutamento/issues) con il template bug report
- **Feature**: [Proponi una novità](https://github.com/dataciviclab/inpa-reclutamento/issues) con il template feature request

## Licenza

MIT — vedi [LICENSE](LICENSE).

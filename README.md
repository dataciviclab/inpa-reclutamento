# inPA Reclutamento

Dati aperti sul reclutamento della Pubblica Amministrazione italiana dal Portale inPA.

## Perché questi dati

[inPA](https://www.inpa.gov.it/) è il portale ufficiale del reclutamento della PA, obbligatorio per tutti gli enti dal 2023. Questo dataset rende interrogabili i bandi di concorso, le comunicazioni di procedura e i tempi di assunzione di tutta la PA italiana — dati che finora restavano chiusi nella piattaforma.

## Cosa contengono

| Dataset | Contenuto | Aggiornamento |
|---------|-----------|---------------|
| `inpa_bandi` | Bandi e avvisi (OPEN + storico CLOSED) — ~50k bandi, ~15k posti | Giornaliero (incrementale) |
| `inpa_comunicazioni` | Comunicazioni di procedura (graduatorie, calendari, esiti) | Giornaliero (incrementale) |
| `inpa_insight` | Analisi cross-dataset: tempi per ento, trasparenza, procedure | Mensile |

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
gs://dataciviclab-clean/inpa-reclutamento/inpa_bandi/2026/
gs://dataciviclab-clean/inpa-reclutamento/inpa_comunicazioni/2026/
```

**DuckDB** — query dirette sui dati:
```sql
SELECT ente, COUNT(*) AS n_bandi, SUM(num_posti) AS posti
FROM read_parquet('gs://dataciviclab-mart/inpa-reclutamento/inpa_bandi/*/mart_efficienza_ente.parquet')
GROUP BY ente ORDER BY posti DESC LIMIT 10;
```

**Dashboard interattiva** — esplora i dati senza codice:
[dataciviclab-inpa-reclutamento.streamlit.app](https://dataciviclab-inpa-reclutamento.streamlit.app/)

## Struttura

```
datasets/
  inpa-bandi/          bandi e avvisi (harvest → clean → mart)
  inpa-comunicazioni/  comunicazioni di procedura
compose/
  inpa-insight/        analisi cross-dataset bandi × comunicazioni
dashboard/             app Streamlit
registry/              catalogo pubblicato
tests/                 test suite
```

## Dashboard

La dashboard è disponibile su [Streamlit Community Cloud](https://dataciviclab-inpa-reclutamento.streamlit.app/).

## Setup locale

```bash
# Installa dipendenze
pip install -e ".[pipeline,dashboard]"

# Harvest completo
make harvest-full

# Esegui pipeline
make run

# Avvia dashboard
make dashboard
```

## Aggiornamenti

- **Giornaliero** (06:00 UTC): harvest incrementale degli OPEN e comunicazioni recenti
- **Mensile** (1° del mese): harvest completo di tutti i dati

## Partecipa

Hai trovato un problema o vuoi contribuire?

- **Discussioni**: [Apri una Discussion](https://github.com/dataciviclab/inpa-reclutamento/discussions) per domande, suggerimenti, analisi
- **Bug**: [Segnala un Issue](https://github.com/dataciviclab/inpa-reclutamento/issues) con il template bug report
- **Feature**: [Proponi una novità](https://github.com/dataciviclab/inpa-reclutamento/issues) con il template feature request

## Licenza

MIT — vedi [LICENSE](LICENSE).

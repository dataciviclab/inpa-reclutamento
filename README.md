# inPA Reclutamento

Dati aperti sul reclutamento della Pubblica Amministrazione italiana dal Portale inPA.

## Cos'è

[inPA](https://www.inpa.gov.it/) è il portale ufficiale del reclutamento della PA, obbligatorio per tutti gli enti dal 2023. Questo repo raccoglie, pulisce e pubblica i dati dei bandi di concorso e delle comunicazioni di procedura.

## Domanda civica

Dove sono e come funzionano i concorsi pubblici in Italia? Quali enti assumono di più, in quali aree, con quali profili e scadenze? Il reclutamento PA è trasparente?

## Dati

| Dataset | Contenuto | Aggiornamento |
|---------|-----------|---------------|
| `inpa-bandi` | Bandi e avvisi (OPEN + storico CLOSED) | Giornaliero (incrementale) |
| `inpa-comunicazioni` | Comunicazioni di procedura (graduatorie, calendari) | Giornaliero (incrementale) |
| `inpa-insight` | Analisi cross-dataset (tempi, trasparenza) | Mensile |

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

## Licenza

MIT — vedi [LICENSE](LICENSE).

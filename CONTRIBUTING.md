# Contribuire a inPA Reclutamento

Come contribuire a questo repo.

## Tipi di contribuzione

- **Dati**: segnalare fonti, problemi di qualità, nuovi dataset
- **Codice**: fix, miglioramenti, nuove funzionalità
- **Dashboard**: nuove pagine, visualizzazioni, UX

## Workflow

1. Fork il repo
2. Crea un branch (`feat/nuova-funzionalita` o `fix/problema`)
3. Fai le tue modifiche
4. Assicurati che i test passino (`make check`)
5. Apri una PR

## Standard

- Segui gli standard del Lab (vedi `analysis/lab-ops/standards/`)
- Usa `ruff` per il formattazione
- Aggiungi test per nuove funzionalità
- Aggiorna la documentazione se necessario

## Struttura del repo

```
datasets/           dataset.yml (contratto pipeline)
compose/            analisi cross-dataset
scripts/            harvest e elaborazione
dashboard/          app Streamlit
registry/           catalogo pubblicato
tests/              test suite
.github/            workflows e template
```

## Test

```bash
make check          # pytest + ruff
make run            # esegui pipeline completa
make dashboard      # avvia dashboard locale
```

## Domande?

Apri una [Discussion](https://github.com/dataciviclab/inpa-reclutamento/discussions) per domande generiche.
Apri un [Issue](https://github.com/dataciviclab/inpa-reclutamento/issues) per bug o feature request.

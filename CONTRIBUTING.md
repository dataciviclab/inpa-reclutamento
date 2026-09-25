# Contribuire a inPA Reclutamento

Come contribuire a questo repo.

## Principi

- **Dati prima**: ogni modifica parte da una domanda civica reale
- **Qualità dei dati**: i contratti `dataset.yml` sono vincolanti — le validazioni devono passare
- **Riuso**: prima di scrivere codice nuovo, verifica se esiste già in `toolkit` o `lab-connectors`
- **Trasparenza**: le modifiche alla pipeline devono essere tracciabili (PR, non commit diretti)

## Tipi di contribuzione

| Tipo | Esempio | Dove |
|------|---------|------|
| **Dati** | Segnalare fonti, problemi di qualità, nuovi dataset | [Discussion](https://github.com/dataciviclab/inpa-reclutamento/discussions) |
| **Codice** | Fix, miglioramenti, nuove funzionalità | PR su `main` |
| **Dashboard** | Nuove pagine, visualizzazioni, UX | PR su `main` |
| **Documentazione** | README, CONTRIBUTING, guides | PR su `main` |

## Workflow

1. Fork il repo
2. Crea un branch (`feat/nuova-funzionalita` o `fix/problema`)
3. Fai le tue modifiche
4. Assicurati che i test passino (`make check`)
5. Apri una PR usando il template fornito

## Aggiungere un nuovo dataset

1. Crea la cartella `datasets/<slug>/` con:
   - `dataset.yml` — contratto pipeline (usa un dataset esistente come模板)
   - `scripts/harvest_*.py` — script di harvest (se la fonte è un'API)
   - `sql/clean.sql` — trasformazione raw → clean
   - `sql/mart_*.sql` — tabelle mart
2. Aggiungi il target Makefile: `run-<slug>`
3. Aggiorna `compose/` se il dataset si collega ad altri
4. Aggiungi test in `tests/` per i contratti

## Aggiungere una pagina alla dashboard

1. Crea `dashboard/pages/NN_Nome_Pagina.py`
2. Usa `sources.py` per caricare i dati (pattern `load_mart`)
3. Segui lo stile delle pagine esistenti
4. Aggiungi il link in `app.py`

## Standard tecnici

- **Lint**: `ruff check` e `ruff format` — zero warning
- **Test**: ogni test ha un solo marker (`contract`, `smoke`, `policy`, `regression`, `adapter`, `pure_unit`)
- **Pipeline**: `dataset.yml` è la fonte di verità per la struttura dati
- **SQL**: `clean.sql` legge solo da `raw_input`, `mart*.sql` legge solo da `clean_input`
- **Commit**: messaggi descrittivi, un modificatore per commit (`fix:`, `feat:`, `docs:`, `refactor:`)

## Test

```bash
make check          # pytest + ruff
make run            # esegui pipeline completa
make dashboard      # avvia dashboard locale
```

## Domande?

Apri una [Discussion](https://github.com/dataciviclab/inpa-reclutamento/discussions) per domande generiche.
Apri un [Issue](https://github.com/dataciviclab/inpa-reclutamento/issues) per bug o feature request.

-- Clean: join bandi chiusi + comunicazioni
-- Produce una vista wide: un bando con le sue comunicazioni collegate

WITH bandi AS (
    SELECT
        id, codice, titolo, figura_ricercata, descrizione,
        data_pubblicazione, data_scadenza, data_visibilita,
        tipo_procedura, num_posti, is_graduatoria,
        status, status_label, categoria, settore, regione, provincia,
        ente, enti_riferimento, categorie, settori, sedi,
        salary_min, salary_max, link_inpa
    FROM read_parquet('{support.bandi.clean}')
),
comunicazioni AS (
    SELECT
        concorso_id,
        COUNT(*) AS n_comunicazioni,
        MIN(data_pubblicazione) AS prima_comunicazione,
        MAX(data_pubblicazione) AS ultima_comunicazione,
        STRING_AGG(DISTINCT categoria, ', ' ORDER BY categoria) AS categorie_comunicazioni
    FROM read_parquet('{support.com.clean}')
    GROUP BY concorso_id
)
SELECT
    b.*,
    COALESCE(c.n_comunicazioni, 0) AS n_comunicazioni,
    c.prima_comunicazione,
    c.ultima_comunicazione,
    c.categorie_comunicazioni,
    CASE WHEN c.concorso_id IS NOT NULL THEN TRUE ELSE FALSE END AS ha_comunicazioni,
    CASE
        WHEN c.prima_comunicazione IS NOT NULL AND b.data_pubblicazione IS NOT NULL
        THEN DATE_DIFF('day', b.data_pubblicazione, c.prima_comunicazione)
    END AS giorni_prima_comunicazione
FROM bandi b
LEFT JOIN comunicazioni c ON b.id = c.concorso_id

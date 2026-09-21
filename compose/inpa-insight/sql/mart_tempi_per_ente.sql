-- Mart tempi: tempo medio bando → prima comunicazione per ente
-- Metrica di trasparenza: quanto tempo impiega un ente a pubblicare aggiornamenti?
-- Solo enti con almeno 3 bandi che hanno ricevuto comunicazioni.
-- Nota: legge dai clean layer ({support.*.clean}) perché servono colonne non presenti nei mart
-- (es. data_pubblicazione dal bando, data_scadenza per filtri temporali)
WITH prima_com AS (
    SELECT concorso_id, MIN(data_pubblicazione) AS prima_data
    FROM read_parquet('{support.com.clean}')
    GROUP BY concorso_id
),
tempi_bando AS (
    SELECT
        b.ente,
        b.id AS bando_id,
        DATE_DIFF('day', b.data_pubblicazione, c.prima_data) AS giorni
    FROM read_parquet('{support.bandi.clean}') b
    JOIN prima_com c ON b.id = c.concorso_id
    WHERE b.data_pubblicazione IS NOT NULL
      AND c.prima_data IS NOT NULL
      AND DATE_DIFF('day', b.data_pubblicazione, c.prima_data) > 0
      AND b.is_graduatoria = FALSE
)
SELECT
    ente,
    COUNT(*) AS n_bandi_con_comunicazioni,
    AVG(giorni)::INT AS media_giorni,
    MEDIAN(giorni)::INT AS mediana_giorni,
    MIN(giorni) AS min_giorni,
    MAX(giorni) AS max_giorni
FROM tempi_bando
WHERE ente IS NOT NULL
GROUP BY ente
HAVING COUNT(*) >= 3
ORDER BY mediana_giorni DESC

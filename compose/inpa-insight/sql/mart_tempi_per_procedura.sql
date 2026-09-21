-- Mart tempi per procedura: tempo medio bando -> prima comunicazione per tipo
-- {support.bandi.clean} = clean layer di inpa-bandi
-- {support.com.clean} = clean layer di inpa-comunicazioni
WITH prima AS (
    SELECT concorso_id, MIN(data_pubblicazione) AS prima_com
    FROM read_parquet('{support.com.clean}')
    GROUP BY concorso_id
)
SELECT
    b.tipo_procedura,
    COUNT(DISTINCT b.id) AS n_bandi_totali,
    COUNT(DISTINCT p.concorso_id) AS n_con_comunicazioni,
    ROUND(100.0 * COUNT(DISTINCT p.concorso_id) / COUNT(DISTINCT b.id), 1) AS pct_con_comunicazioni,
    CAST(AVG(DATE_DIFF('day', b.data_pubblicazione, p.prima_com)) AS INT) AS media_gg,
    CAST(MEDIAN(DATE_DIFF('day', b.data_pubblicazione, p.prima_com)) AS INT) AS mediana_gg
FROM read_parquet('{support.bandi.clean}') b
LEFT JOIN prima p ON b.id = p.concorso_id
WHERE NOT b.is_graduatoria
GROUP BY 1
ORDER BY 6 DESC

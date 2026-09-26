-- Mart tempi per procedura: tempo medio bando → prima comunicazione per tipo
SELECT
    tipo_procedura,
    COUNT(DISTINCT id) AS n_bandi_totali,
    SUM(ha_comunicazioni) AS n_con_comunicazioni,
    ROUND(100.0 * SUM(ha_comunicazioni) / COUNT(*), 1) AS pct_con_comunicazioni,
    AVG(giorni_prima_comunicazione)::INT AS media_gg,
    MEDIAN(giorni_prima_comunicazione)::INT AS mediana_gg
FROM clean_input
WHERE NOT is_graduatoria
GROUP BY 1
ORDER BY 6 DESC

-- Mart tempi: tempo medio bando → prima comunicazione per ente
SELECT
    ente,
    COUNT(*) AS n_bandi_con_comunicazioni,
    AVG(giorni_prima_comunicazione)::INT AS media_giorni,
    MEDIAN(giorni_prima_comunicazione)::INT AS mediana_giorni,
    MIN(giorni_prima_comunicazione) AS min_giorni,
    MAX(giorni_prima_comunicazione) AS max_giorni
FROM clean_input
WHERE giorni_prima_comunicazione > 0
  AND NOT is_graduatoria
  AND ente IS NOT NULL
GROUP BY ente
HAVING COUNT(*) >= 3
ORDER BY mediana_giorni DESC

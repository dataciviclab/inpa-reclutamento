-- Mart enti: classifica enti per bandi e posti
-- Risponde a: quali enti assumono di più?
SELECT
    ente,
    COUNT(*) AS totale_bandi,
    SUM(num_posti) AS totale_posti,
    ROUND(AVG(num_posti), 1) AS media_posti_per_bando,
    COUNT(DISTINCT tipo_procedura) AS procedure_diverse,
    MIN(data_pubblicazione) AS primo_bando,
    MAX(data_pubblicazione) AS ultimo_bando
FROM clean_input
WHERE is_graduatoria = FALSE
  AND ente IS NOT NULL
  AND num_posti IS NOT NULL
  AND num_posti > 0
GROUP BY ente
HAVING COUNT(*) >= 3
ORDER BY totale_posti DESC

-- Mart stipendi: info retributive dove disponibili
-- Risponde a: quanto guadagna chi lavora nella PA?
SELECT
    ente,
    titolo,
    figura_ricercata,
    regione,
    salary_min,
    salary_max,
    CASE
        WHEN salary_min = salary_max THEN 'Fisso'
        WHEN salary_max > 0 THEN 'Range'
        ELSE 'Non specificato'
    END AS tipo_retribuzione
FROM clean_input
WHERE status = 'OPEN'
  AND NOT is_graduatoria
  AND salary_max > 100
  AND salary_max < 100000
ORDER BY salary_max DESC

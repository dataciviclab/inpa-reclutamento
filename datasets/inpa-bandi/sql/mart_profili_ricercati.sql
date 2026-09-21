-- Mart profili ricercati: normalizzazione delle figure professionali richieste
-- Risponde a: che tipo di personale cerca la PA?
SELECT
    CASE
        WHEN UPPER(figura_ricercata) LIKE '%ISTRUTTORE%' THEN 'Istruttore'
        WHEN UPPER(figura_ricercata) LIKE '%FUNZIONARI%' OR UPPER(figura_ricercata) LIKE '%FUNZIONARIO%' THEN 'Funzionario'
        WHEN UPPER(figura_ricercata) LIKE '%DOCENTE%' OR UPPER(figura_ricercata) LIKE '%DOCENTI%' THEN 'Docente'
        WHEN UPPER(figura_ricercata) LIKE '%INFERMIER%' THEN 'Infermiere'
        WHEN UPPER(figura_ricercata) LIKE '%POLIZIA%' THEN 'Polizia Locale'
        WHEN UPPER(figura_ricercata) LIKE '%ASSISTENTE SOCIALE%' THEN 'Assistente Sociale'
        WHEN UPPER(figura_ricercata) LIKE '%OPERATORE SOCIO SANITARIO%' THEN 'OSS'
        WHEN UPPER(figura_ricercata) LIKE '%DIRIGENTE MEDICO%' THEN 'Dirigente Medico'
        WHEN UPPER(figura_ricercata) LIKE '%DIRIGENTE%' THEN 'Dirigente'
        WHEN UPPER(figura_ricercata) LIKE '%FISIOTERAPISTA%' THEN 'Fisioterapista'
        WHEN UPPER(figura_ricercata) LIKE '%AGGIORNAMENTO%' OR UPPER(figura_ricercata) LIKE '%GRADUATORIA%' THEN 'Graduatoria/Aggiornamento'
        WHEN UPPER(figura_ricercata) LIKE '%OPERATORE%' THEN 'Operatore'
        WHEN UPPER(figura_ricercata) LIKE '%COLLABORATORE%' THEN 'Collaboratore'
        ELSE 'Altro'
    END AS profilo,
    COUNT(*) AS n_bandi,
    SUM(num_posti) AS posti_totali,
    COUNT(DISTINCT ente) AS enti_diversi
FROM clean_input
WHERE status = 'OPEN' AND NOT is_graduatoria
GROUP BY 1
ORDER BY 2 DESC

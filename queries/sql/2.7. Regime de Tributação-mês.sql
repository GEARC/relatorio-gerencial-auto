-- QTD Regime tributário do último mês com porcentagem
SELECT  pp.IC_TRIBUTACAO,
        CAST(ROUND(
                (COUNT(e.ID_PESSOA) * 100.0) / 
                (SELECT COUNT(*) 
                 FROM ENCERRAMENTO_PLANO_PARTIC e2, PLANO_PARTICIPANTE pp2
                 WHERE e2.ID_PESSOA = pp2.id_pessoa
                 AND e2.ID_SITUACAO IN (1,2)
                 AND e2.DT_INI_PLANO BETWEEN '2025-05-01' AND '2025-05-31' 
                 AND e2.NR_ANO_REF = 2025 
                 AND e2.NR_MES_REF = 5), 2
            ) AS DECIMAL(5,2)
        ) as porcentagem
FROM ENCERRAMENTO_PLANO_PARTIC e, PLANO_PARTICIPANTE pp
WHERE e.ID_PESSOA = pp.id_pessoa
AND e.ID_SITUACAO IN (1,2)
AND e.DT_INI_PLANO BETWEEN '2025-05-01' AND '2025-05-31' 
AND e.NR_ANO_REF = 2025 
AND e.NR_MES_REF = 5
GROUP BY pp.IC_TRIBUTACAO
ORDER BY porcentagem DESC;
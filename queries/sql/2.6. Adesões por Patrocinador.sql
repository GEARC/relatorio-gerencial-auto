--QTD geral regime trib
SELECT  pp.IC_TRIBUTACAO,
        e.NR_ANO_REF,
        e.NR_MES_REF,
        COUNT(e.ID_PESSOA) as total_mes
FROM ENCERRAMENTO_PLANO_PARTIC e, PLANO_PARTICIPANTE pp
where e.ID_PESSOA = pp.id_pessoa
and e.ID_SITUACAO IN (1, 2, 5, 6, 7, 10)
and e.NR_ANO_REF = 2025 
AND e.NR_MES_REF = 5
group by pp.IC_TRIBUTACAO,
        e.NR_ANO_REF,
        e.NR_MES_REFaca
QUERY = """-- Query para mostrar movimentação mensal (diferenças)
WITH dados_mensais AS (
    SELECT 
        e.ID_SITUACAO,
        ps.NM_SITUACAO,
        e.NR_ANO_REF,
        e.NR_MES_REF,
        COUNT(e.ID_PESSOA) as total_mes
    FROM ENCERRAMENTO_PLANO_PARTIC e
    INNER JOIN PLANO_SITUACAO ps ON e.ID_SITUACAO = ps.ID_SITUACAO
    WHERE e.ID_SITUACAO IN (1, 2, 5, 6, 7, 10)
      AND (
          (e.NR_ANO_REF = 2024 AND e.NR_MES_REF = 12) OR 
          (e.NR_ANO_REF = 2025 AND e.NR_MES_REF BETWEEN 1 AND 5)
      )
    GROUP BY e.ID_SITUACAO, ps.NM_SITUACAO, e.NR_ANO_REF, e.NR_MES_REF
),
dados_pivot AS (
    SELECT 
        ID_SITUACAO,
        NM_SITUACAO,
        SUM(CASE WHEN NR_ANO_REF = 2024 AND NR_MES_REF = 12 THEN total_mes ELSE 0 END) as saldo_2024,
        SUM(CASE WHEN NR_ANO_REF = 2025 AND NR_MES_REF = 1 THEN total_mes ELSE 0 END) as total_jan_2025,
        SUM(CASE WHEN NR_ANO_REF = 2025 AND NR_MES_REF = 2 THEN total_mes ELSE 0 END) as total_fev_2025,
        SUM(CASE WHEN NR_ANO_REF = 2025 AND NR_MES_REF = 3 THEN total_mes ELSE 0 END) as total_mar_2025,
        SUM(CASE WHEN NR_ANO_REF = 2025 AND NR_MES_REF = 4 THEN total_mes ELSE 0 END) as total_abr_2025,
        SUM(CASE WHEN NR_ANO_REF = 2025 AND NR_MES_REF = 5 THEN total_mes ELSE 0 END) as total_mai_2025
    FROM dados_mensais
    GROUP BY ID_SITUACAO, NM_SITUACAO
)
SELECT 
    CASE 
        WHEN NM_SITUACAO = 'PATROCINADO' THEN 1
        WHEN NM_SITUACAO = 'VINCULADO' THEN 2  
        WHEN NM_SITUACAO = 'BPD - SALDO' THEN 3
        WHEN NM_SITUACAO = 'NO PRAZO OPÇÃO INSTITUTOS' THEN 4
        WHEN NM_SITUACAO = 'AUTOPATROCINADO' THEN 5
        WHEN NM_SITUACAO = 'ASSISTIDO' THEN 6
        ELSE 7
    END as ordem,
    NM_SITUACAO as situacao,
    saldo_2024,
    -- Movimentações mensais (diferença em relação ao mês anterior)
    (total_jan_2025 - saldo_2024) as jan_2025,
    (total_fev_2025 - total_jan_2025) as fev_2025,
    (total_mar_2025 - total_fev_2025) as mar_2025,
    (total_abr_2025 - total_mar_2025) as abr_2025,
    (total_mai_2025 - total_abr_2025) as mai_2025,
    -- Acumulado 2025 (diferença total do ano)
    (total_mai_2025 - saldo_2024) as acumulado_2025,
    -- Total geral (saldo atual)
    total_mai_2025 as total_geral
FROM dados_pivot
WHERE saldo_2024 > 0 OR total_mai_2025 > 0
ORDER BY ordem;

"""
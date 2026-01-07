WITH dados_mensais AS (
    SELECT 
        pe.ID_LOCAL,
        lc.NM_LOCAL,
        e.NR_ANO_REF,
        e.NR_MES_REF,
        COUNT(e.ID_PESSOA) as total_mes
    FROM ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps, PESSOA pe , LOCAL lc 
    WHERE e.ID_SITUACAO IN (1, 2, 5, 6, 7, 10)
	  AND pe.ID_LOCAL = lc.ID_LOCAL
	  AND pe.ID_PESSOA = e.ID_PESSOA
	  AND e.ID_SITUACAO = ps.ID_SITUACAO
      AND (
          (e.NR_ANO_REF = 2025 AND e.NR_MES_REF = 4) OR 
          (e.NR_ANO_REF = 2025 AND e.NR_MES_REF = 5)
      )
    GROUP BY pe.ID_LOCAL, lc.NM_LOCAL, e.NR_ANO_REF, e.NR_MES_REF
),
dados_pivot AS (
    SELECT 
        ID_LOCAL,
        NM_LOCAL,
        SUM(CASE WHEN NR_ANO_REF = 2025 AND NR_MES_REF = 4 THEN total_mes ELSE 0 END) as total_mes_anterior_2025,
        SUM(CASE WHEN NR_ANO_REF = 2025 AND NR_MES_REF = 5 THEN total_mes ELSE 0 END) as total_mes_atual_2025
    FROM dados_mensais
    GROUP BY ID_LOCAL, NM_LOCAL
),
movimentacao_maio AS (
    SELECT 
        NM_LOCAL,
        (total_mes_atual_2025- total_mes_anterior_2025) as movimentacao_maio_2025,
        -- Total geral de movimentação em maio para calcular percentual
        (SELECT SUM(total_mes_atual_2025 - total_mes_anterior_2025) 
         FROM dados_pivot 
         WHERE (total_mes_atual_2025 - total_mes_anterior_2025) > 0) as total_geral_movimentacao
    FROM dados_pivot
    WHERE (total_mes_atual_2025- total_mes_anterior_2025) != 0  -- Só locais com movimentação
)
SELECT 
    NM_LOCAL,
    CASE 
        WHEN movimentacao_maio_2025 < 0 THEN '0%'
        ELSE FORMAT(100.0 * movimentacao_maio_2025 / 
                   NULLIF(total_geral_movimentacao, 0), 'N2', 'pt-BR') + '%'
    END as porcentagem
FROM movimentacao_maio
WHERE total_geral_movimentacao > 0
ORDER BY movimentacao_maio_2025 DESC;
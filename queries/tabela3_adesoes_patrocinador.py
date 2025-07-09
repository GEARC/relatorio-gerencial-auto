import datetime

def gerar_query(ano, mes):
    """Gera a query de adesões por patrocinador para um ano e mês específicos."""
    
    data_alvo = datetime.date(ano, mes, 1)
    # Precisamos do mês anterior para calcular a diferença
    data_anterior = data_alvo - datetime.timedelta(days=1)
    ano_anterior_logico = data_anterior.year
    mes_anterior_logico = data_anterior.month

    return f"""
    WITH dados_mensais AS (
        SELECT 
            pe.SG_PESSOA, e.NR_ANO_REF, e.NR_MES_REF, COUNT(e.ID_PESSOA) as total_mes
        FROM ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps ,HIST_EMPRESA he ,empresa emp ,PESSOA pe 
        WHERE e.ID_SITUACAO IN (1, 2, 5, 6, 7, 10)
        AND e.NR_ANO_REF = he.NR_ANO_REF AND e.NR_MES_REF = he.NR_MES_REF AND e.ID_SITUACAO = ps.ID_SITUACAO
        AND e.ID_PESSOA = he.ID_PESSOA AND emp.ID_EMP = he.ID_EMP AND pe.ID_PESSOA = emp.ID_PESSOA_EMP
        AND (
            (e.NR_ANO_REF = {ano_anterior_logico} AND e.NR_MES_REF = {mes_anterior_logico}) OR 
            (e.NR_ANO_REF = {ano} AND e.NR_MES_REF = {mes})
        )
        GROUP BY pe.SG_PESSOA, e.NR_ANO_REF, e.NR_MES_REF
    ),
    dados_pivot AS (
        SELECT 
            SG_PESSOA,
            SUM(CASE WHEN NR_ANO_REF = {ano_anterior_logico} AND NR_MES_REF = {mes_anterior_logico} THEN total_mes ELSE 0 END) as total_mes_anterior,
            SUM(CASE WHEN NR_ANO_REF = {ano} AND NR_MES_REF = {mes} THEN total_mes ELSE 0 END) as total_mes_atual
        FROM dados_mensais
        GROUP BY SG_PESSOA
    ),
    totais_gerais AS (
        SELECT 
            SUM(total_mes_atual) as total_geral_acumulado,
            SUM(CASE WHEN (total_mes_atual - total_mes_anterior) > 0 THEN (total_mes_atual - total_mes_anterior) ELSE 0 END) as total_geral_movimentacao
        FROM dados_pivot
    )
    SELECT 
        Sigla, "Quantidade no mês", "Percentual no mês", "Quantidade total", "Percentual total"
    FROM (
        SELECT 
            dp.SG_PESSOA AS Sigla,
            CASE WHEN (dp.total_mes_atual - dp.total_mes_anterior) < 0 THEN 0 ELSE (dp.total_mes_atual - dp.total_mes_anterior) END as "Quantidade no mês",
            CASE WHEN (dp.total_mes_atual - dp.total_mes_anterior) <= 0 THEN '0,00%' ELSE FORMAT(100.0 * (dp.total_mes_atual - dp.total_mes_anterior) / NULLIF(tg.total_geral_movimentacao, 0), 'N2', 'pt-BR') + '%' END as "Percentual no mês",
            dp.total_mes_atual as "Quantidade total",
            FORMAT(100.0 * dp.total_mes_atual / NULLIF(tg.total_geral_acumulado, 0), 'N2', 'pt-BR') + '%' as "Percentual total",
            0 as ordem_prioridade,
            CASE WHEN (dp.total_mes_atual - dp.total_mes_anterior) < 0 THEN 0 ELSE (dp.total_mes_atual - dp.total_mes_anterior) END as valor_ordem
        FROM dados_pivot dp
        CROSS JOIN totais_gerais tg
        WHERE dp.total_mes_atual > 0 OR (dp.total_mes_atual - dp.total_mes_anterior) != 0
        UNION ALL
        SELECT 
            'TOTAIS' as Sigla,
            tg.total_geral_movimentacao, '100,00%',
            tg.total_geral_acumulado, '100,00%',
            -1 as ordem_prioridade, 9999999 as valor_ordem
        FROM totais_gerais tg
    ) resultado
    ORDER BY ordem_prioridade, valor_ordem DESC;
    """
# queries/grafico2_adesao_ramo_mes.py
import datetime
from dateutil.relativedelta import relativedelta

def gerar_query(ano, mes):
    """Gera a query de adesão mensal (delta) para um ano e mês específicos."""
    
    # Calcula o mês e ano de referência e o anterior a ele
    data_atual = datetime.date(ano, mes, 1)
    data_anterior = data_atual - relativedelta(months=1)
    
    ano_atual = data_atual.year
    mes_atual = data_atual.month
    ano_anterior_logico = data_anterior.year
    mes_anterior_logico = data_anterior.month

    # Monta a query dinamicamente com os valores calculados
    return f"""
    WITH dados_mensais AS (
        SELECT 
            pe.ID_LOCAL, lc.NM_LOCAL, e.NR_ANO_REF, e.NR_MES_REF, COUNT(e.ID_PESSOA) as total_mes
        FROM ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps, PESSOA pe , LOCAL lc 
        WHERE e.ID_SITUACAO IN (1, 2, 5, 6, 7, 10)
        AND pe.ID_LOCAL = lc.ID_LOCAL AND pe.ID_PESSOA = e.ID_PESSOA AND e.ID_SITUACAO = ps.ID_SITUACAO
        AND (
            (e.NR_ANO_REF = {ano_anterior_logico} AND e.NR_MES_REF = {mes_anterior_logico}) OR 
            (e.NR_ANO_REF = {ano_atual} AND e.NR_MES_REF = {mes_atual})
        )
        GROUP BY pe.ID_LOCAL, lc.NM_LOCAL, e.NR_ANO_REF, e.NR_MES_REF
    ),
    dados_pivot AS (
        SELECT 
            ID_LOCAL, NM_LOCAL,
            SUM(CASE WHEN NR_ANO_REF = {ano_anterior_logico} AND NR_MES_REF = {mes_anterior_logico} THEN total_mes ELSE 0 END) as total_mes_anterior,
            SUM(CASE WHEN NR_ANO_REF = {ano_atual} AND NR_MES_REF = {mes_atual} THEN total_mes ELSE 0 END) as total_mes_atual
        FROM dados_mensais
        GROUP BY ID_LOCAL, NM_LOCAL
    ),
    movimentacao_mes AS (
        SELECT 
            NM_LOCAL, (total_mes_atual - total_mes_anterior) as movimentacao_mes,
            (SELECT SUM(total_mes_atual - total_mes_anterior) FROM dados_pivot WHERE (total_mes_atual - total_mes_anterior) > 0) as total_geral_movimentacao
        FROM dados_pivot
        WHERE (total_mes_atual - total_mes_anterior) != 0
    )
    SELECT 
        NM_LOCAL as Ramo,
        movimentacao_mes as Quantidade
    FROM movimentacao_mes
    WHERE total_geral_movimentacao > 0 AND movimentacao_mes > 0
    ORDER BY movimentacao_mes DESC;
    """
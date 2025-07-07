import datetime

def gerar_query(ano, mes):
    """
    Gera a consulta SQL completa e dinâmica para a evolução das adesões.
    """
    ano_anterior = ano - 1
    
    # Monta as colunas de TOTAIS de cada mês
    sql_pivot_cols = ""
    for i in range(1, mes + 1):
        nome_mes = datetime.date(ano, i, 1).strftime('%b').lower()
        sql_pivot_cols += f", SUM(CASE WHEN NR_ANO_REF = {ano} AND NR_MES_REF = {i} THEN total_mes ELSE 0 END) as total_{nome_mes}_{ano}"

    # Monta as colunas de VARIAÇÃO de cada mês
    sql_delta_cols = ""
    for i in range(1, mes + 1):
        nome_mes_atual = datetime.date(ano, i, 1).strftime('%b').lower()
        coluna_total_atual = f"total_{nome_mes_atual}_{ano}"
        
        if i == 1:
            coluna_anterior = f"saldo_{ano_anterior}"
        else:
            nome_mes_anterior = datetime.date(ano, i - 1, 1).strftime('%b').lower()
            coluna_anterior = f"total_{nome_mes_anterior}_{ano}"
        
        # A vírgula inicial aqui está correta, pois vamos juntar com a coluna anterior
        coluna = f", ({coluna_total_atual} - {coluna_anterior}) as {nome_mes_atual}_{ano}"
        sql_delta_cols += coluna

    ultimo_mes_nome = datetime.date(ano, mes, 1).strftime('%b').lower()
    coluna_ultimo_mes = f"total_{ultimo_mes_nome}_{ano}"

    # Junta tudo na query final
    query_final = f"""
    WITH dados_mensais AS (
        SELECT 
            e.ID_SITUACAO, ps.NM_SITUACAO, e.NR_ANO_REF, e.NR_MES_REF, COUNT(e.ID_PESSOA) as total_mes
        FROM ENCERRAMENTO_PLANO_PARTIC e
        INNER JOIN PLANO_SITUACAO ps ON e.ID_SITUACAO = ps.ID_SITUACAO
        WHERE e.ID_SITUACAO IN (1, 2, 5, 6, 7, 10) AND (
            (e.NR_ANO_REF = {ano_anterior} AND e.NR_MES_REF = 12) OR 
            (e.NR_ANO_REF = {ano} AND e.NR_MES_REF BETWEEN 1 AND {mes})
        )
        GROUP BY e.ID_SITUACAO, ps.NM_SITUACAO, e.NR_ANO_REF, e.NR_MES_REF
    ),
    dados_pivot AS (
        SELECT 
            ID_SITUACAO, NM_SITUACAO,
            SUM(CASE WHEN NR_ANO_REF = {ano_anterior} AND NR_MES_REF = 12 THEN total_mes ELSE 0 END) as saldo_{ano_anterior}
            {sql_pivot_cols}
        FROM dados_mensais
        GROUP BY ID_SITUACAO, NM_SITUACAO
    )
    SELECT 
        CASE 
            WHEN NM_SITUACAO = 'PATROCINADO' THEN 1 WHEN NM_SITUACAO = 'VINCULADO' THEN 2 WHEN NM_SITUACAO = 'BPD - SALDO' THEN 3
            WHEN NM_SITUACAO = 'NO PRAZO OPÇÃO INSTITUTOS' THEN 4 WHEN NM_SITUACAO = 'AUTOPATROCINADO' THEN 5
            WHEN NM_SITUACAO = 'ASSISTIDO' THEN 6 ELSE 7
        END as ordem,
        NM_SITUACAO as situacao,
        saldo_{ano_anterior}
        {sql_delta_cols}, -- CORREÇÃO: Removi a vírgula que existia ANTES deste placeholder
        ({coluna_ultimo_mes} - saldo_{ano_anterior}) as acumulado_{ano},
        {coluna_ultimo_mes} as total_geral
    FROM dados_pivot
    WHERE saldo_{ano_anterior} > 0 OR {coluna_ultimo_mes} > 0
    ORDER BY ordem;
    """
    
    return query_final
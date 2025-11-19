def gerar_query(ano, mes):
    """
    Gera a consulta SQL unificada para a Tabela 1, parametrizando ano e mês.
    """
    ano = int(ano)
    mes = int(mes)
    ano_anterior = ano - 1
    
    pivot_lines = []
    select_cols_list = []

    # Loop para gerar colunas de Mês 01 até o mês de referência
    for i in range(1, mes + 1):
        col_name = f"mes_{i:02d}"
        
        # 1. Linha do PIVOT (SUM CASE...): Calcula o saldo ACUMULADO até o mês 'i'
        line = f"        SUM(CASE WHEN NR_ANO_REF = {ano} AND NR_MES_REF = {i} THEN total_mes ELSE 0 END) as {col_name}"
        pivot_lines.append(line)
        
        # 2. Nome da coluna para o SELECT final
        select_cols_list.append(col_name)

    # Junta as linhas do pivot
    sql_pivot_block = ",\n".join(pivot_lines)
    
    # Junta as colunas do select
    sql_select_cols = ", ".join(select_cols_list)

    # Coluna do mês de referência (último mês escolhido)
    coluna_mes_atual = f"mes_{mes:02d}"

    # Filtro WHERE dinâmico: mostra a linha se o saldo anterior ou qualquer mês do ano tiver valor.
    lista_condicoes_where = [f"saldo_{ano_anterior} > 0"]
    for col in select_cols_list:
        lista_condicoes_where.append(f"{col} > 0")
    
    sql_where_clause = " OR ".join(lista_condicoes_where)

    query_final = f"""WITH origem_participante AS (
    -- CTE para encontrar a última situação de origem (Patrocinado ou Vinculado)
    SELECT 
        ID_PESSOA,
        CASE 
            WHEN ID_SITUACAO = 1 THEN 'Patrocinado'
            WHEN ID_SITUACAO = 2 THEN 'Vinculado'
            ELSE 'NÃO DEFINIDA' 
        END AS TIPO_ORIGEM,
        ROW_NUMBER() OVER(PARTITION BY ID_PESSOA ORDER BY DT_INI DESC) as rn
    FROM
        hist_plano_participante
    WHERE
        ID_SITUACAO IN (1, 2)
),
dados_mensais AS (
    -- Esta CTE traz os dados brutos de todas as situações originais (1, 2, 5, 6, 7, 10, 28)
    SELECT
        e.ID_SITUACAO,
        ps.NM_SITUACAO,
        e.NR_ANO_REF,
        e.NR_MES_REF,
        e.ID_PESSOA
    FROM ENCERRAMENTO_PLANO_PARTIC e
    INNER JOIN PLANO_SITUACAO ps ON e.ID_SITUACAO = ps.ID_SITUACAO
    WHERE e.ID_SITUACAO IN (1, 2, 5, 6, 7, 10, 28) 
      AND (
          (e.NR_ANO_REF = {ano_anterior} AND e.NR_MES_REF = 12) OR 
          (e.NR_ANO_REF = {ano} AND e.NR_MES_REF BETWEEN 1 AND {mes})
      )
),
dados_mensais_com_nome_final AS (
    -- Aplica a lógica de detalhamento e define o nome FINAL de cada linha
    SELECT
        e.NR_ANO_REF,
        e.NR_MES_REF,
        e.ID_PESSOA,
        CASE
            WHEN e.NM_SITUACAO = 'BPD - SALDO' AND op.TIPO_ORIGEM = 'Patrocinado' THEN 'BPD (Patrocinado)'
            WHEN e.NM_SITUACAO = 'BPD - SALDO' AND op.TIPO_ORIGEM = 'Vinculado' THEN 'BPD (Vinculado)'
            WHEN e.NM_SITUACAO = 'AUTOPATROCINADO' AND op.TIPO_ORIGEM = 'Patrocinado' THEN 'Autopatrocinado (Patrocinado)'
            WHEN e.NM_SITUACAO = 'AUTOPATROCINADO' AND op.TIPO_ORIGEM = 'Vinculado' THEN 'Autopatrocinado (Vinculado)'
            ELSE e.NM_SITUACAO 
        END AS NM_SITUACAO_FINAL
    FROM dados_mensais e
    LEFT JOIN origem_participante op ON op.id_pessoa = e.id_pessoa AND op.rn = 1
),
dados_mensais_agrupados AS (
    SELECT
        NM_SITUACAO_FINAL AS NM_SITUACAO,
        NR_ANO_REF,
        NR_MES_REF,
        COUNT(ID_PESSOA) AS total_mes
    FROM dados_mensais_com_nome_final
    GROUP BY
        NM_SITUACAO_FINAL,
        NR_ANO_REF,
        NR_MES_REF
),
dados_pivot AS (
    SELECT
        NM_SITUACAO,
        SUM(CASE WHEN NR_ANO_REF = {ano_anterior} AND NR_MES_REF = 12 THEN total_mes ELSE 0 END) as saldo_{ano_anterior},
        {sql_pivot_block}
    FROM dados_mensais_agrupados
    GROUP BY NM_SITUACAO
)
SELECT 
    CASE 
        WHEN NM_SITUACAO = 'PATROCINADO' THEN 1 
        WHEN NM_SITUACAO = 'VINCULADO' THEN 2 
        WHEN NM_SITUACAO = 'BPD (Patrocinado)' THEN 3
        WHEN NM_SITUACAO = 'BPD (Vinculado)' THEN 4
        WHEN NM_SITUACAO = 'NO PRAZO OPÇÃO INSTITUTOS' THEN 5 
        WHEN NM_SITUACAO = 'Autopatrocinado (Patrocinado)' THEN 6
        WHEN NM_SITUACAO = 'Autopatrocinado (Vinculado)' THEN 7
        WHEN NM_SITUACAO = 'ASSISTIDO' THEN 8 
        ELSE 9
    END as ordem,
    NM_SITUACAO as situacao,
    saldo_{ano_anterior},
    {sql_select_cols},
    ({coluna_mes_atual} - saldo_{ano_anterior}) as acumulado_{ano},
    {coluna_mes_atual} as total_geral
FROM dados_pivot
WHERE {sql_where_clause}
ORDER BY ordem;
    """
    return query_final

if __name__ == "__main__":
    print(gerar_query(2025, 9))
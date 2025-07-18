# queries/grafico8_contribuicao_paridade.py

def gerar_query(ano, mes):
    """
    Gera a query completa e dinâmica para o Gráfico 8 (Paridade de Contribuição),
    retornando valores numéricos brutos para o Python.
    """
    # A query é envolvida por um f-string para inserir o ano e mês dinamicamente
    return f"""
    WITH dados_detalhados AS (
        SELECT  
            SUM(CONTRIB_PATROCINADOR) AS CONTRIBUICAO_PATROCINADOR,
            SUM(CONTRIB_PARTICIPANTE) AS CONTRIBUICAO_PARTICIPANTE
        FROM (
            -- Subquery para as contribuições do PARTICIPANTE
            SELECT 
                ff.NR_MES_REF,
                ff.NR_ANO_REF,
                ptc.tipo_contribuicao AS CONTRIBUICAO,
                ff.VL_CONTRIB AS CONTRIB_PARTICIPANTE,
                0 AS CONTRIB_PATROCINADOR
            FROM pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa))
            LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA
            LEFT JOIN portal.dbo.participante_tipo_contribuicao ptc ON ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO
            WHERE 
                pe.IC_EMP_PATROC = 'N'
                AND pe.IC_PARTICIPANTE = 'S'
                AND ptc.tipo_contribuicao IN ('NORMAL','NORMAL - AUTOPATROCINADO','NORMAL - GR. NATALINA','NORMAL - JUROS','NORMAL - JUROS - AUTOPATROCINADO','NORMAL - JUROS - GR. NATALINA')
                AND ff.ID_CONTRIBUICAO IN (SELECT ptc.ID_CONTRIBUICAO_TRUST FROM portal.dbo.participante_tipo_contribuicao ptc WHERE ptc.mantenedor_consolidado = 'PARTICIPANTE' AND ptc.movimentacao IN ('CONTRIBUIÇÃO','AJUSTE',''))
                AND ff.ID_CONTRIBUICAO NOT IN (491,492)
                -- Filtro de data dinâmico
                AND ff.NR_ANO_REF = {ano} AND ff.NR_MES_REF = {mes}

            UNION ALL

            -- Subquery para as contribuições do PATROCINADOR
            SELECT 
                ff.NR_MES_REF,
                ff.NR_ANO_REF,
                ptc.tipo_contribuicao AS CONTRIBUICAO,
                0 AS CONTRIB_PARTICIPANTE,
                ff.VL_CONTRIB AS CONTRIB_PATROCINADOR
            FROM pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa))
            LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA
            LEFT JOIN portal.dbo.participante_tipo_contribuicao ptc ON ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO
            WHERE 
                pe.IC_EMP_PATROC = 'N'
                AND pe.IC_PARTICIPANTE = 'S'
                AND ptc.tipo_contribuicao IN ('NORMAL','NORMAL - AUTOPATROCINADO','NORMAL - GR. NATALINA','NORMAL - JUROS','NORMAL - JUROS - AUTOPATROCINADO','NORMAL - JUROS - GR. NATALINA')
                AND ff.ID_CONTRIBUICAO IN (SELECT ptc.ID_CONTRIBUICAO_TRUST FROM portal.dbo.participante_tipo_contribuicao ptc WHERE ptc.mantenedor_consolidado = 'PATROCINADOR' AND ptc.movimentacao IN ('CONTRIBUIÇÃO','AJUSTE',''))
                AND ff.ID_CONTRIBUICAO NOT IN (491,492)
                -- Filtro de data dinâmico
                AND ff.NR_ANO_REF = {ano} AND ff.NR_MES_REF = {mes}
        ) a
    )
    -- CORREÇÃO: Retorna os valores como números e em linhas, formato ideal para o Python
    SELECT 'PARTICIPANTE' AS Categoria, CONTRIBUICAO_PARTICIPANTE AS Valor FROM dados_detalhados
    UNION ALL
    SELECT 'PATROCINADOR' AS Categoria, CONTRIBUICAO_PATROCINADOR AS Valor FROM dados_detalhados;
    """
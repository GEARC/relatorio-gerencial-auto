# queries/tabela7_contribuicao_patrocinador.py

def gerar_query(ano, mes):
    """
    Gera a query completa e dinâmica para a Tabela 7 (Contribuições por Patrocinador).
    """
    return f"""
    WITH contribuicoes_empresa_detalhada AS (
        select 
            EMPRESA,
            SUM(CASE WHEN NR_MES_REF = {mes} and nr_ano_ref = {ano} THEN CONTRIB_PARTICIPANTE + CONTRIB_PATROCINADOR ELSE 0 END) AS contribuicao_no_mes,
            SUM(CASE WHEN (NR_ANO_REF < {ano}) or (nr_ano_ref = {ano} and NR_MES_REF <= {mes}) THEN CONTRIB_PARTICIPANTE + CONTRIB_PATROCINADOR ELSE 0 END) AS contribuicao_total
        from (
            -- Início da sua subquery completa com UNION ALL
            SELECT  
                emp.sg_pessoa EMPRESA,
                ff.NR_MES_REF,
                ff.NR_ANO_REF,
                ff.VL_CONTRIB CONTRIB_PARTICIPANTE,
                0 CONTRIB_PATROCINADOR
            FROM    pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa)) 
            LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp 
            LEFT JOIN (SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa FROM pessoa a1 WHERE a1.ic_emp_patroc = 'S') emp ON emp.id_pessoa = ep.id_pessoa_emp 
            LEFT JOIN hist_contribuicao ff on ff.id_pessoa = pe.ID_PESSOA
            WHERE 
                pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S'
                AND ff.ID_CONTRIBUICAO in (select ptc.ID_CONTRIBUICAO_TRUST from portal.dbo.participante_tipo_contribuicao ptc where ptc.mantenedor_consolidado = 'PARTICIPANTE' and movimentacao in ('CONTRIBUIÇÃO','AJUSTE','')) 
                AND ff.ID_CONTRIBUICAO not in (491,492)

            UNION ALL

            SELECT  
                emp.sg_pessoa EMPRESA, 
                ff.NR_MES_REF,
                ff.NR_ANO_REF,
                0 CONTRIB_PARTICIPANTE,
                ff.VL_CONTRIB CONTRIB_PATROCINADOR
            FROM    pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa)) 
            LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp 
            LEFT JOIN (SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa FROM pessoa a1 WHERE a1.ic_emp_patroc = 'S') emp ON emp.id_pessoa = ep.id_pessoa_emp 
            LEFT JOIN hist_contribuicao ff on ff.id_pessoa = pe.ID_PESSOA
            WHERE 
                pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S'
                AND ff.ID_CONTRIBUICAO in (select ptc.ID_CONTRIBUICAO_TRUST from portal.dbo.participante_tipo_contribuicao ptc where ptc.mantenedor_consolidado = 'PATROCINADOR' and ptc.movimentacao in ('CONTRIBUIÇÃO','AJUSTE',''))
                AND ff.ID_CONTRIBUICAO not in (491,492)
        ) a
        GROUP BY EMPRESA
    ),
    total_contribuicoes AS (
        SELECT 
            SUM(contribuicao_no_mes) AS total_geral_mes,
            SUM(contribuicao_total) AS total_geral_acumulado
        FROM contribuicoes_empresa_detalhada
    )
    SELECT 
        ce.EMPRESA AS Patrocinador,
        ce.contribuicao_no_mes,
        (ce.contribuicao_no_mes * 100.0) / NULLIF(tc.total_geral_mes, 0) AS representatividade_contribuicao,
        ce.contribuicao_total AS contribuicoes_acumuladas,
        (ce.contribuicao_total * 100.0) / NULLIF(tc.total_geral_acumulado, 0) AS representatividade_patrimonio
    FROM contribuicoes_empresa_detalhada ce
    CROSS JOIN total_contribuicoes tc
    ORDER BY ce.contribuicao_no_mes DESC;
    """
import datetime

def gerar_query(ano, mes):
    """Gera a query para a Tabela 4 de arrecadação por competência, usando a lógica original do usuário."""
    
    # Mapeamento robusto para abreviação de meses, independente do locale
    mapa_mes_abbr = {
        1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
        7: 'jul', 8: 'ago', 9: 'set', 10: 'out', 11: 'nov', 12: 'dez'
    }
    mes_abbr = mapa_mes_abbr.get(mes, 'unk') # 'unk' como fallback
    
    mes_ano_formatado = f"{mes_abbr}/{ano}"

    return f"""
    WITH dados_agrupados AS (
        SELECT 
            CASE 
                WHEN NR_MES_COMP = {mes} AND NR_ANO_COMP = {ano} THEN '{mes_ano_formatado}'
                ELSE 'Outras Competências'
            END AS COMPETENCIA,
            SUM(CONTRIB_PARTICIPANTE + CONTRIB_PATROCINADOR) AS CONTRIBUICAO_TOTAL
        FROM (
            -- Subquery 1 (Participante) usando a sua estrutura completa
            SELECT 
                ff.NR_MES_COMP, ff.NR_ANO_COMP, ff.NR_MES_REF, ff.NR_ANO_REF, ff.VL_CONTRIB AS CONTRIB_PARTICIPANTE, 0 AS CONTRIB_PATROCINADOR
            FROM pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa)) 
            LEFT JOIN empresa_situacao es ON he.id_sit_emp = es.id_sit_emp AND he.id_emp = es.id_emp 
            LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp 
            LEFT JOIN (SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa FROM pessoa a1 WHERE a1.ic_emp_patroc = 'S') emp ON emp.id_pessoa = ep.id_pessoa_emp 
            LEFT JOIN plano_participante pp ON pp.id_pessoa = pe.id_pessoa 
            LEFT JOIN hist_plano_participante hpp ON hpp.id_pessoa = pe.id_pessoa AND Getdate() BETWEEN hpp.dt_ini AND Isnull(hpp.dt_fim, Getdate() + 1) 
            LEFT JOIN plano_situacao ps ON ps.id_situacao = hpp.id_situacao 
            LEFT JOIN PLANO_CATEGORIA pc ON pc.ID_CATEGORIA = hpp.ID_CATEGORIA 
            LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA AND ff.ID_CONTRIBUICAO IN (select ptc.ID_CONTRIBUICAO_TRUST from portal.dbo.participante_tipo_contribuicao ptc where ptc.mantenedor_consolidado = 'PARTICIPANTE' and movimentacao in ('CONTRIBUIÇÃO','AJUSTE','')) AND ff.ID_CONTRIBUICAO NOT IN (491,492)
            LEFT JOIN portal.dbo.participante_tipo_contribuicao ptc ON ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO   
            LEFT JOIN CARGO c ON c.ID_CARGO = pe.ID_CARGO AND c.ID_EMP = pe.ID_EMP 
            LEFT JOIN LOCAL LE ON le.ID_LOCAL = pe.id_local 
            WHERE pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S'
            
            UNION ALL

            -- Subquery 2 (Patrocinador) usando a sua estrutura completa
            SELECT 
                ff.NR_MES_COMP, ff.NR_ANO_COMP, ff.NR_MES_REF, ff.NR_ANO_REF, 0 AS CONTRIB_PARTICIPANTE, ff.VL_CONTRIB AS CONTRIB_PATROCINADOR
            FROM pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa))
            LEFT JOIN empresa_situacao es ON he.id_sit_emp = es.id_sit_emp AND he.id_emp = es.id_emp 
            LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp 
            LEFT JOIN (SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa FROM pessoa a1 WHERE a1.ic_emp_patroc = 'S') emp ON emp.id_pessoa = ep.id_pessoa_emp 
            LEFT JOIN plano_participante pp ON pp.id_pessoa = pe.id_pessoa 
            LEFT JOIN hist_plano_participante hpp ON hpp.id_pessoa = pe.id_pessoa AND Getdate() BETWEEN hpp.dt_ini AND Isnull(hpp.dt_fim, Getdate() + 1) 
            LEFT JOIN plano_situacao ps ON ps.id_situacao = hpp.id_situacao 
            LEFT JOIN PLANO_CATEGORIA pc ON pc.ID_CATEGORIA = hpp.ID_CATEGORIA 
            LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA AND ff.ID_CONTRIBUICAO IN (select ptc.ID_CONTRIBUICAO_TRUST from portal.dbo.participante_tipo_contribuicao ptc where ptc.mantenedor_consolidado = 'PATROCINADOR' and ptc.movimentacao in ('CONTRIBUIÇÃO','AJUSTE','')) AND ff.ID_CONTRIBUICAO NOT IN (491,492)
            LEFT JOIN portal.dbo.participante_tipo_contribuicao ptc ON ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO 
            LEFT JOIN CARGO c ON c.ID_CARGO = pe.ID_CARGO AND c.ID_EMP = pe.ID_EMP 
            LEFT JOIN LOCAL LE ON le.ID_LOCAL = pe.id_local 
            WHERE pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S'
        ) a
        WHERE NR_ANO_REF = {ano} AND NR_MES_REF = {mes}
        GROUP BY 
            CASE 
                WHEN NR_MES_COMP = {mes} AND NR_ANO_COMP = {ano} THEN '{mes_ano_formatado}'
                ELSE 'Outras Competências'
            END
    )
    SELECT 
        COMPETÊNCIA,
        CONTRIBUIÇÃO
    FROM (
        SELECT 
            COMPETENCIA AS COMPETÊNCIA,
            CONTRIBUICAO_TOTAL AS CONTRIBUIÇÃO,
            CASE WHEN COMPETENCIA LIKE '%/%' THEN 1 WHEN COMPETENCIA = 'Outras Competências' THEN 2 ELSE 4 END AS ORDEM
        FROM dados_agrupados
        UNION ALL
        SELECT 
            'TOTAL' AS COMPETÊNCIA,
            SUM(CONTRIBUICAO_TOTAL) AS CONTRIBUIÇÃO,
            3 AS ORDEM
        FROM dados_agrupados
    ) resultado_ordenado
    ORDER BY ORDEM;
    """
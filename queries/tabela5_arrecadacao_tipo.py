import datetime
from dateutil.relativedelta import relativedelta

def gerar_query(ano, mes):
    """
    Gera a query para a Tabela 5, usando a lógica original e completa do usuário
    e tornando-a dinâmica.
    """
    
    data_atual = datetime.date(ano, mes, 1)
    data_anterior = data_atual - relativedelta(months=1)
    
    ano_anterior_logico = data_anterior.year
    mes_anterior_logico = data_anterior.month

    return f"""
    WITH dados_contribuicao AS (
        select NR_MES_REF,
            NR_ANO_REF,
            CASE
                WHEN CONTRIBUICAO IN ('FACULTATIVA', 'FACULTATIVA - GR. NATALINA', 'FACULTATIVA - AUTOPATROCINADO', 'FACULTATIVA ESPORÁDICA', 'FACULTATIVA - JUROS', 'FACULTATIVA - JUROS - AUTOPATROCINADO', 'FACULTATIVA - JUROS - GR. NATALINA', 'FACULTATIVA ESPORÁDICA 2') THEN 'FACULTATIVA'
                WHEN CONTRIBUICAO IN ('MULTA', 'MULTA - GR. NATALINA', 'MULTA - AUTOPATROCINADO') THEN 'MULTA'
                WHEN CONTRIBUICAO IN ('NORMAL', 'NORMAL - AUTOPATROCINADO ', 'NORMAL - GR. NATALINA', 'NORMAL - JUROS', 'NORMAL - JUROS - AUTOPATROCINADO', 'NORMAL - JUROS - GR. NATALINA') THEN 'NORMAL'
                WHEN CONTRIBUICAO = 'PORTABILIDADE' THEN 'PORTABILIDADE' 
                WHEN CONTRIBUICAO IN ('SEGURO', 'SEGURO - AUTOPATROCINADO') THEN 'SEGURO'
                WHEN CONTRIBUICAO = 'BPD' THEN 'TAXA BPD'
                WHEN CONTRIBUICAO IN ('VINCULADA', 'VINCULADA - AUTOPATROCINADO', 'VINCULADA - JUROS', 'VINCULADA - GR. NATALINA', 'VINCULADA - JUROS - AUTOPATROCINADO', 'VINCULADA - JUROS - GR. NATALINA') THEN 'VINCULADA'
            END AS CONTRIBUICAO_TIPO,
            SUM(CONTRIB_PARTICIPANTE) AS TOTAL_CONTRIB_PARTICIPANTE,
            SUM(CONTRIB_PATROCINADOR) AS TOTAL_CONTRIB_PATROCINADOR
        from (
            -- Subquery 1 (Participante)
            SELECT ff.NR_MES_REF, ff.NR_ANO_REF, ptc.tipo_contribuicao CONTRIBUICAO, ff.VL_CONTRIB CONTRIB_PARTICIPANTE, 0 CONTRIB_PATROCINADOR
            FROM pessoa pe LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa)) LEFT JOIN empresa_situacao es ON he.id_sit_emp = es.id_sit_emp AND he.id_emp = es.id_emp LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp LEFT JOIN (SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa FROM pessoa a1 WHERE a1.ic_emp_patroc = 'S') emp ON emp.id_pessoa = ep.id_pessoa_emp LEFT JOIN plano_participante pp ON pp.id_pessoa = pe.id_pessoa LEFT JOIN hist_plano_participante hpp ON hpp.id_pessoa = pe.id_pessoa AND Getdate() BETWEEN hpp.dt_ini AND Isnull(hpp.dt_fim, Getdate() + 1) LEFT JOIN plano_situacao ps ON ps.id_situacao = hpp.id_situacao LEFT JOIN PLANO_CATEGORIA pc on pc.ID_CATEGORIA = hpp.ID_CATEGORIA LEFT JOIN hist_contribuicao ff on ff.id_pessoa = pe.ID_PESSOA and ff.ID_CONTRIBUICAO in (select ptc.ID_CONTRIBUICAO_TRUST from portal.dbo.participante_tipo_contribuicao ptc where 1 = 1 and ptc.mantenedor_consolidado = 'PARTICIPANTE' and movimentacao in ('CONTRIBUIÇÃO','AJUSTE','')) and ff.ID_CONTRIBUICAO not in (491,492) left join portal.dbo.participante_tipo_contribuicao ptc on ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO left join CARGO c on c.ID_CARGO = pe.ID_CARGO AND c.ID_EMP = pe.ID_EMP left join LOCAL LE on le.ID_LOCAL = pe.id_local
            WHERE 1 = 1 AND pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S'
            UNION ALL
            -- Subquery 2 (Patrocinador)
            SELECT ff.NR_MES_REF, ff.NR_ANO_REF, ptc.tipo_contribuicao CONTRIBUICAO, 0 CONTRIB_PARTICIPANTE, ff.VL_CONTRIB CONTRIB_PATROCINADOR
            FROM pessoa pe LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa)) LEFT JOIN empresa_situacao es ON he.id_sit_emp = es.id_sit_emp AND he.id_emp = es.id_emp LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp LEFT JOIN (SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa FROM pessoa a1 WHERE a1.ic_emp_patroc = 'S') emp ON emp.id_pessoa = ep.id_pessoa_emp LEFT JOIN plano_participante pp ON pp.id_pessoa = pe.id_pessoa LEFT JOIN hist_plano_participante hpp ON hpp.id_pessoa = pe.id_pessoa AND Getdate() BETWEEN hpp.dt_ini AND Isnull(hpp.dt_fim, Getdate() + 1) LEFT JOIN plano_situacao ps ON ps.id_situacao = hpp.id_situacao LEFT JOIN PLANO_CATEGORIA pc on pc.ID_CATEGORIA = hpp.ID_CATEGORIA LEFT JOIN hist_contribuicao ff on ff.id_pessoa = pe.ID_PESSOA and ff.ID_CONTRIBUICAO in (select ptc.ID_CONTRIBUICAO_TRUST from portal.dbo.participante_tipo_contribuicao ptc where 1 = 1 and ptc.mantenedor_consolidado = 'PATROCINADOR' and ptc.movimentacao in ('CONTRIBUIÇÃO','AJUSTE','')) and ff.ID_CONTRIBUICAO not in (491,492) left join portal.dbo.participante_tipo_contribuicao ptc on ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO left join CARGO c on c.ID_CARGO = pe.ID_CARGO AND c.ID_EMP = pe.ID_EMP left join LOCAL LE on le.ID_LOCAL = pe.id_local
            WHERE 1 = 1 AND pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S' AND ff.ID_CONTRIBUICAO IS NOT NULL
        ) a
        where 1=1
        and NR_ANO_REF = {ano}
        and NR_MES_REF in ({mes_anterior_logico}, {mes})
        group by NR_MES_REF, NR_ANO_REF,
            CASE
                WHEN CONTRIBUICAO IN ('FACULTATIVA', 'FACULTATIVA - GR. NATALINA', 'FACULTATIVA - AUTOPATROCINADO', 'FACULTATIVA ESPORÁDICA', 'FACULTATIVA - JUROS', 'FACULTATIVA - JUROS - AUTOPATROCINADO', 'FACULTATIVA - JUROS - GR. NATALINA', 'FACULTATIVA ESPORÁDICA 2') THEN 'FACULTATIVA'
                WHEN CONTRIBUICAO IN ('MULTA', 'MULTA - GR. NATALINA', 'MULTA - AUTOPATROCINADO') THEN 'MULTA'
                WHEN CONTRIBUICAO IN ('NORMAL', 'NORMAL - AUTOPATROCINADO ', 'NORMAL - GR. NATALINA', 'NORMAL - JUROS', 'NORMAL - JUROS - AUTOPATROCINADO', 'NORMAL - JUROS - GR. NATALINA') THEN 'NORMAL'
                WHEN CONTRIBUICAO = 'PORTABILIDADE' THEN 'PORTABILIDADE' 
                WHEN CONTRIBUICAO IN ('SEGURO', 'SEGURO - AUTOPATROCINADO') THEN 'SEGURO'
                WHEN CONTRIBUICAO = 'BPD' THEN 'TAXA BPD'
                WHEN CONTRIBUICAO IN ('VINCULADA', 'VINCULADA - AUTOPATROCINADO', 'VINCULADA - JUROS', 'VINCULADA - GR. NATALINA', 'VINCULADA - JUROS - AUTOPATROCINADO', 'VINCULADA - JUROS - GR. NATALINA') THEN 'VINCULADA'
            END
    ),
    resumo_mensal AS (
        SELECT 
            CONTRIBUICAO_TIPO, NR_MES_REF,
            SUM(TOTAL_CONTRIB_PARTICIPANTE + TOTAL_CONTRIB_PATROCINADOR) as total_contribuicao
        FROM dados_contribuicao
        WHERE CONTRIBUICAO_TIPO IS NOT NULL  
        GROUP BY CONTRIBUICAO_TIPO, NR_MES_REF
    ),
    totais AS (
        SELECT 
            CONTRIBUICAO_TIPO,
            SUM(CASE WHEN NR_MES_REF = {mes_anterior_logico} THEN total_contribuicao ELSE 0 END) AS mes_passado,
            SUM(CASE WHEN NR_MES_REF = {mes} THEN total_contribuicao ELSE 0 END) AS mes_atual
        FROM resumo_mensal
        GROUP BY CONTRIBUICAO_TIPO
    ),
    final_com_total AS (
        SELECT 
            CONTRIBUICAO_TIPO, mes_passado, mes_atual,
            CASE WHEN mes_passado = 0 AND mes_atual > 0 THEN 100.00 WHEN mes_passado = 0 AND mes_atual = 0 THEN 0.00 ELSE ROUND(((mes_atual - mes_passado) / mes_passado) * 100, 2) END AS variacao_percentual
        FROM totais
        UNION ALL
        SELECT 
            'TOTAL' AS CONTRIBUICAO_TIPO, SUM(mes_passado), SUM(mes_atual),
            CASE WHEN SUM(mes_passado) = 0 AND SUM(mes_atual) > 0 THEN 100.00 WHEN SUM(mes_passado) = 0 AND SUM(mes_atual) = 0 THEN 0.00 ELSE ROUND(((SUM(mes_atual) - SUM(mes_passado)) / SUM(mes_passado)) * 100, 2) END
        FROM totais
    )
    SELECT 
        CONTRIBUICAO_TIPO AS [Contribuicao],
        mes_passado,
        mes_atual,
        variacao_percentual AS [Variacao]
    FROM final_com_total
    ORDER BY 
        CASE WHEN CONTRIBUICAO_TIPO = 'TOTAL' THEN 'ZZZZ' ELSE CONTRIBUICAO_TIPO END;
    """
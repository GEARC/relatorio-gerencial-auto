def gerar_query(ano, mes):
    """
    Gera a query completa e dinâmica para a Tabela 6 (Arrecadação por Cargo).
    """
    return f"""
    WITH dados_agrupados AS (
        select 
            CASE
                WHEN a.CARGO LIKE 'ANALISTA%' THEN 'ANALISTAS'
                WHEN a.CARGO LIKE 'TÉCNICO%' THEN 'TÉCNICOS'
                WHEN a.CARGO LIKE 'AUXILIAR%' THEN 'AUXILIARES'
                else 'JUÍZES E MEMBROS'
            END AS CARGO,
            COUNT(DISTINCT a.ID_PESSOA) AS QUANTIDADE_PARTICIPANTES,
            SUM(a.CONTRIB_PARTICIPANTE + a.CONTRIB_PATROCINADOR) AS TOTAL_CONTRIBUICAO
        from (
            -- Subquery para contribuições de Participante
            SELECT pe.ID_PESSOA, ff.NR_MES_REF, ff.NR_ANO_REF, c.NM_CARGO CARGO, ff.VL_CONTRIB CONTRIB_PARTICIPANTE, 0 CONTRIB_PATROCINADOR
            FROM pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa))
            LEFT JOIN empresa_situacao es ON he.id_sit_emp = es.id_sit_emp AND he.id_emp = es.id_emp 
            LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp 
            LEFT JOIN (SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa FROM pessoa a1 WHERE a1.ic_emp_patroc = 'S') emp ON emp.id_pessoa = ep.id_pessoa_emp 
            LEFT JOIN plano_participante pp ON pp.id_pessoa = pe.id_pessoa 
            LEFT JOIN hist_plano_participante hpp ON hpp.id_pessoa = pe.id_pessoa AND Getdate() BETWEEN hpp.dt_ini AND Isnull(hpp.dt_fim, Getdate() + 1) 
            LEFT JOIN plano_situacao ps ON ps.id_situacao = hpp.id_situacao 
            LEFT JOIN PLANO_CATEGORIA pc on pc.ID_CATEGORIA = hpp.ID_CATEGORIA 
            LEFT JOIN hist_contribuicao ff on ff.id_pessoa = pe.ID_PESSOA and ff.ID_CONTRIBUICAO in (select ptc.ID_CONTRIBUICAO_TRUST from portal.dbo.participante_tipo_contribuicao ptc where 1 = 1 and ptc.mantenedor_consolidado = 'PARTICIPANTE' and movimentacao in ('CONTRIBUIÇÃO','AJUSTE','')) and ff.ID_CONTRIBUICAO not in (491,492) 
            left join portal.dbo.participante_tipo_contribuicao ptc on ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO   
            left join CARGO c on c.ID_CARGO = pe.ID_CARGO AND c.ID_EMP = pe.ID_EMP 
            left join LOCAL LE on le.ID_LOCAL = pe.id_local 
            WHERE 1 = 1 AND pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S'

            UNION ALL

            -- Subquery para contribuições de Patrocinador
            SELECT pe.ID_PESSOA, ff.NR_MES_REF, ff.NR_ANO_REF, c.NM_CARGO CARGO, 0 CONTRIB_PARTICIPANTE, ff.VL_CONTRIB CONTRIB_PATROCINADOR
            FROM pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa AND he.id_emp = pe.id_emp AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa)) 
            LEFT JOIN empresa_situacao es ON he.id_sit_emp = es.id_sit_emp AND he.id_emp = es.id_emp 
            LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp 
            LEFT JOIN (SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa FROM pessoa a1 WHERE a1.ic_emp_patroc = 'S') emp ON emp.id_pessoa = ep.id_pessoa_emp 
            LEFT JOIN plano_participante pp ON pp.id_pessoa = pe.id_pessoa 
            LEFT JOIN hist_plano_participante hpp ON hpp.id_pessoa = pe.id_pessoa AND Getdate() BETWEEN hpp.dt_ini AND Isnull(hpp.dt_fim, Getdate() + 1) 
            LEFT JOIN plano_situacao ps ON ps.id_situacao = hpp.id_situacao 
            LEFT JOIN PLANO_CATEGORIA pc on pc.ID_CATEGORIA = hpp.ID_CATEGORIA 
            LEFT JOIN hist_contribuicao ff on ff.id_pessoa = pe.ID_PESSOA and ff.ID_CONTRIBUICAO in (select ptc.ID_CONTRIBUICAO_TRUST from portal.dbo.participante_tipo_contribuicao ptc where 1 = 1 and ptc.mantenedor_consolidado = 'PATROCINADOR' and ptc.movimentacao in ('CONTRIBUIÇÃO','AJUSTE','')) and ff.ID_CONTRIBUICAO not in (491,492) 
            left join portal.dbo.participante_tipo_contribuicao ptc on ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO 
            left join CARGO c on c.ID_CARGO = pe.ID_CARGO AND c.ID_EMP = pe.ID_EMP 
            left join LOCAL LE on le.ID_LOCAL = pe.id_local 
            WHERE 1 = 1 AND pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S'
        ) a
        -- Filtro principal agora dinâmico
        where 1=1 and a.NR_ANO_REF = {ano} and a.NR_MES_REF = {mes}
        group by CASE
            WHEN a.CARGO LIKE 'ANALISTA%' THEN 'ANALISTAS'
            WHEN a.CARGO LIKE 'TÉCNICO%' THEN 'TÉCNICOS'
            WHEN a.CARGO LIKE 'AUXILIAR%' THEN 'AUXILIARES'
            else 'JUÍZES E MEMBROS'
        END
    )
    -- Seleção final com cálculos e nomes de colunas simples (sem acentos)
    SELECT 
        CARGO,
        (TOTAL_CONTRIBUICAO * 100.0) / NULLIF(SUM(TOTAL_CONTRIBUICAO) OVER(), 0) AS RepresentatividadeContribuicao,
        CASE WHEN QUANTIDADE_PARTICIPANTES > 0 THEN (TOTAL_CONTRIBUICAO / QUANTIDADE_PARTICIPANTES) ELSE 0 END AS ContribuicaoMedia,
        QUANTIDADE_PARTICIPANTES AS QuantidadeParticipantes,
        (QUANTIDADE_PARTICIPANTES * 100.0) / NULLIF(SUM(QUANTIDADE_PARTICIPANTES) OVER(), 0) AS RepresentatividadeParticipantes,
        TOTAL_CONTRIBUICAO AS TotalContribuicao
    FROM dados_agrupados
    ORDER BY CARGO ASC;
    """
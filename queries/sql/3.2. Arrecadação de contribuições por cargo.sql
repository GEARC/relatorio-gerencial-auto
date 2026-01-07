WITH dados_agrupados AS (
    select 
      CASE
            WHEN a.CARGO LIKE 'ANALISTA%' THEN 'Analistas'
            WHEN a.CARGO LIKE 'TÉCNICO%' THEN 'Técnicos'
            WHEN a.CARGO LIKE 'AUXILIAR%' THEN 'Auxiliar'
            else 'Juizes e membros'
        END AS CARGO,
           COUNT(DISTINCT a.ID_PESSOA) AS QUANTIDADE_PARTICIPANTES,
                 SUM(a.CONTRIB_PARTICIPANTE + a.CONTRIB_PATROCINADOR) AS TOTAL_CONTRIBUICAO
    from (
        SELECT  pe.ID_PESSOA,
                ff.NR_MES_REF,
                ff.NR_ANO_REF,
                c.NM_CARGO CARGO,
                ff.VL_CONTRIB CONTRIB_PARTICIPANTE,
                0 CONTRIB_PATROCINADOR,
                round(ff.QT_COTA *
                (select iv.VL_INDEXADOR 
                from INDEXADOR_VALOR iv
                where iv.dt_indexador = (select max(iv2.dt_indexador) 
                                        from INDEXADOR_VALOR iv2
                                        where iv2.ID_INDEXADOR = iv.ID_INDEXADOR)
                and iv.id_indexador = ff.ID_INDEXADOR),2) as COTA_ATUALIZADA
        FROM   pessoa pe 
               LEFT JOIN hist_empresa he
                      ON he.id_pessoa = pe.id_pessoa 
                         AND he.id_emp = pe.id_emp 
                         AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) 
                                              FROM   hist_empresa he1 
                                              WHERE  he1.id_pessoa = he.id_pessoa) 
                         AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) 
                                              FROM   hist_empresa he1 
                                              WHERE  he1.id_pessoa = he.id_pessoa 
                                                     AND he1.nr_ano_ref = 
                                                         (SELECT Max(he1.nr_ano_ref) 
                                                          FROM   hist_empresa he1 
                                                          WHERE 
                                                         he1.id_pessoa = he.id_pessoa)) 
               LEFT JOIN empresa_situacao es 
                      ON he.id_sit_emp = es.id_sit_emp 
                         AND he.id_emp = es.id_emp 
               LEFT JOIN empresa ep 
                      ON pe.id_emp = ep.id_emp 
               LEFT JOIN (SELECT a1.id_pessoa, 
                                 a1.id_emp, 
                                 a1.sg_pessoa, 
                                 a1.nm_pessoa 
                          FROM   pessoa a1 
                          WHERE  a1.ic_emp_patroc = 'S') emp 
                      ON emp.id_pessoa = ep.id_pessoa_emp 
               LEFT JOIN plano_participante pp 
                      ON pp.id_pessoa = pe.id_pessoa 
               LEFT JOIN hist_plano_participante hpp 
                      ON hpp.id_pessoa = pe.id_pessoa 
                         AND Getdate() BETWEEN hpp.dt_ini AND 
                                               Isnull(hpp.dt_fim, Getdate() + 1) 
               LEFT JOIN plano_situacao ps 
                      ON ps.id_situacao = hpp.id_situacao
               LEFT JOIN PLANO_CATEGORIA pc
                      on pc.ID_CATEGORIA = hpp.ID_CATEGORIA
               LEFT JOIN hist_contribuicao ff
                    on ff.id_pessoa = pe.ID_PESSOA
                        and ff.ID_CONTRIBUICAO in (select ptc.ID_CONTRIBUICAO_TRUST
                                                    from portal.dbo.participante_tipo_contribuicao ptc
                                                    where 1 = 1
                                                    and ptc.mantenedor_consolidado = 'PARTICIPANTE'
                                                    and movimentacao in ('CONTRIBUIÇÃO','AJUSTE','')
                                                    )
                        and ff.ID_CONTRIBUICAO not in (491,492)
                left join portal.dbo.participante_tipo_contribuicao ptc
                    on ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO			
                left join CARGO c
                    on c.ID_CARGO = pe.ID_CARGO
                    AND c.ID_EMP = pe.ID_EMP
                left join LOCAL LE
                    on le.ID_LOCAL = pe.id_local
        WHERE 1 = 1
              AND pe.IC_EMP_PATROC = 'N'
              AND pe.IC_PARTICIPANTE = 'S'

              union all

              SELECT  pe.ID_PESSOA,
                ff.NR_MES_REF,
                ff.NR_ANO_REF,
                c.NM_CARGO CARGO,
                0 CONTRIB_PARTICIPANTE,
                ff.VL_CONTRIB CONTRIB_PATROCINADOR,
                round(ff.QT_COTA *
                (select iv.VL_INDEXADOR 
                from INDEXADOR_VALOR iv
                where iv.dt_indexador = (select max(iv2.dt_indexador) 
                                        from INDEXADOR_VALOR iv2
                                        where iv2.ID_INDEXADOR = iv.ID_INDEXADOR)
                and iv.id_indexador = ff.ID_INDEXADOR),2) as COTA_ATUALIZADA
        FROM   pessoa pe 
               LEFT JOIN hist_empresa he
                      ON he.id_pessoa = pe.id_pessoa 
                         AND he.id_emp = pe.id_emp 
                         AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) 
                                              FROM   hist_empresa he1 
                                              WHERE  he1.id_pessoa = he.id_pessoa) 
                         AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) 
                                              FROM   hist_empresa he1 
                                              WHERE  he1.id_pessoa = he.id_pessoa 
                                                     AND he1.nr_ano_ref = 
                                                         (SELECT Max(he1.nr_ano_ref) 
                                                          FROM   hist_empresa he1 
                                                          WHERE 
                                                         he1.id_pessoa = he.id_pessoa)) 
               LEFT JOIN empresa_situacao es 
                      ON he.id_sit_emp = es.id_sit_emp 
                         AND he.id_emp = es.id_emp 
               LEFT JOIN empresa ep 
                      ON pe.id_emp = ep.id_emp 
               LEFT JOIN (SELECT a1.id_pessoa, 
                                 a1.id_emp, 
                                 a1.sg_pessoa, 
                                 a1.nm_pessoa 
                          FROM   pessoa a1 
                          WHERE  a1.ic_emp_patroc = 'S') emp 
                      ON emp.id_pessoa = ep.id_pessoa_emp 
               LEFT JOIN plano_participante pp 
                      ON pp.id_pessoa = pe.id_pessoa 
               LEFT JOIN hist_plano_participante hpp 
                      ON hpp.id_pessoa = pe.id_pessoa 
                         AND Getdate() BETWEEN hpp.dt_ini AND 
                                               Isnull(hpp.dt_fim, Getdate() + 1) 
               LEFT JOIN plano_situacao ps 
                      ON ps.id_situacao = hpp.id_situacao
               LEFT JOIN PLANO_CATEGORIA pc
                      on pc.ID_CATEGORIA = hpp.ID_CATEGORIA
               LEFT JOIN hist_contribuicao ff
                    on ff.id_pessoa = pe.ID_PESSOA
                        and ff.ID_CONTRIBUICAO in (select ptc.ID_CONTRIBUICAO_TRUST
                                                    from portal.dbo.participante_tipo_contribuicao ptc
                                                    where 1 = 1
                                                    and ptc.mantenedor_consolidado = 'PATROCINADOR'
                                                    and ptc.movimentacao in ('CONTRIBUIÇÃO','AJUSTE','')
                                                    )
                        and ff.ID_CONTRIBUICAO not in (491,492)
                left join portal.dbo.participante_tipo_contribuicao ptc
                    on ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO
                left join CARGO c
                    on c.ID_CARGO = pe.ID_CARGO
                    AND c.ID_EMP = pe.ID_EMP
                left join LOCAL LE
                    on le.ID_LOCAL = pe.id_local
        WHERE 1 = 1
              AND pe.IC_EMP_PATROC = 'N'
              AND pe.IC_PARTICIPANTE = 'S'	  
              )a
    where 1=1
    and a.NR_ANO_REF = 2025
    and a.NR_MES_REF in (4)

    group by CASE
            WHEN a.CARGO LIKE 'ANALISTA%' THEN 'Analistas'
            WHEN a.CARGO LIKE 'TÉCNICO%' THEN 'Técnicos'
            WHEN a.CARGO LIKE 'AUXILIAR%' THEN 'Auxiliar'
            else 'Juizes e membros'
        END
)
SELECT 
    CARGO,
	CAST(
        ROUND(
            (TOTAL_CONTRIBUICAO * 100.0) / SUM(TOTAL_CONTRIBUICAO) OVER(), 
            2
        ) AS DECIMAL(10,2)
    ) AS REPRESENTATIVIDADE_DA_CONTRIBUIÇÃO,
	 CASE 
        WHEN QUANTIDADE_PARTICIPANTES > 0 THEN 
            CAST(
                ROUND(TOTAL_CONTRIBUICAO / QUANTIDADE_PARTICIPANTES, 2) 
                AS DECIMAL(15,2)
            )
        ELSE 0 
    END AS CONTRIBUICAO_MEDIA,
    QUANTIDADE_PARTICIPANTES,
    CAST(
        ROUND(
            (QUANTIDADE_PARTICIPANTES * 100.0) / SUM(QUANTIDADE_PARTICIPANTES) OVER(), 
            2
        ) AS DECIMAL(10,2)
    ) AS REPRESENTATIVIDADE_DOS_PARTICIPANTES,
    TOTAL_CONTRIBUICAO
FROM dados_agrupados
ORDER BY CARGO ASC;
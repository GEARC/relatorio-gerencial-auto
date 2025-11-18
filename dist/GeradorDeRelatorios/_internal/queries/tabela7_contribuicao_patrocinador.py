# queries/tabela7_contribuicao_patrocinador.py

import calendar
def gerar_query(ano, mes):
    """
    Gera a query completa e dinâmica para a Tabela 7 (Contribuições por Patrocinador).
    """
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_limite = f"'{ano}/{mes:02d}/{ultimo_dia}'"
    return f"""
    SELECT 
    mes.EMPRESA,
    mes.CONTRIB_MES AS contribuicao_no_mes,
    FORMAT((mes.CONTRIB_MES * 100.0 / SUM(mes.CONTRIB_MES) OVER ()), 'N2', 'pt-BR') + ' %' AS REPRESENTATIVIDADE_MES_PERC,
    total.CONTRIB_TOTAL,
    FORMAT((CAST(REPLACE(total.CONTRIB_TOTAL, ',', '.') AS MONEY) * 100.0 / SUM(CAST(REPLACE(total.CONTRIB_TOTAL, ',', '.') AS MONEY)) OVER ()), 'N2', 'pt-BR') + ' %' AS REPRESENTATIVIDADE_TOTAL_PERC
FROM (
    SELECT DISTINCT 
        a.EMPRESA,
        ISNULL(CAST(SUM(a.CONTRIB_PARTICIPANTE) + SUM(a.CONTRIB_PATROCINADOR) AS MONEY), 0) AS CONTRIB_MES
    FROM (
        SELECT  
            emp.sg_pessoa AS EMPRESA,
            pc.NM_CATEGORIA,
            ps.nm_situacao AS situac_plano,
            ff.NR_MES_REF,
            ff.NR_ANO_REF,
            ff.VL_CONTRIB AS CONTRIB_PARTICIPANTE,
            0 AS CONTRIB_PATROCINADOR
        FROM pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa 
                AND he.id_emp = pe.id_emp 
                AND he.nr_ano_ref = (
                    SELECT MAX(he1.nr_ano_ref) 
                    FROM hist_empresa he1 
                    WHERE he1.id_pessoa = he.id_pessoa
                )
                AND he.nr_mes_ref = (
                    SELECT MAX(he1.nr_mes_ref) 
                    FROM hist_empresa he1 
                    WHERE he1.id_pessoa = he.id_pessoa 
                        AND he1.nr_ano_ref = (
                            SELECT MAX(he2.nr_ano_ref) 
                            FROM hist_empresa he2 
                            WHERE he2.id_pessoa = he.id_pessoa
                        )
                )
            LEFT JOIN empresa_situacao es ON he.id_sit_emp = es.id_sit_emp 
                AND he.id_emp = es.id_emp
            LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp
            LEFT JOIN (
                SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa 
                FROM pessoa a1 
                WHERE a1.ic_emp_patroc = 'S'
            ) emp ON emp.id_pessoa = ep.id_pessoa_emp
            LEFT JOIN plano_participante pp ON pp.id_pessoa = pe.id_pessoa
            LEFT JOIN hist_plano_participante hpp ON hpp.id_pessoa = pe.id_pessoa 
                AND GETDATE() BETWEEN hpp.dt_ini AND ISNULL(hpp.dt_fim, GETDATE() + 1)
            LEFT JOIN plano_situacao ps ON ps.id_situacao = hpp.id_situacao
            LEFT JOIN PLANO_CATEGORIA pc ON pc.ID_CATEGORIA = hpp.ID_CATEGORIA
            LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA
                AND ff.ID_CONTRIBUICAO IN (
                    SELECT ptc.ID_CONTRIBUICAO_TRUST
                    FROM portal.dbo.participante_tipo_contribuicao ptc
                    WHERE ptc.mantenedor_consolidado = 'PARTICIPANTE'
                        AND ptc.movimentacao IN ('CONTRIBUIÇÃO', 'AJUSTE', '')
                )
                AND ff.ID_CONTRIBUICAO NOT IN (491, 492)
                AND ff.NR_ANO_REF = {ano}
                AND ff.NR_MES_REF IN ({mes})
        WHERE pe.IC_EMP_PATROC = 'N'
            AND pe.IC_PARTICIPANTE = 'S'

        UNION ALL
        SELECT  
            emp.sg_pessoa AS EMPRESA,
            pc.NM_CATEGORIA,
            ps.nm_situacao AS situac_plano,
            ff.NR_MES_REF,
            ff.NR_ANO_REF,
            0 AS CONTRIB_PARTICIPANTE,
            ff.VL_CONTRIB AS CONTRIB_PATROCINADOR
        FROM pessoa pe 
            LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa 
                AND he.id_emp = pe.id_emp 
                AND he.nr_ano_ref = (
                    SELECT MAX(he1.nr_ano_ref) 
                    FROM hist_empresa he1 
                    WHERE he1.id_pessoa = he.id_pessoa
                )
                AND he.nr_mes_ref = (
                    SELECT MAX(he1.nr_mes_ref) 
                    FROM hist_empresa he1 
                    WHERE he1.id_pessoa = he.id_pessoa 
                        AND he1.nr_ano_ref = (
                            SELECT MAX(he2.nr_ano_ref) 
                            FROM hist_empresa he2 
                            WHERE he2.id_pessoa = he.id_pessoa
                        )
                )
            LEFT JOIN empresa_situacao es ON he.id_sit_emp = es.id_sit_emp 
                AND he.id_emp = es.id_emp
            LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp
            LEFT JOIN (
                SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa 
                FROM pessoa a1 
                WHERE a1.ic_emp_patroc = 'S'
            ) emp ON emp.id_pessoa = ep.id_pessoa_emp
            LEFT JOIN plano_participante pp ON pp.id_pessoa = pe.id_pessoa
            LEFT JOIN hist_plano_participante hpp ON hpp.id_pessoa = pe.id_pessoa 
                AND GETDATE() BETWEEN hpp.dt_ini AND ISNULL(hpp.dt_fim, GETDATE() + 1)
            LEFT JOIN plano_situacao ps ON ps.id_situacao = hpp.id_situacao
            LEFT JOIN PLANO_CATEGORIA pc ON pc.ID_CATEGORIA = hpp.ID_CATEGORIA
            LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA
                AND ff.ID_CONTRIBUICAO IN (
                    SELECT ptc.ID_CONTRIBUICAO_TRUST
                    FROM portal.dbo.participante_tipo_contribuicao ptc
                    WHERE ptc.mantenedor_consolidado = 'PATROCINADOR'
                        AND ptc.movimentacao IN ('CONTRIBUIÇÃO', 'AJUSTE', '')
                )
                AND ff.ID_CONTRIBUICAO NOT IN (491, 492)
                AND ff.NR_ANO_REF = {ano}
                AND ff.NR_MES_REF IN ({mes})
        WHERE pe.IC_EMP_PATROC = 'N'
            AND pe.IC_PARTICIPANTE = 'S'
    ) a
    GROUP BY a.EMPRESA
) mes

INNER JOIN (
    SELECT 
        total.empresa AS EMPRESA,
        REPLACE(SUM(total.valor), '.', ',') AS CONTRIB_TOTAL
    FROM (
        SELECT 
            geral.empresa,
            REPLACE(SUM(geral.QUANTIDADE_COTAS), '.', ',') AS QUANTIDADE_COTAS,
            CAST(SUM(geral.VL_ATUALIZADO) AS MONEY) AS valor
        FROM (
            SELECT  
                hc.ID_PESSOA,
                cp.NM_CONTA,
                CC.ID_CONTRIBUICAO AS COD_CONTRIBUICAO,
                co.NM_CONTRIBUICAO,
                CC.ID_CONTA,
                ep.ID_EMP,
                emp.sg_pessoa AS empresa,
                CASE 
                    WHEN ppp.ID_PERFIL = 3 THEN 'COTA'
                    WHEN ppp.ID_PERFIL = 4 THEN 'COTAFCBE'
                    WHEN ppp.ID_PERFIL = 5 THEN 'CT-2040'
                    WHEN ppp.ID_PERFIL = 6 THEN 'CT-2050'
                    WHEN ppp.ID_PERFIL = 7 THEN 'CT-PROT'
                END AS PERFIL,
                HC.ID_INDEXADOR AS INDEXADOR,
                (HC.QT_COTA + HC.QT_COTA_ISENTO) AS QUANTIDADE_COTAS,
                (HC.QT_COTA + HC.QT_COTA_ISENTO) * (
                    SELECT iv.vl_indexador 
                    FROM INDEXADOR_VALOR iv
                    WHERE iv.ID_INDEXADOR = CASE 
                        WHEN ppp.ID_PERFIL = 3 THEN 'COTA'
                        WHEN ppp.ID_PERFIL = 4 THEN 'COTAFCBE'
                        WHEN ppp.ID_PERFIL = 5 THEN 'CT-2040'
                        WHEN ppp.ID_PERFIL = 6 THEN 'CT-2050'
                        WHEN ppp.ID_PERFIL = 7 THEN 'CT-PROT'
                    END
                    AND iv.DT_INDEXADOR = (
                        SELECT MAX(iv1.dt_indexador)
                        FROM INDEXADOR_VALOR iv1
                        WHERE iv1.ID_INDEXADOR = iv.ID_INDEXADOR
                            AND CONCAT(YEAR(iv1.DT_INDEXADOR), FORMAT(MONTH(iv1.DT_INDEXADOR), '00')) <= '{ano}{mes:02d}'
                    ) 
                ) AS VL_ATUALIZADO
            FROM HIST_CONTRIBUICAO HC
                LEFT JOIN PESSOA pe ON hc.ID_PESSOA = pe.ID_PESSOA
                LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp
                LEFT JOIN (
                    SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa 
                    FROM pessoa a1 
                    WHERE a1.ic_emp_patroc = 'S'
                ) emp ON emp.id_pessoa = ep.id_pessoa_emp
                LEFT JOIN WEB_CONTRIBUICAO_APROPRIACAO WEB ON WEB.ID_PESSOA = HC.ID_PESSOA
                    AND WEB.ID_CONTRIBUICAO = HC.ID_CONTRIBUICAO
                    AND WEB.ID_ORIGEM = HC.ID_ORIGEM
                    AND WEB.NR_ANO_COMP = HC.NR_ANO_COMP
                    AND WEB.NR_MES_COMP = HC.NR_MES_COMP
                    AND WEB.NR_ANO_REF = HC.NR_ANO_REF
                    AND WEB.NR_MES_REF = HC.NR_MES_REF
                INNER JOIN CONTA_CONTRIBUICAO CC ON HC.ID_CONTRIBUICAO = CC.ID_CONTRIBUICAO
                INNER JOIN CONTA_PREVIDENCIAL CP ON CP.ID_CONTA = CC.ID_CONTA
                INNER JOIN PERFIL_PLANO_PARTICIPANTE ppp ON ppp.ID_PESSOA = hc.ID_PESSOA
                    AND ppp.DT_VIGENCIA = (
                        SELECT MAX(ppp1.DT_VIGENCIA) 
                        FROM PERFIL_PLANO_PARTICIPANTE ppp1 
                        WHERE ppp1.ID_PESSOA = ppp.ID_PESSOA
                    )
                INNER JOIN CONTRIBUICAO CO ON HC.ID_CONTRIBUICAO = CO.ID_CONTRIBUICAO
                INNER JOIN CONFIG_PERFIL PER ON HC.ID_PERFIL = PER.ID_PERFIL
                INNER JOIN ORIGEM_LANCAMENTO OL ON HC.ID_ORIGEM = OL.ID_ORIGEM
            WHERE CONCAT(hc.NR_ANO_REF, FORMAT(hc.NR_MES_REF, '00')) <=  '{ano}{mes:02d}'
                AND CC.ID_CONTA IN (1, 2, 7, 8, 9, 10, 12, 13, 21, 22, 23, 24) 
        ) GERAL
        GROUP BY geral.empresa

        UNION ALL

        SELECT 
            geral.empresa,
            REPLACE(SUM(geral.QUANTIDADE_COTAS), '.', ',') AS QUANTIDADE_COTAS,
            CAST(SUM(geral.VL_ATUALIZADO) AS MONEY) AS valor
        FROM (
            SELECT  
                hc.ID_PESSOA,
                cp.NM_CONTA,
                CC.ID_CONTRIBUICAO AS COD_CONTRIBUICAO,
                co.NM_CONTRIBUICAO,
                CC.ID_CONTA,
                ep.ID_EMP,
                emp.sg_pessoa AS empresa,
                CASE 
                    WHEN ppp.ID_PERFIL = 3 THEN 'COTA'
                    WHEN ppp.ID_PERFIL = 4 THEN 'COTAFCBE'
                    WHEN ppp.ID_PERFIL = 5 THEN 'CT-2040'
                    WHEN ppp.ID_PERFIL = 6 THEN 'CT-2050'
                    WHEN ppp.ID_PERFIL = 7 THEN 'CT-PROT'
                END AS PERFIL,
                HC.ID_INDEXADOR AS INDEXADOR,
                (HC.QT_COTA + HC.QT_COTA_ISENTO) AS QUANTIDADE_COTAS,
                (HC.QT_COTA + HC.QT_COTA_ISENTO) * (
                    SELECT iv.vl_indexador 
                    FROM INDEXADOR_VALOR iv
                    WHERE iv.ID_INDEXADOR = 'COTAFCBE'
                        AND iv.DT_INDEXADOR = (
                            SELECT MAX(iv1.dt_indexador)
                            FROM INDEXADOR_VALOR iv1
                            WHERE iv1.ID_INDEXADOR = iv.ID_INDEXADOR
                                AND CONCAT(YEAR(iv1.DT_INDEXADOR), FORMAT(MONTH(iv1.DT_INDEXADOR), '00')) <= '{ano}{mes:02d}'
                        ) 
                ) AS VL_ATUALIZADO
            FROM HIST_CONTRIBUICAO HC
                LEFT JOIN PESSOA pe ON hc.ID_PESSOA = pe.ID_PESSOA
                LEFT JOIN empresa ep ON pe.id_emp = ep.id_emp
                LEFT JOIN (
                    SELECT a1.id_pessoa, a1.id_emp, a1.sg_pessoa, a1.nm_pessoa 
                    FROM pessoa a1 
                    WHERE a1.ic_emp_patroc = 'S'
                ) emp ON emp.id_pessoa = ep.id_pessoa_emp
                LEFT JOIN WEB_CONTRIBUICAO_APROPRIACAO WEB ON WEB.ID_PESSOA = HC.ID_PESSOA
                    AND WEB.ID_CONTRIBUICAO = HC.ID_CONTRIBUICAO
                    AND WEB.ID_ORIGEM = HC.ID_ORIGEM
                    AND WEB.NR_ANO_COMP = HC.NR_ANO_COMP
                    AND WEB.NR_MES_COMP = HC.NR_MES_COMP
                    AND WEB.NR_ANO_REF = HC.NR_ANO_REF
                    AND WEB.NR_MES_REF = HC.NR_MES_REF
                INNER JOIN CONTA_CONTRIBUICAO CC ON HC.ID_CONTRIBUICAO = CC.ID_CONTRIBUICAO
                INNER JOIN CONTA_PREVIDENCIAL CP ON CP.ID_CONTA = CC.ID_CONTA
                INNER JOIN PERFIL_PLANO_PARTICIPANTE ppp ON ppp.ID_PESSOA = hc.ID_PESSOA
                    AND ppp.DT_VIGENCIA = (
                        SELECT MAX(ppp1.DT_VIGENCIA) 
                        FROM PERFIL_PLANO_PARTICIPANTE ppp1 
                        WHERE ppp1.ID_PESSOA = ppp.ID_PESSOA
                    )
                INNER JOIN CONTRIBUICAO CO ON HC.ID_CONTRIBUICAO = CO.ID_CONTRIBUICAO
                INNER JOIN CONFIG_PERFIL PER ON HC.ID_PERFIL = PER.ID_PERFIL
                INNER JOIN ORIGEM_LANCAMENTO OL ON HC.ID_ORIGEM = OL.ID_ORIGEM
            WHERE CONCAT(hc.NR_ANO_REF, FORMAT(hc.NR_MES_REF, '00')) <=  '{ano}{mes:02d}'
                AND CC.ID_CONTA IN (3, 4, 20) 
        ) GERAL
        GROUP BY geral.empresa
    ) total
    GROUP BY total.empresa
) total ON mes.EMPRESA = total.EMPRESA

ORDER BY mes.CONTRIB_MES DESC;	
    """
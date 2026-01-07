SELECT 
    RAMO,
    FORMAT(
        (SUM(CONTRIB_PARTICIPANTE + CONTRIB_PATROCINADOR) * 100.0) / 
        (SELECT SUM(CONTRIB_PARTICIPANTE + CONTRIB_PATROCINADOR) 
         FROM (
            SELECT 
				ff.NR_MES_COMP,
				ff.NR_ANO_COMP,
                ff.NR_MES_REF,
                ff.NR_ANO_REF,
                ff.VL_CONTRIB AS CONTRIB_PARTICIPANTE,
                0 AS CONTRIB_PATROCINADOR,
                le.NM_LOCAL AS RAMO,
                pe.ID_PESSOA,
                ff.ID_CONTRIBUICAO
            FROM pessoa pe 
                LEFT JOIN hist_contribuicao ff
                    ON ff.id_pessoa = pe.ID_PESSOA
                    AND ff.ID_CONTRIBUICAO IN (
                        SELECT ptc.ID_CONTRIBUICAO_TRUST
                        FROM portal.dbo.participante_tipo_contribuicao ptc
                        WHERE ptc.mantenedor_consolidado = 'PARTICIPANTE'
                        AND ptc.movimentacao IN ('CONTRIBUI플O','AJUSTE','')
                    )
                    AND ff.ID_CONTRIBUICAO NOT IN (491,492)
                LEFT JOIN LOCAL le
                    ON le.ID_LOCAL = pe.id_local
            WHERE pe.IC_EMP_PATROC = 'N'
                AND pe.IC_PARTICIPANTE = 'S'
                AND ff.VL_CONTRIB IS NOT NULL
            UNION ALL
            SELECT 
				ff.NR_MES_COMP,
				ff.NR_ANO_COMP,
                ff.NR_MES_REF,
                ff.NR_ANO_REF,
                0 AS CONTRIB_PARTICIPANTE,
                ff.VL_CONTRIB AS CONTRIB_PATROCINADOR, 
                le.NM_LOCAL AS RAMO,
                pe.ID_PESSOA,
                ff.ID_CONTRIBUICAO
            FROM pessoa pe 
                LEFT JOIN hist_contribuicao ff
                    ON ff.id_pessoa = pe.ID_PESSOA
                    AND ff.ID_CONTRIBUICAO IN (
                        SELECT ptc.ID_CONTRIBUICAO_TRUST
                        FROM portal.dbo.participante_tipo_contribuicao ptc
                        WHERE ptc.mantenedor_consolidado = 'PATROCINADOR'
                        AND ptc.movimentacao IN ('CONTRIBUI플O','AJUSTE','')
                    )
                    AND ff.ID_CONTRIBUICAO NOT IN (491,492)
                LEFT JOIN LOCAL le
                    ON le.ID_LOCAL = pe.id_local
            WHERE pe.IC_EMP_PATROC = 'N'
                AND pe.IC_PARTICIPANTE = 'S'
                AND ff.VL_CONTRIB IS NOT NULL
        ) total_query
         WHERE  (NR_ANO_REF < 2025 AND  NR_MES_REF <=12) or (nr_ano_ref=2025 and NR_MES_REF <=4)
        ), 
        'N2'
    ) AS PERCENTUAL
FROM (
    SELECT 
		ff.NR_MES_COMP,
		ff.NR_ANO_COMP,
        ff.NR_MES_REF,
        ff.NR_ANO_REF,
        ff.VL_CONTRIB AS CONTRIB_PARTICIPANTE,
        0 AS CONTRIB_PATROCINADOR,
        le.NM_LOCAL AS RAMO,
        pe.ID_PESSOA,
        ff.ID_CONTRIBUICAO
    FROM pessoa pe 
        LEFT JOIN hist_contribuicao ff
            ON ff.id_pessoa = pe.ID_PESSOA
            AND ff.ID_CONTRIBUICAO IN (
                SELECT ptc.ID_CONTRIBUICAO_TRUST
                FROM portal.dbo.participante_tipo_contribuicao ptc
                WHERE ptc.mantenedor_consolidado = 'PARTICIPANTE'
                AND ptc.movimentacao IN ('CONTRIBUI플O','AJUSTE','')
            )
            AND ff.ID_CONTRIBUICAO NOT IN (491,492)
        LEFT JOIN LOCAL le
            ON le.ID_LOCAL = pe.id_local
    WHERE pe.IC_EMP_PATROC = 'N'
        AND pe.IC_PARTICIPANTE = 'S'
        AND ff.VL_CONTRIB IS NOT NULL
    UNION ALL
    SELECT 
		ff.NR_MES_COMP,
		ff.NR_ANO_COMP,
        ff.NR_MES_REF,
        ff.NR_ANO_REF,
        0 AS CONTRIB_PARTICIPANTE,
        ff.VL_CONTRIB AS CONTRIB_PATROCINADOR, 
        le.NM_LOCAL AS RAMO,
        pe.ID_PESSOA,
        ff.ID_CONTRIBUICAO
    FROM pessoa pe 
        LEFT JOIN hist_contribuicao ff
            ON ff.id_pessoa = pe.ID_PESSOA
            AND ff.ID_CONTRIBUICAO IN (
                SELECT ptc.ID_CONTRIBUICAO_TRUST
                FROM portal.dbo.participante_tipo_contribuicao ptc
                WHERE ptc.mantenedor_consolidado = 'PATROCINADOR'
                AND ptc.movimentacao IN ('CONTRIBUI플O','AJUSTE','')
            )
            AND ff.ID_CONTRIBUICAO NOT IN (491,492)
        LEFT JOIN LOCAL le
            ON le.ID_LOCAL = pe.id_local
    WHERE pe.IC_EMP_PATROC = 'N'
        AND pe.IC_PARTICIPANTE = 'S'
        AND ff.VL_CONTRIB IS NOT NULL
) a
WHERE (NR_ANO_REF < 2025 AND  NR_MES_REF <=12) or (nr_ano_ref=2025 and NR_MES_REF <=4)
GROUP BY RAMO
ORDER BY SUM(CONTRIB_PARTICIPANTE + CONTRIB_PATROCINADOR) DESC;
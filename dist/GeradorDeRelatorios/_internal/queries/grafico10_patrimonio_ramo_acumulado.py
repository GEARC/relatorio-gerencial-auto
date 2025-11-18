def gerar_query(ano, mes):

    return f"""
    SELECT 
        RAMO,
        SUM(CONTRIB_PARTICIPANTE + CONTRIB_PATROCINADOR) AS Valor
    FROM (
        -- Sua subquery gigante com UNION ALL para buscar todas as contribuições
        SELECT 
            ff.NR_MES_REF, ff.NR_ANO_REF,
            ff.VL_CONTRIB AS CONTRIB_PARTICIPANTE, 0 AS CONTRIB_PATROCINADOR,
            le.NM_LOCAL AS RAMO
        FROM pessoa pe 
        LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA
            AND ff.ID_CONTRIBUICAO IN (SELECT ptc.ID_CONTRIBUICAO_TRUST FROM portal.dbo.participante_tipo_contribuicao ptc WHERE ptc.mantenedor_consolidado = 'PARTICIPANTE' AND ptc.movimentacao IN ('CONTRIBUIÇÃO','AJUSTE',''))
            AND ff.ID_CONTRIBUICAO NOT IN (491,492)
        LEFT JOIN LOCAL le ON le.ID_LOCAL = pe.id_local
        WHERE pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S' AND ff.VL_CONTRIB IS NOT NULL
        
        UNION ALL
        
        SELECT 
            ff.NR_MES_REF, ff.NR_ANO_REF,
            0 AS CONTRIB_PARTICIPANTE, ff.VL_CONTRIB AS CONTRIB_PATROCINADOR, 
            le.NM_LOCAL AS RAMO
        FROM pessoa pe 
        LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA
            AND ff.ID_CONTRIBUICAO IN (SELECT ptc.ID_CONTRIBUICAO_TRUST FROM portal.dbo.participante_tipo_contribuicao ptc WHERE ptc.mantenedor_consolidado = 'PATROCINADOR' AND ptc.movimentacao IN ('CONTRIBUIÇÃO','AJUSTE',''))
            AND ff.ID_CONTRIBUICAO NOT IN (491,492)
        LEFT JOIN LOCAL le ON le.ID_LOCAL = pe.id_local
        WHERE pe.IC_EMP_PATROC = 'N' AND pe.IC_PARTICIPANTE = 'S' AND ff.VL_CONTRIB IS NOT NULL
    ) a
    -- Filtro dinâmico para pegar tudo até a data de referência
    WHERE (NR_ANO_REF < {ano}) OR (NR_ANO_REF = {ano} AND NR_MES_REF <= {mes})
    GROUP BY RAMO
    ORDER BY SUM(CONTRIB_PARTICIPANTE + CONTRIB_PATROCINADOR) DESC;
    """
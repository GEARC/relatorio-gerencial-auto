def gerar_query(ano, mes):
    """Gera a query que detalha a origem (Patrocinado/Vinculado) para BPD e Autopatrocinado."""
    return f"""
    SELECT
        ISNULL(op.TIPO_ORIGEM, 'NÃO DEFINIDA') AS ORIGEM,
        CONCAT(YEAR(hpp.DT_INI), RIGHT('00' + CAST(MONTH(hpp.DT_INI) AS VARCHAR), 2)) AS ANO_MES,
        CASE
            WHEN ps.nm_situacao LIKE 'BPD%' THEN 'BPD'
            ELSE ps.nm_situacao
        END AS SITUACAO,
        COUNT(pe.id_pessoa) AS QTD
    FROM
        pessoa pe
        LEFT JOIN hist_plano_participante hpp ON hpp.id_pessoa = pe.id_pessoa
        LEFT JOIN plano_situacao ps ON ps.id_situacao = hpp.id_situacao
        LEFT JOIN (
            SELECT
                ID_PESSOA,
                CASE 
                    WHEN ID_SITUACAO = 1 THEN 'Patrocinado'
                    WHEN ID_SITUACAO = 2 THEN 'Vinculado'
                END AS TIPO_ORIGEM,
                ROW_NUMBER() OVER(PARTITION BY ID_PESSOA ORDER BY DT_INI DESC) as rn
            FROM
                hist_plano_participante
            WHERE
                ID_SITUACAO IN (1, 2)
        ) AS op ON op.id_pessoa = pe.id_pessoa AND op.rn = 1
    WHERE
        pe.IC_EMP_PATROC = 'N'
        AND pe.IC_PARTICIPANTE = 'S'
        AND ps.ID_SITUACAO IN (6, 7, 28) -- IDs para Autopatrocinado e BPD
        AND YEAR(hpp.DT_INI) = {ano} AND MONTH(hpp.DT_INI) <= {mes}
    GROUP BY
        op.TIPO_ORIGEM,
        YEAR(hpp.DT_INI),
        MONTH(hpp.DT_INI),
        CASE
            WHEN ps.nm_situacao LIKE 'BPD%' THEN 'BPD'
            ELSE ps.nm_situacao
        END
    ORDER BY
        ANO_MES DESC,
        ORIGEM;
    """
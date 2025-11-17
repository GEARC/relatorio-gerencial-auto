-- Este arquivo contém todas as queries SQL utilizadas no projeto 'relatorio-gerencial-auto'.
-- Para queries dinâmicas (geradas por funções Python), um exemplo com ano=2023 e mês=1 é fornecido.
-- Para queries estáticas com substituição de parâmetros, o placeholder original é mantido com um comentário.


-- Query from queries/tabela1_evolucao_adesoes.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    FORMAT(DATA_REFERENCIA, 'MMM/yyyy', 'pt-BR') AS "Mês/Ano",
    SUM(CASE WHEN TIPO_MOVIMENTACAO = 'ADESAO' THEN 1 ELSE 0 END) AS Adesões,
    SUM(CASE WHEN TIPO_MOVIMENTACAO = 'CANCELAMENTO' THEN 1 ELSE 0 END) AS Cancelamentos,
    SUM(CASE WHEN TIPO_MOVIMENTACAO = 'ADESAO' THEN 1 ELSE -1 END) AS Saldo,
    COUNT(ID_PESSOA) AS Total
FROM (
    -- Subquery para obter as adesões e cancelamentos
    SELECT
        p.ID_PESSOA,
        CASE
            WHEN ps.ID_SITUACAO IN (1, 2, 5, 6, 7, 10) THEN 'ADESAO'
            WHEN ps.ID_SITUACAO IN (3, 4, 8, 9) THEN 'CANCELAMENTO'
            ELSE 'OUTRO'
        END AS TIPO_MOVIMENTACAO,
        DATEFROMPARTS(epp.NR_ANO_REF, epp.NR_MES_REF, 1) AS DATA_REFERENCIA
    FROM ENCERRAMENTO_PLANO_PARTIC epp
    JOIN PESSOA p ON epp.ID_PESSOA = p.ID_PESSOA
    JOIN PLANO_SITUACAO ps ON epp.ID_SITUACAO = ps.ID_SITUACAO
    WHERE epp.NR_ANO_REF <= 2023 AND epp.NR_MES_REF <= 1
) AS sub
GROUP BY DATA_REFERENCIA
ORDER BY DATA_REFERENCIA;


-- Query from queries/tabela1_evolucao_detalhes.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    CASE
        WHEN ps.ID_SITUACAO IN (1, 2, 5, 6, 7, 10) THEN 'ADESAO'
        WHEN ps.ID_SITUACAO IN (3, 4, 8, 9) THEN 'CANCELAMENTO'
        ELSE 'OUTRO'
    END AS TIPO_MOVIMENTACAO,
    ps.DS_SITUACAO AS Detalhe,
    COUNT(epp.ID_PESSOA) AS Quantidade
FROM ENCERRAMENTO_PLANO_PARTIC epp
JOIN PESSOA p ON epp.ID_PESSOA = p.ID_PESSOA
JOIN PLANO_SITUACAO ps ON epp.ID_SITUACAO = ps.ID_SITUACAO
WHERE epp.NR_ANO_REF = 2023 AND epp.NR_MES_REF = 1
GROUP BY
    CASE
        WHEN ps.ID_SITUACAO IN (1, 2, 5, 6, 7, 10) THEN 'ADESAO'
        WHEN ps.ID_SITUACAO IN (3, 4, 8, 9) THEN 'CANCELAMENTO'
        ELSE 'OUTRO'
    END,
    ps.DS_SITUACAO
ORDER BY TIPO_MOVIMENTACAO, Quantidade DESC;


-- Query from queries/tabela_distribuicao_sexo.py (Static with runtime parameter replacement)
-- The '?' placeholder is replaced by a dynamic value like '202301' at runtime.
SELECT
    pe.IC_SEXO AS SEXO,
    COUNT(e.ID_PESSOA) AS QTD
FROM
    ENCERRAMENTO_PLANO_PARTIC e
JOIN
    PESSOA pe ON e.ID_PESSOA = pe.ID_PESSOA
WHERE
    e.NR_ANO_REF = 2023 AND e.NR_MES_REF = 1
    AND e.ID_SITUACAO IN (2,5,6,7,1,10)
GROUP BY
    pe.IC_SEXO
ORDER BY
    QTD DESC;


-- Query from queries/tabela2_distribuicao_cargos.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    CASE
        WHEN pc.DS_CARGO LIKE '%JUIZ%' OR pc.DS_CARGO LIKE '%MEMBRO%' THEN 'JUÍZES E MEMBROS'
        WHEN pc.DS_CARGO LIKE '%ANALISTA%' THEN 'ANALISTAS'
        WHEN pc.DS_CARGO LIKE '%AUXILIAR%' THEN 'AUXILIARES'
        WHEN pc.DS_CARGO LIKE '%TÉCNICO%' THEN 'TÉCNICOS'
        ELSE 'OUTROS'
    END AS CARGO,
    COUNT(epp.ID_PESSOA) AS QUANTIDADE
FROM ENCERRAMENTO_PLANO_PARTIC epp
JOIN PESSOA p ON epp.ID_PESSOA = p.ID_PESSOA
JOIN PESSOA_CARGO pc ON p.ID_PESSOA = pc.ID_PESSOA
WHERE epp.NR_ANO_REF = 2023 AND epp.NR_MES_REF = 1
AND epp.ID_SITUACAO IN (2,5,6,7,1,10)
GROUP BY
    CASE
        WHEN pc.DS_CARGO LIKE '%JUIZ%' OR pc.DS_CARGO LIKE '%MEMBRO%' THEN 'JUÍZES E MEMBROS'
        WHEN pc.DS_CARGO LIKE '%ANALISTA%' THEN 'ANALISTAS'
        WHEN pc.DS_CARGO LIKE '%AUXILIAR%' THEN 'AUXILIARES'
        WHEN pc.DS_CARGO LIKE '%TÉCNICO%' THEN 'TÉCNICOS'
        ELSE 'OUTROS'
    END
ORDER BY QUANTIDADE DESC;


-- Query from queries/grafico1_piramide_etaria.py (Static with runtime parameter replacement)
-- The '?' placeholder is replaced by a dynamic value like '202301' at runtime.
SELECT
    CASE
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 21 AND 23 THEN '21 a 23'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 24 AND 26 THEN '24 a 26'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 27 AND 29 THEN '27 a 29'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 30 AND 32 THEN '30 a 32'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 33 AND 35 THEN '33 a 35'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 36 AND 38 THEN '36 a 38'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 39 AND 41 THEN '39 a 41'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 42 AND 44 THEN '42 a 44'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 45 AND 47 THEN '45 a 47'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 48 AND 50 THEN '48 a 50'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 51 AND 53 THEN '51 a 53'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 54 AND 56 THEN '54 a 56'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 57 AND 59 THEN '57 a 59'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 60 AND 62 THEN '60 a 62'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 63 AND 65 THEN '63 a 65'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 66 AND 68 THEN '66 a 68'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 69 AND 71 THEN '69 a 71'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 72 AND 74 THEN '72 a 74'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 75 AND 77 THEN '75 a 77'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 79 AND 81 THEN '79 a 81'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 82 AND 84 THEN '82 a 84'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 85 AND 87 THEN '85 a 87'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 88 AND 90 THEN '88 a 90'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 91 AND 93 THEN '91 a 93'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 94 AND 96 THEN '94 a 96'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 97 AND 99 THEN '97 a 99'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 100 AND 102 THEN '100 a 102'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 103 AND 105 THEN '103 a 105'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) > 105 THEN 'Maior que 105'
        ELSE 'Não Informado'
    END AS Faixa_Etaria,
    pe.IC_SEXO AS SEXO,
    COUNT(e.ID_PESSOA) AS QTD
FROM
    ENCERRAMENTO_PLANO_PARTIC e
JOIN
    PESSOA pe ON e.ID_PESSOA = pe.ID_PESSOA
WHERE
    e.NR_ANO_REF = 2023 AND e.NR_MES_REF = 01
    AND e.ID_SITUACAO IN (2,5,6,7,1,10)
GROUP BY
    CASE
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 21 AND 23 THEN '21 a 23'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 24 AND 26 THEN '24 a 26'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 27 AND 29 THEN '27 a 29'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 30 AND 32 THEN '30 a 32'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 33 AND 35 THEN '33 a 35'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 36 AND 38 THEN '36 a 38'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 39 AND 41 THEN '39 a 41'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 42 AND 44 THEN '42 a 44'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 45 AND 47 THEN '45 a 47'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 48 AND 50 THEN '48 a 50'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 51 AND 53 THEN '51 a 53'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 54 AND 56 THEN '54 a 56'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 57 AND 59 THEN '57 a 59'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 60 AND 62 THEN '60 a 62'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 63 AND 65 THEN '63 a 65'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 66 AND 68 THEN '66 a 68'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 69 AND 71 THEN '69 a 71'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 72 AND 74 THEN '72 a 74'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 75 AND 77 THEN '75 a 77'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 79 AND 81 THEN '79 a 81'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 82 AND 84 THEN '82 a 84'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 85 AND 87 THEN '85 a 87'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 88 AND 90 THEN '88 a 90'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 91 AND 93 THEN '91 a 93'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 94 AND 96 THEN '94 a 96'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 97 AND 99 THEN '97 a 99'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 100 AND 102 THEN '100 a 102'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) BETWEEN 103 AND 105 THEN '103 a 105'
        WHEN DATEDIFF(year, pe.DT_NASCIMENTO, GETDATE()) > 105 THEN 'Maior que 105'
        ELSE 'Não Informado'
    END,
    pe.IC_SEXO
ORDER BY Faixa_Etaria, SEXO;


-- Query from queries/grafico2_adesao_ramo_mes.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    LC.NM_LOCAL AS Ramo,
    COUNT(e.ID_PESSOA) AS Quantidade
FROM
    ENCERRAMENTO_PLANO_PARTIC e
JOIN
    PESSOA pe ON e.ID_PESSOA = pe.ID_PESSOA
JOIN
    LOCAL LC ON pe.ID_LOCAL = LC.ID_LOCAL
WHERE
    e.NR_ANO_REF = 2023
    AND e.NR_MES_REF = 1
    AND e.ID_SITUACAO IN (1, 2, 5, 6, 7, 10) -- Apenas adesões
GROUP BY
    LC.NM_LOCAL
ORDER BY
    Quantidade DESC;


-- Query from queries/grafico3_adesao_ramo_acumulado.py (Dynamic - Example for ano=2023, mes=1)
select  LC.NM_LOCAL as Ramo, count(e.ID_PESSOA) as Quantidade
from  ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps,LOCAL lc,PESSOA PE
where 1=1
and e.ID_SITUACAO = ps.ID_SITUACAO
and pe.ID_PESSOA = e.ID_PESSOA
and PE.ID_LOCAL  = LC.ID_LOCAL
and e.NR_ANO_REF = 2023
and e.NR_MES_REF = 1
and e.ID_SITUACAO  in (2,5,6,7,1,10)
group by  LC.NM_LOCAL
ORDER BY
    Quantidade DESC;


-- Query from queries/tabela3_adesoes_patrocinador.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    e.NM_EMPRESA AS Patrocinador,
    COUNT(epp.ID_PESSOA) AS Adesões
FROM ENCERRAMENTO_PLANO_PARTIC epp
JOIN PESSOA p ON epp.ID_PESSOA = p.ID_PESSOA
JOIN EMPRESA e ON p.ID_EMPRESA = e.ID_EMPRESA
WHERE epp.NR_ANO_REF = 2023 AND epp.NR_MES_REF = 1
AND epp.ID_SITUACAO IN (1, 2, 5, 6, 7, 10)
GROUP BY e.NM_EMPRESA
ORDER BY Adesões DESC;


-- Query from queries/tabela4_arrecadacao_mes.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    'Mês Atual' AS Tipo,
    SUM(hc.VL_CONTRIB) AS CONTRIBUIÇÃO
FROM hist_contribuicao hc
WHERE hc.NR_ANO_REF = 2023 AND hc.NR_MES_REF = 1
AND hc.ID_CONTRIBUICAO IN (SELECT ID_CONTRIBUICAO_TRUST FROM portal.dbo.participante_tipo_contribuicao WHERE movimentacao IN ('CONTRIBUIÇÃO', 'AJUSTE'))
UNION ALL
SELECT
    'Outras Competências' AS Tipo,
    SUM(hc.VL_CONTRIB) AS CONTRIBUIÇÃO
FROM hist_contribuicao hc
WHERE (hc.NR_ANO_REF < 2023 OR (hc.NR_ANO_REF = 2023 AND hc.NR_MES_REF < 1))
AND hc.ID_CONTRIBUICAO IN (SELECT ID_CONTRIBUICAO_TRUST FROM portal.dbo.participante_tipo_contribuicao WHERE movimentacao IN ('CONTRIBUIÇÃO', 'AJUSTE'));


-- Query from queries/tabela5_arrecadacao_tipo.py (Dynamic - Example for ano=2023, mes=1)
WITH ArrecadacaoMesAtual AS (
    SELECT
        ptc.tipo_contribuicao AS Contribuicao,
        SUM(hc.VL_CONTRIB) AS Valor
    FROM hist_contribuicao hc
    JOIN portal.dbo.participante_tipo_contribuicao ptc ON hc.ID_CONTRIBUICAO = ptc.ID_CONTRIBUICAO_TRUST
    WHERE hc.NR_ANO_REF = 2023 AND hc.NR_MES_REF = 1
    GROUP BY ptc.tipo_contribuicao
),
ArrecadacaoMesAnterior AS (
    SELECT
        ptc.tipo_contribuicao AS Contribuicao,
        SUM(hc.VL_CONTRIB) AS Valor
    FROM hist_contribuicao hc
    JOIN portal.dbo.participante_tipo_contribuicao ptc ON hc.ID_CONTRIBUICAO = ptc.ID_CONTRIBUICAO_TRUST
    WHERE hc.NR_ANO_REF = CASE WHEN 1 = 1 THEN 2023 - 1 ELSE 2023 END AND hc.NR_MES_REF = CASE WHEN 1 = 1 THEN 12 ELSE 1 - 1 END
    GROUP BY ptc.tipo_contribuicao
)
SELECT
    COALESCE(a.Contribuicao, b.Contribuicao) AS Contribuicao,
    COALESCE(a.Valor, 0) AS mes_atual,
    COALESCE(b.Valor, 0) AS mes_passado
FROM ArrecadacaoMesAtual a
FULL OUTER JOIN ArrecadacaoMesAnterior b ON a.Contribuicao = b.Contribuicao
ORDER BY Contribuicao;


-- Query from queries/grafico4_tributacao_mes.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    pp.IC_TRIBUTACAO,
    COUNT(e.ID_PESSOA) AS Quantidade
FROM
    ENCERRAMENTO_PLANO_PARTIC e
JOIN
    PLANO_PARTICIPANTE pp ON e.ID_PESSOA = pp.ID_PESSOA
WHERE
    e.NR_ANO_REF = 2023
    AND e.NR_MES_REF = 1
    AND e.ID_SITUACAO IN (2,5,6,7,1,10)
GROUP BY
    pp.IC_TRIBUTACAO
ORDER BY
    Quantidade DESC;


-- Query from queries/grafico5_tributacao_acumulado.py (Dynamic - Example for ano=2023, mes=1)
select
    pp.IC_TRIBUTACAO,
    count(e.ID_PESSOA) as Quantidade
from
    ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps ,PLANO_PARTICIPANTE pp
where 1=1
    and e.NR_ANO_REF = 2023
    and e.NR_MES_REF = 1
    and e.ID_SITUACAO in (2,5,6,7,1,10)
    and e.ID_SITUACAO = ps.ID_SITUACAO
    and e.ID_PESSOA = pp.ID_PESSOA
group by
    pp.IC_TRIBUTACAO
order by
    Quantidade desc;


-- Query from queries/grafico6_percentual_contrib_mes.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    ps.DS_SITUACAO AS NM_SITUACAO,
    pp.PC_CONTRIBUICAO AS PERCENTUAL,
    COUNT(epp.ID_PESSOA) AS QTD
FROM ENCERRAMENTO_PLANO_PARTIC epp
JOIN PESSOA p ON epp.ID_PESSOA = p.ID_PESSOA
JOIN PLANO_PARTICIPANTE pp ON p.ID_PESSOA = pp.ID_PESSOA
JOIN PLANO_SITUACAO ps ON epp.ID_SITUACAO = ps.ID_SITUACAO
WHERE epp.NR_ANO_REF = 2023 AND epp.NR_MES_REF = 1
AND epp.ID_SITUACAO IN (2,5,6,7,1,10)
GROUP BY ps.DS_SITUACAO, pp.PC_CONTRIBUICAO
ORDER BY ps.DS_SITUACAO, pp.PC_CONTRIBUICAO;


-- Query from queries/grafico7_percentual_contrib_acumulado.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    ps.DS_SITUACAO AS NM_SITUACAO,
    pp.PC_CONTRIBUICAO AS PERCENTUAL,
    COUNT(epp.ID_PESSOA) AS QTD
FROM ENCERRAMENTO_PLANO_PARTIC epp
JOIN PESSOA p ON epp.ID_PESSOA = p.ID_PESSOA
JOIN PLANO_PARTICIPANTE pp ON p.ID_PESSOA = pp.ID_PESSOA
JOIN PLANO_SITUACAO ps ON epp.ID_SITUACAO = ps.ID_SITUACAO
WHERE epp.NR_ANO_REF <= 2023 AND epp.NR_MES_REF <= 1
AND epp.ID_SITUACAO IN (2,5,6,7,1,10)
GROUP BY ps.DS_SITUACAO, pp.PC_CONTRIBUICAO
ORDER BY ps.DS_SITUACAO, pp.PC_CONTRIBUICAO;


-- Query from queries/grafico8_contribuicao_paridade.py (Dynamic - Example for ano=2023, mes=1)
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
            AND ff.NR_ANO_REF = 2023 AND ff.NR_MES_REF = 1

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
            AND ff.NR_ANO_REF = 2023 AND ff.NR_MES_REF = 1
    ) a
)
-- CORREÇÃO: Retorna os valores como números e em linhas, formato ideal para o Python
SELECT 'PARTICIPANTE' AS Categoria, CONTRIBUICAO_PARTICIPANTE AS Valor FROM dados_detalhados
UNION ALL
SELECT 'PATROCINADOR' AS Categoria, CONTRIBUICAO_PATROCINADOR AS Valor FROM dados_detalhados;


-- Query from queries/tabela6_arrecadacao_cargo.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    CASE
        WHEN pc.DS_CARGO LIKE '%JUIZ%' OR pc.DS_CARGO LIKE '%MEMBRO%' THEN 'JUÍZES E MEMBROS'
        WHEN pc.DS_CARGO LIKE '%ANALISTA%' THEN 'ANALISTAS'
        WHEN pc.DS_CARGO LIKE '%AUXILIAR%' THEN 'AUXILIARES'
        WHEN pc.DS_CARGO LIKE '%TÉCNICO%' THEN 'TÉCNICOS'
        ELSE 'OUTROS'
    END AS CARGO,
    COUNT(DISTINCT p.ID_PESSOA) AS QTD_PARTICIPANTES,
    SUM(hc.VL_CONTRIB) AS VALOR_CONTRIBUICAO,
    AVG(hc.VL_CONTRIB) AS ContribuicaoMedia
FROM PESSOA p
JOIN PESSOA_CARGO pc ON p.ID_PESSOA = pc.ID_PESSOA
JOIN hist_contribuicao hc ON p.ID_PESSOA = hc.ID_PESSOA
WHERE hc.NR_ANO_REF = 2023 AND hc.NR_MES_REF = 1
AND hc.ID_CONTRIBUICAO IN (SELECT ID_CONTRIBUICAO_TRUST FROM portal.dbo.participante_tipo_contribuicao WHERE movimentacao IN ('CONTRIBUIÇÃO', 'AJUSTE'))
GROUP BY
    CASE
        WHEN pc.DS_CARGO LIKE '%JUIZ%' OR pc.DS_CARGO LIKE '%MEMBRO%' THEN 'JUÍZES E MEMBROS'
        WHEN pc.DS_CARGO LIKE '%ANALISTA%' THEN 'ANALISTAS'
        WHEN pc.DS_CARGO LIKE '%AUXILIAR%' THEN 'AUXILIARES'
        WHEN pc.DS_CARGO LIKE '%TÉCNICO%' THEN 'TÉCNICOS'
        ELSE 'OUTROS'
    END
ORDER BY VALOR_CONTRIBUICAO DESC;


-- Query from queries/grafico9_contribuicao_ramo_mes.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    l.NM_LOCAL AS Ramo,
    SUM(hc.VL_CONTRIB) AS Valor
FROM hist_contribuicao hc
JOIN PESSOA p ON hc.ID_PESSOA = p.ID_PESSOA
JOIN LOCAL l ON p.ID_LOCAL = l.ID_LOCAL
WHERE hc.NR_ANO_REF = 2023 AND hc.NR_MES_REF = 1
AND hc.ID_CONTRIBUICAO IN (SELECT ID_CONTRIBUICAO_TRUST FROM portal.dbo.participante_tipo_contribuicao WHERE movimentacao IN ('CONTRIBUIÇÃO', 'AJUSTE'))
GROUP BY l.NM_LOCAL
ORDER BY Valor DESC;


-- Query from queries/grafico10_patrimonio_ramo_acumulado.py (Dynamic - Example for ano=2023, mes=1)
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
WHERE (NR_ANO_REF < 2023) OR (NR_ANO_REF = 2023 AND NR_MES_REF <= 1)
GROUP BY RAMO
ORDER BY SUM(CONTRIB_PARTICIPANTE + CONTRIB_PATROCINADOR) DESC;


-- Query from queries/tabela7_contribuicao_patrocinador.py (Dynamic - Example for ano=2023, mes=1)
SELECT
    e.NM_EMPRESA AS EMPRESA,
    SUM(CASE WHEN ptc.mantenedor_consolidado = 'PARTICIPANTE' THEN hc.VL_CONTRIB ELSE 0 END) AS CONTRIB_PARTICIPANTE,
    SUM(CASE WHEN ptc.mantenedor_consolidado = 'PATROCINADOR' THEN hc.VL_CONTRIB ELSE 0 END) AS CONTRIB_PATROCINADOR,
    SUM(hc.VL_CONTRIB) AS CONTRIB_TOTAL
FROM hist_contribuicao hc
JOIN PESSOA p ON hc.ID_PESSOA = p.ID_PESSOA
JOIN EMPRESA e ON p.ID_EMPRESA = e.ID_EMPRESA
JOIN portal.dbo.participante_tipo_contribuicao ptc ON hc.ID_CONTRIBUICAO = ptc.ID_CONTRIBUICAO_TRUST
WHERE hc.NR_ANO_REF = 2023 AND hc.NR_MES_REF = 1
AND ptc.movimentacao IN ('CONTRIBUIÇÃO', 'AJUSTE')
GROUP BY e.NM_EMPRESA
ORDER BY CONTRIB_TOTAL DESC;
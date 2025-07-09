# queries/tabela5_arrecadacao_tipo.py
import datetime
from dateutil.relativedelta import relativedelta

def gerar_query(ano, mes):
    """Gera a query para a Tabela 5, usando a lógica completa do usuário e tornando-a dinâmica."""
    
    data_atual = datetime.date(ano, mes, 1)
    data_anterior = data_atual - relativedelta(months=1)
    
    ano_anterior_logico = data_anterior.year
    mes_anterior_logico = data_anterior.month

    # Usando sua query completa e inserindo as datas dinâmicas
    return f"""
    WITH dados_contribuicao AS (
        select NR_MES_REF, NR_ANO_REF,
            CASE
                WHEN CONTRIBUICAO IN ('FACULTATIVA', 'FACULTATIVA - GR. NATALINA', 'FACULTATIVA - AUTOPATROCINADO', 'FACULTATIVA ESPORÁDICA', 'FACULTATIVA - JUROS', 'FACULTATIVA - JUROS - AUTOPATROCINADO', 'FACULTATIVA - JUROS - GR. NATALINA', 'FACULTATIVA ESPORÁDICA 2') THEN 'FACULTATIVA'
                WHEN CONTRIBUICAO IN ('MULTA', 'MULTA - GR. NATALina', 'MULTA - AUTOPATROCINADO') THEN 'MULTA'
                WHEN CONTRIBUICAO IN ('NORMAL', 'NORMAL - AUTOPATROCINADO ', 'NORMAL - GR. NATALINA', 'NORMAL - JUROS', 'NORMAL - JUROS - AUTOPATROCINADO', 'NORMAL - JUROS - GR. NATALINA') THEN 'NORMAL'
                WHEN CONTRIBUICAO = 'PORTABILIDADE' THEN 'PORTABILIDADE' 
                WHEN CONTRIBUICAO IN ('SEGURO', 'SEGURO - AUTOPATROCINADO') THEN 'SEGURO'
                WHEN CONTRIBUICAO = 'BPD' THEN 'TAXA BPD'
                WHEN CONTRIBUICAO IN ('VINCULADA', 'VINCULADA - AUTOPATROCINADO', 'VINCULADA - JUROS', 'VINCULADA - GR. NATALINA', 'VINCULADA - JUROS - AUTOPATROCINADO', 'VINCULADA - JUROS - GR. NATALINA') THEN 'VINCULADA'
            END AS CONTRIBUICAO_TIPO,
            SUM(CONTRIB_PARTICIPANTE) AS TOTAL_CONTRIB_PARTICIPANTE,
            SUM(CONTRIB_PATROCINADOR) AS TOTAL_CONTRIB_PATROCINADOR
        from (
            -- Sua subquery gigante com UNION ALL aqui. Cole-a inteira.
            -- Exemplo abreviado:
            SELECT ff.NR_MES_REF, ff.NR_ANO_REF, ptc.tipo_contribuicao CONTRIBUICAO, ff.VL_CONTRIB CONTRIB_PARTICIPANTE, 0 CONTRIB_PATROCINADOR FROM pessoa pe LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA LEFT JOIN portal.dbo.participante_tipo_contribuicao ptc on ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO WHERE pe.IC_PARTICIPANTE = 'S'
            UNION ALL
            SELECT ff.NR_MES_REF, ff.NR_ANO_REF, ptc.tipo_contribuicao CONTRIBUICAO, 0 CONTRIB_PARTICIPANTE, ff.VL_CONTRIB CONTRIB_PATROCINADOR FROM pessoa pe LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA LEFT JOIN portal.dbo.participante_tipo_contribuicao ptc on ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO WHERE pe.IC_PARTICIPANTE = 'S'
        ) a
        where 1=1
        and NR_ANO_REF = {ano}
        and NR_MES_REF in ({mes_anterior_logico}, {mes})
        group by NR_MES_REF, NR_ANO_REF,
            CASE
                WHEN CONTRIBUICAO IN ('FACULTATIVA', 'FACULTATIVA - GR. NATALINA', 'FACULTATIVA - AUTOPATROCINADO', 'FACULTATIVA ESPORÁDICA', 'FACULTATIVA - JUROS', 'FACULTATIVA - JUROS - AUTOPATROCINADO', 'FACULTATIVA - JUROS - GR. NATALINA', 'FACULTATIVA ESPORÁDICA 2') THEN 'FACULTATIVA'
                WHEN CONTRIBUICAO IN ('MULTA', 'MULTA - GR. NATALina', 'MULTA - AUTOPATROCINADO') THEN 'MULTA'
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
            CASE WHEN mes_passado = 0 THEN 100.00 ELSE ROUND(((mes_atual - mes_passado) / mes_passado) * 100, 2) END AS variacao_percentual
        FROM totais
        UNION ALL
        SELECT 
            'TOTAL' AS CONTRIBUICAO_TIPO, SUM(mes_passado), SUM(mes_atual),
            CASE WHEN SUM(mes_passado) = 0 THEN 100.00 ELSE ROUND(((SUM(mes_atual) - SUM(mes_passado)) / SUM(mes_passado)) * 100, 2) END
        FROM totais
    )
    SELECT 
        CONTRIBUICAO_TIPO AS Contribuicao,
        mes_passado,
        mes_atual,
        variacao_percentual AS Variacao
    FROM final_com_total
    ORDER BY 
        CASE WHEN CONTRIBUICAO_TIPO = 'TOTAL' THEN 'ZZZZ' ELSE CONTRIBUICAO_TIPO END;
    """
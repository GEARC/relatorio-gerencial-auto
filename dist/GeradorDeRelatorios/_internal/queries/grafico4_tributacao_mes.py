def gerar_query(ano, mes):
    """
    Gera a query para o gráfico de tributação MENSAL.
    Retorna a contagem bruta de participantes que aderiram no mês de referência.
    """
    return f"""
    SELECT 
        pp.IC_TRIBUTACAO,
        COUNT(e.ID_PESSOA) as Quantidade
    FROM 
        ENCERRAMENTO_PLANO_PARTIC e, 
        PLANO_PARTICIPANTE pp
    WHERE 
        e.ID_PESSOA = pp.id_pessoa
        AND e.ID_SITUACAO IN (1,2) -- Apenas participantes Ativos
        AND e.NR_ANO_REF = {ano} 
        AND e.NR_MES_REF = {mes}
        -- Assumindo que DT_INI_PLANO indica a data de adesão
        AND YEAR(e.DT_INI_PLANO) = {ano}
        AND MONTH(e.DT_INI_PLANO) = {mes}
    GROUP BY 
        pp.IC_TRIBUTACAO
    ORDER BY 
        Quantidade DESC;
    """
def gerar_query(ano, mes):
    """
    Gera a query para a Tabela de Distribuição por Cargos,
    usando a data fornecida pelo usuário.
    """
    return f"""
    select  ISNULL(cg.CARGO, 'TOTAL') AS CARGO, sum(cg.qtd) AS QTD
    from (
        select 
            count(e.ID_PESSOA) as qtd,
            CASE
                WHEN C.NM_CARGO LIKE 'ANALISTA%' THEN 'Analistas'
                WHEN C.NM_CARGO LIKE 'TÉCNICO%' THEN 'Técnicos'
                WHEN C.NM_CARGO LIKE 'JUIZ%' OR C.NM_CARGO LIKE 'DESEMBARGADOR%' THEN 'Magistrados'
                WHEN C.NM_CARGO LIKE 'MINISTRO%' THEN 'Ministro'
                WHEN C.NM_CARGO LIKE 'PROMOTOR%' OR C.NM_CARGO LIKE 'PROCURADOR%' OR C.NM_CARGO LIKE 'SUBPROCURADOR%' THEN 'Membros MPU'
                WHEN C.NM_CARGO LIKE 'AUXILIAR%' THEN 'Auxiliar'
                ELSE 'Outros Cargos'
            END AS CARGO
        from ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps, cargo c, pessoa p
        where 1=1
            and e.ID_SITUACAO = ps.ID_SITUACAO
            and e.ID_PESSOA=  p.ID_PESSOA
            and p.ID_EMP = c.ID_EMP
            and p.ID_CARGO = c.ID_CARGO
            -- CORREÇÃO: Filtro de data agora é dinâmico
            and e.NR_ANO_REF = {ano}
            and e.NR_MES_REF = {mes}
            and e.ID_SITUACAO in (2,5,6,7,1,10)
        group by c.NM_CARGO
    ) cg
    group by ROLLUP (cg.CARGO)
    ORDER BY CASE WHEN cg.CARGO IS NULL THEN 1 ELSE 0 END, QTD DESC;
    """
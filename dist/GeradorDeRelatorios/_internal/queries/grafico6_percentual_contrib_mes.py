def gerar_query(ano, mes):
    """Gera a query de percentual de contribuição para o MÊS de referência."""
    return f"""
    select count(ps.ID_SITUACAO) QTD, ps.NM_SITUACAO, h.PC_CONTRIB PERCENTUAL
    from ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps, HIST_CONTRIBUICAO_PERCENTUAL h
    where e.ID_PESSOA = h.ID_PESSOA
    and h.ID_CONTRIBUICAO in (1,7)
    and e.ID_SITUACAO = ps.ID_SITUACAO
    and h.DT_VIGENCIA = (select max(h2.dt_vigencia) 
                         from HIST_CONTRIBUICAO_PERCENTUAL h2
                         where h2.ID_PESSOA = h.ID_PESSOA
                         and h2.ID_CONTRIBUICAO = h.ID_CONTRIBUICAO)
    and e.NR_ANO_REF = {ano}
    and e.NR_MES_REF = {mes}
    and e.ID_SITUACAO IN (1, 2)
    and e.DT_INI_PLANO BETWEEN DATEFROMPARTS({ano}, {mes}, 1) AND EOMONTH(DATEFROMPARTS({ano}, {mes}, 1))
    group by ps.NM_SITUACAO,ps.ID_SITUACAO, h.PC_CONTRIB
    """
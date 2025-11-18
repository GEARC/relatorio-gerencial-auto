def gerar_query(ano, mes):
    """Gera a query de adesão acumulada para um ano e mês específicos."""
    return f"""
    select  LC.NM_LOCAL as Ramo, count(e.ID_PESSOA) as Quantidade
    from  ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps,LOCAL lc,PESSOA PE
    where 1=1
    and e.ID_SITUACAO = ps.ID_SITUACAO
    and pe.ID_PESSOA = e.ID_PESSOA
    and PE.ID_LOCAL  = LC.ID_LOCAL
    and e.NR_ANO_REF = {ano}
    and e.NR_MES_REF = {mes}
    and e.ID_SITUACAO  in (2,5,6,7,1,10)
    group by  LC.NM_LOCAL
    ORDER BY
        Quantidade DESC;
    """
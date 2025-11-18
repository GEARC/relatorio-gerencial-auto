def gerar_query(ano, mes):
    """
    Gera a query para o gráfico de tributação acumulado.
    Retorna a contagem bruta em vez de percentual formatado.
    """
    return f"""
    select 
        pp.IC_TRIBUTACAO,
        count(e.ID_PESSOA) as Quantidade
    from  
        ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps ,PLANO_PARTICIPANTE pp 
    where 1=1
        and e.NR_ANO_REF = {ano}
        and e.NR_MES_REF = {mes}
        and e.ID_SITUACAO in (2,5,6,7,1,10)
        and e.ID_SITUACAO = ps.ID_SITUACAO
        and e.ID_PESSOA = pp.ID_PESSOA
    group by 
        pp.IC_TRIBUTACAO
    order by 
        Quantidade desc;
    """
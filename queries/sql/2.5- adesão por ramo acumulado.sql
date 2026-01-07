select  LC.NM_LOCAL,
FORMAT(100.0 * count(e.ID_PESSOA) / (
            select count(ID_PESSOA) 
				from ENCERRAMENTO_PLANO_PARTIC e2
				where 1=1
					and e2.NR_ANO_REF = 2025
					and e2.NR_MES_REF = 5
					and e2.ID_SITUACAO in (2,5,6,7,1,10))
    , 'N2', 'pt-BR') + '%' as porcentagem
from  ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps,LOCAL lc,PESSOA PE
where 1=1
and e.ID_SITUACAO = ps.ID_SITUACAO
and pe.ID_PESSOA = e.ID_PESSOA
and PE.ID_LOCAL  = LC.ID_LOCAL
and e.NR_ANO_REF = 2025
and e.NR_MES_REF = 5
and e.ID_SITUACAO  in (2,5,6,7,1,10)
group by  LC.NM_LOCAL
ORDER BY  
    100.0 * COUNT(e.ID_PESSOA) / (
        SELECT COUNT(ID_PESSOA) 
        FROM ENCERRAMENTO_PLANO_PARTIC e2
        WHERE e2.NR_ANO_REF = 2025
          AND e2.NR_MES_REF = 5
          AND e2.ID_SITUACAO IN (2,5,6,7,1,10)
    ) DESC;

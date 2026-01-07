select count(ID_PESSOA) qtd, e.ID_SITUACAO, ps.NM_SITUACAO
from  ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps
where 1=1
and e.ID_SITUACAO = ps.ID_SITUACAO
and concat(nr_ano_ref, FORMAT(NR_MES_REF, '00')) = '202505'
and e.ID_SITUACAO  in (2,5,6,7,1,10)
--and concat(year(DT_INI_PLANO ), FORMAT(month(DT_INI_PLANO ), '00')) = '202504'
group by e.ID_SITUACAO, ps.NM_SITUACAO

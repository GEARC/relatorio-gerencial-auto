select sum(fe.qtd) QTD,  fe.SEXO
from (select count(e.ID_PESSOA) qtd,
		p.IC_SEXO SEXO
		from  ENCERRAMENTO_PLANO_PARTIC e, PLANO_SITUACAO ps, pessoa p
		where 1=1
		and e.ID_SITUACAO = ps.ID_SITUACAO
		and e.ID_PESSOA = p.ID_PESSOA
		and e.NR_ANO_REF = 2025
        and e.NR_MES_REF = 5
		and e.ID_SITUACAO  in (2,5,6,7,1,10)
		group by p.DT_NASCIMENTO, p.IC_SEXO) FE
group by  fe.SEXO


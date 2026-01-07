SELECT 
    p.ID_EMP as ORGAO, 
    p.NR_MATRICULA as MATRICULA,
    p.SG_PESSOA as PARTICIPANTE,
    p.NR_CNPJ_CPF as CPF,
    hc.nr_ano_comp as ano_comp,
    hc.nr_mes_comp as mes_comp
FROM HIST_PLANO_PARTICIPANTE hpp,
     PESSOA p,
     PLANO_SITUACAO ps,
     HIST_CONTRIBUICAO hc
WHERE hpp.ID_PESSOA = p.ID_PESSOA
  AND ps.ID_SITUACAO = hpp.ID_SITUACAO
  AND hc.ID_PESSOA = p.ID_PESSOA
  AND p.SG_PESSOA = 'sergio rodrigues'
  -- Usando matemática: ano*100 + mês (ex: 2024*100 + 3 = 202403)
  AND (hc.NR_ANO_COMP * 100 + hc.NR_MES_COMP) = (
      SELECT MAX(hc1.NR_ANO_COMP * 100 + hc1.NR_MES_COMP)
      FROM HIST_CONTRIBUICAO hc1
      WHERE hc1.ID_PESSOA = p.ID_PESSOA
        AND hc1.nr_ano_ref = (
            SELECT MAX(hc2.nr_ano_ref) 
            FROM HIST_CONTRIBUICAO hc2 
            WHERE hc2.id_pessoa = hc1.id_pessoa
        )
  )
  AND NOT EXISTS(
      SELECT 1
      FROM HIST_PLANO_PARTICIPANTE hpp2,
           PLANO_SITUACAO ps2
      WHERE hpp2.ID_PESSOA = p.ID_PESSOA
        AND ps2.ID_SITUACAO = hpp2.ID_SITUACAO
        AND hpp2.DT_FIM IS NOT NULL
  );

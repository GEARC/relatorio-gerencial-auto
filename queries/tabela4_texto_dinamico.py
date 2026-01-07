import datetime
import locale

def gerar_query(ano, mes):
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        
    return f"""
        SELECT 
            ISNULL(CAST(SUM(ff.VL_CONTRIB) AS MONEY), 0) AS CONTRIB
        FROM pessoa pe 
        LEFT JOIN hist_empresa he ON he.id_pessoa = pe.id_pessoa 
            AND he.id_emp = pe.id_emp 
            AND he.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa) 
            AND he.nr_mes_ref = (SELECT Max(he1.nr_mes_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa AND he1.nr_ano_ref = (SELECT Max(he1.nr_ano_ref) FROM hist_empresa he1 WHERE he1.id_pessoa = he.id_pessoa))
        LEFT JOIN hist_contribuicao ff ON ff.id_pessoa = pe.ID_PESSOA
        LEFT JOIN portal.dbo.participante_tipo_contribuicao ptc ON ptc.id_contribuicao_trust = ff.ID_CONTRIBUICAO
        WHERE 
            pe.IC_EMP_PATROC = 'N'
            AND pe.IC_PARTICIPANTE = 'S'
            AND ptc.tipo_contribuicao IN ('NORMAL','NORMAL - AUTOPATROCINADO','NORMAL - GR. NATALINA','NORMAL - JUROS','NORMAL - JUROS - AUTOPATROCINADO','NORMAL - JUROS - GR. NATALINA')
            AND ff.ID_CONTRIBUICAO IN (
                SELECT ptc2.ID_CONTRIBUICAO_TRUST 
                FROM portal.dbo.participante_tipo_contribuicao ptc2 
                WHERE ptc2.mantenedor_consolidado = 'PARTICIPANTE' 
                    AND ptc2.movimentacao IN ('CONTRIBUIÇÃO','AJUSTE','')
                    AND ptc2.mantenedor_contribuicao = 'AUTOPATROCINADO'
            )
            AND ff.ID_CONTRIBUICAO NOT IN (491,492)
            AND ff.NR_ANO_REF = {ano} 
            AND ff.NR_MES_REF = {mes}
    """
import pandas as pd
import locale

def transformar_dados_evolucao(df_geral_raw, df_detalhes_raw, data_alvo):
    """
    Combina os dados gerais e detalhados para montar a Tabela 1 final.
    """
    if df_geral_raw.empty:
        print("Aviso: DataFrame geral de evolução está vazio.")
        return pd.DataFrame()
        
    ano = data_alvo.year
    ano_anterior = ano - 1

    # --- 1. Processa os dados GERAIS ---
    df_geral = df_geral_raw.set_index('situacao').drop(columns=['ordem', 'total_geral'], errors='ignore')
    for col in df_geral.columns: df_geral[col] = pd.to_numeric(df_geral[col], errors='coerce')
    df_geral = df_geral.fillna(0).T
    
    novos_nomes_geral = {}
    for idx in df_geral.index:
        if idx.startswith('saldo_'): novos_nomes_geral[idx] = f"Saldo {ano_anterior}"
        elif idx.startswith('acumulado_'): novos_nomes_geral[idx] = f"Acumulado/{ano}"
        else: novos_nomes_geral[idx] = idx.replace('_', '/')
    df_geral = df_geral.rename(index=novos_nomes_geral)
    
    # --- 2. Processa os dados de DETALHES ---
    df_pivot_detalhes = pd.DataFrame()
    if df_detalhes_raw is not None and not df_detalhes_raw.empty:
        df_detalhes_raw['ANO_MES'] = pd.to_datetime(df_detalhes_raw['ANO_MES'], format='%Y%m').dt.strftime('%b/%Y').str.lower()
        df_pivot_detalhes = df_detalhes_raw.pivot_table(
            index='ANO_MES', columns=['SITUACAO', 'ORIGEM'], values='QTD', aggfunc='sum'
        ).fillna(0)

    # --- 3. Combina os dois DataFrames ---
    df_combinado = pd.concat([df_geral, df_pivot_detalhes], axis=1, join='outer').fillna(0)
    
    # --- 4. Monta a tabela final com a estrutura correta ---
    
    # Define a estrutura do cabeçalho de duas linhas (MultiIndex)
    colunas_finais = pd.MultiIndex.from_tuples([
        ('Mês/Ano', ''), ('Patrocinado', ''), ('Vinculado', ''), ('BPD', 'Patrocinado'), ('BPD', 'Vinculado'),
        ('Autopatrocinado', 'Patrocinado'), ('Autopatrocinado', 'Vinculado'),
        ('No prazo opção dos institutos', ''), ('Assistido', '')
    ])
    
    # Cria o DataFrame final com a estrutura correta
    df_final = pd.DataFrame(index=df_combinado.index, columns=colunas_finais)

    # Preenche o DataFrame final com os dados combinados
    df_final[('Patrocinado', '')] = df_combinado.get('PATROCINADO', 0)
    df_final[('Vinculado', '')] = df_combinado.get('VINCULADO', 0)
    df_final[('BPD', 'Patrocinado')] = df_combinado.get(('BPD', 'Patrocinado'), 0)
    df_final[('BPD', 'Vinculado')] = df_combinado.get(('BPD', 'Vinculado'), 0)
    df_final[('Autopatrocinado', 'Patrocinado')] = df_combinado.get(('AUTOPATROCINADO', 'Patrocinado'), 0)
    df_final[('Autopatrocinado', 'Vinculado')] = df_combinado.get(('AUTOPATROCINADO', 'Vinculado'), 0)
    df_final[('No prazo opção dos institutos', '')] = df_combinado.get('NO PRAZO OPÇÃO INSTITUTOS', 0)
    df_final[('Assistido', '')] = df_combinado.get('ASSISTIDO', 0)
    
    df_final = df_final.fillna(0).astype(int)
    
    # Adiciona a coluna Total
    df_final[('Total', '')] = df_final.sum(axis=1)

    # Adiciona a linha de Acumulado Total
    acumulado_total_row = df_final.loc[f"Saldo {ano_anterior}"] + df_final.loc[f"Acumulado/{ano}"]
    df_final.loc['Acumulado Total'] = acumulado_total_row
    
    # Prepara o DataFrame para ser usado pela função que gera a imagem
    df_final.reset_index(inplace=True)
    df_final.columns = [' '.join(col).strip() for col in df_final.columns.values]
    
    return df_final.rename(columns={'Mês/Ano ': 'Mês/Ano'})

def formatar_tabela_arrecadacao(df, data_alvo):
    """Formata o DataFrame da Tabela 5 para exibição."""
    if df.empty:
        return df
    
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    
    # Pega os nomes dos meses
    mes_atual_nome = data_alvo.strftime('%B/%Y').capitalize()
    mes_passado_nome = (data_alvo - pd.DateOffset(months=1)).strftime('%B/%Y').capitalize()

    # Renomeia as colunas
    df = df.rename(columns={'mes_passado': mes_passado_nome, 'mes_atual': mes_atual_nome})

    # Formata as colunas de moeda
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    df[mes_passado_nome] = df[mes_passado_nome].apply(lambda x: locale.currency(x, grouping=True))
    df[mes_atual_nome] = df[mes_atual_nome].apply(lambda x: locale.currency(x, grouping=True))
    
    # Formata a coluna de variação
    df['Variacao'] = df['Variacao'].apply(lambda x: f'{x:.2f}%'.replace('.',','))
    
    df.rename(columns={
        'Contribuicao': 'Contribuição', 
        'Variacao': 'Variação'
    }, inplace=True)

    return df

def formatar_tabela_cargo(df):
    """Formata o DataFrame da Tabela 6 para exibição, usando nomes de colunas simples."""
    if df.empty:
        return df
    
    # Adiciona a linha de Total Geral ANTES de formatar, usando os dados brutos
    total_contribuicao_geral = df['TotalContribuicao'].sum()
    total_participantes_geral = df['QuantidadeParticipantes'].sum()
    
    total_row = pd.DataFrame([{
        'CARGO': 'TOTAL',
        'RepresentatividadeContribuicao': '',
        'ContribuicaoMedia': '',
        'QuantidadeParticipantes': '',
        'RepresentatividadeParticipantes': '',
        'TotalContribuicao': total_contribuicao_geral
    }])
    
    df_com_total = pd.concat([df, total_row], ignore_index=True)

    # Formata as colunas
    df_com_total['RepresentatividadeContribuicao'] = df_com_total['RepresentatividadeContribuicao'].apply(lambda x: f'{x:.1f}%'.replace('.',',') if isinstance(x, (int, float)) else x)
    df_com_total['ContribuicaoMedia'] = df_com_total['ContribuicaoMedia'].apply(lambda x: locale.currency(x, grouping=True) if isinstance(x, (int, float)) else x)
    df_com_total['QuantidadeParticipantes'] = df_com_total['QuantidadeParticipantes'].apply(lambda x: f'{x:,.0f}'.replace(',','.') if isinstance(x, (int, float)) else x)
    df_com_total['RepresentatividadeParticipantes'] = df_com_total['RepresentatividadeParticipantes'].apply(lambda x: f'{x:.1f}%'.replace('.',',') if isinstance(x, (int, float)) else x)
    df_com_total['TotalContribuicao'] = df_com_total['TotalContribuicao'].apply(lambda x: locale.currency(x, grouping=True) if isinstance(x, (int, float)) else x)

    # Renomeia as colunas para a versão final, com acentos
    df_com_total.rename(columns={
        'CARGO': 'CARGO',
        'RepresentatividadeContribuicao': 'REPRESENTATIVIDADE DA CONTRIBUIÇÃO',
        'ContribuicaoMedia': 'CONTRIBUIÇÃO MÉDIA',
        'QuantidadeParticipantes': 'QUANTIDADE DE PARTICIPANTES',
        'RepresentatividadeParticipantes': 'REPRESENTATIVIDADE DOS PARTICIPANTES',
        'TotalContribuicao': 'TOTAL CONTRIBUIÇÃO'
    }, inplace=True)
    
    return df_com_total.fillna('')

def formatar_tabela_patrocinador(df):
    """Formata o DataFrame da Tabela 7 para exibição."""
    if df.empty:
        return df

    # Calcula a linha de TOTAL antes de formatar
    total_mes = df['contribuicao_no_mes'].sum()
    total_acumulado = df['contribuicoes_acumuladas'].sum()
    
    total_row = pd.DataFrame([{
        'Patrocinador': 'TOTAL',
        'contribuicao_no_mes': total_mes,
        'representatividade_contribuicao': 100.0,
        'contribuicoes_acumuladas': total_acumulado,
        'representatividade_patrimonio': 100.0
    }])
    
    df_com_total = pd.concat([total_row, df], ignore_index=True)

    # Aplica a formatação de moeda e percentual
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    df_com_total['contribuicao_no_mes'] = df_com_total['contribuicao_no_mes'].apply(lambda x: locale.currency(x, grouping=True))
    df_com_total['representatividade_contribuicao'] = df_com_total['representatividade_contribuicao'].apply(lambda x: f'{x:.2f}%'.replace('.', ','))
    df_com_total['contribuicoes_acumuladas'] = df_com_total['contribuicoes_acumuladas'].apply(lambda x: locale.currency(x, grouping=True))
    df_com_total['representatividade_patrimonio'] = df_com_total['representatividade_patrimonio'].apply(lambda x: f'{x:.2f}%'.replace('.', ','))
    
    # Renomeia as colunas para a versão final
    df_com_total.rename(columns={
        'Patrocinador': 'Patrocinador',
        'contribuicao_no_mes': 'Contribuição no mês',
        'representatividade_contribuicao': 'Representatividade da contribuição',
        'contribuicoes_acumuladas': 'Contribuições acumuladas',
        'representatividade_patrimonio': 'Representatividade do patrimônio'
    }, inplace=True)
    
    return df_com_total
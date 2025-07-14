import pandas as pd
import locale

def transformar_dados_evolucao(df_raw, data_alvo):
    """
    Recebe o DataFrame no formato da consulta e o transforma
    para o formato visual do relatório de forma dinâmica.
    """
    if df_raw.empty:
        return pd.DataFrame()
        
    ano = data_alvo.year
    ano_anterior = ano - 1

    df_raw = df_raw.set_index('situacao').drop(columns=['ordem'], errors='ignore')
    for col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')
    df_raw = df_raw.fillna(0)
    df_formatado = df_raw.T
    
    colunas_renomear = {
        'PATROCINADO': 'Patrocinado', 'VINCULADO': 'Vinculado', 'BPD - SALDO': 'BPD',
        'NO PRAZO OPÇÃO INSTITUTOS': 'No prazo opção dos institutos', 'AUTOPATROCINADO': 'Autopatrocinado',
        'ASSISTIDO': 'Assistido'
    }
    df_formatado.rename(columns=colunas_renomear, inplace=True)

    ordem_colunas = ['Patrocinado', 'Vinculado', 'BPD', 'No prazo opção dos institutos', 'Autopatrocinado', 'Assistido']
    for col in ordem_colunas:
        if col not in df_formatado.columns:
            df_formatado[col] = 0
    df_formatado = df_formatado[ordem_colunas]

    df_formatado['Total'] = df_formatado.sum(axis=1).astype(int)
    df_formatado.columns.name = None

    # --- LÓGICA DE RENOMEAÇÃO DINÂMICA ---
    total_geral_row = df_formatado.loc['total_geral']
    df_formatado = df_formatado.drop('total_geral')

    novos_nomes_index = {}
    for nome_coluna in df_formatado.index:
        if nome_coluna.startswith('saldo_'):
            novos_nomes_index[nome_coluna] = f"Saldo {ano_anterior}"
        elif nome_coluna.startswith('acumulado_'):
            novos_nomes_index[nome_coluna] = f"Acumulado/{ano}"
        else: # É uma coluna de mês, ex: 'jan_2024'
            partes = nome_coluna.split('_')
            novos_nomes_index[nome_coluna] = f"{partes[0]}/{partes[1]}"
            
    df_formatado = df_formatado.rename(index=novos_nomes_index)

    df_formatado.loc['Acumulado Total'] = total_geral_row
    
    return df_formatado.reset_index().rename(columns={'index': 'Mês/Ano'})

def formatar_tabela_arrecadacao(df, data_alvo):
    """Formata o DataFrame da Tabela 5 para exibição."""
    if df.empty:
        return df
    
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
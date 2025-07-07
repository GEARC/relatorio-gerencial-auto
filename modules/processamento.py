import pandas as pd

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
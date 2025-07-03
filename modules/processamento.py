import pandas as pd

def transformar_dados_evolucao(df_raw):
    """Recebe o DataFrame da consulta de evolução e o transforma para o formato visual."""
    if df_raw.empty: return pd.DataFrame()
    df_raw = df_raw.set_index('situacao').drop(columns=['ordem'], errors='ignore')
    for col in df_raw.columns: df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')
    df_raw = df_raw.fillna(0); df_formatado = df_raw.T
    colunas_renomear = {'PATROCINADO': 'Patrocinado','VINCULADO': 'Vinculado','BPD - SALDO': 'BPD','NO PRAZO OPÇÃO INSTITUTOS': 'No prazo opção dos institutos','AUTOPATROCINADO': 'Autopatrocinado','ASSISTIDO': 'Assistido'}
    df_formatado.rename(columns=colunas_renomear, inplace=True)
    ordem_colunas = ['Patrocinado', 'Vinculado', 'BPD', 'No prazo opção dos institutos', 'Autopatrocinado', 'Assistido']
    for col in ordem_colunas:
        if col not in df_formatado.columns: df_formatado[col] = 0
    df_formatado = df_formatado[ordem_colunas]
    df_formatado['Total'] = df_formatado.sum(axis=1).astype(int); df_formatado.columns.name = None
    total_geral_row = df_formatado.loc['total_geral']; df_formatado = df_formatado.drop('total_geral')
    novos_nomes_index = {'saldo_2024': 'Saldo 2024','jan_2025': 'jan/2025','fev_2025': 'fev/2025','mar_2025': 'mar/2025','abr_2025': 'abr/2025','mai_2025': 'mai/2025','acumulado_2025': 'Acumulado/2025'}
    df_formatado = df_formatado.rename(index=novos_nomes_index); df_formatado.loc['Acumulado Total'] = total_geral_row
    return df_formatado.reset_index().rename(columns={'index': 'Mês/Ano'})
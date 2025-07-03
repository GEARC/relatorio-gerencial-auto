import os
import imgkit
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd # Adicione esta importação se ainda não tiver
from config import PATH_WKHTMLTOIMAGE # Importa o caminho da configuração

config = imgkit.config(wkhtmltoimage=PATH_WKHTMLTOIMAGE)

def gerar_imagem_tabela(df, nome_arquivo_saida):
    if df.empty:
        print(f"DataFrame vazio, não foi possível gerar a imagem {nome_arquivo_saida}.")
        return False
    html_tabela = df.to_html(index=False, border=0)
    css_estilo = """<style>@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');body{font-family:'Open Sans',sans-serif;font-size:14px;}table{border-collapse:collapse;width:100%;color:#333;}th,td{border:1px solid #E0E0E0;text-align:center;padding:8px;vertical-align:middle;font-size:14px;}th{background-color:#0F406D;color:white;font-weight:bold;font-size:15px;}td:first-child{text-align:left;}tr{background-color:white;}</style>"""
    html_completo = f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{css_estilo}</head><body>{html_tabela}</body></html>"
    options = {'--enable-local-file-access': None, 'quality': '100', 'width': 600, 'encoding': "UTF-8", 'zoom': 1.0}
    try:
        imgkit.from_string(html_completo, nome_arquivo_saida, config=config, options=options)
        print(f"Imagem da tabela gerada: {nome_arquivo_saida}")
        return True
    except Exception as e:
        print(f"Erro ao gerar imagem da tabela: {e}")
        return False

def criar_grafico_piramide_etaria(df, caminho_para_salvar):
    if df.empty:
        print("DataFrame vazio, não é possível gerar o gráfico.")
        return False
    df_pivot = df.pivot(index='Faixa_Etaria', columns='SEXO', values='QTD').fillna(0)
    df_pivot = df_pivot.rename(columns={'F': 'Feminino', 'M': 'Masculino'})
    if 'Feminino' not in df_pivot: df_pivot['Feminino'] = 0
    if 'Masculino' not in df_pivot: df_pivot['Masculino'] = 0
    ordem_correta = ['21 a 23', '24 a 26', '27 a 29', '30 a 32', '33 a 35', '36 a 38', '39 a 41','42 a 44', '45 a 47', '48 a 50', '51 a 53', '54 a 56', '57 a 59', '60 a 62','Maior que 62 anos']
    df_pivot = df_pivot.reindex(ordem_correta).dropna()
    if df_pivot.empty:
        print("ERRO: DataFrame ficou vazio após reindexar.")
        return False
    df_pivot['Feminino'] = -df_pivot['Feminino']
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(df_pivot.index, df_pivot['Feminino'], color='#9b2242', label='Feminino')
    ax.barh(df_pivot.index, df_pivot['Masculino'], color='#003366', label='Masculino')
    limite_eixo = ax.get_xlim()[1]
    limite_texto = limite_eixo * 0.15 
    for i, (valor_m, valor_f) in enumerate(zip(df_pivot['Masculino'], df_pivot['Feminino'])):
        if valor_m < limite_texto:
            ax.text(valor_m + 50, i, f'{int(valor_m)}', ha='left', va='center', fontsize=8, color='black')
        else:
            ax.text(valor_m - 50, i, f'{int(valor_m)}', ha='right', va='center', fontsize=9, color='white')
        if abs(valor_f) < limite_texto:
            ax.text(valor_f - 50, i, f'{abs(int(valor_f))}', ha='right', va='center', fontsize=8, color='black')
        else:
            ax.text(valor_f + 50, i, f'{abs(int(valor_f))}', ha='left', va='center', fontsize=9, color='white')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{abs(int(x)):,.0f}'.replace(',', '.')))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
    ax.spines[['top','right','left']].set_visible(False)
    plt.savefig(caminho_para_salvar, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Gráfico de pirâmide gerado: {caminho_para_salvar}")
    return True
import os
import imgkit
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from config import PATH_WKHTMLTOIMAGE
import textwrap

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

def criar_grafico_barras_verticais(df, caminho_para_salvar, titulo_grafico):
    """Cria um gráfico de barras verticais com rótulos horizontais e legíveis."""
    if df.empty:
        print(f"DataFrame vazio, não é possível gerar o gráfico '{titulo_grafico}'.")
        return False

    labels_originais = df.iloc[:, 0]
    valores = df.iloc[:, 1]
    
    total_geral = valores.sum()
    if total_geral == 0:
        print(f"Total de valores é zero para o gráfico '{titulo_grafico}'.")
        return False
    
    # --- CORREÇÃO 1: QUEBRA DE LINHA AUTOMÁTICA NOS RÓTULOS ---
    # Quebra o texto em múltiplas linhas se ele tiver mais de 15 caracteres
    labels = ['\n'.join(textwrap.wrap(l, 15)) for l in labels_originais]
    
    plt.style.use('seaborn-v0_8-whitegrid')
    # --- CORREÇÃO 2: AUMENTA A LARGURA DA FIGURA ---
    fig, ax = plt.subplots(figsize=(15, 8)) # Antes era (12, 7)
    
    cores = ['#003366', '#d62728', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    bars = ax.bar(labels, valores, color=cores[:len(labels)])
    
    for bar in bars:
        altura = bar.get_height()
        percentual = (altura / total_geral) * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            altura,
            f'{percentual:.2f}%;\n{int(altura)}',
            ha='center', va='bottom', fontsize=9
        )
        
    ax.set_title(titulo_grafico, fontsize=16)
    ax.set_ylabel('Quantidade de Participantes')
    
    # Mantém os rótulos na horizontal (rotação 0)
    plt.xticks(rotation=0)
    
    ax.spines[['top','right']].set_visible(False)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.20)
    
    # Ajusta o layout para garantir que os rótulos não sejam cortados
    fig.tight_layout()
    
    plt.savefig(caminho_para_salvar, dpi=300) # bbox_inches='tight' removido em favor de tight_layout()
    plt.close(fig)
    print(f"Gráfico de barras gerado: {caminho_para_salvar}")
    return True

def criar_grafico_donut(df, caminho_para_salvar, titulo_grafico):
    """Cria um gráfico de donut com rótulos de porcentagem posicionados de forma inteligente."""
    if df.empty:
        print(f"DataFrame vazio, não é possível gerar o gráfico '{titulo_grafico}'.")
        return False

    mapeamento_tributacao = { 'R': 'Regressiva', 'P': 'Progressiva', 'N': 'No prazo de opção*' }
    df['Legenda'] = df.iloc[:, 0].map(mapeamento_tributacao).fillna(df.iloc[:, 0])
    
    labels_legenda = df['Legenda']
    valores = pd.to_numeric(df.iloc[:, 1])
    
    cores = ['#DD7E2E', '#0F406D', '#5DADE2']
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 7), subplot_kw=dict(aspect="equal"))

    # Plota a base do gráfico sem nenhum texto automático
    wedges, texts = ax.pie(
        valores,
        startangle=90,
        colors=cores,
        wedgeprops=dict(width=0.4, edgecolor='w')
    )

    # --- LÓGICA DE POSICIONAMENTO CONDICIONAL ---
    total = sum(valores)
    limite_para_texto_interno = 10  # Limite de 10% para o texto ficar dentro

    for i, p in enumerate(wedges):
        percentual = (valores.iloc[i] / total) * 100
        
        # Pega o ângulo e o raio do meio da fatia
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        
        # Se a fatia for pequena, coloca o texto FORA
        if percentual < limite_para_texto_interno:
            # Posição fora do gráfico (raio > 1.0)
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            # Alinha o texto para fora
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            ax.text(x * 1.1, y * 1.1, f'{percentual:.0f}%', ha=horizontalalignment, va='center', color='black', size=10)
        
        # Se a fatia for grande, coloca o texto DENTRO
        else:
            # Posição dentro do anel
            y = np.sin(np.deg2rad(ang)) * 0.85
            x = np.cos(np.deg2rad(ang)) * 0.85
            
            # Lógica para cor de texto visível
            slice_color = wedges[i].get_facecolor()
            r, g, b, _ = slice_color
            luminance = 0.299*r + 0.587*g + 0.114*b
            text_color = 'black' if luminance > 0.5 else 'white'
            
            ax.text(x, y, f'{percentual:.0f}%', ha='center', va='center', color=text_color, weight='bold', size=12)

    ax.axis('equal')
    ax.legend(wedges, labels_legenda, title="Regime", loc="center left", bbox_to_anchor=(1.05, 0.5), frameon=False)
    ax.set_title(titulo_grafico, fontsize=16, pad=20)
    
    plt.savefig(caminho_para_salvar, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Gráfico de donut gerado: {caminho_para_salvar}")
    return True
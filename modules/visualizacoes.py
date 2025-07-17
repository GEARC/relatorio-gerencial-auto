import os
import imgkit
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
import textwrap
from config import PATH_WKHTMLTOIMAGE
from adjustText import adjust_text


config = imgkit.config(wkhtmltoimage=PATH_WKHTMLTOIMAGE)
FONTE_TEXTO = "Fonte: DISEG/GEARC"

def gerar_imagem_tabela(df, nome_arquivo_saida):
    if df.empty:
        print(f"DataFrame vazio, não foi possível gerar a imagem {nome_arquivo_saida}.")
        return False
    html_tabela = df.to_html(index=False, border=0)
    html_footer = f"""
    <div class="footer">
        {FONTE_TEXTO}
    </div>
    """
    
    css_estilo = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');
        body { font-family: 'Open Sans', sans-serif; font-size: 14px; }
        table { border-collapse: collapse; width: 100%; color: #333; }
        th, td {
            border: 1px solid #E0E0E0;
            text-align: center;
            padding: 8px;
            vertical-align: middle;
            font-size: 14px;
        }
        th {
            background-color: #0F406D;
            color: white;
            font-weight: bold;
            font-size: 15px;
        }
        td:first-child { text-align: left; }
        tr { background-color: white; }
        /* CORREÇÃO: Nova regra para deixar a última linha da tabela em negrito */
        tr:last-child {
            font-weight: bold;
        }
    </style>
    """
    html_completo = f"<!DOCTYPE html><html><head>{css_estilo}</head><body>{html_tabela}{html_footer}</body></html>"
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
        
    # --- CORREÇÃO APLICADA AQUI ---
    # Troca 'pivot' por 'pivot_table' com a função de agregação 'sum'.
    # Isso garante que todas as linhas para a mesma categoria sejam somadas.
    df_pivot = df.pivot_table(
        index='Faixa_Etaria', 
        columns='SEXO', 
        values='QTD', 
        aggfunc='sum'
    ).fillna(0)
    
    df_pivot = df_pivot.rename(columns={'F': 'Feminino', 'M': 'Masculino'})
    if 'Feminino' not in df_pivot: df_pivot['Feminino'] = 0
    if 'Masculino' not in df_pivot: df_pivot['Masculino'] = 0
    
    # A ordenação e o resto da lógica continuam os mesmos
    ordem_correta = [
        '21 a 23', '24 a 26', '27 a 29', '30 a 32', '33 a 35', 
        '36 a 38', '39 a 41', '42 a 44', '45 a 47', '48 a 50', 
        '51 a 53', '54 a 56', '57 a 59', '60 a 62', '63 a 65', 
        '66 a 68', '69 a 71', '72 a 74', '75 a 77', '79 a 81', 
        '82 a 84', '85 a 87', '88 a 90', '91 a 93', '94 a 96', 
        '97 a 99', '100 a 102', '103 a 105', 'Maior que 105'
    ]
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

    fig.text(0.05, 0.01, FONTE_TEXTO, ha='left', va='bottom', fontsize=11, color='#000')
    
    plt.savefig(caminho_para_salvar, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Gráfico de pirâmide gerado: {caminho_para_salvar}")
    return True

def criar_grafico_barras_verticais(df, caminho_para_salvar, titulo_grafico, formato_label='default'):
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
    
    cores_por_orgao = {
        'JUSTIÇA TRABALHISTA': '#003366',
        'JUSTIÇA FEDERAL': '#d62728',
        'MPU': '#ff7f0e',
        'JUSTIÇA ELEITORAL': '#2ca02c',
        'TJDFT': '#9467bd',
        'STJ': '#8c564b',
        'STF': '#e377c2',
        'JUSTIÇA MILITAR': '#7f7f7f',
        'CNJ': '#bcbd22',
        'CNMP': '#17becf',
        'OUTRO ÓRGÃO/ENTIDADE': '#FF6B6B'  # Cor diferenciada para "outros"
    }
    
    # Aplicar cores baseadas nos labels originais (antes da quebra de linha)
    cores_aplicadas = [cores_por_orgao.get(label, '#cccccc') for label in labels_originais]
    bars = ax.bar(labels, valores, color=cores_aplicadas)
    
    for bar in bars:
        altura = bar.get_height()
        percentual = (altura / total_geral) * 100
        
        # Define o texto do rótulo com base no parâmetro
        if formato_label == 'percent_only':
            texto_rotulo = f'{percentual:.2f}%'.replace('.', ',')
        else: # Padrão: mostra percentual e valor absoluto
            texto_rotulo = f'{percentual:.2f}%\n{int(altura)}'.replace('.', ',')
            
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            altura,
            texto_rotulo,
            ha='center', va='bottom', fontsize=16
        )

    ax.set_title(titulo_grafico, fontsize=16)
    
    # Mantém os rótulos na horizontal (rotação 0)
    plt.xticks(rotation=0)
    
    ax.spines[['top','right']].set_visible(False)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.20)
    
    # Ajusta o layout para garantir que os rótulos não sejam cortados
    fig.tight_layout()
    
    plt.subplots_adjust(bottom=0.10)
    ax.text(0, -0.09, FONTE_TEXTO, transform=ax.transAxes,
            ha='left', va='top', fontsize=11, color='#000')
    
    plt.savefig(caminho_para_salvar, dpi=300) # bbox_inches='tight' removido em favor de tight_layout()
    plt.close(fig)
    print(f"Gráfico de barras gerado: {caminho_para_salvar}")
    return True

def criar_grafico_donut(df, caminho_para_salvar, titulo_grafico):
    """Cria um gráfico de donut com rótulos de porcentagem bem posicionados."""
    if df.empty:
        print(f"DataFrame vazio, não é possível gerar o gráfico '{titulo_grafico}'.")
        return False

    mapeamento_tributacao = { 'R': 'Regressiva', 'P': 'Progressiva', 'N': 'Sem opção*' }
    df['Legenda'] = df.iloc[:, 0].map(mapeamento_tributacao).fillna(df.iloc[:, 0])
    
    labels_legenda = df['Legenda']
    valores = pd.to_numeric(df.iloc[:, 1])
    
    mapa_de_cores = {'Regressiva': '#DD7E2E', 'Progressiva': '#5DADE2', 'Sem opção*': '#0F406D'}
    cores_ordenadas = [mapa_de_cores.get(label, '#808080') for label in labels_legenda]
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 7), subplot_kw=dict(aspect="equal"))

    # Plota a base do gráfico sem nenhum texto automático
    wedges, texts = ax.pie(
        valores,
        startangle=90,
        colors=cores_ordenadas,
        wedgeprops=dict(width=0.4, edgecolor='w')
    )

    # --- LÓGICA DE RÓTULOS COM AJUSTE AUTOMÁTICO ---
    total = sum(valores)
    if total == 0: return False
    
    limite_para_texto_interno = 7  # Limite para o texto ficar dentro
    textos_para_ajustar = [] # Lista para guardar os textos externos

    for i, p in enumerate(wedges):
        percentual = (valores.iloc[i] / total) * 100
        
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        
        # Se a fatia for pequena, prepara o texto para ajuste externo
        if percentual < limite_para_texto_interno:
            texto_externo = ax.text(x * 1.1, y * 1.1, f'{percentual:.2f}%'.replace('.',','), 
                                    ha='center', va='center', color='black', size=10)
            textos_para_ajustar.append(texto_externo)
        
        # Se a fatia for grande, coloca o texto DENTRO
        else:
            slice_color = wedges[i].get_facecolor()
            luminance = mcolors.rgb_to_hsv(slice_color[:3])[2]
            text_color = 'black' if luminance > 0.5 else 'white'
            ax.text(x * 0.82, y * 0.82, f'{percentual:.2f}%'.replace('.',','), 
                    ha='center', va='center', color=text_color, weight='bold', size=11)

    # Chama a biblioteca para ajustar apenas os textos externos, evitando sobreposição
    adjust_text(textos_para_ajustar, 
                arrowprops=dict(arrowstyle="-", color='gray', lw=0.5))

    ax.axis('equal')
    ax.legend(wedges, labels_legenda, title="", loc="center left", bbox_to_anchor=(1.05, 0.5), frameon=False)
    ax.set_title(titulo_grafico, fontsize=16, pad=20)
    
    fig.text(0.05, 0.01, FONTE_TEXTO, ha='left', va='bottom', fontsize=11, color='#000')

    plt.savefig(caminho_para_salvar, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Gráfico de donut gerado: {caminho_para_salvar}")
    return True

def criar_grafico_barras_agrupadas(df, caminho_para_salvar, titulo):
    """Cria um gráfico de barras agrupadas e o salva como imagem."""
    if df.empty:
        print(f"DataFrame vazio, não é possível gerar o gráfico '{titulo}'.")
        return False

    # Renomeia para um padrão conhecido
    df = df.rename(columns={'NM_SITUACAO': 'Situacao', 'PERCENTUAL': 'Percentual', 'QTD': 'Qtd'})
    
    # Pivota os dados
    df_pivot = df.pivot_table(index='Percentual', columns='Situacao', values='Qtd', fill_value=0)
    
    # Converte a contagem para percentual DENTRO de cada grupo (Vinculado, Patrocinado)
    df_percent = df_pivot.div(df_pivot.sum(axis=0), axis=1) * 100
    
    # Formata o índice para ter o símbolo de %
    df_percent.index = [f'{i:.2f}%'.replace('.',',') for i in df_percent.index]

    labels = df_percent.index
    x = np.arange(len(labels))  # Posições dos rótulos
    width = 0.35  # Largura das barras

    fig, ax = plt.subplots(figsize=(12, 7))
    # Plota as barras para 'PATROCINADO'
    rects1 = ax.bar(x - width/2, df_percent.get('PATROCINADO', 0), width, label='Patrocinado', color='#0F406D')
    # Plota as barras para 'VINCULADO'
    rects2 = ax.bar(x + width/2, df_percent.get('VINCULADO', 0), width, label='Vinculado', color='#DD7E2E')

    # Adiciona os rótulos de porcentagem
    ax.bar_label(rects1, padding=3, fmt='%.2f%%')
    ax.bar_label(rects2, padding=3, fmt='%.2f%%')

    ax.set_title(titulo, fontsize=16)
    ax.set_xticks(x, labels)
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.set_ylim(top=ax.get_ylim()[1] * 1.15)
    fig.tight_layout()

    plt.subplots_adjust(bottom=0.10)
    ax.text(0, -0.09, FONTE_TEXTO, transform=ax.transAxes,
            ha='left', va='top', fontsize=11, color='#000')
    
    plt.savefig(caminho_para_salvar, dpi=300)
    plt.close(fig)
    return True

def criar_grafico_paridade(df, caminho_para_salvar, titulo_grafico):
    """Cria o Gráfico 8 de paridade com formatação específica e fontes maiores."""
    if df.empty:
        print(f"DataFrame vazio, não é possível gerar o gráfico '{titulo_grafico}'.")
        return False

    categorias = df.iloc[:, 0]
    valores = pd.to_numeric(df.iloc[:, 1])
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(8, 6)) # Tamanho ajustado
    
    # Cores para participante (laranja) e patrocinador (azul escuro)
    cores = ['#DD7E2E', '#0F406D']
    bars = ax.bar(categorias, valores, color=cores)
    
    # --- CORREÇÃO: Formatação dos rótulos como moeda e com fonte maior ---
    ax.bar_label(
        bars, 
        padding=3, 
        fmt='R$ {:_> #,.2f}', # Formato de moeda BRL
        fontsize=11 
    )
    
    # Remove o eixo Y, pois os valores já estão nas barras
    ax.get_yaxis().set_visible(False)
    ax.spines[['top','right', 'left']].set_visible(False)
    
    # --- CORREÇÃO: Aumenta o tamanho da fonte do eixo X ---
    plt.xticks(fontsize=12)
    
    # Aumenta o limite superior para os rótulos caberem bem
    ax.set_ylim(top=ax.get_ylim()[1] * 1.1)

    plt.subplots_adjust(bottom=0.10)
    ax.text(0, -0.09, FONTE_TEXTO, transform=ax.transAxes,
            ha='left', va='top', fontsize=11, color='#000')

    plt.savefig(caminho_para_salvar, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Gráfico de paridade gerado: {caminho_para_salvar}")
    return True
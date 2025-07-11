import os
import datetime
import locale
import win32com.client
import pythoncom
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from docx.shared import RGBColor
from docx.enum.table import WD_ALIGN_VERTICAL


# Importa as funções dos outros módulos que serão usadas aqui
from modules.visualizacoes import gerar_imagem_tabela, criar_grafico_piramide_etaria, criar_grafico_barras_verticais, criar_grafico_donut, criar_grafico_barras_agrupadas, criar_grafico_paridade
from modules.processamento import transformar_dados_evolucao, formatar_tabela_arrecadacao, formatar_tabela_cargo, formatar_tabela_patrocinador

def garantir_estilos(doc):
    """Verifica e formata os estilos essenciais do documento."""
    styles = doc.styles
    FONTE_PADRAO = 'Open Sans'
    
    try:
        style_normal = styles['Normal']
        style_normal.paragraph_format.first_line_indent = None
        font_normal = style_normal.font
        font_normal.name = FONTE_PADRAO
        font_normal.size = Pt(10)
    except KeyError:
        print("Aviso: Estilo 'Normal' não encontrado.")

    nomes_necessarios = {
        'Título 2': {'size': 15, 'bold': True}, 
        'Título 3': {'size': 13, 'bold': True},
        'CorpoComRecuo': {'size': 10, 'first_line_indent': Inches(0.5)}
    }
    
    style_names_in_doc = [s.name for s in styles]

    for nome_pt, props in nomes_necessarios.items():
        if nome_pt not in style_names_in_doc:
            print(f"Criando estilo '{nome_pt}'...")
            base_style = styles['Normal']
            new_style = styles.add_style(nome_pt, 1)
            new_style.base_style = base_style
            font = new_style.font
            font.name = FONTE_PADRAO
            font.size = Pt(props['size'])
            font.bold = props.get('bold', False)
            
            if 'first_line_indent' in props:
                new_style.paragraph_format.first_line_indent = props['first_line_indent']

def adicionar_tabela_nativa_word(documento, df):
    """Adiciona uma tabela nativa, estilizada, compacta e com formatação condicional."""
    if df.empty:
        documento.add_paragraph("[Dados da tabela não encontrados.]", style='CorpoComRecuo')
        return

    table = documento.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    
    # CORREÇÃO 3: Ajusta o layout da tabela para evitar quebras de linha indevidas
    try:
        larguras = (Inches(1.5), Inches(1.1), Inches(1.1), Inches(1.2), Inches(1.1))
        for i, largura in enumerate(larguras):
            table.columns[i].width = largura
    except IndexError:
        print("Aviso: O número de larguras definidas não corresponde ao número de colunas da tabela.")

    # Adiciona e estiliza o cabeçalho
    hdr_cells = table.rows[0].cells
    for i, col_name in enumerate(df.columns):
        cell = hdr_cells[i]
        run = cell.paragraphs[0].add_run(str(col_name))
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shading_elm = parse_xml(r'<w:shd {} w:fill="0F406D"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shading_elm)
    
    table.rows[0]._tr.get_or_add_trPr().append(parse_xml(r'<w:tblHeader {}/>'.format(nsdecls('w'))))

    # Adiciona as linhas de dados com formatação
    for _, row_data in df.iterrows():
        row_cells = table.add_row().cells
        # CORREÇÃO 1: Verifica se esta é a linha de "TOTAL"
        is_total_row = str(row_data.iloc[0]) == 'TOTAL'
        
        for i, cell_data in enumerate(row_data):
            cell = row_cells[i]
            cell.text = str(cell_data)
            paragraph = cell.paragraphs[0]
            
            # CORREÇÃO 2: Centraliza o conteúdo de todas as células
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            # Aplica negrito se for a linha de TOTAL
            if is_total_row:
                for run in paragraph.runs:
                    run.font.bold = True

            # Deixa a tabela mais compacta
            p_format = paragraph.paragraph_format
            p_format.space_before = Pt(3)
            p_format.space_after = Pt(3)

def gerar_relatorio_word(dados, data_alvo):
    """Gera o documento Word completo com todas as seções."""
    TEMPLATE_PATH = 'template.docx'
    try:
        doc = Document(TEMPLATE_PATH)
    except Exception as e:
        print(f"Erro ao abrir o template: {e}")
        return None
    
    garantir_estilos(doc)
    
    mes_ano_texto = data_alvo.strftime("%B de %Y")
    
    # --- 1. INTRODUÇÃO ---
    contador_titulo2 = 1
    doc.add_paragraph(f'{contador_titulo2}. Introdução', style='Título 2')
    doc.add_paragraph(
        "Este relatório, elaborado pela Gerência de Arrecadação e Cadastro (Gearc), consiste em um conjunto de informações, na forma de textos, indicadores, gráficos e tabelas, com o intuito de apresentar o perfil dos participantes, sua distribuição e composição segundo diferentes características.",
        style='CorpoComRecuo'
    )
    contador_titulo2 += 1
    
    # --- 2. CADASTRO ---
    doc.add_paragraph(f'\n{contador_titulo2}. Cadastro', style='Título 2')
    contador_titulo3 = 1
    
    # --- 2.1 EVOLUÇÃO DAS ADESÕES (SEÇÃO REATIVADA) ---
    doc.add_paragraph(f"{contador_titulo2}.{contador_titulo3}. Evolução das Adesões", style='Título 3')
    
    df_evolucao_raw = dados.get('evolucao_adesoes')
    if df_evolucao_raw is not None and not df_evolucao_raw.empty:
        df_evolucao_formatado = transformar_dados_evolucao(df_evolucao_raw, data_alvo)
        
        # --- LÓGICA DE TEXTO DINÂMICO ATUALIZADA ---
        try:
            nome_linha_mes = data_alvo.strftime('%b/%Y').lower()
            df_temp = df_evolucao_formatado.set_index('Mês/Ano')
            aumento_participantes = int(df_temp.loc[nome_linha_mes, 'Total'])
            
            texto_dinamico = f"Com as movimentações ocorridas no mês de {mes_ano_texto}, houve a entrada de {aumento_participantes} participantes na base. As ocorrências estão assim distribuídas:"
            doc.add_paragraph(texto_dinamico, style='CorpoComRecuo')
        except (KeyError, IndexError, Exception) as e:
            print(f"Aviso: Não foi possível calcular a variação do mês para o texto dinâmico. Erro: {e}")
            doc.add_paragraph(f"As ocorrências e movimentações do mês de {mes_ano_texto} estão assim distribuídas:", style='CorpoComRecuo')
        
        p = doc.add_paragraph("Tabela 1. Evolução mensal das adesões")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caminho_imagem_tabela1 = os.path.join('assets', 'tabela_evolucao.png')
        if gerar_imagem_tabela(df_evolucao_formatado, caminho_imagem_tabela1):
            doc.add_picture(caminho_imagem_tabela1, width=Inches(6.2))
    else:
        doc.add_paragraph("[Dados para a tabela de evolução não foram encontrados.]", style='CorpoComRecuo')
        
    doc.add_paragraph("Fonte: DISEG/GEARC")
    contador_titulo3 += 1
    # --- FIM DA SEÇÃO 2.1 ---

    # --- 2.2 Distribuição de participantes por sexo ---
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Distribuição de participantes por sexo", style='Título 3')
    df_sexo = dados.get('distribuicao_sexo')
    if df_sexo is not None and not df_sexo.empty:
        try:
            total_masc = int(df_sexo[df_sexo['SEXO'] == 'M']['QTD'].iloc[0])
            total_fem = int(df_sexo[df_sexo['SEXO'] == 'F']['QTD'].iloc[0])
            total_geral = total_masc + total_fem
            if total_geral > 0:
                percentual_masc = (total_masc / total_geral) * 100
                percentual_fem = (total_fem / total_geral) * 100
                doc.add_paragraph(f"Atualmente, o percentual de participantes está representado em {percentual_masc:.2f}% e {percentual_fem:.2f}% de mulheres.", style='CorpoComRecuo')
            tabela_sexo_resumo = pd.DataFrame({'SITUAÇÃO': ['Total de Participantes'], 'FEMININO': [total_fem], 'MASCULINO': [total_masc], 'TOTAL GERAL': [total_geral]})
            caminho_imagem_tabela_sexo = os.path.join('assets', 'tabela_sexo.png')
            if gerar_imagem_tabela(tabela_sexo_resumo, caminho_imagem_tabela_sexo):
                 doc.add_picture(caminho_imagem_tabela_sexo, width=Inches(6.0))
        except (IndexError, KeyError) as e:
            print(f"ERRO: Não foi possível processar dados de sexo: {e}")
            doc.add_paragraph("[Dados de distribuição por sexo em formato inesperado.]", style='CorpoComRecuo')
    else:
        doc.add_paragraph("[Dados de distribuição por sexo não encontrados.]", style='CorpoComRecuo')
    contador_titulo3 += 1

    # --- 2.3 Distribuição de participantes por Sexo e Grupos de Idade ---
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Distribuição de participantes por Sexo e Grupos de Idade", style='Título 3')
    df_piramide = dados.get('piramide_etaria')
    if df_piramide is not None and not df_piramide.empty:
        try:
            contagem_por_faixa = df_piramide.groupby('Faixa_Etaria')['QTD'].sum()
            maior_faixa = contagem_por_faixa.idxmax()
            texto_concentracao = f"A maior concentração de participantes está distribuída entre as idades de {maior_faixa}."
            doc.add_paragraph(texto_concentracao, style='CorpoComRecuo')
        except Exception as e:
            print(f"Erro ao calcular a maior faixa etária: {e}")
            doc.add_paragraph(f"{texto_concentracao}", style='CorpoComRecuo')
    else:
        doc.add_paragraph("A concentração de participantes está distribuída entre as idades de 36 a 44 anos.", style='CorpoComRecuo')
    
    p = doc.add_paragraph("Gráfico 1. Distribuição de participantes por sexo e grupo de idade*")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_grafico_piramide = os.path.join('assets', 'grafico_piramide_etaria.png')
    if df_piramide is not None:
        if criar_grafico_piramide_etaria(df_piramide, caminho_grafico_piramide):
            doc.add_picture(caminho_grafico_piramide, width=Inches(6.2))
        else:
            doc.add_paragraph("[Falha ao gerar o gráfico de pirâmide etária.]")
    else:
        doc.add_paragraph("[Dados para o gráfico de pirâmide não foram encontrados.]")
    doc.add_paragraph("Fonte: DISEG/GEARC")
    
  # --- 3. ADICIONA A NOVA SEÇÃO 2.4 ---
    contador_titulo2 = 2 # Assumindo que estamos na seção 2
    contador_titulo3 += 1  # Próximo número disponível
    
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Distribuição de participantes por Cargos e Categoria", style='Título 3')
    
    p_legenda_t2 = doc.add_paragraph("Tabela 2. Distribuição de participantes por cargo")
    p_legenda_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_legenda_t2.paragraph_format.space_after = Pt(6)
    
    df_cargos = dados.get('distribuicao_cargos')
    caminho_imagem_tabela_cargos = os.path.join('assets', 'tabela_cargos.png')
    
    if df_cargos is not None and not df_cargos.empty:
        if gerar_imagem_tabela(df_cargos, caminho_imagem_tabela_cargos):
            doc.add_picture(caminho_imagem_tabela_cargos, width=Inches(4.0))
            paragrafo_imagem = doc.paragraphs[-1]
            paragrafo_imagem.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragrafo_imagem.paragraph_format.space_before = Pt(0)
    else:
        doc.add_paragraph("[Dados para a tabela de distribuição por cargos não foram encontrados.]", style='CorpoComRecuo')
        
    p_fonte_t2 = doc.add_paragraph("Fonte: DISEG/GEARC")
    p_fonte_t2.paragraph_format.space_before = Pt(6)

    # --- ADICIONA A NOVA SEÇÃO 2.4 (era 2.5 no doc original) ---
    contador_titulo3 += 1 # Incrementa para o próximo número de seção
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Adesão por Ramo da Justiça", style='Título 3')

    # Texto dinâmico
    df_adesao_mes = dados.get('adesao_ramo_mes')
    df_adesao_acumulado = dados.get('adesao_ramo_acumulado')

    if df_adesao_mes is not None and not df_adesao_mes.empty:
        ramo_maior_adesao = df_adesao_mes.iloc[0, 0]
        numero_maior_adesao = int(df_adesao_mes.iloc[0, 1])
        ramo_maior_total = df_adesao_acumulado.iloc[0, 0]
        numero_maior_total = int(df_adesao_acumulado.iloc[0, 1])

        doc.add_paragraph(
            f"No mês de {data_alvo.strftime('%B/%Y')}, a {ramo_maior_adesao} obteve o maior número de adesões ({numero_maior_adesao}) e, desde o "
            f"início do funcionamento da Funpresp-Jud, a {ramo_maior_total} permanece com o maior número de participantes ({numero_maior_total}).",
            style='CorpoComRecuo'
        )

    # Gráfico 2: Mensal
    p_legenda_g2 = doc.add_paragraph(f"Gráfico 2. Distribuição de participantes por ramo da justiça ({data_alvo.strftime('%B/%Y')})")
    p_legenda_g2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_g2 = os.path.join('assets', 'grafico_adesao_mes.png')
    if criar_grafico_barras_verticais(df_adesao_mes, caminho_g2, "Adesões no Mês por Ramo"):
        doc.add_picture(caminho_g2, width=Inches(6.2))
    doc.add_paragraph("Fonte: DISEG/GEARC")

    # Gráfico 3: Acumulado
    p_legenda_g3 = doc.add_paragraph("Gráfico 3. Distribuição de participantes por ramo da justiça (acumulado)")
    p_legenda_g3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_g3 = os.path.join('assets', 'grafico_adesao_acumulado.png')
    if criar_grafico_barras_verticais(df_adesao_acumulado, caminho_g3, "Total de Participantes por Ramo"):
        doc.add_picture(caminho_g3, width=Inches(6.2))
    doc.add_paragraph("Fonte: DISEG/GEARC")

    # --- NOVA SEÇÃO 2.5: ADESÕES POR PATROCINADOR ---
   # --- 2.5 Adesões por Patrocinador ---
    contador_titulo2 = 2 # Exemplo
    contador_titulo3 += 1 # Exemplo
    
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Adesões por Patrocinador", style='Título 3')
    
    p_legenda_t3 = doc.add_paragraph("Tabela 3. Adesões por patrocinador")
    p_legenda_t3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_legenda_t3.paragraph_format.space_before = Pt(12)
    p_legenda_t3.paragraph_format.space_after = Pt(6)

    adicionar_tabela_nativa_word(doc, dados.get('adesoes_patrocinador'))

    p_fonte_t3 = doc.add_paragraph("Fonte: DISEG/GEARC")
    p_fonte_t3.paragraph_format.space_before = Pt(6)


     # --- SEÇÃO ATUALIZADA: REGIME DE TRIBUTAÇÃO ---
    contador_titulo3 += 1
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Regime de Tributação (Imposto de Renda)", style='Título 3')
    

    # --- Gráfico 4: MENSAL ---
    df_tributacao_mes = dados.get('regime_tributacao_mes')
    if df_tributacao_mes is not None and not df_tributacao_mes.empty:
        try:
            total_mes = df_tributacao_mes['Quantidade'].sum()
            # Converte os dados para um formato fácil de buscar
            opcoes = df_tributacao_mes.set_index('IC_TRIBUTACAO')['Quantidade']
            
            # Pega a quantidade de cada opção, com 0 se não existir
            qtd_regressiva = opcoes.get('R', 0)
            qtd_progressiva = opcoes.get('P', 0)
            qtd_sem_opcao = opcoes.get('N', 0)
            
            # Calcula os percentuais
            perc_regressiva = (qtd_regressiva / total_mes) * 100 if total_mes > 0 else 0
            perc_progressiva = (qtd_progressiva / total_mes) * 100 if total_mes > 0 else 0
            perc_sem_opcao = (qtd_sem_opcao / total_mes) * 100 if total_mes > 0 else 0

            # Monta o texto completo
            texto_dinamico = (
                f"Em {data_alvo.strftime('%B/%Y')}, o perfil de tributação demonstra a preferência de {perc_regressiva:.0f}% dos participantes pelo regime regressivo (Gráfico 4). "
            )
            doc.add_paragraph(texto_dinamico, style='CorpoComRecuo')

        except Exception as e:
            print(f"Aviso: Não foi possível gerar o texto dinâmico de tributação. Erro: {e}")
    
    # Adiciona o segundo parágrafo, que é estático
    p_lei = doc.add_paragraph(style='CorpoComRecuo')
    p_lei.add_run("No acumulado percebemos uma grande preferência pelo regime regressivo de tributação (Gráfico 5). Com base na ")
    p_lei.add_run("Lei 14.803").bold = True
    p_lei.add_run(", datada de ")
    p_lei.add_run("10/1/2024").bold = True
    p_lei.add_run(", houve uma importante alteração no regime de tributação para os participantes de planos de previdência complementar. Agora, ")
    p_lei.add_run("os participantes").bold = True
    p_lei.add_run(" têm a liberdade de escolher entre os regimes ")
    p_lei.add_run("progressivo ou regressivo").bold = True
    p_lei.add_run(" no momento da obtenção do benefício ou do primeiro resgate dos valores acumulados.")
    # --- FIM DA LÓGICA DE TEXTO ---

    # Gráfico 4: Mensal
    p_legenda_g4 = doc.add_paragraph(f"Gráfico 4. Distribuição regime de tributação ({data_alvo.strftime('%B/%Y')})")
    p_legenda_g4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_g4 = os.path.join('assets', 'grafico_tributacao_mes.png')
    if criar_grafico_donut(df_tributacao_mes, caminho_g4, f"Regime de Tributação ({data_alvo.strftime('%B/%Y')})"):
        doc.add_picture(caminho_g4, width=Inches(5.0))
        paragrafo_grafico = doc.paragraphs[-1]; paragrafo_grafico.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Gráfico 5: Acumulado
    p_legenda_g5 = doc.add_paragraph("Gráfico 5. Distribuição regime de tributação (acumulado)")
    p_legenda_g5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_g5 = os.path.join('assets', 'grafico_tributacao_acumulado.png')
    if criar_grafico_donut(dados.get('regime_tributacao_acumulado'), caminho_g5, "Regime de Tributação (Acumulado)"):
        doc.add_picture(caminho_g5, width=Inches(5.0))
        paragrafo_grafico = doc.paragraphs[-1]; paragrafo_grafico.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph("Fonte: DISEG/GEARC")

    # --- NOVA SEÇÃO 2.8: PERCENTUAL DE CONTRIBUIÇÃO ---
    contador_titulo3 += 1 # Incrementa o contador para a nova seção
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Percentual de Contribuição", style='Título 3')

    # Parágrafo 1 (estático)
    doc.add_paragraph(
        "Um bom sinal da qualidade da opção dos participantes é relacionado ao percentual escolhido. "
        "Segregando as categorias de participantes vinculados e patrocinados percebemos a opção oposta "
        "em relação à escolha do percentual de contribuição mensal.",
        style='CorpoComRecuo'
    )

    # --- Lógica para os parágrafos dinâmicos ---
    df_mes = dados.get('percentual_contrib_mes')
    df_acumulado = dados.get('percentual_contrib_acumulado')

    if df_mes is not None and df_acumulado is not None and not df_mes.empty and not df_acumulado.empty:
        try:
            # --- Cálculos para o texto ---
            # Assegura que a coluna de percentual seja numérica
            df_mes['PERCENTUAL'] = pd.to_numeric(df_mes['PERCENTUAL'])
            df_acumulado['PERCENTUAL'] = pd.to_numeric(df_acumulado['PERCENTUAL'])

            # Dados Mensais
            df_mes_vinc = df_mes[df_mes['NM_SITUACAO'] == 'VINCULADO']
            total_vinc_mes = df_mes_vinc['QTD'].sum()
            qtd_vinc_65_mes = df_mes_vinc[df_mes_vinc['PERCENTUAL'] == 6.5]['QTD'].sum()
            perc_vinc_65_mes = (qtd_vinc_65_mes / total_vinc_mes) * 100 if total_vinc_mes > 0 else 0

            df_mes_patro = df_mes[df_mes['NM_SITUACAO'] == 'PATROCINADO']
            total_patro_mes = df_mes_patro['QTD'].sum()
            qtd_patro_85_mes = df_mes_patro[df_mes_patro['PERCENTUAL'] == 8.5]['QTD'].sum()
            perc_patro_85_mes = (qtd_patro_85_mes / total_patro_mes) * 100 if total_patro_mes > 0 else 0

            # Dados Acumulados
            df_acum_vinc = df_acumulado[df_acumulado['NM_SITUACAO'] == 'VINCULADO']
            total_vinc_acum = df_acum_vinc['QTD'].sum()
            qtd_vinc_65_acum = df_acum_vinc[df_acum_vinc['PERCENTUAL'] == 6.5]['QTD'].sum()
            perc_vinc_65_acum = (qtd_vinc_65_acum / total_vinc_acum) * 100 if total_vinc_acum > 0 else 0

            df_acum_patro = df_acumulado[df_acumulado['NM_SITUACAO'] == 'PATROCINADO']
            total_patro_acum = df_acum_patro['QTD'].sum()
            qtd_patro_85_acum = df_acum_patro[df_acum_patro['PERCENTUAL'] == 8.5]['QTD'].sum()
            perc_patro_85_acum = (qtd_patro_85_acum / total_patro_acum) * 100 if total_patro_acum > 0 else 0

            # Parágrafo 2 (Vinculados)
            texto_vinculados = (
                f"Para os participantes vinculados a melhor opção é a escolha do percentual mínimo (6,5%), "
                f"com o objetivo de aproveitar a isenção da taxa de carregamento sobre a contribuição facultativa. "
                f"Em {data_alvo.strftime('%B/%Y')}, {perc_vinc_65_mes:.2f}% dos participantes vinculados optaram pelo percentual de 6,5% "
                f"e a opção pelo percentual mínimo chega a {perc_vinc_65_acum:.2f}% da preferência dos participantes "
                f"desde o início do funcionamento do plano."
            )
            doc.add_paragraph(texto_vinculados, style='CorpoComRecuo')

            # Parágrafo 3 (Patrocinados)
            texto_patrocinados = (
                f"Para os participantes patrocinados a opção mais vantajosa é contribuir com o percentual máximo (8,5%), "
                f"obtendo a contrapartida máxima da contribuição patronal. Em {data_alvo.strftime('%B/%Y')}, "
                f"{perc_patro_85_mes:.2f}% dos participantes optaram pelo percentual máximo. Já no acumulado, "
                f"desde o início do plano, temos {perc_patro_85_acum:.2f}% dos participantes com o percentual de 8,5%."
            )
            doc.add_paragraph(texto_patrocinados, style='CorpoComRecuo')

        except Exception as e:
            print(f"Aviso: não foi possível gerar o texto dinâmico de percentuais. Erro: {e}")
            doc.add_paragraph("[Não foi possível gerar os textos descritivos para esta seção.]", style='CorpoComRecuo')
    else:
        doc.add_paragraph("[Dados insuficientes para gerar os textos descritivos.]", style='CorpoComRecuo')

    # Gráfico 6: Mensal
    p_legenda_g6 = doc.add_paragraph(f"Gráfico 6. Distribuição do percentual de contribuição ({data_alvo.strftime('%B/%Y')})")
    p_legenda_g6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_g6 = os.path.join('assets', 'grafico_percentual_mes.png')
    if criar_grafico_barras_agrupadas(df_mes, caminho_g6, f"Distribuição Mensal ({data_alvo.strftime('%B/%Y')})"):
        doc.add_picture(caminho_g6, width=Inches(6.2))
    doc.add_paragraph("Fonte: DISEG/GEARC")

    # Gráfico 7: Acumulado
    p_legenda_g7 = doc.add_paragraph("Gráfico 7. Distribuição do percentual de contribuição (acumulado)")
    p_legenda_g7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_g7 = os.path.join('assets', 'grafico_percentual_acumulado.png')
    if criar_grafico_barras_agrupadas(df_acumulado, caminho_g7, "Distribuição Acumulada"):
        doc.add_picture(caminho_g7, width=Inches(6.2))
    doc.add_paragraph("Fonte: DISEG/GEARC")

      # --- NOVA SEÇÃO 3: ARRECADAÇÃO ---
    contador_titulo2 += 1
    doc.add_paragraph(f'\n{contador_titulo2}. Arrecadação', style='Título 2')
    
    # --- Lógica do Texto e Tabela 4 ---
    df_arrec_tabela = dados.get('arrecadacao_tabela')
    if df_arrec_tabela is not None and not df_arrec_tabela.empty:
        try:
            # Pega o valor da primeira linha (mês atual) e segunda (outras)
            valor_mes_atual = df_arrec_tabela.iloc[0, 1]
            valor_outras = df_arrec_tabela.iloc[1, 1]
            doc.add_paragraph(
                f"A arrecadação das contribuições no mês de {data_alvo.strftime('%B/%Y')} atingiu o valor de R$ {valor_mes_atual / 1_000_000:.1f} milhões. "
                f"Foram arrecadados aproximadamente R$ {valor_outras / 1_000_000:.1f} milhões referente a contribuições de outras competências.",
                style='CorpoComRecuo'
            )
            # Formata a coluna de contribuição como moeda
            df_arrec_tabela['CONTRIBUIÇÃO'] = df_arrec_tabela['CONTRIBUIÇÃO'].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
        except Exception as e:
            print(f"Aviso: Não foi possível gerar texto dinâmico de arrecadação. Erro: {e}")

    p_legenda_t4 = doc.add_paragraph("Tabela 4. Arrecadação de contribuições por mês competência")
    p_legenda_t4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_t4 = os.path.join('assets', 'tabela_arrecadacao.png')
    if gerar_imagem_tabela(df_arrec_tabela, caminho_t4):
        doc.add_picture(caminho_t4, width=Inches(4.0))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Fonte: DISEG/GEARC")

    # --- Lógica do Texto e Gráfico 8 ---
    df_arrec_grafico = dados.get('arrecadacao_grafico')
    
    # --- CORREÇÃO: Adiciona o texto dinâmico ---
    if df_arrec_grafico is not None and not df_arrec_grafico.empty:
        try:
            # Extrai valores para o texto
            s_paridade = df_arrec_grafico.set_index('Categoria')['Valor']
            contrib_participante = s_paridade.get('PARTICIPANTE', 0)
            contrib_patrocinador = s_paridade.get('PATROCINADOR', 0)
            diferenca = abs(contrib_participante - contrib_patrocinador)
            
            # Formata o valor da diferença como moeda brasileira
            diferenca_formatada = f"R$ {diferenca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            p_paridade = doc.add_paragraph(style='CorpoComRecuo')
            p_paridade.add_run("Verificamos a paridade das contribuições entre participante e patrocinador, identificando uma diferença de ")
            p_paridade.add_run(diferenca_formatada).bold = True
            p_paridade.add_run(". Grande parte desse valor se deve ao repasse realizado por um dos órgãos apenas da contribuição dos participantes, sem o correspondente aporte do patrocinador.")

        except Exception as e:
            print(f"Aviso: Não foi possível gerar texto dinâmico de paridade. Erro: {e}")

    p_legenda_g8 = doc.add_paragraph("\nGráfico 8. Contribuição normal (participante e patrocinador)")
    p_legenda_g8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_legenda_g8.paragraph_format.space_after = Pt(6)

    caminho_g8 = os.path.join('assets', 'grafico_paridade.png')
    
    # --- CORREÇÃO: Chama a nova função de gráfico dedicada ---
    if criar_grafico_paridade(df_arrec_grafico, caminho_g8, "Paridade de Contribuição"):
        doc.add_picture(caminho_g8, width=Inches(5.0))
        paragrafo_grafico = doc.paragraphs[-1]
        paragrafo_grafico.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragrafo_grafico.paragraph_format.space_before = Pt(0)
    
    p_fonte_g8 = doc.add_paragraph("Fonte: DISEG/GEARC")
    p_fonte_g8.paragraph_format.space_before = Pt(6)
    
     # --- NOVA SEÇÃO 3.1: ARRECADAÇÃO DE CONTRIBUIÇÃO TOTAL ---
    contador_titulo2 = 3 # Agora é a seção 3
    contador_titulo3 = 1
    doc.add_paragraph(f"\n{contador_titulo2}.1. Arrecadação de contribuição total", style='Título 3')
    
    # Texto 1 (estático)
    doc.add_paragraph("Abaixo demonstramos a distribuição das contribuições que resultaram no total arrecadado para o mês, bem como a variação percentual em relação ao mês anterior:", style='CorpoComRecuo')

    p_legenda_t5 = doc.add_paragraph("Tabela 5. Arrecadação por tipo de contribuição")
    p_legenda_t5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Pega os dados brutos e formata para exibição
    df_arrec_raw = dados.get('arrecadacao_tipo')
    df_arrec_formatado = formatar_tabela_arrecadacao(df_arrec_raw.copy(), data_alvo)
    
    caminho_t5 = os.path.join('assets', 'tabela_arrecadacao_tipo.png')
    if gerar_imagem_tabela(df_arrec_formatado, caminho_t5):
        doc.add_picture(caminho_t5, width=Inches(6.2))
        # ... (código para centralizar imagem)
    
    doc.add_paragraph("Fonte: DISEG/GEARC")

    # Texto 2 (dinâmico)
    df_arrec_raw = dados.get('arrecadacao_tipo')
    if df_arrec_raw is not None and not df_arrec_raw.empty:
        try:
            # Pega a linha de totais para análise
            total_row = df_arrec_raw[df_arrec_raw['Contribuicao'] == 'TOTAL'].iloc[0]
            variacao_total = total_row['Variacao']
            
            # Define o texto de aumento ou queda
            status_variacao = "um aumento" if variacao_total > 0 else "uma queda"
            
            # Encontra qual tipo de contribuição teve o maior impacto na mudança
            df_tipos = df_arrec_raw[df_arrec_raw['Contribuicao'] != 'TOTAL'].copy()
            df_tipos['dif_abs'] = abs(df_tipos['mes_atual'] - df_tipos['mes_passado'])
            maior_impacto = df_tipos.loc[df_tipos['dif_abs'].idxmax()]
            tipo_maior_impacto = maior_impacto['Contribuicao'].lower()

            texto_dinamico2 = (
                f"Com base na tabela acima, observa-se que o total arrecadado em {data_alvo.strftime('%B de %Y')} "
                f"apresentou {status_variacao} de {abs(variacao_total):.2f}% em relação a { (data_alvo - pd.DateOffset(months=1)).strftime('%B de %Y')}. "
                f"Essa variação foi impulsionada, sobretudo, pela arrecadação da contribuição {tipo_maior_impacto}."
            )
            doc.add_paragraph(texto_dinamico2, style='CorpoComRecuo')

        except Exception as e:
            print(f"Aviso: não foi possível gerar o texto dinâmico da Tabela 5. Erro: {e}")

    contador_titulo2 = 3 # Agora é a seção 3
    contador_titulo3 += 1
        # --- NOVA SEÇÃO 3.2: ARRECADAÇÃO POR CARGO ---
    """Adiciona a seção 3.2 de Arrecadação por Cargo."""
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3} Arrecadação de contribuições por cargo", style='Título 3')

    df_cargo_raw = dados.get('arrecadacao_cargo')
    
    if df_cargo_raw is not None and not df_cargo_raw.empty:
        try:
            # --- CORREÇÃO APLICADA AQUI ---
            # Ordena os dados usando o nome da coluna sem acento ('ContribuicaoMedia')
            df_ordenado = df_cargo_raw.sort_values(by='ContribuicaoMedia', ascending=False)
            
            # Extrai os valores para o texto dinâmico (exemplo)
            juizes_media = df_ordenado[df_ordenado['CARGO'] == 'JUÍZES E MEMBROS']['ContribuicaoMedia'].iloc[0]
            analistas_media = df_ordenado[df_ordenado['CARGO'] == 'ANALISTAS']['ContribuicaoMedia'].iloc[0]
            
            # Constrói o texto dinâmico (exemplo)
            texto_p1 = doc.add_paragraph(style='CorpoComRecuo')
            texto_p1.add_run("Analisando a contribuição média dos participantes patrocinados, observa-se que os Juízes e Membros ocupam a primeira posição, com um valor médio de ")
            texto_p1.add_run(f"{locale.currency(juizes_media, grouping=True)}").bold = True
            texto_p1.add_run(", seguidos pelos Analistas, com ")
            texto_p1.add_run(f"{locale.currency(analistas_media, grouping=True)}.").bold = True
            
            # Adiciona os outros parágrafos
            doc.add_paragraph("Ressalta-se que o cenário apresentado considera apenas as contribuições normais, referentes ao mês corrente e às competências anteriores, tanto dos participantes quanto dos patrocinadores.", style='CorpoComRecuo')
            doc.add_paragraph("O detalhamento da arrecadação, bem como a quantidade de participantes por cargo, pode ser visualizado na Tabela 6.", style='CorpoComRecuo')

            # Gera a imagem da tabela
            p_legenda_t6 = doc.add_paragraph("Tabela 6. Arrecadação por cargo/representatividade (participantes patrocinados)")
            p_legenda_t6.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Chama a função de formatação
            df_cargo_formatado = formatar_tabela_cargo(df_cargo_raw.copy())
            caminho_t6 = os.path.join('assets', 'tabela_arrecadacao_cargo.png')
            
            if gerar_imagem_tabela(df_cargo_formatado, caminho_t6):
                doc.add_picture(caminho_t6, width=Inches(6.2))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph("Fonte: DISEG/GEARC")

        except Exception as e:
            print(f"Aviso: não foi possível gerar a seção de arrecadação por cargo. Erro: {e}")

     # --- NOVA SEÇÃO 3.3: CONTRIBUIÇÕES POR RAMO DA JUSTIÇA ---
    contador_titulo3 += 1 # Incrementa para o próximo número
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Contribuições por ramo da justiça", style='Título 3')

    # Lógica para o texto dinâmico
    df_contrib_ramo_mes = dados.get('contribuicao_ramo_mes')
    if df_contrib_ramo_mes is not None and not df_contrib_ramo_mes.empty:
        # A query já ordena por valor, então o primeiro da lista é o maior
        ramo_maior_volume = df_contrib_ramo_mes.iloc[0, 0]
        
        texto_dinamico = (
            f"Em {data_alvo.strftime('%B/%Y')} a {ramo_maior_volume} teve o maior volume de contribuições. "
            "Desde o início do plano, temos a Justiça Trabalhista com maior patrimônio acumulado."
        )
        doc.add_paragraph(texto_dinamico, style='CorpoComRecuo')
    
    # Gráfico 9: Mensal
    p_legenda_g9 = doc.add_paragraph(f"Gráfico 9. Distribuição de contribuições por ramo do patrocinador ({data_alvo.strftime('%B/%Y')})")
    p_legenda_g9.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_g9 = os.path.join('assets', 'grafico_contribuicao_ramo_mes.png')
    
    # Reutilizando nossa função de gráfico de barras!
    if criar_grafico_barras_verticais(df_contrib_ramo_mes, caminho_g9, "Contribuição Mensal por Ramo", formato_label='percent_only'):
        doc.add_picture(caminho_g9, width=Inches(6.2))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("Fonte: DISEG/GEARC")

    p_legenda_g10 = doc.add_paragraph("\nGráfico 10. Distribuição do patrimônio por ramo da justiça (acumulado)")
    p_legenda_g10.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caminho_g10 = os.path.join('assets', 'grafico_patrimonio_acumulado.png')
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Chama a mesma função, mas com o novo parâmetro para mostrar apenas a porcentagem
    if criar_grafico_barras_verticais(
        dados.get('patrimonio_ramo_acumulado'), 
        caminho_g10, 
        "", 
        formato_label='percent_only' # <--- NOVO PARÂMETRO
    ):
        doc.add_picture(caminho_g10, width=Inches(6.2))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph("Fonte: DISEG/GEARC")

     # --- NOVA SEÇÃO 3.4: CONTRIBUIÇÕES POR PATROCINADOR ---
    contador_titulo3 += 1 # Ajuste o número da seção conforme necessário
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Contribuições por patrocinador", style='Título 3')
    
    df_patrocinador_raw = dados.get('contribuicao_patrocinador')
    
    if df_patrocinador_raw is not None and not df_patrocinador_raw.empty:
        # Texto dinâmico
        patrocinador_mes = df_patrocinador_raw.iloc[0]['Patrocinador']
        df_sorted_acumulado = df_patrocinador_raw.sort_values(by='contribuicoes_acumuladas', ascending=False)
        patrocinador_acumulado = df_sorted_acumulado.iloc[0]['Patrocinador']
        
        doc.add_paragraph(
            f"Em {data_alvo.strftime('%B/%Y')}, o {patrocinador_mes} ficou no topo do ranking na contribuição mensal e "
            f"o {patrocinador_acumulado} continua com o maior patrimônio por patrocinador.",
            style='CorpoComRecuo'
        )

        # Formata e adiciona a tabela nativa
        p_legenda_t7 = doc.add_paragraph("Tabela 7. Arrecadação e Patrimônio por patrocinador")
        p_legenda_t7.alignment = WD_ALIGN_PARAGRAPH.CENTER
        df_patrocinador_formatado = formatar_tabela_patrocinador(df_patrocinador_raw.copy())
        adicionar_tabela_nativa_word(doc, df_patrocinador_formatado)
        
    doc.add_paragraph("Fonte: DISEG/GEARC")

    nome_arquivo = f"Relatorio_Gerencial_Completo_{data_alvo.strftime('%Y-%m')}.docx"
    doc.save(nome_arquivo)
    print(f"\nRelatório '{nome_arquivo}' gerado com sucesso!")
    return nome_arquivo

def converter_docx_para_pdf(caminho_docx):
    """Converte um arquivo .docx para .pdf usando o Microsoft Word."""
    pythoncom.CoInitialize()
    try:
        word = win32com.client.Dispatch("Word.Application"); word.visible = False
        doc_path = os.path.abspath(caminho_docx); pdf_path = os.path.splitext(doc_path)[0] + ".pdf"
        doc = word.Documents.Open(doc_path); doc.SaveAs(pdf_path, FileFormat=17); doc.Close(); word.Quit()
        print(f"Arquivo convertido para PDF: {pdf_path}"); return True
    except Exception as e: print(f"Erro ao converter para PDF: {e}"); return False
    finally: pythoncom.CoUninitialize()
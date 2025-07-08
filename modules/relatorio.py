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

# Importa as funções dos outros módulos que serão usadas aqui
from modules.visualizacoes import gerar_imagem_tabela, criar_grafico_piramide_etaria
from modules.visualizacoes import gerar_imagem_tabela, criar_grafico_piramide_etaria, criar_grafico_barras_verticais
from modules.processamento import transformar_dados_evolucao


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
    """Adiciona uma tabela nativa, estilizada e compacta ao Word."""
    if df.empty:
        documento.add_paragraph("[Dados da tabela não encontrados.]", style='CorpoComRecuo')
        return

    table = documento.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    
    # Adiciona e estiliza o cabeçalho
    hdr_cells = table.rows[0].cells
    for i, col_name in enumerate(df.columns):
        cell = hdr_cells[i]
        run = cell.paragraphs[0].add_run(str(col_name))
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        # Ajusta o espaçamento do parágrafo do cabeçalho
        cell.paragraphs[0].paragraph_format.space_before = Pt(6)
        cell.paragraphs[0].paragraph_format.space_after = Pt(6)
        # Colore o fundo da célula
        shading_elm = parse_xml(r'<w:shd {} w:fill="0F406D"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shading_elm)
    
    table.rows[0]._tr.get_or_add_trPr().append(parse_xml(r'<w:tblHeader {}/>'.format(nsdecls('w'))))

    # Adiciona as linhas de dados
    for _, row_data in df.iterrows():
        row_cells = table.add_row().cells
        # Verifica se esta é a linha de "TOTAIS"
        is_total_row = str(row_data.iloc[0]) == 'TOTAIS'
        
        for i, cell_data in enumerate(row_data):
            cell = row_cells[i]
            cell.text = str(cell_data)
            paragraph = cell.paragraphs[0]
            
            # --- CORREÇÃO 1: Deixa a tabela mais compacta ---
            # Remove o espaçamento antes e depois dos parágrafos em todas as células de dados
            p_format = paragraph.paragraph_format
            p_format.space_before = Pt(3)
            p_format.space_after = Pt(3)
            
            # --- CORREÇÃO 2: Deixa a linha de TOTAIS em negrito ---
            if is_total_row:
                for run in paragraph.runs:
                    run.font.bold = True

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
            
            texto_dinamico = f"Com as movimentações ocorridas no mês de {mes_ano_texto}, houve aumento de {aumento_participantes} participantes na base. As ocorrências estão assim distribuídas:"
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
    contador_titulo3 = 4 # Próximo número disponível
    
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
    contador_titulo3 = 5 # Exemplo
    
    doc.add_paragraph(f"\n{contador_titulo2}.{contador_titulo3}. Adesões por Patrocinador", style='Título 3')
    
    p_legenda_t3 = doc.add_paragraph("Tabela 3. Adesões por patrocinador")
    p_legenda_t3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_legenda_t3.paragraph_format.space_before = Pt(12)
    p_legenda_t3.paragraph_format.space_after = Pt(6)

    adicionar_tabela_nativa_word(doc, dados.get('adesoes_patrocinador'))

    p_fonte_t3 = doc.add_paragraph("Fonte: DISEG/GEARC")
    p_fonte_t3.paragraph_format.space_before = Pt(6)

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
import os
import datetime
import locale
import win32com.client
import pythoncom
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Importa as funções dos outros módulos que serão usadas aqui
from modules.visualizacoes import gerar_imagem_tabela, criar_grafico_piramide_etaria
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
                doc.add_paragraph(f"Atualmente, o percentual de paricipantes está representado em {percentual_masc:.2f}% e {percentual_fem:.2f}% de mulheres.", style='CorpoComRecuo')
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
            doc.add_picture(caminho_imagem_tabela_cargos, width=Inches(4.2))
            paragrafo_imagem = doc.paragraphs[-1]
            paragrafo_imagem.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragrafo_imagem.paragraph_format.space_before = Pt(0)
    else:
        doc.add_paragraph("[Dados para a tabela de distribuição por cargos não foram encontrados.]", style='CorpoComRecuo')
        
    p_fonte_t2 = doc.add_paragraph("Fonte: DISEG/GEARC")
    p_fonte_t2.paragraph_format.space_before = Pt(6)

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
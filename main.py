import pandas as pd
from sqlalchemy import create_engine
import urllib
import datetime
import locale
import os
import win32com.client
import pythoncom

# --- Módulos do projeto ---
from config import DB_CONFIG
from modules.relatorio import gerar_relatorio_word, converter_docx_para_pdf
from modules.database import conectar_banco, buscar_dados
from queries.tabela1_evolucao_adesoes import gerar_query as gerar_query_evolucao
from queries.tabela2_distribuicao_sexo import QUERY as query_distribuicao_sexo
from queries.tabela3_distribuicao_cargos import QUERY as query_distribuicao_cargos
from queries.grafico1_piramide_etaria import QUERY as query_piramide_etaria

def solicitar_data_relatorio():
    """Solicita ao usuário o ano e o mês para o relatório."""
    while True:
        try:
            ano = int(input(">>> Digite o ano do relatório (ex: 2025): "))
            if 2000 < ano < 2100: break
            else: print("Ano inválido, por favor tente novamente.")
        except ValueError: print("Entrada inválida. Por favor, digite um número para o ano.")
    
    while True:
        try:
            mes = int(input(">>> Digite o mês do relatório (ex: 5 para maio): "))
            if 1 <= mes <= 12: break
            else: print("Mês inválido, por favor digite um número de 1 a 12.")
        except ValueError: print("Entrada inválida. Por favor, digite um número para o mês.")
            
    return datetime.date(ano, mes, 1)

def main():
    """Função principal que orquestra a automação do relatório."""
    print("--- Automação do Relatório Gerencial ---")
    
    data_alvo = solicitar_data_relatorio()
    ano_alvo = data_alvo.year
    mes_alvo = data_alvo.month
    
    print(f"\nGerando relatório para o período de {data_alvo.strftime('%B de %Y')}...")
    
    engine = conectar_banco()
    if engine is None: return

    dados_relatorio = {}
    
    # --- LÓGICA DE QUERY DINÂMICA UNIFICADA ---
    # Para todas as queries, vamos construir a string completa em Python.
    
    # 1. Gerar query de Evolução (método já estava correto)
    print("\nBuscando dados para Evolução das Adesões...")
    query_evolucao_dinamica = gerar_query_evolucao(ano_alvo, mes_alvo)
    dados_relatorio['evolucao_adesoes'] = buscar_dados(query_evolucao_dinamica, engine)
    
    # 2. Gerar as outras queries dinamicamente, substituindo o '?'
    param_texto_data = f"{ano_alvo}{mes_alvo:02d}"
    
    print("\nBuscando dados para Distribuição por Sexo...")
    # Substitui o '?' na query pelo texto da data, que já está entre aspas
    query_sexo_dinamica = query_distribuicao_sexo.replace('?', f"'{param_texto_data}'")
    # Executa a query completa, sem enviar 'params'
    dados_relatorio['distribuicao_sexo'] = buscar_dados(query_sexo_dinamica, engine)
    
    print("\nBuscando dados para o Gráfico de Pirâmide Etária...")
    # Faz o mesmo para a outra consulta
    query_piramide_dinamica = query_piramide_etaria.replace('?', f"'{param_texto_data}'")
    dados_relatorio['piramide_etaria'] = buscar_dados(query_piramide_dinamica, engine)

      # --- 2. EXECUTA A NOVA QUERY ---
    print("\nBuscando dados para Distribuição por Cargos...")
    query_cargos_dinamica = query_distribuicao_cargos.replace('?', f"'{param_texto_data}'")
    dados_relatorio['distribuicao_cargos'] = buscar_dados(query_cargos_dinamica, engine)
    
    # --- Geração dos arquivos ---
    nome_arquivo_docx = gerar_relatorio_word(dados_relatorio, data_alvo)
    
    if nome_arquivo_docx:
        converter_docx_para_pdf(nome_arquivo_docx)

    print("\n--- Processo finalizado com sucesso! ---")

if __name__ == "__main__":
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    main()
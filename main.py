import pandas as pd
from sqlalchemy import create_engine
import urllib
import datetime
import locale
import os
import win32com.client
import pythoncom
from config import DB_CONFIG
from modules.relatorio import gerar_relatorio_word, converter_docx_para_pdf
from modules.database import conectar_banco, buscar_dados
from queries.tabela1_evolucao_adesoes import gerar_query as gerar_query_evolucao
from queries.tabela_distribuicao_sexo import QUERY as query_distribuicao_sexo
from queries.tabela2_distribuicao_cargos import QUERY as query_distribuicao_cargos
from queries.grafico1_piramide_etaria import QUERY as query_piramide_etaria
from queries.grafico2_adesao_ramo_mes import gerar_query as gerar_query_g2_ramo_mes
from queries.grafico3_adesao_ramo_acumulado import gerar_query as gerar_query_g3_ramo_acumulado
from queries.tabela3_adesoes_patrocinador import gerar_query as gerar_query_patrocinador
from queries.tabela4_arrecadacao_mes import gerar_query as gerar_query_tabela4
from queries.tabela5_arrecadacao_tipo import gerar_query as gerar_query_tabela5
from queries.grafico4_tributacao_mes import gerar_query as gerar_query_g4_tributacao
from queries.grafico5_tributacao_acumulado import gerar_query as gerar_query_g5_tributacao
from queries.grafico6_percentual_contrib_mes import gerar_query as gerar_query_g6
from queries.grafico7_percentual_contrib_acumulado import gerar_query as gerar_query_g7
from queries.grafico8_contribuicao_paridade import gerar_query as gerar_query_grafico8
from queries.tabela6_arrecadacao_cargo import gerar_query as gerar_query_tabela6
from queries.grafico9_contribuicao_ramo_mes import gerar_query as gerar_query_g9
from queries.grafico10_patrimonio_ramo_acumulado import gerar_query as gerar_query_g10

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

    params_ano_mes_int = [ano_alvo, mes_alvo]
    param_texto_data = f"{ano_alvo}{mes_alvo:02d}"
    params_texto = [param_texto_data]
    

    print("\nBuscando dados para Evolução das Adesões...")
    query_evolucao_dinamica = gerar_query_evolucao(ano_alvo, mes_alvo)
    dados_relatorio['evolucao_adesoes'] = buscar_dados(query_evolucao_dinamica, engine)
    
    param_texto_data = f"{ano_alvo}{mes_alvo:02d}"
    
    print("\nBuscando dados para Distribuição por Sexo...")
    query_sexo_dinamica = query_distribuicao_sexo.replace('?', f"'{param_texto_data}'")
    dados_relatorio['distribuicao_sexo'] = buscar_dados(query_sexo_dinamica, engine)
    
    print("\nBuscando dados para o Gráfico de Pirâmide Etária...")
    query_piramide_dinamica = query_piramide_etaria.replace('?', f"'{param_texto_data}'")
    dados_relatorio['piramide_etaria'] = buscar_dados(query_piramide_dinamica, engine)

    print("\nBuscando dados para Distribuição por Cargos...")
    query_cargos_dinamica = query_distribuicao_cargos.replace('?', f"'{param_texto_data}'")
    dados_relatorio['distribuicao_cargos'] = buscar_dados(query_cargos_dinamica, engine)

    print("\nBuscando dados para Gráfico de Adesão Mensal por Ramo...")
    query_g2_dinamica = gerar_query_g2_ramo_mes(ano_alvo, mes_alvo)
    dados_relatorio['adesao_ramo_mes'] = buscar_dados(query_g2_dinamica, engine)
    
    print("\nBuscando dados para Gráfico de Adesão Acumulada por Ramo...")
    query_g3_dinamica = gerar_query_g3_ramo_acumulado(ano_alvo, mes_alvo)
    dados_relatorio['adesao_ramo_acumulado'] = buscar_dados(query_g3_dinamica, engine)

    print("\nBuscando dados para Adesões por Patrocinador...")
    query_patrocinador_dinamica = gerar_query_patrocinador(ano_alvo, mes_alvo)
    dados_relatorio['adesoes_patrocinador'] = buscar_dados(query_patrocinador_dinamica, engine)

    print("\nBuscando dados para o Gráfico Mensal de Regime de Tributação...")
    query_g4_dinamica = gerar_query_g4_tributacao(ano_alvo, mes_alvo)
    dados_relatorio['regime_tributacao_mes'] = buscar_dados(query_g4_dinamica, engine)

    print("\nBuscando dados para o Gráfico de Regime de Tributação...")
    query_g5_dinamica = gerar_query_g5_tributacao(ano_alvo, mes_alvo)
    dados_relatorio['regime_tributacao_acumulado'] = buscar_dados(query_g5_dinamica, engine)

    print("\nBuscando dados para o Gráfico Mensal de Percentual de Contribuição...")
    query_g6_dinamica = gerar_query_g6(ano_alvo, mes_alvo)
    dados_relatorio['percentual_contrib_mes'] = buscar_dados(query_g6_dinamica, engine)
    
    print("\nBuscando dados para o Gráfico Acumulado de Percentual de Contribuição...")
    query_g7_dinamica = gerar_query_g7(ano_alvo, mes_alvo)
    dados_relatorio['percentual_contrib_acumulado'] = buscar_dados(query_g7_dinamica, engine)

    print("\nBuscando dados para a Tabela de Arrecadação...")
    query_t4_dinamica = gerar_query_tabela4(ano_alvo, mes_alvo)
    dados_relatorio['arrecadacao_tabela'] = buscar_dados(query_t4_dinamica, engine)

    print("\nBuscando dados para o Gráfico de Paridade...")
    query_g8_dinamica = gerar_query_grafico8(ano_alvo, mes_alvo)
    dados_relatorio['arrecadacao_grafico'] = buscar_dados(query_g8_dinamica, engine)
    
    print("\nBuscando dados para a Tabela de Arrecadação por Tipo...")
    query_t5_dinamica = gerar_query_tabela5(ano_alvo, mes_alvo)
    dados_relatorio['arrecadacao_tipo'] = buscar_dados(query_t5_dinamica, engine)

    print("\nBuscando dados para a Tabela de Arrecadação por Cargo...")
    query_t6_dinamica = gerar_query_tabela6(ano_alvo, mes_alvo)
    dados_relatorio['arrecadacao_cargo'] = buscar_dados(query_t6_dinamica, engine)

    print("\nBuscando dados para o Gráfico de Contribuição Mensal por Ramo...")
    query_g9_dinamica = gerar_query_g9(ano_alvo, mes_alvo)
    dados_relatorio['contribuicao_ramo_mes'] = buscar_dados(query_g9_dinamica, engine)

    print("\nBuscando dados para o Gráfico de Patrimônio Acumulado por Ramo...")
    query_g10_dinamica = gerar_query_g10(ano_alvo, mes_alvo)
    dados_relatorio['patrimonio_ramo_acumulado'] = buscar_dados(query_g10_dinamica, engine)
    
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
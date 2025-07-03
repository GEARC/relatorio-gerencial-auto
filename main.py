# main.py (VERSÃO CORRIGIDA)

import datetime
import locale
from config import DB_CONFIG
# Adicionando a importação que estava faltando
from queries.grafico1_piramide_etaria import QUERY as query_piramide_etaria
from queries.tabela1_evolucao_adesoes import QUERY as query_evolucao_adesoes
from queries.tabela2_distribuicao_sexo import QUERY as query_distribuicao_sexo
from modules.database import conectar_banco, buscar_dados
from modules.relatorio import gerar_relatorio_word, converter_docx_para_pdf


def solicitar_data_relatorio():
    """Solicita ao usuário o ano e o mês para o relatório."""
    while True:
        try:
            ano = int(input(">>> Digite o ano do relatório (ex: 2025): "))
            if 2000 < ano < 2100:
                break
            else:
                print("Ano inválido, por favor tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número para o ano.")
    
    while True:
        try:
            mes = int(input(">>> Digite o mês do relatório (ex: 5 para maio): "))
            if 1 <= mes <= 12:
                break
            else:
                print("Mês inválido, por favor digite um número de 1 a 12.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número para o mês.")
            
    return datetime.date(ano, mes, 1)


def main():
    """Função principal que orquestra a automação do relatório."""
    print("--- Automação do Relatório Gerencial ---")
    
    data_alvo = solicitar_data_relatorio()
    
    print(f"\nGerando relatório para o período de {data_alvo.strftime('%B de %Y')}...")
    
    engine = conectar_banco()
    if engine is None: 
        return

    dados_relatorio = {}
    
    print("\nBuscando dados para Evolução das Adesões...")
    dados_relatorio['evolucao_adesoes'] = buscar_dados(query_evolucao_adesoes, engine)
    
    print("\nBuscando dados para Distribuição por Sexo...")
    dados_relatorio['distribuicao_sexo'] = buscar_dados(query_distribuicao_sexo, engine)
    
    # --- CORREÇÃO: LINHA DE BUSCA DE DADOS DO GRÁFICO ADICIONADA ---
    print("\nBuscando dados para o Gráfico de Pirâmide Etária...")
    dados_relatorio['piramide_etaria'] = buscar_dados(query_piramide_etaria, engine)
    
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
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
from queries.tabela1_evolucao_detalhes import gerar_query as gerar_query_evolucao_detalhes
from queries.tabela_distribuicao_sexo import QUERY as query_distribuicao_sexo
from queries.tabela2_distribuicao_cargos import gerar_query as gerar_query
from queries.grafico1_piramide_etaria import QUERY as query_piramide_etaria
from queries.grafico2_adesao_ramo_mes import gerar_query as gerar_query_g2_ramo_mes
from queries.grafico3_adesao_ramo_acumulado import gerar_query as gerar_query_g3_ramo_acumulado
from queries.tabela3_adesoes_patrocinador import gerar_query as gerar_query_patrocinador
from queries.tabela5_arrecadacao_tipo import gerar_query as gerar_query_tabela5
from queries.grafico4_tributacao_mes import gerar_query as gerar_query_g4_tributacao
from queries.grafico5_tributacao_acumulado import gerar_query as gerar_query_g5_tributacao
from queries.grafico6_percentual_contrib_mes import gerar_query as gerar_query_g6
from queries.grafico7_percentual_contrib_acumulado import gerar_query as gerar_query_g7
from queries.grafico8_contribuicao_paridade import gerar_query as gerar_query_grafico8
from queries.tabela6_arrecadacao_cargo import gerar_query as gerar_query_tabela6
from queries.grafico9_contribuicao_ramo_mes import gerar_query as gerar_query_g9
from queries.grafico10_patrimonio_ramo_acumulado import gerar_query as gerar_query_g10
from queries.tabela7_contribuicao_patrocinador import gerar_query as gerar_query_tabela7

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
            
    # Garante que a função sempre retorne um objeto de data
    return datetime.date(ano, mes, 1)

def salvar_queries_em_txt(queries_dict, caminho_saida, data_alvo):
    """Salva um dicionário de queries SQL em um arquivo de texto."""
    
    # Define o nome do arquivo e o caminho completo
    nome_arquivo = f"queries_executadas_{data_alvo.strftime('%Y-%m')}.txt"
    caminho_completo = os.path.join(caminho_saida, nome_arquivo)

    try:
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            f.write(f"--- Queries Executadas para o Relatório de {data_alvo.strftime('%B de %Y')} ---\n\n")
            for nome, query in queries_dict.items():
                f.write(f"-- Query para: {nome}\n")
                f.write("--------------------------------------------------\n")
                f.write(query)
                f.write("\n\n\n")
        print(f"Arquivo de queries salvo com sucesso em: {caminho_completo}")
        return True
    except Exception as e:
        print(f"ERRO ao salvar o arquivo de queries: {e}")
        return False

def salvar_tabelas_em_excel(dados_relatorio, caminho_saida, data_alvo):
    """Salva os DataFrames das tabelas do relatório em um arquivo Excel."""
    
    # Mapeia as chaves de dados para nomes de abas mais amigáveis
    mapa_tabelas = {
        'evolucao_adesoes': 'T1 - Evolução Adesões',
        'evolucao_detalhes': 'T1 - Detalhes Evolução',
        'distribuicao_sexo': 'T - Distribuição por Sexo',
        'distribuicao_cargos': 'T2 - Distribuição Cargos',
        'adesoes_patrocinador': 'T3 - Adesões Patrocinador',
        'arrecadacao_tabela': 'T4 - Arrecadação Competência',
        'arrecadacao_tipo': 'T5 - Arrecadação por Tipo',
        'arrecadacao_cargo': 'T6 - Arrecadação por Cargo',
        'contribuicao_patrocinador': 'T7 - Contribuição Patrocinador'
    }

    nome_arquivo = f"tabelas_relatorio_{data_alvo.strftime('%Y-%m')}.xlsx"
    caminho_completo = os.path.join(caminho_saida, nome_arquivo)

    try:
        with pd.ExcelWriter(caminho_completo, engine='xlsxwriter') as writer:
            print("\nIniciando a geração da planilha Excel com as tabelas...")
            for chave_dados, nome_aba in mapa_tabelas.items():
                if chave_dados in dados_relatorio and not dados_relatorio[chave_dados].empty:
                    # Limita o nome da aba a 31 caracteres, que é o limite do Excel
                    nome_aba_curto = nome_aba[:31]
                    dados_relatorio[chave_dados].to_excel(writer, sheet_name=nome_aba_curto, index=False)
                    print(f" -> Aba '{nome_aba_curto}' salva.")
        print(f"\nPlanilha com as tabelas salva com sucesso em: {caminho_completo}")
        return True
    except Exception as e:
        print(f"ERRO ao salvar a planilha Excel: {e}")
        return False

def main():
    """Função principal que orquestra a automação do relatório."""
    print("--- Automação do Relatório Gerencial ---")
    
    data_alvo = solicitar_data_relatorio()
    ano_alvo = data_alvo.year
    mes_alvo = data_alvo.month
    
    print(f"\nGerando relatório para o período de {data_alvo.strftime('%B de %Y')}...")
    
    engine = None
    try:
        engine = conectar_banco()
        if engine is None: return

        dados_relatorio = {}
        queries_executadas = {}

        param_texto_data = f"{ano_alvo}{mes_alvo:02d}"
        
        print("\nBuscando dados para Evolução das Adesões...")
        query_evolucao_dinamica = gerar_query_evolucao(ano_alvo, mes_alvo)
        queries_executadas['Tabela 1 - Evolução das Adesões'] = query_evolucao_dinamica
        dados_relatorio['evolucao_adesoes'] = buscar_dados(query_evolucao_dinamica, engine)

        print("\nBuscando dados para Detalhes da Evolução das Adesões...")
        query_evolucao_detalhes_dinamica = gerar_query_evolucao_detalhes(ano_alvo, mes_alvo)
        queries_executadas['Tabela 1 - Detalhes da Evolução'] = query_evolucao_detalhes_dinamica
        dados_relatorio['evolucao_detalhes'] = buscar_dados(query_evolucao_detalhes_dinamica, engine)
        
        print("\nBuscando dados para Distribuição por Sexo...")
        query_sexo_dinamica = query_distribuicao_sexo.replace('?', f"'{param_texto_data}'")
        queries_executadas['Tabela - Distribuição por Sexo'] = query_sexo_dinamica
        dados_relatorio['distribuicao_sexo'] = buscar_dados(query_sexo_dinamica, engine)
        
        print("\nBuscando dados para o Gráfico de Pirâmide Etária...")
        query_piramide_dinamica = query_piramide_etaria.replace('?', f"'{param_texto_data}'")
        queries_executadas['Gráfico 1 - Pirâmide Etária'] = query_piramide_dinamica
        dados_relatorio['piramide_etaria'] = buscar_dados(query_piramide_dinamica, engine)

        print("\nBuscando dados para Distribuição por Cargos...")
        query_cargos_dinamica = gerar_query(ano_alvo, mes_alvo)
        queries_executadas['Tabela 2 - Distribuição por Cargos'] = query_cargos_dinamica
        dados_relatorio['distribuicao_cargos'] = buscar_dados(query_cargos_dinamica, engine)

        print("\nBuscando dados para Gráfico de Adesão Mensal por Ramo...")
        query_g2_dinamica = gerar_query_g2_ramo_mes(ano_alvo, mes_alvo)
        queries_executadas['Gráfico 2 - Adesão Mensal por Ramo'] = query_g2_dinamica
        dados_relatorio['adesao_ramo_mes'] = buscar_dados(query_g2_dinamica, engine)
        
        print("\nBuscando dados para Gráfico de Adesão Acumulada por Ramo...")
        query_g3_dinamica = gerar_query_g3_ramo_acumulado(ano_alvo, mes_alvo)
        queries_executadas['Gráfico 3 - Adesão Acumulada por Ramo'] = query_g3_dinamica
        dados_relatorio['adesao_ramo_acumulado'] = buscar_dados(query_g3_dinamica, engine)

        print("\nBuscando dados para Adesões por Patrocinador...")
        query_patrocinador_dinamica = gerar_query_patrocinador(ano_alvo, mes_alvo)
        queries_executadas['Tabela 3 - Adesões por Patrocinador'] = query_patrocinador_dinamica
        dados_relatorio['adesoes_patrocinador'] = buscar_dados(query_patrocinador_dinamica, engine)

        print("\nBuscando dados para o Gráfico Mensal de Regime de Tributação...")
        query_g4_dinamica = gerar_query_g4_tributacao(ano_alvo, mes_alvo)
        queries_executadas['Gráfico 4 - Tributação (Mês)'] = query_g4_dinamica
        dados_relatorio['regime_tributacao_mes'] = buscar_dados(query_g4_dinamica, engine)

        print("\nBuscando dados para o Gráfico de Regime de Tributação...")
        query_g5_dinamica = gerar_query_g5_tributacao(ano_alvo, mes_alvo)
        queries_executadas['Gráfico 5 - Tributação (Acumulado)'] = query_g5_dinamica
        dados_relatorio['regime_tributacao_acumulado'] = buscar_dados(query_g5_dinamica, engine)

        print("\nBuscando dados para o Gráfico Mensal de Percentual de Contribuição...")
        query_g6_dinamica = gerar_query_g6(ano_alvo, mes_alvo)
        queries_executadas['Gráfico 6 - Percentual de Contribuição (Mês)'] = query_g6_dinamica
        dados_relatorio['percentual_contrib_mes'] = buscar_dados(query_g6_dinamica, engine)
        
        print("\nBuscando dados para o Gráfico Acumulado de Percentual de Contribuição...")
        query_g7_dinamica = gerar_query_g7(ano_alvo, mes_alvo)
        queries_executadas['Gráfico 7 - Percentual de Contribuição (Acumulado)'] = query_g7_dinamica
        dados_relatorio['percentual_contrib_acumulado'] = buscar_dados(query_g7_dinamica, engine)

        print("\nBuscando dados para a Tabela de Arrecadação...")
        # Query otimizada para a Tabela 4.
        # Em vez de duas varreduras na tabela, fazemos uma única varredura e usamos CASE.
        query_t4_dinamica = f"""
        SELECT
            CASE
                WHEN hc.NR_ANO_REF = {ano_alvo} AND hc.NR_MES_REF = {mes_alvo} THEN 'Mês Atual'
                ELSE 'Outras Competências'
            END AS Tipo,
            SUM(hc.VL_CONTRIB) AS CONTRIBUIÇÃO
        FROM hist_contribuicao hc
        WHERE hc.ID_CONTRIBUICAO IN (SELECT ID_CONTRIBUICAO_TRUST FROM portal.dbo.participante_tipo_contribuicao WHERE movimentacao IN ('CONTRIBUIÇÃO', 'AJUSTE'))
        GROUP BY CASE WHEN hc.NR_ANO_REF = {ano_alvo} AND hc.NR_MES_REF = {mes_alvo} THEN 'Mês Atual' ELSE 'Outras Competências' END;
        """
        queries_executadas['Tabela 4 - Arrecadação por Competência'] = query_t4_dinamica.strip()
        dados_relatorio['arrecadacao_tabela'] = buscar_dados(query_t4_dinamica, engine)

        print("\nBuscando dados para o Gráfico de Paridade...")
        query_g8_dinamica = gerar_query_grafico8(ano_alvo, mes_alvo)
        queries_executadas['Gráfico 8 - Paridade Contribuição Normal'] = query_g8_dinamica
        dados_relatorio['arrecadacao_grafico'] = buscar_dados(query_g8_dinamica, engine)
        
        print("\nBuscando dados para a Tabela de Arrecadação por Tipo...")
        query_t5_dinamica = gerar_query_tabela5(ano_alvo, mes_alvo)
        queries_executadas['Tabela 5 - Arrecadação por Tipo'] = query_t5_dinamica
        dados_relatorio['arrecadacao_tipo'] = buscar_dados(query_t5_dinamica, engine)

        print("\nBuscando dados para a Tabela de Arrecadação por Cargo...")
        query_t6_dinamica = gerar_query_tabela6(ano_alvo, mes_alvo)
        queries_executadas['Tabela 6 - Arrecadação por Cargo'] = query_t6_dinamica
        dados_relatorio['arrecadacao_cargo'] = buscar_dados(query_t6_dinamica, engine)

        print("\nBuscando dados para o Gráfico de Contribuição Mensal por Ramo...")
        query_g9_dinamica = gerar_query_g9(ano_alvo, mes_alvo)
        queries_executadas['Gráfico 9 - Contribuição por Ramo (Mês)'] = query_g9_dinamica
        dados_relatorio['contribuicao_ramo_mes'] = buscar_dados(query_g9_dinamica, engine)

        print("\nBuscando dados para o Gráfico de Patrimônio Acumulado por Ramo...")
        query_g10_dinamica = gerar_query_g10(ano_alvo, mes_alvo)
        queries_executadas['Gráfico 10 - Patrimônio por Ramo (Acumulado)'] = query_g10_dinamica
        dados_relatorio['patrimonio_ramo_acumulado'] = buscar_dados(query_g10_dinamica, engine)

        print("\nBuscando dados para Contribuições por Patrocinador...")
        query_t7_dinamica = gerar_query_tabela7(ano_alvo, mes_alvo)
        queries_executadas['Tabela 7 - Contribuição por Patrocinador'] = query_t7_dinamica
        dados_relatorio['contribuicao_patrocinador'] = buscar_dados(query_t7_dinamica, engine)
        #if not dados_relatorio[''].empty:
            #dados_relatorio[''].to_csv('amostra_dados_.csv', index=False, encoding='utf-8-sig')
           
            
        nome_arquivo_docx = gerar_relatorio_word(dados_relatorio, data_alvo)
        
        if nome_arquivo_docx:
            # Pega o diretório onde o DOCX foi salvo para usar para o TXT
            caminho_saida_relatorio = os.path.dirname(nome_arquivo_docx)
            
            # Salva o arquivo de texto com as queries
            salvar_queries_em_txt(queries_executadas, caminho_saida_relatorio, data_alvo)
            
            # Salva a planilha Excel com as tabelas
            salvar_tabelas_em_excel(dados_relatorio, caminho_saida_relatorio, data_alvo)

            # Converte o DOCX para PDF
            # Inicializa o COM para a thread atual para evitar erros de "chamada rejeitada"
            # ao interagir com o Word em alguns ambientes.
            pythoncom.CoInitialize()
            converter_docx_para_pdf(nome_arquivo_docx)

    except PermissionError as e:
        print(f"\nERRO DE PERMISSÃO: {e}")
        print("Verifique se o arquivo de relatório (.docx) não está aberto no Microsoft Word ou em outro programa.")
        print("Feche o arquivo e tente executar o script novamente.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
    finally:
        if engine:
            engine.dispose()
            print("\nConexão com o banco de dados fechada.")

    print("\n--- Processo finalizado com sucesso! ---")

if __name__ == "__main__":
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    main()
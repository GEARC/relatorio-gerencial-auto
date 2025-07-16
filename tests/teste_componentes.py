# testes_componentes.py

# Adiciona a pasta principal do projeto ao caminho de busca do Python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.visualizacoes import criar_grafico_donut
import pandas as pd

print("--- Iniciando ambiente de teste de componentes ---")
print("\nTestando a função 'criar_grafico_donut'...")

try:
    # Constrói o caminho para a subpasta 'amostras'
    caminho_amostra = os.path.join('tests', 'amostras', 'amostra_dados_regime_tributacao_mes.csv')
    df_teste = pd.read_csv(caminho_amostra) 
    
    print("Dados de amostra carregados com sucesso de:", caminho_amostra)

    # --- CORREÇÃO APLICADA AQUI ---
    # 1. Pega o diretório do arquivo de teste atual
    diretorio_teste = os.path.dirname(__file__)
    # 2. Junta o diretório com o nome do arquivo de saída
    caminho_saida = os.path.join(diretorio_teste, 'teste_donut.png')
    # --- FIM DA CORREÇÃO ---
    
    sucesso = criar_grafico_donut(df_teste, caminho_saida, "Teste do Gráfico Donut")

    if sucesso:
        print(f"\nTeste bem-sucedido! Gráfico de teste salvo em: '{caminho_saida}'")
    else:
        print("\nA função foi executada, mas não gerou um gráfico.")

except FileNotFoundError:
    print(f"\nERRO: Arquivo de amostra não encontrado no caminho: '{caminho_amostra}'")
    print("Por favor, verifique se o nome do arquivo e as pastas estão corretos.")

print("\n--- Testes finalizados ---")
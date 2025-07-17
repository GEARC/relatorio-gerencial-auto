# testes_componentes.py


import sys
import os
diretorio_atual = os.path.dirname(__file__)
pasta_principal = os.path.abspath(os.path.join(diretorio_atual, '..'))
sys.path.insert(0, pasta_principal)

# Importa APENAS a função específica que você quer testar do módulo de visualizações.
from modules.visualizacoes import criar_grafico_piramide_etaria
# Importa o pandas para ler o arquivo de dados de amostra.
import pandas as pd

print("--- Iniciando ambiente de teste de componentes ---")

# --- Testando um Componente Específico: O Gráfico de Donut ---
print("\nTestando a função 'criar_grafico_piramide_etaria'...")

try:
    # 1. Carregar Dados de Amostra
    # Em vez de conectar ao banco (que é lento), lemos os dados de um arquivo CSV local.
    # Isso torna o teste quase instantâneo.
    # O caminho é construído para encontrar o arquivo dentro da pasta 'tests/amostras'.
    caminho_amostra = os.path.join('tests', 'amostras', 'amostra_dados_regime_tributacao_mes.csv')
    df_teste = pd.read_csv(caminho_amostra) 
    
    print(f"Dados de amostra carregados com sucesso de: {caminho_amostra}")

    # 2. Definir o Caminho de Saída
    # O gráfico gerado será salvo na mesma pasta deste script de teste ('tests/').
    caminho_saida = os.path.join(diretorio_atual, 'criar_grafico_piramide_etaria')

    # 3. Executar a Função
    # Chama apenas a função que queremos testar, passando os dados de amostra.
    sucesso = criar_grafico_piramide_etaria(df_teste, caminho_saida, "Teste do Gráfico criar_grafico_piramide_etaria")

    # 4. Verificar o Resultado
    # Imprime uma mensagem de sucesso ou falha para sabermos o que aconteceu.
    if sucesso:
        print(f"\nTeste bem-sucedido! Gráfico de teste salvo em: '{caminho_saida}'")
    else:
        print("\nA função foi executada, mas não gerou um gráfico (verifique se os dados de amostra não estão vazios).")

# Tratamento de erro caso o arquivo de amostra não seja encontrado.
except FileNotFoundError:
    print(f"\nERRO: Arquivo de amostra não encontrado no caminho: '{caminho_amostra}'")
    print("Por favor, verifique se o nome do arquivo e as pastas estão corretos.")
# Tratamento de outros erros possíveis durante o teste.
except Exception as e:
    print(f"\nOcorreu um erro inesperado durante o teste: {e}")

print("\n--- Testes finalizados ---")
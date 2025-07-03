import pandas as pd
from sqlalchemy import create_engine
import urllib
from config import DB_CONFIG # Importa a configuração

def conectar_banco():
    """Estabelece e retorna um 'engine' do SQLAlchemy."""
    try:
        params = urllib.parse.quote_plus(
            f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
        )
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        engine.connect().close()
        print("Conexão bem-sucedida!")
        return engine
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def buscar_dados(query, engine):
    """Executa uma query e retorna os dados como um DataFrame pandas."""
    try:
        df = pd.read_sql(query, engine)
        print(f"Consulta executada: {len(df)} linhas retornadas.")
        return df
    except Exception as e:
        print(f"Erro na consulta: {e}")
        return pd.DataFrame()
import pandas as pd
from sqlalchemy import create_engine
import urllib
from config import DB_CONFIG

def conectar_banco(log_callback=print):
    """Estabelece e retorna um 'engine' do SQLAlchemy."""
    try:
        params = urllib.parse.quote_plus(
            f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
        )
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        engine.connect().close()
        log_callback("Conexão bem-sucedida!")
        return engine
    except Exception as e:
        log_callback(f"Erro ao conectar: {e}")
        return None

# --- FUNÇÃO SIMPLIFICADA ---
# Removemos o argumento 'params' pois não será mais usado
def buscar_dados(query, engine, log_callback=print, params=None):
    """
    Executa uma query e retorna os dados como um DataFrame pandas.
    Agora aceita um argumento 'params' opcional.
    """
    try:
        # A função read_sql agora usa o argumento 'params' que foi passado
        df = pd.read_sql(query, engine, params=params)
        log_callback(f"Consulta executada: {len(df)} linhas retornadas.")
        return df
    except Exception as e:
        log_callback(f"Erro na consulta: {e}")
        return pd.DataFrame()
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import sys

# --- COLOQUE A URL DO SEU BANCO DO RENDER AQUI ---
# É a mesma que você colocou nas variáveis de ambiente
URL_BANCO_RENDER = "postgresql://dados_analiticos_user:265C3o5Tzqh8Nv2xIJTPu3kl3Ef5eWkG@dpg-d3smgqeuk2gs73fsl3og-a.oregon-postgres.render.com/dados_analiticos"
# --------------------------------------------------

ARQUIVO_SQLITE_LOCAL = "dados_analiticos.db"
NOME_DA_TABELA = "dados_consolidados"

def migrar_dados():
    print(f"Iniciando migração de dados de '{ARQUIVO_SQLITE_LOCAL}' para o Render...")

    try:
        # 1. Ler os dados do banco local (SQLite)
        print(f"Lendo dados da tabela '{NOME_DA_TABELA}' do arquivo local...")
        conn_local = sqlite3.connect(ARQUIVO_SQLITE_LOCAL)
        df = pd.read_sql_query(f"SELECT * FROM {NOME_DA_TABELA}", conn_local)
        conn_local.close()
        
        if df.empty:
            print("Erro: O banco de dados local está vazio. Abortando.")
            return
            
        print(f"Sucesso! {len(df)} linhas lidas.")

    except Exception as e:
        print(f"ERRO CRÍTICO ao ler o arquivo local '{ARQUIVO_SQLITE_LOCAL}': {e}", file=sys.stderr)
        print("Verifique se o nome do arquivo e da tabela estão corretos.", file=sys.stderr)
        return

    try:
        # 2. Conectar ao banco de dados do Render (PostgreSQL)
        print("Conectando ao banco de dados do Render...")
        engine_render = create_engine(URL_BANCO_RENDER)
        
        # 3. Escrever os dados no Render
        print(f"Enviando dados para a tabela '{NOME_DA_TABELA}' no Render...")
        # 'if_exists='replace'' vai apagar a tabela antiga e criar uma nova com seus dados
        df.to_sql(NOME_DA_TABELA, engine_render, if_exists='replace', index=False)
        
        print("\n--- MIGRAÇÃO CONCLUÍDA COM SUCESSO! ---")
        print("Seus dados do TCC agora estão no banco de dados do Render.")

    except Exception as e:
        print(f"ERRO CRÍTICO ao conectar ou escrever no banco do Render: {e}", file=sys.stderr)
        print("Verifique se a URL_BANCO_RENDER está correta e se o banco no Render está 'Available'.", file=sys.stderr)

if __name__ == "__main__":
    migrar_dados()
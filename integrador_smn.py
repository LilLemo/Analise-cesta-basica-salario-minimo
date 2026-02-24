import sqlite3
import pandas as pd

DB_FILE = 'dados_analiticos.db'
CSV_SMN_FILE = 'smn_dados.csv'
TABLE_NAME = 'dados_consolidados'
NEW_COLUMN_NAME = 'salario_minimo_necessario'

def integrar_smn():
    """
    Lê os dados do Salário Mínimo Necessário de um CSV e
    atualiza o banco de dados principal.
    """
    try:
        print("Iniciando a integração dos dados do Salário Mínimo Necessário...")
        
        # --- Conectar ao banco de dados ---
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # --- 1. Adicionar a nova coluna à tabela, se ela não existir ---
        try:
            print(f"Verificando se a coluna '{NEW_COLUMN_NAME}' existe...")
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN {NEW_COLUMN_NAME} REAL")
            conn.commit()
            print(f"Coluna '{NEW_COLUMN_NAME}' adicionada com sucesso!")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"A coluna '{NEW_COLUMN_NAME}' já existe. Nenhuma alteração na estrutura da tabela foi necessária.")
            else:
                raise e

        # --- 2. Ler os novos dados do CSV ---
        print(f"Lendo os novos dados de '{CSV_SMN_FILE}'...")
        # A MUDANÇA ESTÁ AQUI: Adicionamos o delimiter=';'
        df_smn = pd.read_csv(CSV_SMN_FILE, delimiter=';')
        
        # Garante que a data está no formato correto para comparação
        df_smn['data'] = pd.to_datetime(df_smn['data'], dayfirst=True).dt.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{len(df_smn)} registros de SMN encontrados.")

        # --- 3. Atualizar cada linha no banco de dados ---
        print("Atualizando o banco de dados. Isso pode levar alguns segundos...")
        updates_realizados = 0
        for index, row in df_smn.iterrows():
            data_registro = row['data']
            valor_registro = row['valor_smn']
            
            cursor.execute(f"""
                UPDATE {TABLE_NAME}
                SET {NEW_COLUMN_NAME} = ?
                WHERE data = ?
            """, (valor_registro, data_registro))
            
            if cursor.rowcount > 0:
                updates_realizados += 1

        conn.commit()
        conn.close()

        print("\n--- Integração Concluída! ---")
        print(f"Total de linhas no CSV: {len(df_smn)}")
        print(f"Total de registros correspondentes atualizados no banco de dados: {updates_realizados}")

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{CSV_SMN_FILE}' não foi encontrado. Verifique o nome e o local do arquivo.")
    except KeyError as e:
        print(f"ERRO DE COLUNA: A coluna {e} não foi encontrada no seu arquivo CSV. Verifique se os cabeçalhos estão exatamente como 'data', 'salario_nominal', 'valor_smn'.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    integrar_smn()
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import json
import itertools
import os

# --- CONFIGURAÇÕES ---
DB_FILE = 'dados_analiticos.db'
OUTPUT_FOLDER = 'resultados' 
HORAS_TRABALHO_MES = 220

# --- FUNÇÃO DE ANÁLISE ---
def gerar_analise_comparativa(periodo_gov1, periodo_gov2, df):
    """
    Calcula as métricas para dois governos e salva os resultados.
    Agora inclui o crescimento percentual do salário e da cesta básica.
    """
    try:
        resultado_json = {}
        
        for i, periodo in enumerate([periodo_gov1, periodo_gov2]):
            # Filtra e ordena os dados para o governo específico
            df_gov = df[df['Governo'] == periodo].sort_values(by='data')
            if df_gov.empty:
                return # Pula se não houver dados

            # --- CÁLCULOS EXISTENTES ---
            media_salario = df_gov['Salario'].mean()
            media_cesta = df_gov['valor_nominal'].mean()
            percentual_cesta_come = (media_cesta / media_salario) * 100 if media_salario > 0 else 0
            horas_necessarias = (media_cesta / media_salario) * HORAS_TRABALHO_MES if media_salario > 0 else 0
            media_smn = "Dados Indisponíveis"

            # --- NOVOS CÁLCULOS ADICIONADOS ---
            # Pega o primeiro e último valor do período
            salario_inicial = df_gov['Salario'].iloc[0]
            salario_final = df_gov['Salario'].iloc[-1]
            cesta_inicial = df_gov['valor_nominal'].iloc[0]
            cesta_final = df_gov['valor_nominal'].iloc[-1]

            # Calcula o crescimento percentual (com proteção para divisão por zero)
            crescimento_salario_perc = ((salario_final - salario_inicial) / salario_inicial) * 100 if salario_inicial > 0 else 0
            inflacao_cesta_perc = ((cesta_final - cesta_inicial) / cesta_inicial) * 100 if cesta_inicial > 0 else 0
            
            # --- GERAÇÃO DO GRÁFICO (sem alterações) ---
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df_gov['data'], df_gov['Salario'], label='Salário Mínimo (R$)', color='#e94560', marker='o')
            ax.plot(df_gov['data'], df_gov['valor_nominal'], label='Cesta Básica (R$)', color='#50fa7b', marker='o')
            ax.set_title(f'Evolução SM vs. Cesta Básica\n{periodo}', color='white', fontsize=16, fontfamily='monospace')
            ax.set_ylabel('Valor (R$)', color='white', fontfamily='monospace')
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            nome_grafico_linha = f'{OUTPUT_FOLDER}/grafico_linha_{periodo.replace(" ", "_")}.png'
            if not os.path.exists(nome_grafico_linha):
                plt.savefig(nome_grafico_linha, transparent=True)
            plt.close(fig)
            
            # --- MONTAGEM DO JSON ---
            dados_pizza = {'labels': ['Cesta Básica', 'Sobra do Salário'], 'valores': [percentual_cesta_come, 100 - percentual_cesta_come]}
            
            resultado_json[f'governo{i+1}'] = {
                'nome': periodo,
                'grafico_linha_path': nome_grafico_linha,
                'dados_pizza': dados_pizza,
                'kpi_horas_trabalho': round(horas_necessarias, 2),
                'kpi_smn': media_smn,
                # --- NOVOS DADOS ADICIONADOS AO JSON ---
                'salario_inicial': round(salario_inicial, 2),
                'salario_final': round(salario_final, 2),
                'crescimento_salario_perc': round(crescimento_salario_perc, 2),
                'inflacao_cesta_perc': round(inflacao_cesta_perc, 2)
            }

        # Garante a ordem dos nomes no arquivo para o Javascript encontrar
        gov1_sorted, gov2_sorted = sorted([periodo_gov1, periodo_gov2])
        json_filename = f'{OUTPUT_FOLDER}/comparativo_{gov1_sorted.replace(" ", "_")}_vs_{gov2_sorted.replace(" ", "_")}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(resultado_json, f, ensure_ascii=False, indent=4)
            
        return f"Gerado: {json_filename}"

    except Exception as e:
        return f"Erro ao processar '{periodo_gov1}' vs '{periodo_gov2}': {e}"

# --- EXECUÇÃO AUTOMÁTICA ---
def main():
    """
    Função principal que orquestra a geração de todas as combinações.
    """
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    print("Iniciando análise completa...")
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM dados_consolidados", conn)
    conn.close()
    
    df['data'] = pd.to_datetime(df['data'])
    
    lista_governos = df['Governo'].unique()
    combinacoes = list(itertools.combinations(lista_governos, 2))
    
    print(f"Encontrados {len(combinacoes)} pares de governos para comparar.")
    
    for par in combinacoes:
        gov1, gov2 = par
        resultado = gerar_analise_comparativa(gov1, gov2, df)
        print(resultado)
        
    print("\nAnálise completa finalizada! Todos os arquivos JSON agora estão mais ricos!")

if __name__ == '__main__':
    main()
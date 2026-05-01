import pandas as pd

caminho = r'C:\Projetos\ProjetosFaculdade\PNAD_continua\Banco_de_dados.csv' # Edite o caminho para o local onde o arquivo CSV está armazenado
df = pd.read_csv(caminho)

def calcular_bloco_stats(dataframe, agrupadores, variaveis, rotulo_tipo):
    """Auxiliar para calcular estatísticas e rotular o nível de agregação"""
    if agrupadores:
        # Agrupa e calcula média e mediana (isso gera o MultiIndex)
        resumo = dataframe.groupby(agrupadores)[variaveis].agg(['mean', 'median'])
        
        # Achata as colunas de dois andares para um nome simples
        resumo.columns = [f"{coluna[0]}_{coluna[1]}" for coluna in resumo.columns]
        resumo = resumo.reset_index()
        
        # Calcula a Moda separadamente e adiciona ao resumo
        for var in variaveis:
            moda_valores = dataframe.groupby(agrupadores)[var].apply(lambda x: x.mode().iloc[0] if not x.mode().empty else None).values
            resumo[f'{var}_moda'] = moda_valores
            
    else:
        # Cálculo Global (sem groupby, já cria colunas simples)
        resumo_data = {}
        for var in variaveis:
            resumo_data[f'{var}_mean'] = [dataframe[var].mean()]
            resumo_data[f'{var}_median'] = [dataframe[var].median()]
            
            moda_s = dataframe[var].mode()
            resumo_data[f'{var}_moda'] = [moda_s.iloc[0] if not moda_s.empty else None]
            
        resumo = pd.DataFrame(resumo_data)
        resumo['Ano'] = 'TOTAL'
        resumo['Trimestre'] = 'GERAL'

    resumo['Tipo_Registro'] = rotulo_tipo
    return resumo

variaveis_analise = ['V2007','V2009','V2010','V403412','V4039']

stats_trimestral = calcular_bloco_stats(df, ['Ano', 'Trimestre'], variaveis_analise, "Trimestral")

stats_anual = calcular_bloco_stats(df, ['Ano'], variaveis_analise, "Consolidado Anual")
stats_anual['Trimestre'] = 'Todos' # Preenche a coluna de trimestre para permitir a união

stats_geral = calcular_bloco_stats(df, [], variaveis_analise, "Total do Banco")

df_final = pd.concat([stats_trimestral, stats_anual, stats_geral], ignore_index=True)

# Reorganizar colunas para facilitar a leitura no Excel
colunas_ordenadas = ['Tipo_Registro', 'Ano', 'Trimestre'] + [c for c in df_final.columns if c not in ['Tipo_Registro', 'Ano', 'Trimestre']]
df_final = df_final[colunas_ordenadas]

# Salvar no Excel
df_final.to_excel("Relatorio_PNAD_Segmentado.xlsx", index=False)

print("Relatório completo gerado com sucesso!")
import pandas as pd
# Parte 1
df = pd.read_csv("C:\\Projetos\\ProjetosFaculdade\\PNAD_continua\\Banco_de_dados.csv", encoding='utf-8')
#fillna(0) para substituir os valores nulos por 0, caso contrário, a soma resultaria em NaN e só nos necessários
df['Rendimento Principal'] = df['V403412'].fillna(0) + df['V403422'].fillna(0)
df['Rendimento Secundário'] = df['V405112'].fillna(0) + df['V405122'].fillna(0)
df['Outros Rendimentos'] = df['V405912'].fillna(0) + df['V405922'].fillna(0)
df['Rendimento Total'] = df['Rendimento Principal'] + df['Rendimento Secundário'] + df['Outros Rendimentos']
print(df.head())

# Parte 2
df_temp1 = df[['V2009','V4039','V4039C', 'Rendimento Total']]
print(df_temp1.head())
df2 = df_temp1[['V2009', 'V4039', 'V4039C', 'Rendimento Total']].agg(['mean', 'median'])
df2 = df2.T
df2.columns = ['Média', 'Mediana']
df2.index.name = 'Variável'
print(df2)
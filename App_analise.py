import pandas as pd
import matplotlib.pyplot as plt

# Certifique-se de que o Banco_de_dados.csv está na mesma pasta que este script
caminho_arquivo = "/workspaces/ProjetosFaculdade/PNAD_continua/Banco_de_dados.csv"
print("Lendo o arquivo de dados...")
df = pd.read_csv(caminho_arquivo, encoding='utf-8')

# fillna(0) para substituir valores nulos por 0 e somar os rendimentos
df['Rendimento Principal'] = df['V403412'].fillna(0) + df['V403422'].fillna(0)
df['Rendimento Secundário'] = df['V405112'].fillna(0) + df['V405122'].fillna(0)
df['Outros Rendimentos'] = df['V405912'].fillna(0) + df['V405922'].fillna(0)
df['Rendimento Total'] = df['Rendimento Principal'] + df['Rendimento Secundário'] + df['Outros Rendimentos']

print("\n--- Primeiras linhas do DataFrame Principal ---")
print(df.head())

# PARTE 2: Estatísticas Descritivas
df_temp1 = df[['V2009', 'V4039', 'V4039C', 'Rendimento Total']]

# Funções auxiliares para calcular os quartis
def q1(x):
    return x.quantile(0.25)

def q3(x):
    return x.quantile(0.75)

# Calculando média, mediana, desvio-padrão, Q1 e Q3
df2 = df_temp1[['V2009', 'V4039', 'V4039C', 'Rendimento Total']].agg(['mean', 'median', 'std', q1, q3])
df2 = df2.T  
df2.columns = ['Média', 'Mediana', 'Desvio-padrão', 'Q1', 'Q3']
df2.index.name = 'Variável'

print("\n--- Tabela de Estatísticas Gerais (df2) ---")
print(df2)

# PARTE 3: Novos DataFrames de Comparação

# Mapeamento opcional para a variável de Sexo (1=Homem, 2=Mulher) para melhor visualização
df['Sexo_Label'] = df['V2007'].map({1: 'Homem', 2: 'Mulher'}).fillna(df['V2007'])

# A) Comparação por Sexo
df_sexo = df.groupby('Sexo_Label').agg(
    Idade_Média=('V2009', 'mean'),
    Renda_Média=('Rendimento Total', 'mean'),
    Renda_Mediana=('Rendimento Total', 'median')
)
df_sexo.index.name = 'Sexo'

print("\n--- Tabela A: Comparação por Sexo (V2007) ---")
print(df_sexo.round(2))

# B) Comparação por Escolaridade
df_escolaridade = df.groupby('V3009A').agg(
    Renda_Média=('Rendimento Total', 'mean'),
    Renda_Mediana=('Rendimento Total', 'median')
)
df_escolaridade.index.name = 'Nível de Instrução (V3009A)'

print("\n--- Tabela B: Comparação por Escolaridade (V3009A) ---")
print(df_escolaridade.round(2))

# PARTE 4: Geração de Gráficos (Exportando PNG)
print("\nGerando os gráficos e salvando como imagens no painel lateral...")

# 1. Histograma da renda total
plt.figure(figsize=(10, 6))
plt.hist(df['Rendimento Total'], bins=50, color='skyblue', edgecolor='black')
plt.title('Histograma - Rendimento Total')
plt.xlabel('Rendimento Total (R$)')
plt.ylabel('Frequência')
plt.grid(axis='y', alpha=0.75)
plt.savefig('1_Histograma_Renda.png')
plt.close()

# 1.1 Renda por Faixas de Rendimento

# Defina o valor do salário mínimo correspondente ao ano dos dados (ex: 1412.00 para 2024)
sm = 1412.00

# Definir os limites dos intervalos (bins) e os respetivos rótulos (labels)
limites = [-1, 0, sm, 2*sm, 3*sm, 5*sm, 10*sm, float('inf')]
rotulos = ['Sem rendimento', 'Até 1 SM', '1 a 2 SM', '2 a 3 SM', '3 a 5 SM', '5 a 10 SM', 'Mais de 10 SM']

# Criar uma nova coluna no DataFrame com as faixas de rendimento
df['Faixa_Renda'] = pd.cut(df['Rendimento Total'], bins=limites, labels=rotulos)

print("\n--- Distribuição por Faixas de Rendimento ---")
print(df['Faixa_Renda'].value_counts().reindex(rotulos)) # reindex garante a ordem correta na exibição

# Geração do Gráfico de Barras para as Faixas
print("\nA gerar o gráfico de barras das faixas de rendimento...")

faixas_renda = plt.figure(figsize=(10, 6))

# Contar os valores, reordenar pelos rótulos definidos e plotar o gráfico de barras
df['Faixa_Renda'].value_counts().reindex(rotulos).plot(kind='bar', color='lightcoral', edgecolor='black')

plt.title('Distribuição da População por Faixas de Rendimento')
plt.xlabel('Faixas de Rendimento (em Salários Mínimos)')
plt.ylabel('Frequência')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.4)
plt.tight_layout()

# Guardar a imagem no explorador de ficheiros do Codespaces
plt.savefig('1.1_Histograma_Renda.png')
plt.close(faixas_renda)

# 2. Histograma da idade (V2009)
plt.figure(figsize=(10, 6))
plt.hist(df['V2009'].dropna(), bins=20, color='lightgreen', edgecolor='black')
plt.title('Histograma - Idade (V2009)')
plt.xlabel('Idade (Anos)')
plt.ylabel('Frequência')
plt.grid(axis='y', alpha=0.75)
plt.savefig('2_Histograma_Idade.png')
plt.close()

# 3. Gráfico de barras do nível de instrução (V3009A)
instrucao = plt.figure(figsize=(10, 6))
df['V3009A'].value_counts().sort_index().plot(kind='bar', color='coral', edgecolor='black')
plt.title('Nível de Instrução (V3009A)')
plt.xlabel('Categorias de Instrução (Códigos)')
plt.ylabel('Frequência')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('3_chart_bar_Instrucao.png')
plt.close(instrucao)

# 4. Gráfico de barras do CNAE Agrupado (V4039C)
cnae = plt.figure(figsize=(12, 6))
df['V4039C'].value_counts().sort_index().plot(kind='bar', color='orchid', edgecolor='black')
plt.title('CNAE Agrupado (V4039C)')
plt.xlabel('Grupamentos de Atividade Principal (Códigos)')
plt.ylabel('Frequência')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('4_CNAE.png')
plt.close(cnae)

#4.1 Top 20
print("\nGerando gráfico do CNAE Macro (Top 20)...")
df['CNAE_MACRO'] = df['CNAE_MACRO'].astype(str).str.zfill(2)

# 3. Contagem: Calcula a frequência, pega apenas os 20 maiores (.head(20)) e ordena do menor para o maior
dados_cnae_macro = df['CNAE_MACRO'].value_counts(dropna=True).head(20).sort_values(ascending=True)

# 4. Geração do gráfico
cnae_macro_top20 = plt.figure(figsize=(12, 10))
dados_cnae_macro.plot(kind='barh', color='mediumseagreen', edgecolor='black')
plt.title('Top 20 Setores de Atividade (CNAE Macro)')
plt.xlabel('Frequência (Nº de Pessoas)')
plt.ylabel('')
plt.grid(axis='x', alpha=0.4)
plt.tight_layout()

# Salva a imagem
plt.savefig('CNAE_Macro_Top20.png')
plt.close(cnae_macro_top20)

# PARTE 5: Respondendo às Perguntas de Pesquisa

print("\nGerando gráficos analíticos de renda...")


# 1. Relação Escolaridade x Rendimento
df_com_renda = df[df['Rendimento Total'] > 0]
pivot_tab_esc = df_com_renda.groupby('V3009A')['Rendimento Total'].median()
chart_bar_esc = plt.figure(figsize=(10, 6))
pivot_tab_esc.plot(kind='bar', color='coral', edgecolor='black')
plt.title('Mediana de Rendimento por Nível de Instrução')
plt.xlabel('Nível de Instrução (V3009A)')
plt.ylabel('Renda Mediana (R$)')
plt.xticks(rotation=0)
plt.grid(axis='y', alpha=0.4)
plt.tight_layout()
plt.savefig('8_chart_bar_Escolaridade_Renda.png')
plt.close(chart_bar_esc)

# 2. Diferença de Renda entre Sexos
pivot_tab_sexo = df_com_renda.groupby('Sexo_Label')['Rendimento Total'].median()
chart_bar_sexo = plt.figure(figsize=(8, 6))
cores_sexo = ['#1f77b4', '#d62728'] # Azul e Vermelho para contrastar
pivot_tab_sexo.plot(kind='bar', color=cores_sexo, edgecolor='black')
plt.title('Mediana de Rendimento por Sexo')
plt.xlabel('Sexo (V2007)')
plt.ylabel('Renda Mediana (R$)')
plt.xticks(rotation=0)
plt.grid(axis='y', alpha=0.4)

# Adicionando o valor exato no topo de cada barra para facilitar a leitura
for index, value in enumerate(pivot_tab_sexo):
    plt.text(index, value + (value*0.02), f'R$ {value:.2f}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('9_chart_bar_Sexo_Renda.png')
plt.close(chart_bar_sexo)

# 3. Rendimento por setor

pivot_tab_cnae_renda = df_com_renda.groupby('CNAE_MACRO')['Rendimento Total'].median().sort_values(ascending=True).tail(15)

chart_bar_cnae_renda = plt.figure(figsize=(12, 8))
pivot_tab_cnae_renda.plot(kind='barh', color='gold', edgecolor='black')

plt.title('Top 15 Setores Econômicos com Maiores Rendas Medianas')
plt.xlabel('Renda Mediana (R$)')
plt.ylabel('')
plt.grid(axis='x', alpha=0.4)
plt.tight_layout()
plt.savefig('10_chart_bar_CNAE_Maiores_Rendas.png')
plt.close(chart_bar_cnae_renda)

print("Processo finalizado! Os dados foram processados e as imagens salvas com sucesso.")
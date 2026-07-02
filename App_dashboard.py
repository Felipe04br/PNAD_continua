import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. CONFIGURAÇÃO DA PÁGINA
# Definindo layout largo e paleta base pelo tema do Streamlit
st.set_page_config(
    page_title="Dashboard Socioeconômico - PNAD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de cores personalizada (Verdes e Azul-Petróleo)
COR_PRINCIPAL = '#20B2AA'  # Light Sea Green
COR_SECUNDARIA = '#008080' # Teal / Azul-petróleo
COR_DESTAQUE = '#3CB371'   # Medium Sea Green
COR_FUNDO_GRAFICO = '#F0FDF4'

# 2. CARREGAMENTO E TRATAMENTO DOS DADOS
@st.cache_data
def carregar_dados():
    # Ajuste o caminho se necessário
    caminho_arquivo = "Banco_de_dados.csv"
    try:
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado em: {caminho_arquivo}. Verifique o diretório.")
        return pd.DataFrame()

    # Tratamento de Rendimentos
    df['Rendimento Principal'] = df.get('V403412', 0).fillna(0) + df.get('V403422', 0).fillna(0)
    df['Rendimento Secundário'] = df.get('V405112', 0).fillna(0) + df.get('V405122', 0).fillna(0)
    df['Outros Rendimentos'] = df.get('V405912', 0).fillna(0) + df.get('V405922', 0).fillna(0)
    df['Rendimento Total'] = df['Rendimento Principal'] + df['Rendimento Secundário'] + df['Outros Rendimentos']

    # Mapeamento de Labels
    if 'V2007' in df.columns:
        df['Sexo_Label'] = df['V2007'].map({1: 'Homem', 2: 'Mulher'}).fillna('Não Informado')
    
    # Criação de Faixas de Renda (Salário Mínimo base: 1412.00)
    sm = 1412.00
    limites = [-1, 0, sm, 2*sm, 3*sm, 5*sm, 10*sm, float('inf')]
    rotulos = ['Sem rendimento', 'Até 1 SM', '1 a 2 SM', '2 a 3 SM', '3 a 5 SM', '5 a 10 SM', 'Mais de 10 SM']
    df['Faixa_Renda'] = pd.cut(df['Rendimento Total'], bins=limites, labels=rotulos)

    # Garantir que a coluna V2009 (Idade) seja numérica
    if 'V2009' in df.columns:
        df['V2009'] = pd.to_numeric(df['V2009'], errors='coerce')

    return df

df = carregar_dados()

if not df.empty:
    # 3. BARRA LATERAL (FILTROS)
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5526/5526465.png", width=100) # Ícone ilustrativo genérico
    st.sidebar.title("Filtros de Interação")

    # Filtro de Sexo
    opcoes_sexo = ['Todos'] + list(df['Sexo_Label'].dropna().unique())
    filtro_sexo = st.sidebar.selectbox("Selecionar Sexo:", opcoes_sexo)

    # Filtro de Idade (Slider)
    idade_min = int(df['V2009'].min()) if not pd.isna(df['V2009'].min()) else 0
    idade_max = int(df['V2009'].max()) if not pd.isna(df['V2009'].max()) else 100
    filtro_idade = st.sidebar.slider("Faixa Etária (V2009):", min_value=idade_min, max_value=idade_max, value=(idade_min, idade_max))

    # Filtro de Escolaridade (V3009A)
    opcoes_esc = ['Todas'] + list(df['V3009A'].dropna().unique())
    filtro_esc = st.sidebar.selectbox("Nível de Instrução (V3009A):", opcoes_esc)

    # Aplicação dos Filtros no DataFrame
    df_filtrado = df.copy()
    
    if filtro_sexo != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Sexo_Label'] == filtro_sexo]
        
    df_filtrado = df_filtrado[(df_filtrado['V2009'] >= filtro_idade[0]) & (df_filtrado['V2009'] <= filtro_idade[1])]
    
    if filtro_esc != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['V3009A'] == filtro_esc]

    # 4. CORPO DO DASHBOARD
    st.title("📊 Dashboard Analítico PNAD - Perfil Socioeconômico")
    st.markdown("---")

    # A) ESTATÍSTICAS DESCRITIVAS (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    
    renda_media = df_filtrado['Rendimento Total'].mean()
    renda_mediana = df_filtrado['Rendimento Total'].median()
    idade_media = df_filtrado['V2009'].mean()
    total_pessoas = len(df_filtrado)

    col1.metric("Total de Pessoas (Amostra)", f"{total_pessoas:,}".replace(',', '.'))
    col2.metric("Renda Média", f"R$ {renda_media:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    col3.metric("Renda Mediana", f"R$ {renda_mediana:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    col4.metric("Idade Média", f"{idade_media:.1f} anos")

    st.markdown("---")

    # B) GRÁFICOS INTERATIVOS
    st.subheader("Visualizações e Gráficos")
    aba1, aba2, aba3 = st.tabs(["Distribuição de Renda", "Análise por Escolaridade", "Perfil Demográfico e Setorial"])

    with aba1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**População por Faixas de Rendimento (Salários Mínimos)**")
            fig, ax = plt.subplots(figsize=(8, 5))
            contagem_faixas = df_filtrado['Faixa_Renda'].value_counts().reindex(
                ['Sem rendimento', 'Até 1 SM', '1 a 2 SM', '2 a 3 SM', '3 a 5 SM', '5 a 10 SM', 'Mais de 10 SM']
            )
            contagem_faixas.plot(kind='bar', color=COR_PRINCIPAL, edgecolor='black', ax=ax)
            ax.set_ylabel('Frequência')
            plt.xticks(rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
            
        with c2:
            st.markdown("**Top 10 Setores (CNAE Macro) com Maiores Rendas Medianas**")
            # Filtra quem tem renda > 0 para a mediana não ser distorcida por zeros
            df_com_renda = df_filtrado[df_filtrado['Rendimento Total'] > 0]
            if not df_com_renda.empty and 'CNAE_MACRO' in df_com_renda.columns:
                pivot_cnae = df_com_renda.groupby('CNAE_MACRO')['Rendimento Total'].median().sort_values(ascending=True).tail(10)
                fig, ax = plt.subplots(figsize=(8, 5))
                pivot_cnae.plot(kind='barh', color=COR_SECUNDARIA, edgecolor='black', ax=ax)
                ax.set_xlabel('Renda Mediana (R$)')
                ax.grid(axis='x', alpha=0.3)
                st.pyplot(fig)
            else:
                st.info("Dados insuficientes para gerar este gráfico com os filtros atuais.")

    with aba2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Mediana de Rendimento por Nível de Instrução**")
            if not df_com_renda.empty:
                pivot_esc = df_com_renda.groupby('V3009A')['Rendimento Total'].median()
                fig, ax = plt.subplots(figsize=(8, 5))
                pivot_esc.plot(kind='bar', color=COR_DESTAQUE, edgecolor='black', ax=ax)
                ax.set_ylabel('Renda Mediana (R$)')
                plt.xticks(rotation=0)
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
            else:
                st.info("Sem dados de renda para exibir.")

        with c2:
            st.markdown("**Distribuição da População por Nível de Instrução**")
            fig, ax = plt.subplots(figsize=(8, 5))
            df_filtrado['V3009A'].value_counts().sort_index().plot(kind='bar', color=COR_PRINCIPAL, edgecolor='black', ax=ax)
            ax.set_ylabel('Frequência')
            plt.xticks(rotation=0)
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)

    with aba3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Distribuição de Idade (V2009)**")
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(df_filtrado['V2009'].dropna(), bins=20, color=COR_DESTAQUE, edgecolor='black')
            ax.set_xlabel('Idade (Anos)')
            ax.set_ylabel('Frequência')
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
            
        with c2:
            st.markdown("**Mediana de Rendimento por Sexo**")
            if not df_com_renda.empty:
                pivot_sexo = df_com_renda.groupby('Sexo_Label')['Rendimento Total'].median()
                fig, ax = plt.subplots(figsize=(8, 5))
                # Alternando cores na paleta para diferenciar
                cores = [COR_SECUNDARIA, COR_PRINCIPAL] 
                pivot_sexo.plot(kind='bar', color=cores, edgecolor='black', ax=ax)
                ax.set_ylabel('Renda Mediana (R$)')
                plt.xticks(rotation=0)
                ax.grid(axis='y', alpha=0.3)
                # Anotações em cima das barras
                for index, value in enumerate(pivot_sexo):
                    ax.text(index, value + (value*0.02), f'R$ {value:.2f}', ha='center', va='bottom', fontweight='bold')
                st.pyplot(fig)
            else:
                st.info("Sem dados de renda para exibir.")

    st.markdown("---")

    # C) TABELAS E ESTATÍSTICAS
    st.subheader("Análises Tabulares e Resumos Estatísticos")
    
    col_t1, col_t2 = st.columns([1, 1])

    with col_t1:
        st.markdown("##### 1. Estatísticas Descritivas Globais")
        st.markdown("Cálculo de Média, Mediana, Desvio Padrão e Quartis das variáveis quantitativas.")
        
        # Função para Quartis
        def q1(x): return x.quantile(0.25)
        def q3(x): return x.quantile(0.75)
        
        cols_numericas = ['V2009', 'Rendimento Total']
        if all(c in df_filtrado.columns for c in cols_numericas):
            df_stats = df_filtrado[cols_numericas].agg(['mean', 'median', 'std', q1, q3]).T
            df_stats.columns = ['Média', 'Mediana', 'Desvio-Padrão', 'Q1 (25%)', 'Q3 (75%)']
            st.dataframe(df_stats.style.format("{:.2f}").background_gradient(cmap='Greens', axis=None), use_container_width=True)
            
    with col_t2:
        st.markdown("##### 2. Análise de Renda por Nível de Instrução")
        st.markdown("Comparativo de indicadores de renda agregados pela formação.")
        
        if 'V3009A' in df_filtrado.columns:
            df_esc = df_filtrado.groupby('V3009A').agg(
                Total_Pessoas=('V2009', 'count'),
                Renda_Média=('Rendimento Total', 'mean'),
                Renda_Mediana=('Rendimento Total', 'median')
            )
            df_esc.index.name = 'Código/Nível de Instrução'
            st.dataframe(df_esc.style.format({"Renda_Média": "R$ {:.2f}", "Renda_Mediana": "R$ {:.2f}"}).background_gradient(cmap='Teal', subset=['Renda_Mediana']), use_container_width=True)

    st.caption("Nota: Todos os dados apresentados respondem dinamicamente aos filtros aplicados no menu lateral esquerdo.")
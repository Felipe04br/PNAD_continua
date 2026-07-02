import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io  # Importação necessária para salvar e baixar imagens dos gráficos

# ==========================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(
    page_title="Dashboard Socioeconômico - PNAD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de cores personalizada (Verdes e Azul-Petróleo)
COR_PRINCIPAL = '#20B2AA'  # Light Sea Green
COR_SECUNDARIA = '#008080'  # Teal / Azul-petróleo
COR_DESTAQUE = '#3CB371'  # Medium Sea Green


# ==========================================================
# 2. CARREGAMENTO E TRATAMENTO DOS DADOS
# ==========================================================
@st.cache_data
def carregar_dados():
    caminho_arquivo = "Banco_de_dados.csv"
    try:
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado em: {caminho_arquivo}. Verifique se o nome e a pasta estão corretos.")
        return pd.DataFrame()

    # Tratamento de Rendimentos
    df['Rendimento Principal'] = pd.to_numeric(df.get('V403412', 0), errors='coerce').fillna(0) + \
                                 pd.to_numeric(df.get('V403422', 0), errors='coerce').fillna(0)

    df['Rendimento Secundário'] = pd.to_numeric(df.get('V405112', 0), errors='coerce').fillna(0) + \
                                  pd.to_numeric(df.get('V405122', 0), errors='coerce').fillna(0)

    df['Outros Rendimentos'] = pd.to_numeric(df.get('V405912', 0), errors='coerce').fillna(0) + \
                               pd.to_numeric(df.get('V405922', 0), errors='coerce').fillna(0)

    df['Rendimento Total'] = df['Rendimento Principal'] + df['Rendimento Secundário'] + df['Outros Rendimentos']

    # Mapeamento de Labels - Sexo (V2007)
    if 'V2007' in df.columns:
        df['V2007_Num'] = pd.to_numeric(df['V2007'], errors='coerce')
        df['Sexo_Label'] = df['V2007_Num'].map({1.0: 'Homem', 2.0: 'Mulher'}).fillna('Não Informado')

    # Mapeamento de Labels - Cor ou Raça (V2010)
    dicionario_raca = {
        1: 'Branca',
        2: 'Preta',
        3: 'Amarela',
        4: 'Parda',
        5: 'Indígena',
        9: 'Ignorado'
    }
    if 'V2010' in df.columns:
        df['V2010_Num'] = pd.to_numeric(df['V2010'], errors='coerce')
        df['Cor_Raca_Label'] = df['V2010_Num'].map(dicionario_raca).fillna('Não Informado')

    # Criação da Coluna de Período (Ano + Trimestre)
    if 'Ano' in df.columns and 'Trimestre' in df.columns:
        df['Periodo'] = df['Ano'].astype(str) + " T" + df['Trimestre'].astype(str)
    else:
        df['Periodo'] = 'Período Único'

    # Mapeamento de Labels - Nível de Instrução (V3009A)
    dicionario_instrucao = {
        1: '01 - Creche, pré-escola ou alfabetização',
        2: '02 - Ensino Fundamental (Regular)',
        3: '03 - Ensino Fundamental (EJA/Supletivo)',
        4: '04 - Ensino Médio (Regular)',
        5: '05 - Ensino Médio (EJA/Supletivo)',
        6: '06 - Superior de Graduação',
        7: '07 - Especialização de Nível Superior',
        8: '08 - Mestrado',
        9: '09 - Doutorado',
        10: '10 - Alfabetização de Jovens e Adultos',
        11: '11 - Creche',
        12: '12 - Pré-escola',
        13: '13 - Classe de Alfabetização',
        14: '14 - Alfabetização de Jovens e Adultos',
        15: '15 - Antigo Primário (Elementar)'
    }

    if 'V3009A' in df.columns:
        df['V3009A_Num'] = pd.to_numeric(df['V3009A'], errors='coerce')
        df['V3009A_Label'] = df['V3009A_Num'].map(dicionario_instrucao).fillna('Não Informado/Aplicável')

    # Criação de Faixas de Renda (Salário Mínimo base: 1412.00)
    sm = 1412.00
    limites = [-1, 0, sm, 2 * sm, 3 * sm, 5 * sm, 10 * sm, float('inf')]
    rotulos = ['Sem rendimento', 'Até 1 SM', '1 a 2 SM', '2 a 3 SM', '3 a 5 SM', '5 a 10 SM', 'Mais de 10 SM']
    df['Faixa_Renda'] = pd.cut(df['Rendimento Total'], bins=limites, labels=rotulos)

    # Garantir que a coluna V2009 (Idade) seja numérica
    if 'V2009' in df.columns:
        df['V2009'] = pd.to_numeric(df['V2009'], errors='coerce')

    return df


df = carregar_dados()

# Executa o painel apenas se o dataframe não estiver vazio
if not df.empty:

    # ==========================================================
    # 3. BARRA LATERAL (FILTROS)
    # ==========================================================
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5526/5526465.png", width=100)
    st.sidebar.title("Filtros de Interação")

    opcoes_periodo = sorted(list(df['Periodo'].dropna().unique()))
    filtro_periodos = st.sidebar.multiselect("Períodos:", opcoes_periodo, default=opcoes_periodo)

    opcoes_sexo = ['Todos'] + list(df['Sexo_Label'].dropna().unique())
    filtro_sexo = st.sidebar.selectbox("Selecionar Sexo:", opcoes_sexo)

    opcoes_raca = sorted(list(df['Cor_Raca_Label'].dropna().unique()))
    filtro_raca = st.sidebar.multiselect("Cor ou Raça (V2010):", opcoes_raca, default=opcoes_raca)

    opcoes_esc = sorted(list(df['V3009A_Label'].dropna().unique()))
    filtro_esc = st.sidebar.multiselect("Nível de Instrução (V3009A):", opcoes_esc, default=opcoes_esc)

    idade_min = int(df['V2009'].min()) if not pd.isna(df['V2009'].min()) else 0
    idade_max = int(df['V2009'].max()) if not pd.isna(df['V2009'].max()) else 100
    filtro_idade = st.sidebar.slider("Faixa Etária (V2009):", min_value=idade_min, max_value=idade_max,
                                     value=(idade_min, idade_max))

    # ==========================================================
    # APLICAÇÃO DOS FILTROS NO DATAFRAME
    # ==========================================================
    df_filtrado = df.copy()

    if filtro_periodos:
        df_filtrado = df_filtrado[df_filtrado['Periodo'].isin(filtro_periodos)]
    else:
        df_filtrado = pd.DataFrame(columns=df.columns)

    if filtro_sexo != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Sexo_Label'] == filtro_sexo]

    if filtro_raca:
        df_filtrado = df_filtrado[df_filtrado['Cor_Raca_Label'].isin(filtro_raca)]
    else:
        df_filtrado = pd.DataFrame(columns=df.columns)

    if filtro_esc:
        df_filtrado = df_filtrado[df_filtrado['V3009A_Label'].isin(filtro_esc)]
    else:
        df_filtrado = pd.DataFrame(columns=df.columns)

    df_filtrado = df_filtrado[(df_filtrado['V2009'] >= filtro_idade[0]) & (df_filtrado['V2009'] <= filtro_idade[1])]

    # ==========================================================
    # 4. CORPO DO DASHBOARD
    # ==========================================================
    st.title("📊 Dashboard Analítico PNAD - Perfil Socioeconômico")
    st.markdown("---")

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados. Por favor, ajuste as opções na barra lateral.")
    else:
        # Base de renda maior que 0
        df_com_renda = df_filtrado[df_filtrado['Rendimento Total'] > 0]

        # A) ESTATÍSTICAS DESCRITIVAS (KPIs)
        col1, col2, col3, col4 = st.columns(4)

        renda_media = df_com_renda['Rendimento Total'].mean() if not df_com_renda.empty else 0
        renda_mediana = df_com_renda['Rendimento Total'].median() if not df_com_renda.empty else 0
        idade_media = df_filtrado['V2009'].mean()
        total_pessoas = len(df_filtrado)

        col1.metric("Total de Pessoas (Amostra)", f"{total_pessoas:,}".replace(',', '.'))
        col2.metric("Renda Média", f"R$ {renda_media:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        col3.metric("Renda Mediana", f"R$ {renda_mediana:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        col4.metric("Idade Média", f"{idade_media:.1f} anos")

        st.markdown("---")

        # B) GRÁFICOS INTERATIVOS
        st.subheader("Visualizações e Gráficos")

        aba1, aba2, aba3, aba4, aba5 = st.tabs([
            "Distribuição de Renda",
            "Análise por Escolaridade",
            "Perfil Demográfico",
            "CNAE",
            "Desigualdade Social"
        ])

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

                # Download Gráfico 1
                buf1 = io.BytesIO()
                fig.savefig(buf1, format="png", bbox_inches='tight')
                st.download_button(label="📥 Baixar Gráfico (PNG)", data=buf1.getvalue(),
                                   file_name="faixas_rendimento.png", mime="image/png", key="btn_g1")

            with c2:
                st.markdown("**Mediana de Rendimento por Sexo**")
                if not df_com_renda.empty:
                    pivot_sexo = df_com_renda.groupby('Sexo_Label')['Rendimento Total'].median()
                    fig, ax = plt.subplots(figsize=(8, 5))
                    cores = [COR_SECUNDARIA, COR_PRINCIPAL]
                    pivot_sexo.plot(kind='bar', color=cores, edgecolor='black', ax=ax)
                    ax.set_ylabel('Renda Mediana (R$)')
                    plt.xticks(rotation=0)
                    ax.grid(axis='y', alpha=0.3)
                    for index, value in enumerate(pivot_sexo):
                        ax.text(index, value + (value * 0.02), f'R$ {value:.2f}', ha='center', va='bottom',
                                fontweight='bold')
                    st.pyplot(fig)

                    # Download Gráfico 2
                    buf2 = io.BytesIO()
                    fig.savefig(buf2, format="png", bbox_inches='tight')
                    st.download_button(label="📥 Baixar Gráfico (PNG)", data=buf2.getvalue(),
                                       file_name="mediana_sexo.png", mime="image/png", key="btn_g2")
                else:
                    st.info("Sem dados de renda para exibir.")

        with aba2:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Mediana de Rendimento por Nível de Instrução**")
                if not df_com_renda.empty:
                    pivot_esc = df_com_renda.groupby('V3009A_Label')['Rendimento Total'].median()
                    fig, ax = plt.subplots(figsize=(8, 5))
                    pivot_esc.plot(kind='bar', color=COR_DESTAQUE, edgecolor='black', ax=ax)
                    ax.set_ylabel('Renda Mediana (R$)')
                    plt.xticks(rotation=45, ha='right')
                    ax.grid(axis='y', alpha=0.3)
                    st.pyplot(fig)

                    # Download Gráfico 3
                    buf3 = io.BytesIO()
                    fig.savefig(buf3, format="png", bbox_inches='tight')
                    st.download_button(label="📥 Baixar Gráfico (PNG)", data=buf3.getvalue(),
                                       file_name="mediana_instrucao.png", mime="image/png", key="btn_g3")
                else:
                    st.info("Sem dados de renda para exibir.")

            with c2:
                st.markdown("**Distribuição da População por Nível de Instrução**")
                fig, ax = plt.subplots(figsize=(8, 5))
                df_filtrado['V3009A_Label'].value_counts().sort_index().plot(kind='bar', color=COR_PRINCIPAL,
                                                                             edgecolor='black', ax=ax)
                ax.set_ylabel('Frequência')
                plt.xticks(rotation=45, ha='right')
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)

                # Download Gráfico 4
                buf4 = io.BytesIO()
                fig.savefig(buf4, format="png", bbox_inches='tight')
                st.download_button(label="📥 Baixar Gráfico (PNG)", data=buf4.getvalue(),
                                   file_name="distribuicao_instrucao.png", mime="image/png", key="btn_g4")

        with aba3:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("**Distribuição de Idade (V2009)**")
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.hist(df_filtrado['V2009'].dropna(), bins=20, color=COR_DESTAQUE, edgecolor='black')
                ax.set_xlabel('Idade (Anos)')
                ax.set_ylabel('Frequência')
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)

                # Download Gráfico 5
                buf5 = io.BytesIO()
                fig.savefig(buf5, format="png", bbox_inches='tight')
                st.download_button(label="📥 Baixar Gráfico (PNG)", data=buf5.getvalue(),
                                   file_name="distribuicao_idade.png", mime="image/png", key="btn_g5")

        with aba4:
            st.markdown("**Top 10 Setores (CNAE Macro) com Maiores Rendas Medianas**")
            if not df_com_renda.empty and 'CNAE_MACRO' in df_com_renda.columns:
                pivot_cnae = df_com_renda.groupby('CNAE_MACRO')['Rendimento Total'].median().sort_values(
                    ascending=True).tail(10)
                fig, ax = plt.subplots(figsize=(12, 6))
                pivot_cnae.plot(kind='barh', color=COR_DESTAQUE, edgecolor='black', ax=ax)
                ax.set_xlabel('Renda Mediana (R$)')
                ax.grid(axis='x', alpha=0.3)
                st.pyplot(fig)

                # Download Gráfico 6
                buf6 = io.BytesIO()
                fig.savefig(buf6, format="png", bbox_inches='tight')
                st.download_button(label="📥 Baixar Gráfico (PNG)", data=buf6.getvalue(), file_name="setores_cnae.png",
                                   mime="image/png", key="btn_g6")
            else:
                st.info("A coluna CNAE_MACRO não foi encontrada ou dados insuficientes.")

        with aba5:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Mediana de Rendimento por Cor ou Raça**")
                if not df_com_renda.empty and 'Cor_Raca_Label' in df_com_renda.columns:
                    pivot_raca = df_com_renda.groupby('Cor_Raca_Label')['Rendimento Total'].median().sort_values(
                        ascending=True)
                    fig, ax = plt.subplots(figsize=(8, 5))
                    pivot_raca.plot(kind='barh', color=COR_DESTAQUE, edgecolor='black', ax=ax)
                    ax.set_xlabel('Renda Mediana (R$)')
                    ax.set_ylabel('')
                    ax.grid(axis='x', alpha=0.3)
                    st.pyplot(fig)

                    # Download Gráfico 7
                    buf7 = io.BytesIO()
                    fig.savefig(buf7, format="png", bbox_inches='tight')
                    st.download_button(label="📥 Baixar Gráfico (PNG)", data=buf7.getvalue(),
                                       file_name="mediana_raca.png", mime="image/png", key="btn_g7")
                else:
                    st.info("Sem dados de renda para exibir.")

            with c2:
                st.markdown("**Distribuição da População por Cor ou Raça**")
                if 'Cor_Raca_Label' in df_filtrado.columns:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    contagem_raca = df_filtrado['Cor_Raca_Label'].value_counts().sort_values(ascending=False)
                    contagem_raca.plot(kind='bar', color=COR_PRINCIPAL, edgecolor='black', ax=ax)
                    ax.set_ylabel('Frequência')
                    plt.xticks(rotation=45, ha='right')
                    ax.grid(axis='y', alpha=0.3)
                    st.pyplot(fig)

                    # Download Gráfico 8
                    buf8 = io.BytesIO()
                    fig.savefig(buf8, format="png", bbox_inches='tight')
                    st.download_button(label="📥 Baixar Gráfico (PNG)", data=buf8.getvalue(),
                                       file_name="distribuicao_raca.png", mime="image/png", key="btn_g8")
                else:
                    st.info("Sem dados para exibir.")

        st.markdown("---")

        # ==========================================================
        # C) TABELAS E ESTATÍSTICAS
        # ==========================================================
        st.subheader("Análises Tabulares e Resumos Estatísticos")

        col_t1, col_t2 = st.columns([1, 1])

        with col_t1:
            st.markdown("##### 1. Estatísticas Descritivas Globais")
            st.markdown("Cálculo de Média, Mediana, Desvio Padrão e Quartis das variáveis quantitativas.")


            def q1(x): return x.quantile(0.25)


            def q3(x): return x.quantile(0.75)


            if 'V2009' in df_filtrado.columns and 'Rendimento Total' in df_com_renda.columns:
                df_stats_idade = df_filtrado[['V2009']].rename(columns={'V2009': 'Idade'}).agg(
                    ['mean', 'median', 'std', q1, q3]).T
                df_stats_renda = df_com_renda[['Rendimento Total']].agg(['mean', 'median', 'std', q1, q3]).T

                df_stats = pd.concat([df_stats_idade, df_stats_renda])
                df_stats.columns = ['Média', 'Mediana', 'Desvio-Padrão', 'Q1 (25%)', 'Q3 (75%)']
                df_stats.index.name = 'Variável'

                st.dataframe(df_stats.style.format("{:.2f}").background_gradient(cmap='Greens', axis=None),
                             use_container_width=True)

                # Download Tabela 1 (CSV)
                csv_stats = df_stats.to_csv().encode('utf-8')
                st.download_button(label="📥 Baixar Tabela (CSV)", data=csv_stats, file_name="estatisticas_globais.csv",
                                   mime="text/csv", key="btn_t1")

        with col_t2:
            st.markdown("##### 2. Análise de Renda por Nível de Instrução")
            st.markdown("Comparativo de indicadores de renda agregados pela formação.")

            if 'V3009A_Label' in df_filtrado.columns:
                df_esc = df_com_renda.groupby('V3009A_Label').agg(
                    Total_Pessoas=('Rendimento Total', 'count'),
                    Renda_Média=('Rendimento Total', 'mean'),
                    Renda_Mediana=('Rendimento Total', 'median')
                )
                df_esc.index.name = 'Nível de Instrução'
                st.dataframe(
                    df_esc.style.format({"Renda_Média": "R$ {:.2f}", "Renda_Mediana": "R$ {:.2f}"}).background_gradient(
                        cmap='GnBu', subset=['Renda_Mediana']), use_container_width=True)

                # Download Tabela 2 (CSV)
                csv_esc = df_esc.to_csv().encode('utf-8')
                st.download_button(label="📥 Baixar Tabela (CSV)", data=csv_esc, file_name="renda_por_instrucao.csv",
                                   mime="text/csv", key="btn_t2")

        st.caption(
            "Nota: Todos os dados apresentados respondem dinamicamente aos filtros aplicados no menu lateral esquerdo. As estatísticas de renda englobam apenas pessoas com rendimento superior a zero.")
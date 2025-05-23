# Instale dependências necessárias (se ainda não fez)
#!pip install streamlit pandas numpy matplotlib seaborn plotly scikit-learn pyngrok --quiet

# Salve o app.py atualizado com duas abas: individual e geral
#%%writefile app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Dashboard Ambiental - I²A²", layout='wide')

# Carregar e mostrar o logo do grupo no topo
logo = Image.open("logo_grupo88.png")

st.image(logo, width=50)  # Ajuste a largura conforme necessário
# TELA INICIAL DO GRUPO
st.markdown("## 👥 Grupo 88 – Projeto Avaliativo I²A²")
st.markdown("### Alunos:")
st.markdown("""
- João Paulo da Silva Cardoso – celular: +55 91 98273-6292
- Lucas Maia – celular: +55 91 98063-5989
- Adrianny Lima – celular: +55 91 98119-6260
- Denis de Castro Silva – celular: +55 91 98164-9172
- Renato Moraes da Silva – celular: +55 91 99318-1086
- Arthur Melo – celular: +55 91 98325-2564
""")
st.markdown("---")
st.markdown("### ⚠️ Faça o upload do dataset para continuar:")
uploaded_file = st.file_uploader("Upload do arquivo CSV", type=["csv"])
      
if uploaded_file is not None:

    # Carregar dados
    df = pd.read_csv(uploaded_file)
    
    # Classificar risco de queimada
    def classificar_risco(freq):
        if freq > 7:
            return 'Alto'
        elif 4 <= freq <= 7:
            return 'Médio'
        else:
            return 'Baixo'

    df['Risco de Queimada'] = df['Frequência de Queimadas (ano)'].apply(classificar_risco)

    # Abas para navegação
    tab1, tab2 = st.tabs(["📍 Análise Individual", "🌍 Análise Geral das 200 Comunidades"])

    with tab1:
        # Sidebar - Filtros
        st.sidebar.header("🔍 Filtros")
        municipios = sorted(df['Município'].unique())
        municipio_selecionado = st.sidebar.selectbox("Selecione um Município", options=municipios, key="municipio_ind")

        # Filtrar comunidades do município selecionado
        df_municipio = df[df['Município'] == municipio_selecionado]
        comunidades_do_municipio = sorted(df_municipio['Comunidade'].unique())
        comunidade_selecionada = st.sidebar.selectbox("Selecione uma Comunidade", options=comunidades_do_municipio, key="comunidade_ind")

        # Dados da comunidade selecionada
        df_comunidade = df_municipio[df_municipio['Comunidade'] == comunidade_selecionada]

        # Seção 1: Informações da Comunidade
        st.subheader(f"📍 Informações da Comunidade: {comunidade_selecionada}")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Município:** {df_comunidade['Município'].values[0]}")
            st.markdown(f"**Estado:** {df_comunidade['Estado'].values[0]}")
            st.markdown(f"**Presença de Escola:** {df_comunidade['Presença de Escola (Sim/Não)'].values[0]}")
            st.markdown(f"**Unidade de Saúde:** {df_comunidade['Presença de Unidade de Saúde (Sim/Não)'].values[0]}")
            st.markdown(f"**Risco Ambiental:** {df_comunidade['Risco de Queimada'].values[0]}")

        with col2:
            st.markdown(f"**Cobertura Vegetal (%):** {df_comunidade['Cobertura Vegetal (%)'].values[0]}")
            st.markdown(f"**Queimadas/Ano:** {df_comunidade['Frequência de Queimadas (ano)'].values[0]}")
            st.markdown(f"**Renda Média (R$):** R$ {df_comunidade['Renda Média Mensal (R$)'].values[0]:,.2f}")
            st.markdown(f"**Distância Urbana (km):** {df_comunidade['Distância de Área Urbana (km)'].values[0]} km")
            st.markdown(f"**Acesso à Água Potável (%):** {df_comunidade['Acesso à Água Potável (%)'].values[0]}")

        # Calcular médias do município
        medias_municipio = df_municipio[['Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)',
                                        'Renda Média Mensal (R$)', 'Distância de Área Urbana (km)']].mean().round(2)

        # Dados da comunidade selecionada
        dados_comunidade = df_comunidade[['Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)',
                                        'Renda Média Mensal (R$)', 'Distância de Área Urbana (km)']].iloc[0].round(2)

        # Gráficos comparativos
        st.subheader("🧮 Comparação com a Média do Município")

        for var in ['Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)', 'Renda Média Mensal (R$)', 'Distância de Área Urbana (km)']:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[comunidade_selecionada],
                y=[dados_comunidade[var]],
                name=f'Comunidade',
                marker_color='skyblue'
            ))
            fig.add_trace(go.Bar(
                x=['Média do Município'],
                y=[medias_municipio[var]],
                name=f'Média de {municipio_selecionado}',
                marker_color='lightgreen'
            ))

            fig.update_layout(
                title=f"{var} - {comunidade_selecionada} vs Média do Município",
                yaxis_title=var,
                xaxis_title="",
                barmode='group',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        # Boxplot do município para análise geral
        st.subheader("🧩 Distribuição Geral das Comunidades no Município")
        variavel_boxplot = st.selectbox("Selecione a variável para análise", [
            'Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)', 'Renda Média Mensal (R$)',
            'Acesso à Água Potável (%)', 'Distância de Área Urbana (km)'
        ])
        fig_box = px.box(df_municipio, y=variavel_boxplot, points="all",
                         color='Comunidade', hover_name='Comunidade',
                         title=f"Distribuição de '{variavel_boxplot}' no município {municipio_selecionado}")
        st.plotly_chart(fig_box, use_container_width=True)

        # Gráfico de dispersão local
        st.subheader("🌱 Relação entre Cobertura Vegetal e Frequência de Queimadas")
        fig_scatter = px.scatter(
            df_municipio,
            x='Cobertura Vegetal (%)',
            y='Frequência de Queimadas (ano)',
            color='Comunidade',
            size='Frequência de Queimadas (ano)',
            hover_name='Comunidade',
            title=f"Relação no Município de {municipio_selecionado}"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Hipótese Ambiental
        st.subheader("🧠 Hipótese Ambiental Sugerida")
        st.markdown("""
        > **Comunidades com menor cobertura vegetal parecem ter maior frequência de queimadas**, independentemente do nível de renda ou acesso à água potável.
        
        Essa tendência pode estar associada à pressão antrópica, expansão agrícola ou atividades ilegais como extração de madeira e abertura de pastagens.
        """)

        # Recomendação de Uso da IA
        st.subheader("🤖 Recomendação de Uso da Inteligência Artificial")
        st.markdown("""
        Uma técnica valiosa de Inteligência Artificial aplicada foi a **clusterização com K-Means**, usada para agrupar comunidades com características similares. Isso permitiu identificar grupos de comunidades com comportamentos semelhantes e priorizar políticas públicas localizadas.

        Também é possível usar modelos simples de **classificação com Árvore de Decisão**, treinando um modelo com base na cobertura vegetal, proximidade urbana e renda, para prever quais comunidades estão mais propensas a ter alta frequência de queimadas.

        Mesmo sem correlações estatísticas fortes, essas técnicas ajudam a organizar os dados e extrair conhecimento útil para educação ambiental e planejamento territorial.
        """)

        # Tabela com todas as comunidades do município
        st.subheader(f"🧑‍🤝‍🧑 Comunidades do Município: {municipio_selecionado}")
        st.dataframe(df_municipio[['Comunidade', 'Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)',
                                  'Renda Média Mensal (R$)', 'Distância de Área Urbana (km)', 'Risco de Queimada']])

    with tab2:
        st.subheader("🌍 Análise Geral das 200 Comunidades")
        st.markdown("### 🔍 Padrões Ambientais entre Todas as Comunidades")

        # Histograma geral da frequência de queimadas
        st.markdown("#### 🔥 Frequência de Queimadas nas 200 Comunidades")
        fig_hist_queimadas = px.histogram(df, x='Frequência de Queimadas (ano)', nbins=10,
                                          title="Distribuição de Queimadas nas Comunidades")
        st.plotly_chart(fig_hist_queimadas, use_container_width=True)

        # Scatter Plot entre Cobertura Vegetal e Queimadas (todas as comunidades)
        st.markdown("#### 🌱 Relação entre Cobertura Vegetal e Frequência de Queimadas")
        fig_scatter_all = px.scatter(
            df,
            x='Cobertura Vegetal (%)',
            y='Frequência de Queimadas (ano)',
            color='Risco de Queimada',
            size='Índice de Desmatamento (%)',
            hover_name='Comunidade',
            title="Relação Geral entre Cobertura Vegetal e Frequência de Queimadas"
        )
        st.plotly_chart(fig_scatter_all, use_container_width=True)

        # Boxplot por risco
        st.markdown("#### 🧩 Distribuição por Nível de Risco")
        fig_box_risco = px.box(df, x='Risco de Queimada', y='Cobertura Vegetal (%)', points="all",
                              title="Cobertura Vegetal por Nível de Risco")
        st.plotly_chart(fig_box_risco, use_container_width=True)

        # Clusterização com K-Means (para todas as comunidades)
        st.subheader("#### 🤖 Agrupamento com IA – K-Means")
        cols_cluster = ['Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)', 'Distância de Área Urbana (km)', 'Índice de Desmatamento (%)']
        X = df[cols_cluster]

        # Padronizar os dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Aplicar K-Means
        kmeans = KMeans(n_clusters=4, random_state=42)
        kmeans.fit(X_scaled)  # Aqui está a correção
        df['Cluster'] = kmeans.labels_  # Agora funciona!

        # Scatter Plot colorido por cluster
        fig_cluster = px.scatter(
            df,
            x='Cobertura Vegetal (%)',
            y='Frequência de Queimadas (ano)',
            color='Cluster',
            size='Índice de Desmatamento (%)',
            hover_name='Comunidade',
            title="Agrupamento com K-Means (Todas as Comunidades)"
        )
        st.plotly_chart(fig_cluster, use_container_width=True)

        # Boxplot de Queimadas por Cluster
        fig_box_cluster = px.box(df, x='Cluster', y='Frequência de Queimadas (ano)', points="all",
                                title="Distribuição de Queimadas por Grupo (Cluster)")
        st.plotly_chart(fig_box_cluster, use_container_width=True)

        # Mapa Simulado por Risco Ambiental
        st.markdown("#### 🗺️ Localização Simulada por Risco Ambiental")

        municipios_coords = {
            "SÃO DOMINGOS DO CAPIM": (-1.4556, -48.4902),
            "SALINÓPOLIS": (-1.3765, -46.7442),
            "TRACUATEUA": (-1.4333, -47.7667),
            "SÃO MIGUEL DO GUAMÁ": (-1.6333, -48.4333),
            "PALESTINA DO PARÁ": (-5.8795, -47.9297),
            "ALTAMIRA": (-3.2017, -52.2194),
            "SANTARÉM": (-2.4396, -54.7306),
            "BELÉM": (-1.4556, -48.4902),
        }

        df['Latitude'] = df['Município'].map(lambda m: municipios_coords.get(m, (np.nan, np.nan))[0])
        df['Longitude'] = df['Município'].map(lambda m: municipios_coords.get(m, (np.nan, np.nan))[1])

        fig_mapa_all = px.scatter_mapbox(
            df.dropna(subset=['Latitude', 'Longitude']),
            lat='Latitude',
            lon='Longitude',
            color='Risco de Queimada',
            size='Frequência de Queimadas (ano)',
            hover_name='Comunidade',
            zoom=4,
            center={"lat": -3, "lon": -50},
            mapbox_style="open-street-map",
            title="Localização Simulada por Risco Ambiental"
        )
        st.plotly_chart(fig_mapa_all, use_container_width=True)

        # Tabela dos clusters
        st.markdown("#### 📋 Clusters de Vulnerabilidade Ambiental")
        st.dataframe(df[['Comunidade', 'Município', 'Cluster', 'Risco de Queimada', 'Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)']].head(15))

        # Serviços Básicos por Município
        # Presença de Escola por Município
        st.markdown("### 👩‍🏫 Presença de Escolas por Município")

        # Contagem de 'Sim/Não' por município
        escola_por_municipio = df.groupby('Município')['Presença de Escola (Sim/Não)'].value_counts().unstack(fill_value=0)
        escola_por_municipio['Total'] = escola_por_municipio['Sim'] + escola_por_municipio['Não']
        escola_por_municipio['% Escolas'] = (escola_por_municipio['Sim'] / escola_por_municipio['Total']) * 100
        escola_por_municipio = escola_por_municipio[['Sim', 'Não', '% Escolas']].round(2)

        # Gráfico de barras empilhadas – Escolas
        fig_escola = px.bar(
            escola_por_municipio.reset_index(),
            x='Município',
            y=['Sim', 'Não'],
            title="Distribuição de Comunidades com e sem Escolas",
            labels={'value': 'Quantidade', 'variable': 'Presença de Escola'},
            barmode='group'
        )
        st.plotly_chart(fig_escola, use_container_width=True)

        # Tabela de escolas
        st.markdown("#### 📋 Tabela: Presença de Escolas")
        st.dataframe(escola_por_municipio[['Sim', 'Não', '% Escolas']])


        # Presença de Unidade de Saúde por Município
        st.markdown("### 🏥 Presença de Unidades de Saúde por Município")

        saude_por_municipio = df.groupby('Município')['Presença de Unidade de Saúde (Sim/Não)'].value_counts().unstack(fill_value=0)
        saude_por_municipio['Total'] = saude_por_municipio['Sim'] + saude_por_municipio['Não']
        saude_por_municipio['% Saúde'] = (saude_por_municipio['Sim'] / saude_por_municipio['Total']) * 100
        saude_por_municipio = saude_por_municipio[['Sim', 'Não', '% Saúde']].round(2)

        # Gráfico de barras – Saúde
        fig_saude = px.bar(
            saude_por_municipio.reset_index(),
            x='Município',
            y=['Sim', 'Não'],
            title="Distribuição de Comunidades com e sem Unidade de Saúde",
            labels={'value': 'Quantidade', 'variable': 'Presença de Saúde'},
            barmode='group'
        )
        st.plotly_chart(fig_saude, use_container_width=True)

        # Tabela de saúde
        st.markdown("#### 📋 Tabela: Presença de Unidade de Saúde")
        st.dataframe(saude_por_municipio[['Sim', 'Não', '% Saúde']])





    # Registro Escrito Final (até 150 palavras)
    st.subheader("📝 Registro Escrito Final (até 150 palavras)")
    st.markdown("""
    Após análise exploratória do dataset fornecido pela I²A², observamos que comunidades com menor cobertura vegetal tendem a apresentar maior incidência de queimadas, independentemente da renda ou acesso a serviços básicos. Utilizamos técnicas de visualização e IA para agrupar comunidades com perfis similhantes e priorizar intervenções. O dashboard permite filtrar por município e comunidade, comparando seus indicadores com a média local. Além disso, incluímos uma seção dedicada à análise geral das 200 comunidades, com histogramas, boxplots e clusterização com K-Means, revelando padrões territoriais importantes. Mesmo sem correlações estatísticas fortes, a leitura crítica dos dados ajuda a identificar vulnerabilidades e apoiar decisões com base em evidências locais. A proposta reforça o uso da IA como ferramenta de apoio à análise ambiental, promovendo justiça socioambiental e cidadania consciente.
    """)

else:
    st.info("📂 Aguarde o upload do dataset para iniciar a análise.")

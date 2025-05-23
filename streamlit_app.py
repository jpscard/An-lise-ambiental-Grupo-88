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
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Dashboard Ambiental - I²A²", layout='wide')

# Função para centralizar elementos com markdown
def center_element(element, width=50):
    col1, col2, col3 = st.columns([1, width, 1])
    with col2:
        st.markdown(element, unsafe_allow_html=True)

# Carregar logo e mostrar centralizado
logo = Image.open("logo_grupo88.png")
center_element(f"<div style='text-align:center;'><img src='Analise_Ambiental-Grupo-88/logo_grupo88.png;base64,{image_to_base64(logo)}' width='200'></div>")

# Título centralizado
center_element("<h1 style='text-align:center;'>Dashboard Ambiental - Projeto I²A²</h1>")
center_element("<h3 style='text-align:center;'>Grupo 88 – Inteligência Artificial Aplicada à Análise Ambiental</h3>")

# Função auxiliar para converter imagem em base64
def image_to_base64(img):
    import base64
    from io import BytesIO
    buffered = BytesIO()
    img.save(buffered, format=img.format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Navegação no sidebar
st.sidebar.title("🧭 Navegação")
pagina = st.sidebar.radio("Ir para", ["Apresentação", "Análise Individual", "Análise Geral das 200 Comunidades"])

# Seção de apresentação
if pagina == "Apresentação":
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
        st.session_state.uploaded_file = uploaded_file
        st.success("✅ Dataset carregado com sucesso! Acesse as outras páginas no menu lateral.")

# Análise Individual
elif pagina == "Análise Individual":
    if 'uploaded_file' not in st.session_state:
        st.warning("⚠️ Por favor, faça o upload do dataset na aba de Apresentação primeiro.")
    else:
        uploaded_file = st.session_state.uploaded_file
        df = pd.read_csv(uploaded_file)

        def classificar_risco(freq):
            if freq > 7:
                return 'Alto'
            elif 4 <= freq <= 7:
                return 'Médio'
            else:
                return 'Baixo'

        df['Risco de Queimada'] = df['Frequência de Queimadas (ano)'].apply(classificar_risco)

        # Filtros no sidebar
        st.sidebar.header("🔍 Filtros")
        municipios = sorted(df['Município'].unique())
        municipio_selecionado = st.sidebar.selectbox("Selecione um Município", options=municipios, key="municipio_ind")
        df_municipio = df[df['Município'] == municipio_selecionado]
        comunidades_do_municipio = sorted(df_municipio['Comunidade'].unique())
        comunidade_selecionada = st.sidebar.selectbox("Selecione uma Comunidade", options=comunidades_do_municipio, key="comunidade_ind")
        df_comunidade = df_municipio[df_municipio['Comunidade'] == comunidade_selecionada]

        # Informações da comunidade
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

        # Comparativos com média do município
        medias_municipio = df_municipio[['Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)',
                                         'Renda Média Mensal (R$)', 'Distância de Área Urbana (km)']].mean().round(2)
        dados_comunidade = df_comunidade[['Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)',
                                         'Renda Média Mensal (R$)', 'Distância de Área Urbana (km)']].iloc[0].round(2)

        for var in ['Cobertura Vegetal (%)', 'Frequência de Queimadas (ano)', 'Renda Média Mensal (R$)', 'Distância de Área Urbana (km)']:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=[comunidade_selecionada], y=[dados_comunidade[var]], name=f'Comunidade'))
            fig.add_trace(go.Bar(x=['Média do Município'], y=[medias_municipio[var]], name=f'Média de {municipio_selecionado}'))
            fig.update_layout(title=f"{var} - {comunidade_selecionada} vs Média do Município", barmode='group', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# Análise Geral
elif pagina == "Análise Geral das 200 Comunidades":
    if 'uploaded_file' not in st.session_state:
        st.warning("⚠️ Por favor, faça o upload do dataset na aba de Apresentação primeiro.")
    else:
        uploaded_file = st.session_state.uploaded_file
        df = pd.read_csv(uploaded_file)

        def classificar_risco(freq):
            if freq > 7:
                return 'Alto'
            elif 4 <= freq <= 7:
                return 'Médio'
            else:
                return 'Baixo'

        df['Risco de Queimada'] = df['Frequência de Queimadas (ano)'].apply(classificar_risco)

        st.subheader("🌍 Análise Geral das 200 Comunidades")
        st.markdown("### 🔍 Padrões Ambientais entre Todas as Comunidades")

        # Histograma geral
        fig_hist_queimadas = px.histogram(df, x='Frequência de Queimadas (ano)', nbins=10,
                                          title="Distribuição de Queimadas nas Comunidades")
        st.plotly_chart(fig_hist_queimadas, use_container_width=True)

        # Scatter Plot
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

# Sidebar com conclusões e análises gerais
st.sidebar.markdown("## 📌 Conclusões e Análises Principais")
st.sidebar.markdown("""
- **Comunidades com menor cobertura vegetal tendem a ter maior frequência de queimadas**, independentemente de renda ou acesso à água.
- O uso de **K-Means** ajudou a identificar grupos com características similares para políticas públicas localizadas.
- Mesmo sem correlações estatísticas fortes, técnicas de visualização e IA ajudam a extrair conhecimento útil para educação ambiental.
""")

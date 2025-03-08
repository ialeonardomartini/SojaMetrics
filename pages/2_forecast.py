import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import statsmodels.api as sm
import numpy as np
import os

# ---------------------- config streamlit ----------------------------------------

st.set_page_config(page_title = "Forecast da Soja", layout = "wide")
st.sidebar.markdown("Desenvolvido por [Leonardo Martini](https://www.linkedin.com/in/leonardormartini/)")





# ------------------------------------ Carregamento dos DADOS -----------------------------------------------------

# Obtendo o diretório base do script atual
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))

# Construindo os caminhos completos para os arquivos
path_soja_mensal = os.path.join(base_dir, "soja_mensal.csv")
path_soja_anual = os.path.join(base_dir, "soja_anual.csv")
path_variacao_cambial = os.path.join(base_dir, "variacao_cambial.csv")

# Verificando se os arquivos existem antes de carregar
if not os.path.exists(path_soja_mensal):
    raise FileNotFoundError(f"❌ Arquivo não encontrado: {path_soja_mensal}")
if not os.path.exists(path_soja_anual):
    raise FileNotFoundError(f"❌ Arquivo não encontrado: {path_soja_anual}")
if not os.path.exists(path_variacao_cambial):
    raise FileNotFoundError(f"❌ Arquivo não encontrado: {path_variacao_cambial}")

# Carregando os arquivos CSV no pandas
df = pd.read_csv(path_soja_mensal, index_col=0)
df_ano = pd.read_csv(path_soja_anual)
df_dolar = pd.read_csv(path_variacao_cambial, index_col=0)

# 1️⃣ Garantir que a coluna de datas está no formato correto
df["ano_mes"] = pd.to_datetime(df["ano_mes"])
df["periodo"] = df["ano_mes"]
df_ano["periodo"] = pd.to_datetime(df_ano["periodo"], format="%Y")
df_dolar["periodo"] = pd.to_datetime(df_dolar["datetime"])
df_dolar = df_dolar.rename(columns={"close": "cambio_usdbrl"})

# 2️⃣ Criar `df_saldo` com os dados mensais
df_saldo = df[(df["ano"] >= 2000) & (df["ano"] <= 2024)].copy()
df_saldo["periodo"] = pd.to_datetime(df_saldo["ano_mes"])
df_saldo.loc[:, "saldo_estoque"] = df_saldo["estoque"].diff()
df_saldo = df_saldo.fillna(0)

# 3️⃣ Converter `df_dolar` para dados mensais pegando o último valor de cada mês
df_dolar_mensal = df_dolar.resample("M", on="periodo").last().reset_index()

# 4️⃣ Ajustar `periodo` para o primeiro dia do mês (01)
df_dolar_mensal["periodo"] = df_dolar_mensal["periodo"].dt.to_period("M").dt.to_timestamp()

# 4️⃣ Mesclar `df_saldo` (mensal) com `df_dolar_mensal` (câmbio mensal)
df_saldo = df_saldo.merge(df_dolar_mensal[["periodo", "cambio_usdbrl"]], on="periodo", how="left")


# ------------------------------------ Interface do Usuário ----------------------------------------

with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>📈 Previsão de Preços da Soja</h3>", unsafe_allow_html=True)

    # **1️⃣ Seção para entrada de dados do usuário**
    st.markdown("### 🔢 Insira os valores para prever o preço da soja:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cambio_previsto = st.number_input("Câmbio USD/BRL esperado:", min_value=3.0, max_value=10.0, value=6.0, step=0.1)
        #saldo_oferta_demanda = st.number_input("Saldo Oferta-Demanda esperado (mil toneladas):", min_value=-50000, max_value=50000, value=0, step=1000)

    with col2:
        periodo_previsto = st.slider("Quantos meses no futuro deseja prever?", min_value=1, max_value=48, value=12, step=1)

    
    # Selecionar a variável de preço a ser prevista
    preco_selecionado = st.selectbox("Selecione o Preço a Ser Previsto:", 
                                     ["Chicago - CBOT (US$/t)", "FOB Porto - Paranaguá (US$/t)", 
                                      "Maringá / PR - R$/saca (sem ICMS)", "Mogiana / SP - R$/saca (sem ICMS)", 
                                      "Passo Fundo / RS - R$/saca (sem ICMS)", "Rondonopolis / MT - R$/saca (sem ICMS)"],
                                      index=5)
    
    tabela_precos = {
        "Chicago - CBOT (US$/t)": "chicago_cbot_u$/t",
        "FOB Porto - Paranaguá (US$/t)": "fob_porto_paranagua_u$/t",
        "Maringá / PR - R$/saca (sem ICMS)": "maringa_r$/saca",
        "Mogiana / SP - R$/saca (sem ICMS)": "mogiana_r$/saca",
        "Passo Fundo / RS - R$/saca (sem ICMS)": "passofundo_r$/saca",
        "Rondonopolis / MT - R$/saca (sem ICMS)": "rondonopolis_r$/saca",
    }
    
    coluna_preco = tabela_precos[preco_selecionado]
    

    # Preparação dos dados**
    df_modelo = df_saldo.copy()
    df_modelo = df_modelo.sort_values("periodo")
    df_modelo = df_modelo[["periodo", coluna_preco, "cambio_usdbrl"]].dropna()

    # **3️⃣ Construção do Modelo de Machine Learning (Regressão OLS Simples)**
    X = df_modelo[["cambio_usdbrl"]]
    y = df_modelo[[coluna_preco]]
    X, y = X.align(y, join="inner", axis=0)
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()
    residuos = model.resid  # Diferença entre valores reais e previstos
    desvio_padrao = np.std(residuos)

    # Previsão do Preço Futuro 
    dados_previstos = pd.DataFrame({
        "const": 1,
        "cambio_usdbrl": cambio_previsto
    }, index=[df_modelo["periodo"].max() + pd.DateOffset(months=periodo_previsto)])

    previsao = model.predict(dados_previstos)[0]

    df_futuro = df_modelo.copy()
    df_futuro["periodo"] = pd.to_datetime(df_futuro["periodo"])
    data_futura = df_futuro["periodo"].max() + pd.DateOffset(months=periodo_previsto)
    df_previsao = pd.DataFrame({"periodo": [data_futura], coluna_preco: [previsao], "cambio_usdbrl": [cambio_previsto]})
    df_futuro = pd.concat([df_futuro, df_previsao], ignore_index=True)

    # Supondo que data_futura seja um objeto datetime
    data_futura_formatada = data_futura.strftime("%Y-%m")  # Formato AAAA-MM

    # Formatando previsao como moeda em reais (R$)
    previsao_formatada = f"{previsao:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # **5️⃣ Exibição dos Resultados**
    st.markdown(f"### 📊 Preço previsto para {data_futura_formatada} em {previsao_formatada} {preco_selecionado.split("-")[1]}")

    # 🔹 Ajuste do intervalo de confiança apenas para a previsão
    fator_confianca = 1.5  # Ajuste fino para evitar intervalos muito amplos
    limite_superior = previsao + (fator_confianca * desvio_padrao)
    limite_inferior = previsao - (fator_confianca * desvio_padrao)

    # 🔹 Última data real do preço (precisamos incluir no intervalo)
    ultima_data_real = df_futuro["periodo"].max() - pd.DateOffset(months=periodo_previsto)

    # Criar DataFrame do intervalo para incluir a última data real
    df_confianca = pd.DataFrame({
        "periodo": [ultima_data_real, data_futura],
        "limite_superior": [df_futuro[df_futuro["periodo"] == ultima_data_real][coluna_preco].values[0], limite_superior],
        "limite_inferior": [df_futuro[df_futuro["periodo"] == ultima_data_real][coluna_preco].values[0], limite_inferior]
    })

    # **6️⃣ Gráfico de projeção**
    fig_forecast = go.Figure()

    fig_forecast.add_trace(go.Scatter(
        x=df_futuro["periodo"], 
        y=df_futuro[coluna_preco], 
        mode="lines", 
        name="Histórico", 
        line=dict(color="yellow", width=2)
    ))

    fig_forecast.add_trace(go.Scatter(
        x=[data_futura], 
        y=[previsao], 
        mode="markers", 
        name="Previsão",
        marker=dict(color="red", size=15, symbol="circle")
    ))

    fig_forecast.add_trace(go.Scatter(
        x=[ultima_data_real, data_futura, data_futura, ultima_data_real],  
        y=[df_confianca["limite_superior"].iloc[0], df_confianca["limite_superior"].iloc[1], 
            df_confianca["limite_inferior"].iloc[1], df_confianca["limite_inferior"].iloc[0]],  
        fill="toself",
        fillcolor="rgba(255,140,0,0.3)",  # Laranja escuro com transparência
        line=dict(color="rgba(255,140,0,1)", dash="dash", width=1),  # Contorno laranja forte
        name="Intervalo de Confiança (95%)"
    ))

    fig_forecast.update_layout(
        xaxis_title="Ano",
        yaxis_title=preco_selecionado,
        height=400,
        margin=dict(l=10, r=10, t=25, b=10),
        xaxis=dict(
            showline=True,  
            linecolor="gray",  
            linewidth=1, 
            tickmode="linear",
            dtick="M12",
            tickformat="%Y",
            tickangle = 45,
            showgrid = True,
            gridwidth = 0.5
            ),
        yaxis=dict(
            showline=True,  # Linha no zero do eixo Y
            linecolor="gray",
            linewidth=1,
            showgrid = True,
            gridwidth = 0.1
            ),
        legend=dict(
            orientation="h",  # Legenda horizontal
            yanchor="top", 
            y=-0.3,  # Move a legenda para baixo do eixo X
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig_forecast, use_container_width=True)

    # 🔍 Exibir estatísticas do modelo

    col1, col2, col3, col4, col5 = st.columns([0.25, 0.25, 0.2, 0.2, 0.2])
    with col1:
        st.metric(label="Coeficiente de Determinação (R²)", value=f"{model.rsquared:.4f}")
    
    with col2:
        st.metric(label="Desvio Padrão dos Resíduos", value=f"{desvio_padrao:.2f}")

    with col3:
        st.metric(label="Limite superior", value=f"{limite_superior:.2f}")
    
    with col4:
        st.metric(label="Previsão", value=f"{previsao:.2f}")

    with col5:
        st.metric(label="Limite inferior", value=f"{limite_inferior:.2f}")
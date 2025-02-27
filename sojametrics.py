import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# -------------------------------- funções --------------------------------------------

def plot_sparkline(df_ano, coluna, titulo):
    """Cria um pequeno gráfico de linha (sparkline) para mostrar a evolução do KPI."""

    # Definir se a tendência é de alta (verde) ou baixa (vermelho)
    inicio = df_ano[coluna].iloc[0]
    fim = df_ano[coluna].iloc[-1]
    cor_verde = "#2ca02c"  # Verde vibrante do Streamlit
    cor_vermelha = "#d62728"  # Vermelho vibrante do Streamlit
    cor = cor_verde if fim >= inicio else cor_vermelha
    fill_cor = "rgba(44, 200, 44, 0.3)" if fim >= inicio else "rgba(214, 39, 40, 0.3)"  # Transparência ajustada

    fig = go.Figure()

    
    fig.add_trace(go.Scatter(
        x=df_ano["periodo"], 
        y=df_ano[coluna], 
        mode='lines',
        fill='tozeroy',
        line=dict(width=2, color=cor),
        fillcolor=fill_cor,
        name=titulo
    ))

    # Personalizando o layout do gráfico
    fig.update_layout(
        height=50,  # Altura pequena para o gráfico ficar compacto
        margin=dict(l=20, r=20, t=0, b=0),  # Remove margens para economizar espaço
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),  # Esconder eixos
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    )
    
    return fig




# ------------------------------------ Carregamento DADOS -----------------------------------------------------

df = pd.read_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/database/soja_mensal.csv", index_col = 0)
df_ano = pd.read_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/database/soja_anual.csv")
df_dolar = pd.read_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/database/variacao_cambial.csv", index_col=0)
df = df[(df["ano"] >= 2000) & (df["ano"] <= 2024)]
df_ano = df_ano[(df_ano["periodo"] >= 2000) & (df_ano["periodo"] <= 2024)]
df_dolar = df_dolar[(df_dolar["ano"] >= 2000) & (df_dolar["ano"] <= 2024)]

# ---------------------- config streamlit ----------------------------------------

st.set_page_config(page_title = "sojametrics", layout = "wide")




# --------------------------- titulo -----------------------------------------------
with st.container(border=True):

        st.markdown("<h3 style='margin-left: 10px;'> 🌾 A Dinâmica da Soja: Como Câmbio, Oferta e Demanda Impactam os Preços no Brasil</h3>", unsafe_allow_html=True)
        st.markdown("<h5 style='margin-left: 10px;'> Fonte Dados: ABIOVE</h5>", unsafe_allow_html=True)



# ----------------------------- seção 01 - KPIs ------------------------------------

with st.container(border=True):

    subtitulo, periodo, preco = st.columns([2,1,1.5])    

    with subtitulo:
    
        st.markdown("<h4 style='margin-top: 10px; margin-left: 10px;''>📊 KPIs para Panorama do Mercado de Soja</h4>", unsafe_allow_html=True)

    with periodo:
        anos_selecionados = st.slider("Selecione o Período:", 
                                    min_value=int(df["ano"].min()), 
                                    max_value=int(df["ano"].max()), 
                                    value=(int(df["ano"].min()), int(df["ano"].max())),
                                    key="slider_1")

    with preco:
        preco_selecionado = st.selectbox("Selecione o Preço:", 
                                        ("Chicago - CBOT (US$/t)", 
                                        "FOB Porto - Paranaguá (US$/t)", 
                                        "Maringá / PR - R$/saca (sem ICMS)", 
                                        "Mogiana / SP - R$/saca (sem ICMS)", 
                                        "Passo Fundo / RS - R$/saca (sem ICMS)", 
                                        "Rondonopolis / MT - R$/saca (sem ICMS)"), 
                                        index = 5,
                                        key="select_1")

    # filtro e tratamento de dados

    df_kpi = df[(df["ano"] >= anos_selecionados[0]) & (df["ano"] <= anos_selecionados[1])]
    df_ano_kpi = df_ano[(df_ano["periodo"] >= anos_selecionados[0]) & (df_ano["periodo"] <= anos_selecionados[1])]
    df_dolar_kpi = df_dolar[(df_dolar["ano"] >= anos_selecionados[0]) & (df_dolar["ano"] <= anos_selecionados[1])]
    df_kpi["ano_mes"] = pd.to_datetime(df_kpi["ano_mes"])
    df_kpi["periodo"] = df_kpi["ano_mes"]
    df_ano_kpi["saldo"] = df_ano_kpi["estoque_final"] - df_ano_kpi["estoque_inicial"]
    df_dolar_kpi["periodo"] = pd.to_datetime(df_dolar_kpi["datetime"])

    # obter ultimo e penultimo ano disponiveis
    ultimo_ano = df_kpi["ano"].max()
    penultimo_ano = ultimo_ano - 1

    # obter dados kpis
    df_ultimo_ano = df_ano_kpi[df_ano_kpi["periodo"] == ultimo_ano]
    df_penultimo_ano = df_ano_kpi[df_ano_kpi["periodo"] == penultimo_ano]

    # Criando layout com 4 colunas para os KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        dado_atual_estoque = df_ultimo_ano["estoque_inicial"].iloc[0]
        dado_anterior_estoque = df_penultimo_ano["estoque_inicial"].iloc[0]

        dado_atual_saldo = df_ultimo_ano["estoque_final"].iloc[-1] - dado_atual_estoque
        dado_anterior_saldo = df_penultimo_ano["estoque_final"].iloc[-1] - dado_anterior_estoque
        variacao_saldo = ((dado_atual_saldo - dado_anterior_saldo) / dado_anterior_saldo) * 100

        st.metric(
            label = f"**Saldo Oferta/Demanda {df_kpi["ano"].max()} (1000 t)**",
            value = f"{dado_atual_saldo/1000:.1f}k",
            delta = f"{variacao_saldo:.2f}% YoY",
            border = True
        )

        st.plotly_chart(plot_sparkline(df_ano_kpi, "saldo", "Saldo Oferta / Demanda"), use_container_width=True)

    with kpi2:
        variacao_estoque = ((dado_atual_estoque - dado_anterior_estoque) / dado_anterior_estoque) * 100

        st.metric(
            label = f"**Estoque Inicial {df_kpi["ano"].max()} (1000 t)**",
            value = f"{dado_atual_estoque}",
            delta = f"{variacao_estoque:.2f}% YoY",
            border = True
        )

        st.plotly_chart(plot_sparkline(df_ano_kpi, "estoque_inicial", "Estoque Inicial"), use_container_width=True)

    with kpi3:
        dado_atual_prod = df_ultimo_ano["producao"].iloc[-1]
        dado_anterior_prod = df_penultimo_ano["producao"].iloc[-1]
        variacao_prod = ((dado_atual_prod - dado_anterior_prod) / dado_anterior_prod) * 100

        st.metric(
            label = f"**Produção {df_kpi["ano"].max()} (1000 t)**",
            value = f"{dado_atual_prod/1000:.1f}k",
            delta = f"{variacao_prod:.2f}% YoY",
            border = True
        )

        st.plotly_chart(plot_sparkline(df_ano_kpi, "producao", "Produção"), use_container_width=True)

    with kpi4:
        dado_atual_imp = df_ultimo_ano["importacao"].iloc[-1]
        dado_anterior_imp = df_penultimo_ano["importacao"].iloc[-1]
        variacao_imp = ((dado_atual_imp - dado_anterior_imp) / dado_anterior_imp) * 100

        st.metric(
            label = f"**Importação {df_kpi["ano"].max()} (1000 t)**",
            value = f"{dado_atual_imp}",
            delta = f"{variacao_imp:.2f}% YoY",
            border = True
        )

        st.plotly_chart(plot_sparkline(df_ano_kpi, "importacao", "Importação"), use_container_width=True)

    # Criando layout com 4 colunas para os KPIs
    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

    with kpi5:
        dado_atual_exp = df_ultimo_ano["exportacao"].iloc[-1]
        dado_anterior_exp = df_penultimo_ano["exportacao"].iloc[-1]
        variacao_exp = ((dado_atual_exp - dado_anterior_exp) / dado_anterior_exp) * 100

        st.metric(
            label = f"**Exportação {df_kpi["ano"].max()} (1000 t)**",
            value = f"{dado_atual_exp/1000:.1f}k",
            delta = f"{variacao_exp:.2f}% YoY",
            border = True
        )

        st.plotly_chart(plot_sparkline(df_ano_kpi, "exportacao", "Exportação"), use_container_width=True)

    with kpi6:
        dado_atual_proc = df_ultimo_ano["processamento"].iloc[-1]
        dado_anterior_proc = df_penultimo_ano["processamento"].iloc[-1]
        variacao_proc = ((dado_atual_proc - dado_anterior_proc) / dado_anterior_proc) * 100

        st.metric(
            label = f"**Processamento {df_kpi["ano"].max()} (1000 t)**",
            value = f"{dado_atual_proc/1000:.1f}k",
            delta = f"{variacao_proc:.2f}% YoY",
            border = True
        )

        st.plotly_chart(plot_sparkline(df_ano_kpi, "processamento", "Processamento"), use_container_width=True)

    with kpi7:
        df_dolar_ultimo_ano = df_dolar_kpi[df_dolar_kpi["ano"] == ultimo_ano].sort_values("datetime")
        df_dolar_penultimo_ano = df_dolar_kpi[df_dolar_kpi["ano"] == penultimo_ano]
    
        dado_atual_dolar = df_dolar_ultimo_ano["close"].iloc[-1]
        dado_anterior_dolar = df_dolar_penultimo_ano["close"].iloc[-1]
        variacao_dolar = ((dado_atual_dolar - dado_anterior_dolar) / dado_anterior_dolar) * 100

        st.metric(
            label = f"**Cambîo  USD/BRL {df_kpi["ano"].max()}**",
            value = f"{dado_atual_dolar}",
            delta = f"{variacao_dolar:.2f}% YoY",
            border = True
        )
    
        st.plotly_chart(plot_sparkline(df_dolar_kpi, "close", "Câmbio USD/BRL"), use_container_width=True)

    with kpi8:

        tabela_preco = {
            "Chicago - CBOT (US$/t)": "chicago_cbot_u$/t",
            "FOB Porto - Paranaguá (US$/t)": "fob_porto_paranagua_u$/t",
            "Maringá / PR - R$/saca (sem ICMS)": "maringa_r$/saca",
            "Mogiana / SP - R$/saca (sem ICMS)": "mogiana_r$/saca",
            "Passo Fundo / RS - R$/saca (sem ICMS)": "passofundo_r$/saca",
            "Rondonopolis / MT - R$/saca (sem ICMS)": "rondonopolis_r$/saca",
        }

        coluna_preco = tabela_preco[preco_selecionado]

        df_preco_ultimo_ano = df_kpi[df_kpi["ano"] == ultimo_ano].sort_values("ano_mes")
        df_preco_penultimo_ano = df_kpi[df_kpi["ano"] == penultimo_ano].sort_values("ano_mes")

        dado_atual_preco = df_preco_ultimo_ano[coluna_preco].iloc[-1]
        dado_anterior_preco = df_preco_penultimo_ano[coluna_preco].iloc[-1]
        variacao_preco = ((dado_atual_preco - dado_anterior_preco) / dado_anterior_preco) * 100
    
        st.metric(
            label = f"**{preco_selecionado}**",
            value = f"{dado_atual_preco:.2f}",
            delta = f"{variacao_preco:.2f}% YoY",
            border = True
        )

        st.plotly_chart(plot_sparkline(df_kpi, coluna_preco, f"{preco_selecionado}"), use_container_width=True)

# ----------------------------- seção 02 - macroeconomico ------------------------------------

with st.container(border=True):

    titulo, periodo, tipo_preco = st.columns([2, 1, 1.5])

    with titulo:
        st.markdown("<h4 style='margin-top: 10px; margin-left: 10px;''>🌍 Cenário Macroeconômico – Impacto do Câmbio</h4>", unsafe_allow_html=True)

    with periodo:
        anos_selecionados_2 = st.slider(
            "Selecione o Período:",
            min_value=int(df["ano"].min()),
            max_value=int(df["ano"].max()),
            value=(int(df["ano"].min()), int(df["ano"].max())),
            key="slider_2"
        )

    with tipo_preco:
        preco_selecionado_2 = st.selectbox(
            "Selecione o Preço:",
            ["Chicago - CBOT (US$/t)", "FOB Porto - Paranaguá (US$/t)", 
            "Maringá / PR - R$/saca (sem ICMS)", "Mogiana / SP - R$/saca (sem ICMS)", 
            "Passo Fundo / RS - R$/saca (sem ICMS)", "Rondonopolis / MT - R$/saca (sem ICMS)"],
            index=5,
            key="select_2"
        )

    # filtro e tratamento de dados

    df_dolar_secao2 = df_dolar[(df_dolar["ano"] >= anos_selecionados_2[0]) & (df_dolar["ano"] <= anos_selecionados_2[1])]
    df_dolar_secao2["periodo"] = pd.to_datetime(df_dolar_secao2["datetime"])

    df_secao2 = df[(df["ano"] >= anos_selecionados_2[0]) & (df["ano"] <= anos_selecionados_2[1])]
    df_secao2["periodo"] = df_secao2["ano_mes"]



    # -------------------------------- Criando o gráfico do câmbio --------------------------------
    
    fig_cambio = go.Figure()

    # Adicionando linha do câmbio ao longo do tempo
    fig_cambio.add_trace(go.Scatter(
        x=df_dolar_secao2["periodo"],
        y=df_dolar_secao2["close"],
        mode='lines',
        name='Câmbio USD/BRL',
        line=dict(color='#FF8800', width=3)
    ))

    # Identificando e destacando a variação anual

    df_ultimo_dia_do_ano = df_dolar_secao2.groupby("ano").last().reset_index()
    df_ultimo_dia_do_ano["var_anual"] = df_ultimo_dia_do_ano["close"].pct_change()*100
    df_ultimo_dia_do_ano = df_ultimo_dia_do_ano.fillna(0)

    for i in range(1, len(df_ultimo_dia_do_ano)):
        ano = df_ultimo_dia_do_ano["ano"].iloc[i]
        periodo = df_ultimo_dia_do_ano["periodo"].iloc[i]
        valor = df_ultimo_dia_do_ano["close"].iloc[i]
        variacao_anual = df_ultimo_dia_do_ano["var_anual"].iloc[i]
        
        fig_cambio.add_annotation(
            x=periodo,
            y=valor,
            text=f"{variacao_anual:.1f}%<br>YoY",
            showarrow=True,
            arrowhead=4,
            ax = -15,  # Define a posição final da seta no eixo X (ajuste conforme necessário)
            ay = -60,  # Aumenta o comprimento da seta
            font=dict(color="green" if variacao_anual > 0 else "red", size=12),
            bgcolor="rgba(255,255,255,0.7)"
        )

    # adicionando eventos no grafico

    eventos = [
        {"data": "2002-10-28", "texto": "Lula eleito"},
        {"data": "2008-07-27", "texto": "Crise Financeira"},
        {"data": "2014-08-10", "texto": "Recessão Brasil"},
        {"data": "2016-01-10", "texto": "Impeachment Dilma"},
        {"data": "2018-10-28", "texto": "Bolsonaro eleito"},
        {"data": "2020-02-02", "texto": "COVID-19"},
        {"data": "2022-10-02", "texto": "Lula eleito"}
    ]

    df_eventos = pd.DataFrame(eventos)
    df_eventos["data"] = pd.to_datetime(df_eventos["data"])

    for i, row in df_eventos.iterrows():
        fig_cambio.add_vline(
            x = row["data"],
            line_width=2,
            line_dash="dash",
            line_color="blue"
            #annotation_position="top",
            #annotation_font_size=12
        )

            # Definir a posição da anotação (topo para os 3 primeiros, base para os demais)
        if i < 3:
            y_pos = df_dolar_secao2["close"].max()+1.5  # Anotações superiores
            ay = -60  # Direção da seta para cima
        else:
            y_pos = df_dolar_secao2["close"].min()  # Anotações inferiores
            ay = 60  # Direção da seta para baixo

        # Transformar espaços em quebras de linha usando "<br>"
        texto_formatado = row["texto"].replace(" ", "<br>")

        fig_cambio.add_annotation(
            x=row["data"],
            y=y_pos,  # Posiciona no topo do gráfico
            text=texto_formatado,
            showarrow = False,
            font=dict(size=12, color="blue"),
            bgcolor="rgba(255,255,255,0.7)",
            align="center"
        )

    fig_cambio.update_layout(
        yaxis_title="USD/BRL",
        xaxis_title="Periodo",
        height=400,
        margin=dict(l=10, r=10, t=20, b=10),
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
            )
    )   

    st.plotly_chart(fig_cambio, use_container_width=True)




    # ------------------------------ comparacao - cambio vs preco soja ------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h5 style='margin-left: 50px;'> 🔄 Comparação: Câmbio vs. Preço da Soja</h5>", unsafe_allow_html=True)
    
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatter(
            x=df_dolar_secao2["periodo"],
            y=df_dolar_secao2["close"],
            mode='lines',
            name='Câmbio USD/BRL',
            yaxis='y1',
            line=dict(color='#FF8800', width=2)
        ))

        tabela_preco_2 = {
            "Chicago - CBOT (US$/t)": "chicago_cbot_u$/t",
            "FOB Porto - Paranaguá (US$/t)": "fob_porto_paranagua_u$/t",
            "Maringá / PR - R$/saca (sem ICMS)": "maringa_r$/saca",
            "Mogiana / SP - R$/saca (sem ICMS)": "mogiana_r$/saca",
            "Passo Fundo / RS - R$/saca (sem ICMS)": "passofundo_r$/saca",
            "Rondonopolis / MT - R$/saca (sem ICMS)": "rondonopolis_r$/saca",
        }

        coluna_preco_2 = tabela_preco_2[preco_selecionado_2]


        fig_comp.add_trace(go.Scatter(
            x=df_secao2["periodo"],
            y=df_secao2[coluna_preco_2],
            mode='lines',
            name=f'Preço da Soja ({preco_selecionado_2})',
            yaxis='y2',
            line=dict(color='#008000', width=2)
        ))

        fig_comp.update_layout(
            yaxis=dict(
                title="USD/BRL", 
                side="left",
                showline=True,
                linecolor="gray",
                linewidth=1
                ),
            yaxis2=dict(
                title=preco_selecionado, 
                overlaying="y", 
                side="right",
                showline=True,
                linecolor="gray",
                linewidth=1
                ),
            xaxis=dict(
                title="Periodo",
                showline=True,
                linecolor="gray",
                linewidth=1,
                tickmode="linear",
                dtick="M24",
                tickangle=45
                ),
            height=400,
            legend=dict(
                orientation="h",  # Deixa a legenda horizontal
                yanchor="top",
                y=-0.24 # Posiciona a legenda abaixo do gráfico
            ),
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(fig_comp, use_container_width=True)

    with col2:
        st.markdown("<h5 style='margin-left: 50px;'> 🔍 Correlação entre Câmbio e Preço da Soja</h5>", unsafe_allow_html=True)

        df_dolar_secao2["periodo"] = pd.to_datetime(df_dolar_secao2["ano"].astype(str) + "-" + df_dolar_secao2["mes"].astype(str) + "-01")
        df_secao2["periodo"] = pd.to_datetime(df_secao2["periodo"])
        df_dolar_secao2.info()
        df_secao2.info()

        df_merged = pd.merge(df_secao2[["periodo", "chicago_cbot_u$/t", "fob_porto_paranagua_u$/t", "maringa_r$/saca", "mogiana_r$/saca", "passofundo_r$/saca", "rondonopolis_r$/saca"]], df_dolar_secao2[["periodo", "close"]], on="periodo", how="outer")

        fig_scatter = px.scatter(
            df_merged, 
            x=coluna_preco_2, 
            y="close", 
            trendline="ols",  # Adiciona a linha de tendência automaticamente
            trendline_color_override="blue",
            labels={coluna_preco_2: f"Preço da Soja ({preco_selecionado_2})", "close": "Câmbio (USD/BRL)"},
            color_discrete_sequence=["#ADFF2F"],
            opacity=0.5
        )

        fig_scatter.update_layout(
            xaxis=dict(
                title = f"Preço da Soja ({preco_selecionado_2})",
                showline=True,
                linecolor="gray",
                linewidth=1
                ),
            yaxis=dict(
                title = "Câmbio (USD/BRL)",
                showline=True,
                linecolor="gray",
                linewidth=1
                ),            
            height=400,
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(fig_scatter, use_container_width=True)


        # ------------------------------ correlacao e insights do preço ------------------------------------------------------

    col, col1, col2 = st.columns([0.3,1,2.5])

    with col1:
        st.markdown("<h5 style='margin-left: 50px;'> 📊 Estatísticas da Correlação</h5>", unsafe_allow_html=True)
        #st.markdown("<br>", unsafe_allow_html=True)  # Adiciona espaço entre os blocos
    
        # Calcular correlação
        correlacao = df_merged["close"].corr(df_merged[coluna_preco_2])

        # Exibir resultado formatado
        st.metric(
            label="**Correlação (Câmbio vs. Preço da Soja)**",
            value=f"{correlacao:.4f}",
            delta="Positiva" if correlacao > 0 else "Negativa",
            border = True
        )

    with col2:

        st.markdown("""
            <div style='margin-left: 80px; margin-right: 80px; margin-bottom: 20px; text-align: center;'>
                <h5 style='margin-left: 50px;'> 📢 Insights sobre o Impacto do Câmbio</h5>
                <p style='font-size: 14px;'>
                    ✔  O câmbio é um dos principais fatores que influenciam o preço da soja no Brasil, afetando diretamente a competitividade das exportações e a disponibilidade interna do produto.<br>
                    ✔  A correlação estatística confirma essa relação, indicando que variações cambiais têm impacto mensurável sobre a formação de preços no mercado brasileiro.<br>
                    ✔  Eventos macroeconômicos globais amplificam essa relação, tornando o acompanhamento do câmbio essencial para a análise e previsão dos preços da soja.
                </p>
            </div>
            """, unsafe_allow_html=True)
        


# ----------------------------- seção 03 - Oferta ------------------------------------

with st.container(border=True):
        
    titulo, periodo, espaco = st.columns([2, 1, 0.3])

    with titulo:
        st.markdown("<h4 style='margin-top: 10px; margin-left: 10px;''> 🧐 Análise da Oferta: Produção, Importação e Estoques</h4>", unsafe_allow_html=True)

    with periodo:
        anos_selecionados_3 = st.slider(
            "Selecione o Período:",
            min_value=int(df["ano"].min()),
            max_value=int(df["ano"].max()),
            value=(int(df["ano"].min()), int(df["ano"].max())),
            key="slider_3"
        )

    # filtro e tratamento de dados

    df_oferta = df[(df["ano"] >= anos_selecionados_3[0]) & (df["ano"] <= anos_selecionados_3[1])]
    df_oferta["periodo"] = pd.to_datetime(df_oferta["ano_mes"])

    df_oferta_anual = df_ano[(df_ano["periodo"] >= anos_selecionados_3[0]) & (df_ano["periodo"] <= anos_selecionados_3[1])]

    col1 , col2 = st.columns(2)

    with col1:
        st.markdown("<h5 style='margin-left: 50px;'> 🚜 Produção e Importação Anual</h5>", unsafe_allow_html=True)
        fig_prod_imp = go.Figure()

        fig_prod_imp.add_trace(go.Scatter(
            x=df_oferta_anual["periodo"], 
            y=df_oferta_anual["producao"], 
            mode="lines+markers",
            name="Produção Anual" ,
            line=dict(color="#FF8800", width=2),
            yaxis="y2"
        ))

        fig_prod_imp.add_trace(go.Bar(
            x=df_oferta_anual["periodo"], 
            y=df_oferta_anual["importacao"], 
            marker_color="#008000",
            name="Importação Anual",
            opacity=0.7,
            yaxis="y1"
        ))

        fig_prod_imp.update_layout(
            xaxis=dict(
                title="Ano",
                showline=True,
                linecolor="gray",
                linewidth=1,
                tickmode="linear",
                dtick="2",
                tickangle=45
                ),
            yaxis2=dict(
                title="Produção Mil Toneladas",
                side="left",
                overlaying="y",
                showline=True,
                linecolor="gray",
                linewidth=1
            ),
            yaxis=dict(
                title="Importação Mil Toneladas",
                side="right",
                showline=True,
                linecolor="gray",
                linewidth=1
            ),
            legend=dict(
                orientation="h", 
                yanchor="top", 
                y=-0.24,
                x=0.2
                ),
            height=400,
            margin=dict(l=10, r=10, t=20, b=10)
        )
       
        
        st.plotly_chart(fig_prod_imp, use_container_width=True)


    with col2:
        st.markdown("<h5 style='margin-left: 50px;'> 📈 Evolução dos Estoques</h5>", unsafe_allow_html=True)
        fig_estoques = go.Figure()

        fig_estoques.add_trace(go.Scatter(
            x=df_oferta_anual["periodo"], 
            y=df_oferta_anual["estoque_final"],
            mode="lines+markers", 
            name="Estoque", 
            line=dict(
                color="#ADFF2F", 
                width=3
                )
        ))

        fig_estoques.update_layout(
            xaxis=dict(
                title="Período",
                showline=True,
                linecolor="gray",
                linewidth=1,
                tickmode="linear",
                dtick=2,
                tickangle=45                           
                ), 
            yaxis=dict(
                title="Estoque Mil Toneladas",
                showline=True,
                linecolor="gray",
                linewidth=1
                ),
            height=400,
            margin=dict(l=10, r=10, t=20, b=10)
            )
        
        st.plotly_chart(fig_estoques, use_container_width=True)




# ----------------------------- seção 04 - Demanda ------------------------------------

with st.container(border=True):
        
    titulo, periodo, espaco = st.columns([2, 1, 0.3])

    with titulo:
        st.markdown("<h4 style='margin-top: 10px; margin-left: 10px;''> 💡 Análise da Demanda: Exportação, Processamento e Sementes</h4>", unsafe_allow_html=True)

    with periodo:
        anos_selecionados_4 = st.slider(
            "Selecione o Período:",
            min_value=int(df["ano"].min()),
            max_value=int(df["ano"].max()),
            value=(int(df["ano"].min()), int(df["ano"].max())),
            key="slider_4"
        )

    # filtro e tratamento de dados

    df_demanda = df[(df["ano"] >= anos_selecionados_4[0]) & (df["ano"] <= anos_selecionados_4[1])]
    df_demanda["periodo"] = pd.to_datetime(df_oferta["ano_mes"])

    df_demanda_anual = df_ano[(df_ano["periodo"] >= anos_selecionados_4[0]) & (df_ano["periodo"] <= anos_selecionados_4[1])]

    col1 , col2 = st.columns(2)

    with col1:
        st.markdown("<h5 style='margin-left: 50px;'> 🌱 Exportação e Sementes/Outros</h5>", unsafe_allow_html=True)
        fig_exp = go.Figure()

        fig_exp.add_trace(go.Scatter(
            x=df_demanda_anual["periodo"], 
            y=df_demanda_anual["exportacao"], 
            mode="lines+markers",
            name="Exportação Anual" ,
            line=dict(color="#FF8800", width=2),
            yaxis="y2"
        ))

        fig_exp.add_trace(go.Bar(
            x=df_demanda_anual["periodo"], 
            y=df_demanda_anual["Sementes/Outros"], 
            marker_color="#008000",
            name="Sementes / Outros",
            opacity=0.7,
            yaxis="y1"
        ))

        fig_exp.update_layout(
            xaxis=dict(
                title="Ano",
                showline=True,
                linecolor="gray",
                linewidth=1,
                tickmode="linear",
                dtick="2",
                tickangle=45
                ),
            yaxis2=dict(
                title="Exportação Mil Toneladas",
                side="left",
                overlaying="y",
                showline=True,
                linecolor="gray",
                linewidth=1
            ),
            yaxis=dict(
                title="Utilização Sementes / Outros",
                side="right",
                showline=True,
                linecolor="gray",
                linewidth=1
            ),
            legend=dict(
                orientation="h", 
                yanchor="top", 
                y=-0.24,
                x=0.2
                ),
            height=400,
            margin=dict(l=10, r=10, t=20, b=10)
        )
       
        
        st.plotly_chart(fig_exp, use_container_width=True)


    with col2:
        st.markdown("<h5 style='margin-left: 50px;'> 📈 Evolução do Processamento</h5>", unsafe_allow_html=True)
        fig_proc = go.Figure()

        fig_proc.add_trace(go.Scatter(
            x=df_demanda_anual["periodo"], 
            y=df_demanda_anual["processamento"],
            mode="lines+markers", 
            name="Processamento Anual", 
            line=dict(
                color="#ADFF2F", 
                width=3
                )
        ))

        fig_proc.update_layout(
            xaxis=dict(
                title="Período",
                showline=True,
                linecolor="gray",
                linewidth=1,
                tickmode="linear",
                dtick=2,
                tickangle=45                           
                ), 
            yaxis=dict(
                title="Processamento Mil Toneladas",
                showline=True,
                linecolor="gray",
                linewidth=1
                ),
            height=400,
            margin=dict(l=10, r=10, t=20, b=10)
            )
        
        st.plotly_chart(fig_proc, use_container_width=True)



# ----------------------------- seção 05 - Dinâmica Oferta / Demanda e Impacto no Preço ------------------------------------

with st.container(border=True):
        
    titulo, periodo, preco = st.columns([2, 1, 1.5])

    with titulo:
        st.markdown("<h4 style='margin-top: 10px; margin-left: 10px;''> 💰 Dinâmica Oferta-Demanda e Impacto no Preço</h4>", unsafe_allow_html=True)

    with periodo:
        anos_selecionados_5 = st.slider(
            "Selecione o Período:",
            min_value=int(df["ano"].min()),
            max_value=int(df["ano"].max()),
            value=(int(df["ano"].min()), int(df["ano"].max())),
            key="slider_5"
        )

    with preco:
        preco_selecionado_5 = st.selectbox(
            "Selecione o Preço:",
            ["Chicago - CBOT (US$/t)", "FOB Porto - Paranaguá (US$/t)", 
            "Maringá / PR - R$/saca (sem ICMS)", "Mogiana / SP - R$/saca (sem ICMS)", 
            "Passo Fundo / RS - R$/saca (sem ICMS)", "Rondonopolis / MT - R$/saca (sem ICMS)"],
            index=5,
            key="select_5"
        )

    # filtro e tratamento de dados



    df_saldo = df[(df["ano"] >= anos_selecionados_5[0]) & (df["ano"] <= anos_selecionados_5[1])]
    df_saldo["periodo"] = pd.to_datetime(df_oferta["ano_mes"])
    df_saldo["saldo_estoque"] = df_saldo["estoque"].diff()
    df_saldo = df_saldo.fillna(0)
  
    df_saldo_anual = df_ano[(df_ano["periodo"] >= anos_selecionados_5[0]) & (df_ano["periodo"] <= anos_selecionados_5[1])]
    df_saldo_anual["saldo_estoque"] = df_saldo_anual["estoque_final"] - df_saldo_anual["estoque_inicial"]
    df_saldo_anual = df_saldo_anual.fillna(0)

    tabela_preco_5 = {
            "Chicago - CBOT (US$/t)": "chicago_cbot_u$/t",
            "FOB Porto - Paranaguá (US$/t)": "fob_porto_paranagua_u$/t",
            "Maringá / PR - R$/saca (sem ICMS)": "maringa_r$/saca",
            "Mogiana / SP - R$/saca (sem ICMS)": "mogiana_r$/saca",
            "Passo Fundo / RS - R$/saca (sem ICMS)": "passofundo_r$/saca",
            "Rondonopolis / MT - R$/saca (sem ICMS)": "rondonopolis_r$/saca",
        }

    coluna_preco_5 = tabela_preco_5[preco_selecionado_5]


    col1 , col2 = st.columns(2)

    with col1:
        st.markdown("<h5 style='margin-left: 50px;'>  Saldo Oferta-Demanda vs. Preço da Soja</h5>", unsafe_allow_html=True)
        fig_prod_imp = go.Figure()

        # barras oferta / Demanda
        fig_prod_imp.add_trace(go.Bar(
            x=df_saldo_anual["periodo"], 
            y=df_saldo_anual["saldo_estoque"], 
            marker_color="#008000",
            name=f'Saldo Oferta-Demanda',
            opacity=0.7,
            yaxis="y1",
            xaxis="x1"
        ))


        # linha do preço da soja
        fig_prod_imp.add_trace(go.Scatter(
            x=df_saldo["periodo"], 
            y=df_saldo[coluna_preco_5], 
            marker_color="#FF8800",
            name=f'{preco_selecionado_5}',
            opacity=0.7,
            yaxis="y2",
            xaxis="x2"
        ))

        fig_prod_imp.update_layout(
            xaxis=dict(
                title="Ano",
                showline=True,
                linecolor="gray",
                linewidth=1,
                tickmode="linear",
                dtick=2,
                tickangle=45
                ),  
            xaxis2=dict(
                showline=False,
                overlaying="x",
                showticklabels=False
                ),
            yaxis=dict(
                title="Saldo Oferta-Demanda",
                side="left",
                showline=True,
                linecolor="gray",
                linewidth=1
            ),
            yaxis2=dict(
                title='Preço da Soja',
                side="right",
                overlaying="y",
                showline=True,
                linecolor="gray",
                linewidth=1
            ),
            legend=dict(
                orientation="h", 
                yanchor="top", 
                y=-0.24
                ),
            height=400,
            margin=dict(l=10, r=10, t=20, b=10)
        )
       
        
        st.plotly_chart(fig_prod_imp, use_container_width=True)


    with col2:
        st.markdown("<h5 style='margin-left: 50px;'> 🔍 Correlação entre Saldo Oferta-Demanda e Preço da Soja</h5>", unsafe_allow_html=True)

        fig_scatter = px.scatter(
            df_saldo, 
            x=coluna_preco_5, 
            y="saldo_estoque", 
            trendline="ols",  # Adiciona a linha de tendência automaticamente
            trendline_color_override="blue",
            labels={coluna_preco_5: f"Preço da Soja ({preco_selecionado_5})", "saldo_estoque": "Saldo Oferta-Demanda"},
            color_discrete_sequence=["#ADFF2F"],
            opacity=0.5
        )

        fig_scatter.update_layout(
            xaxis=dict(
                title = f"Preço da Soja ({preco_selecionado_5})",
                showline=True,
                linecolor="gray",
                linewidth=1
                ),
            yaxis=dict(
                title = "Saldo Oferta-Demanda",
                showline=True,
                linecolor="gray",
                linewidth=1
                ),            
            height=400,
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

    col, col1, col2 = st.columns([0.3,1,2.5])

    with col1:
        st.markdown("<h5 style='margin-left: 50px;'> 📊 Estatísticas da Correlação</h5>", unsafe_allow_html=True)
        #st.markdown("<br>", unsafe_allow_html=True)  # Adiciona espaço entre os blocos
    
        # Calcular correlação
        correlacao = df_saldo["saldo_estoque"].corr(df_saldo[coluna_preco_5])

        # Exibir resultado formatado
        st.metric(
            label="**Correlação Oferta-Demanda vs. Preço da Soja**",
            value=f"{correlacao:.4f}",
            delta="Positiva" if correlacao > 0 else "Negativa",
            border = True
        )

    with col2:

        st.markdown("""
            <div style='margin-left: 80px; margin-right: 80px; margin-bottom: 20px; text-align: center;'>
                <h5 style='margin-left: 50px;'> 📢 Insights sobre o Impacto da Oferta-Demanda</h5>
                <p style='font-size: 14px;'>
                    ✔  A correlação entre saldo oferta-demanda e o preço da soja é fraca, indicando que estoques e fluxos internos de oferta e demanda têm impacto limitado na precificação do grão.<br>
                    ✔  O câmbio se mostrou um fator muito mais influente, reforçando que o mercado internacional e a competitividade das exportações são os principais direcionadores do preço da soja no Brasil.<br>
                    ✔  Embora o saldo oferta-demanda não seja um forte preditor do preço, ele pode impactar a volatilidade no curto prazo, especialmente em safras com quebra de produção ou demanda inesperada.
                </p>
            </div>
            """, unsafe_allow_html=True)
        


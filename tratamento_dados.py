import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Caminho do arquivo (ajuste conforme necessário)
file_path = "database/complexo-soja.xlsx"
df_balanco = pd.read_excel(file_path, sheet_name="BALANÇO ANUAL").iloc[:, :-2]
df_processamento = pd.read_excel(file_path, sheet_name="PROCESSAMENTO").iloc[:, :-2]
df_exportacao = pd.read_excel(file_path, sheet_name="EXPORTAÇÃO TOTAL").iloc[:, :-2]
df_importacao = pd.read_excel(file_path, sheet_name="IMPORTAÇÃO").iloc[:, :-2]
df_estoques = pd.read_excel(file_path, sheet_name="ESTOQUES").iloc[:, :-2]
df_precos = pd.read_excel(file_path, sheet_name="PREÇOS").iloc[:, :-2]
df_compra = pd.read_excel(file_path, sheet_name="COMPRAS").iloc[:, :-2]
dolar_path = "database/variacao_cambial.csv"
df_dolar = pd.read_csv(dolar_path, index_col=0)


# tratando df_balanco para salvar como soja_anual.csv
df_balanco = df_balanco[df_balanco['PRODUTO'] == '1. Grão']
df_balanco = df_balanco.pivot(index="DATA", columns="DISCRIMINAÇÃO", values="VALOR")
df_balanco = df_balanco.reset_index()
df_balanco.columns.name = None
df_balanco["DATA"] = pd.to_datetime(df_balanco["DATA"]).dt.year
df_balanco = df_balanco.rename(columns={"DATA": "periodo"})
df_balanco = df_balanco.rename(columns={"2.1.1. - Estoque Inicial": "estoque_inicial"})
df_balanco = df_balanco.rename(columns={"2.1.2. - Produção": "producao"})
df_balanco = df_balanco.rename(columns={"2.1.3. - Importação": "importacao"})
df_balanco = df_balanco.rename(columns={"2.1.4. - Sementes/Outros": "Sementes/Outros"})
df_balanco = df_balanco.rename(columns={"2.1.5. - Exportação": "exportacao"})
df_balanco = df_balanco.rename(columns={"2.1.6. - Processamento": "processamento"})
df_balanco = df_balanco.rename(columns={"2.1.7. - Estoque Final": "estoque_final"})
df_balanco = df_balanco.round(2)

df_dolar_ano = df_dolar.rename(columns={"datetime": "ano_mes"})
df_dolar_ano = df_dolar_ano.rename(columns={"close": "usdbrl"})
df_dolar_ano["ano_mes"] = pd.to_datetime(df_dolar_ano["ano_mes"])
df_dolar_ano["ano"] = df_dolar_ano["ano_mes"].dt.year
df_dolar_ano = df_dolar_ano.sort_values(["ano", "ano_mes"], ascending=[True, True])
df_dolar_ano = df_dolar_ano.groupby("ano").last().reset_index()
df_dolar_ano = df_dolar_ano[["ano", "usdbrl"]]
df_dolar_ano = df_dolar_ano.rename(columns={"ano": "periodo"})

df_balanco = pd.merge(df_balanco, df_dolar_ano, on="periodo", how="left")

# exportando para csv
df_balanco.to_csv("database/soja_anual1.csv", index=False, encoding="utf-8")

# tratando df_estoques contendo saldo para salvar como soja_mensal.csv
df_estoques = df_estoques.iloc[:, :-2]
df_estoques = df_estoques.rename(columns={"DATA": "ano_mes"})
df_estoques = df_estoques.rename(columns={"SOJA": "estoque"})
df_estoques = df_estoques.sort_values(by="ano_mes")
df_estoques["saldo"] = df_estoques["estoque"].diff()
df_estoques = df_estoques.sort_values(by="ano_mes", ascending=False)
df_estoques = df_estoques.fillna(0)

# tratando df_exportacao para salvar como soja_mensal.csv
df_exportacao = df_exportacao.iloc[:, :-2]
df_exportacao = df_exportacao.rename(columns={"DATA": "ano_mes"})
df_exportacao = df_exportacao.rename(columns={"SOJA": "exportacao"})

# tratando df_processamento para salvar como soja_mensal.csv
df_processamento = df_processamento.rename(columns={"DATA": "ano_mes"})
df_processamento = df_processamento.rename(columns={"VALOR": "processamento"})

# tratando df_compra para salvar como soja_mensal.csv
df_compra = df_compra.rename(columns={"DATA": "ano_mes"})
df_compra = df_compra.rename(columns={"COMPRAS": "compra_liquida"})

# tratando df_importacao para salvar como soja_mensal.csv
df_importacao = df_importacao.iloc[:, :-2]
df_importacao = df_importacao.rename(columns={"DATA": "ano_mes"})
df_importacao = df_importacao.rename(columns={"SOJA": "importacao"})

# tratando df_precos para salvar como soja_mensal.csv
df_precos = df_precos[df_precos['produto'] == '1 - Grão']
df_precos = df_precos.iloc[:, 4:]
df_precos = df_precos[['data', 'discriminacao', 'valor']]
df_precos = df_precos.pivot(index="data", columns="discriminacao", values="valor")
df_precos = df_precos.loc[:, ~df_precos.columns.isna()]
df_precos = df_precos.reset_index()
df_precos.columns.name = None
df_precos = df_precos.drop(columns=["1.2 - Prêmio (US$/t)"])
df_precos = df_precos.rename(columns={"data": "ano_mes"})
df_precos = df_precos.rename(columns={"1.1 - Chicago - CBOT (US$/t)": "chicago_cbot_u$/t"})
df_precos = df_precos.rename(columns={"1.3 - FOB Porto - Paranaguá (US$/t)": "fob_porto_paranagua_u$/t"})
df_precos = df_precos.rename(columns={"1.4 - Mercado Interno - Maringá / PR - R$/saca (sem ICMS)": "maringa_r$/saca"})
df_precos = df_precos.rename(columns={"1.5 - Mercado Interno - Mogiana / SP - R$/saca (sem ICMS)": "mogiana_r$/saca"})
df_precos = df_precos.rename(columns={"1.6 - Mercado Interno - Passo Fundo / RS - R$/saca (sem ICMS)": "passofundo_r$/saca"})
df_precos = df_precos.rename(columns={"1.7 - Mercado Interno - Rondonopolis / MT - R$/saca (sem ICMS)": "rondonopolis_r$/saca"})

# criando dataframe soja_mensal
soja_mensal = pd.DataFrame()
soja_mensal = pd.merge(df_estoques, df_exportacao, on="ano_mes", how="outer")
soja_mensal = pd.merge(soja_mensal, df_processamento, on="ano_mes", how="outer")
soja_mensal = pd.merge(soja_mensal, df_compra, on="ano_mes", how="outer")
soja_mensal = pd.merge(soja_mensal, df_importacao, on="ano_mes", how="outer")
soja_mensal = pd.merge(soja_mensal, df_precos, on="ano_mes", how="outer")
soja_mensal["ano"] = pd.to_datetime(soja_mensal["ano_mes"]).dt.year
soja_mensal["mes"] = pd.to_datetime(soja_mensal["ano_mes"]).dt.month

#adicionando producao em soja_mensal

pesos_mensais = {
    1: 0.10,  # Janeiro
    2: 0.15,  # Fevereiro
    3: 0.25,  # Março (Pico)
    4: 0.20,  # Abril
    5: 0.10,  # Maio
    6: 0.05,  # Junho
    7: 0.05,  # Julho
    8: 0.05,  # Agosto
    9: 0.05,  # Setembro
    10: 0.05, # Outubro
    11: 0.05, # Novembro
    12: 0.05  # Dezembro
}

producao = df_balanco[['periodo', 'producao']].rename(columns={"periodo": "ano"})
soja_mensal = pd.merge(soja_mensal, producao, on="ano", how="outer")
soja_mensal['producao'] = soja_mensal['producao'] * soja_mensal['mes'].map(pesos_mensais)

# adicionando variação cambial

df_dolar = df_dolar.rename(columns={"datetime": "ano_mes"})
df_dolar = df_dolar.rename(columns={"close": "usdbrl"})

df_dolar["ano_mes"] = pd.to_datetime(df_dolar["ano_mes"])
soja_mensal["ano_mes"] = pd.to_datetime(soja_mensal["ano_mes"])

df_dolar["ano"] = df_dolar["ano_mes"].dt.year
df_dolar["mes"] = df_dolar["ano_mes"].dt.month
df_dolar = df_dolar.sort_values(["ano", "mes", "ano_mes"])
df_dolar_proximo = (
    df_dolar.groupby(["ano", "mes"])
    .apply(lambda x: x.iloc[(x["ano_mes"] - pd.to_datetime(x["ano_mes"].dt.strftime("%Y-%m-01"))).abs().argmin()])
    .reset_index(drop=True)
)

df_dolar_proximo["ano_mes"] = df_dolar_proximo["ano_mes"].dt.strftime("%Y-%m-01")
df_dolar_proximo["ano_mes"] = pd.to_datetime(df_dolar_proximo["ano_mes"])
df_dolar_proximo = df_dolar_proximo[['ano_mes','usdbrl']]

soja_mensal = pd.merge(soja_mensal, df_dolar_proximo, on="ano_mes", how="left")


# organizando colunas
soja_mensal = soja_mensal[['mes','ano','ano_mes','estoque','exportacao','processamento','compra_liquida','importacao','saldo','producao','chicago_cbot_u$/t','fob_porto_paranagua_u$/t','maringa_r$/saca','mogiana_r$/saca','passofundo_r$/saca','rondonopolis_r$/saca','usdbrl']]

# exportando para csv
soja_mensal.to_csv("database/soja_mensal1.csv", index=True, encoding="utf-8")

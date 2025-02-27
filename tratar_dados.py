import pandas as pd

# Dicionário para converter nome do mês em número
meses_dict = {
    "Jan": "01", "Fev": "02", "Mar": "03", "Abr": "04", "Mai": "05", "Jun": "06",
    "Jul": "07", "Ago": "08", "Set": "09", "Out": "10", "Nov": "11", "Dez": "12"
}

# ------------------------------------ Estoque ------------------------------------------------------

df_estoque = pd.read_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/extracao/estoque.csv")
df_estoque = df_estoque.fillna(0)

df_estoque = df_estoque.melt(id_vars = ["ano"], var_name = "periodo", value_name = "estoque")
df_estoque = df_estoque.rename(columns = {"ano":"mes"})
df_estoque = df_estoque.rename(columns = {"periodo":"ano"})

df_estoque['ano_mes'] = df_estoque['ano'].astype(str) + '-' + df_estoque['mes'].map(meses_dict)

df_estoque = df_estoque[["mes", "ano", "ano_mes", "estoque"]]

# ----------------------------------- Exportacao ---------------------------------------------------

df_exportacao = pd.read_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/extracao/exportacao.csv")
df_exportacao = df_exportacao.fillna(0)

df_exportacao = df_exportacao.melt(id_vars = ["ano"], var_name = "periodo", value_name = "exportacao")
df_exportacao = df_exportacao.rename(columns = {"ano":"mes"})
df_exportacao = df_exportacao.rename(columns = {"periodo":"ano"})

df_exportacao['ano_mes'] = df_exportacao['ano'].astype(str) + '-' + df_exportacao['mes'].map(meses_dict)

df_exportacao = df_exportacao[["mes", "ano", "ano_mes", "exportacao"]]

# ----------------------------------- processamento ---------------------------------------------------

df_processamento = pd.read_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/extracao/processamento.csv")
df_processamento = df_processamento.fillna(0)

df_processamento = df_processamento.melt(id_vars = ["ano"], var_name = "periodo", value_name = "processamento")
df_processamento = df_processamento.rename(columns = {"ano":"mes"})
df_processamento = df_processamento.rename(columns = {"periodo":"ano"})

df_processamento['ano_mes'] = df_processamento['ano'].astype(str) + '-' + df_processamento['mes'].map(meses_dict)

df_processamento = df_processamento[["mes", "ano", "ano_mes", "processamento"]]


# -------------------------------------- producao ----------------------------------------------------

df_complexo_soja_anual = pd.read_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/extracao/complexo_soja_anual.csv")

df_complexo_soja_anual = df_complexo_soja_anual.rename(columns = {"Produção":"producao"})
df_complexo_soja_anual = df_complexo_soja_anual.rename(columns = {"periodo":"ano"})
df_complexo_soja_anual["ano"] = df_complexo_soja_anual["ano"].astype(int)

# ----------------------------------- compra liquida ---------------------------------------------------

df_compra_liquida = pd.read_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/extracao/compra_liquida.csv")
df_compra_liquida = df_compra_liquida.fillna(0)

df_compra_liquida = df_compra_liquida.melt(id_vars = ["ano"], var_name = "periodo", value_name = "compra_liquida")
df_compra_liquida = df_compra_liquida.rename(columns = {"ano":"mes"})
df_compra_liquida = df_compra_liquida.rename(columns = {"periodo":"ano"})

df_compra_liquida['ano_mes'] = df_compra_liquida['ano'].astype(str) + '-' + df_compra_liquida['mes'].map(meses_dict)

df_compra_liquida = df_compra_liquida[["mes", "ano", "ano_mes", "compra_liquida"]]


# ----------------------------------- preco ---------------------------------------------------

df_preco = pd.read_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/extracao/preco.csv")
df_preco = df_preco.fillna(0)

df_preco["mes"] = df_preco["periodo"].str[:3].str.capitalize()  # Pegando os 3 primeiros caracteres (mês)
df_preco["ano"] = df_preco["periodo"].str[-2:].astype(int)
df_preco["ano"] = df_preco["ano"].apply(lambda x: x + 2000 if x < 50 else x + 1900)
df_preco['ano_mes'] = df_preco['ano'].astype(str) + '-' + df_preco['mes'].map(meses_dict)

df_preco = df_preco.rename(columns = {"Chicago - CBOT (US$/t)":"chicago_cbot_u$/t"})
df_preco = df_preco.rename(columns = {"FOB Porto - Paranaguá (US$/t)":"fob_porto_paranagua_u$/t"})
df_preco = df_preco.rename(columns = {"Maringá / PR - R$/saca (sem ICMS)":"maringa_r$/saca"})
df_preco = df_preco.rename(columns = {"Mogiana / SP - R$/saca (sem ICMS)":"mogiana_r$/saca"})
df_preco = df_preco.rename(columns = {"Passo Fundo / RS - R$/saca (sem ICMS)":"passofundo_r$/saca"})
df_preco = df_preco.rename(columns = {"Rondonopolis / MT - R$/saca (sem ICMS)":"rondonopolis_r$/saca"})

df_preco = df_preco.drop(columns=["periodo"])

df_preco = df_preco[["mes", "ano", "ano_mes", "chicago_cbot_u$/t", "fob_porto_paranagua_u$/t", "maringa_r$/saca", "mogiana_r$/saca", "passofundo_r$/saca", "rondonopolis_r$/saca"]]

# ------------------------------------ merge estoque e exportaçao -------------------------------------------
df_merged = pd.merge(df_estoque[["mes", "ano", "ano_mes", "estoque"]], df_exportacao[["mes", "ano", "ano_mes", "exportacao"]], on = "ano_mes", how = "outer")

df_merged['mes_x'] = df_merged['mes_x'].fillna(df_merged['mes_y'])
df_merged['ano_x'] = df_merged['ano_x'].fillna(df_merged['ano_y'])
df_merged["estoque"] = df_merged["estoque"].fillna(0)

df_merged = df_merged.drop(columns=["mes_y", "ano_y"])

# ------------------------------------ merge com processamento -------------------------------------------

df_merged = pd.merge(df_merged[["mes_x", "ano_x", "ano_mes", "estoque", "exportacao"]], df_processamento[["mes", "ano", "ano_mes", "processamento"]], on = "ano_mes", how = "outer")

df_merged['mes_x'] = df_merged['mes_x'].fillna(df_merged['mes'])
df_merged['ano_x'] = df_merged['ano_x'].fillna(df_merged['ano'])
df_merged["estoque"] = df_merged["estoque"].fillna(0)
df_merged["exportacao"] = df_merged["exportacao"].fillna(0)
df_merged["processamento"] = df_merged["processamento"].fillna(0)

df_merged = df_merged.drop(columns=["mes", "ano"])

# ------------------------------------ merge com compra liquida -------------------------------------------

df_merged = pd.merge(df_merged[["mes_x", "ano_x", "ano_mes", "estoque", "exportacao", "processamento"]], df_compra_liquida[["mes", "ano", "ano_mes", "compra_liquida"]], on = "ano_mes", how = "outer")

df_merged["compra_liquida"] = df_merged["compra_liquida"].fillna(0)

df_merged = df_merged.drop(columns=["mes", "ano"])
df_merged = df_merged.rename(columns = {"mes_x":"mes"})
df_merged = df_merged.rename(columns = {"ano_x":"ano"})


# ------------------------- criar saldo = Estoque + compra liquida - (exportacao + processamento) ---------------------------------------

df_merged["saldo"] = df_merged["estoque"] + df_merged["compra_liquida"] - df_merged["exportacao"] - df_merged["processamento"]


# ------------------------------------ merge com producao -------------------------------------------

df_merged["ano"] = df_merged["ano"].astype(int)

df_merged = pd.merge(df_merged[["mes", "ano", "ano_mes", "estoque", "exportacao", "processamento", "compra_liquida", "saldo"]], df_complexo_soja_anual[["ano", "producao"]], on = "ano", how = "outer")

df_merged["producao"] = df_merged["producao"].fillna(0)


# ------------------------------------ merge com preco -------------------------------------------

df_merged = pd.merge(df_merged[["mes", "ano", "ano_mes", "estoque", "exportacao", "processamento", "compra_liquida", "saldo", "producao"]], df_preco[["ano_mes", "chicago_cbot_u$/t", "fob_porto_paranagua_u$/t", "maringa_r$/saca", "mogiana_r$/saca", "passofundo_r$/saca", "rondonopolis_r$/saca"]], on = "ano_mes", how = "outer")

df_merged = df_merged.fillna(0)

# ------------------------------------ formatacao dados --------------------------------------

df_merged["ano"] = df_merged["ano"].astype(int)

df_merged["ano_mes"] = pd.to_datetime(df_merged["ano_mes"], format="%Y-%m")

df_merged.to_csv("/Users/leonardomartini/Documents/Github/SojaMetrics/database/soja.csv")




df_merged.info()



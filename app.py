"""Plataforma Financeira Integrada — Tríade (BACEN + B3 + CVM)."""

import streamlit as st

from src.dados import ORIGEM_BANCO, carregar_dados
from src.filtros import aplicar_filtros, barra_lateral
from src.kpis import exibir_kpis

st.set_page_config(page_title="Tríade Financeira", page_icon="📊", layout="wide")

dados, origem, motivo = carregar_dados()
filtros = barra_lateral(dados["dim_empresa"])

with st.sidebar:
    st.divider()
    if origem == ORIGEM_BANCO:
        st.success(f"Fonte dos dados: {origem}")
    else:
        st.warning(f"Fonte dos dados: {origem}")
        st.caption(f"Banco indisponível ({motivo}); exibindo a cópia local dos dados.")

st.title("Plataforma Financeira Integrada — Tríade")
st.caption("Macroeconomia (BACEN) · Mercado (B3) · Balanços (CVM) — 2019 a 2023")

if not filtros["empresas"]:
    st.warning("Nenhuma empresa selecionada. Escolha ao menos um setor e uma empresa na barra lateral.")
    st.stop()

integrado = aplicar_filtros(dados["fato_anual_integrado"], filtros)


# KPIs: último exercício do período escolhido, comparado ao exercício anterior
anual_empresas = dados["fato_anual_integrado"]
anual_empresas = anual_empresas[anual_empresas["ticker"].isin(filtros["empresas"])]
st.subheader(f"Indicadores-chave — exercício de {filtros['ano_fim']}")
exibir_kpis(dados["fato_macro_anual"], anual_empresas, filtros["ano_fim"])

# Prévia temporária do recorte — será substituída pelos KPIs, gráficos e abas nos próximos cards
st.subheader("Recorte selecionado")
st.write(f"{len(filtros['empresas'])} empresa(s) · exercícios de "
         f"{filtros['ano_inicio']} a {filtros['ano_fim']} · {len(integrado)} registros")
st.dataframe(integrado[["ticker", "empresa", "setor", "ano", "receita_liquida",
                        "lucro_liquido", "roe", "retorno_anual", "selic_media_pct"]],
             hide_index=True)

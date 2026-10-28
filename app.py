"""Plataforma Financeira Integrada — Tríade (BACEN + B3 + CVM)."""

import streamlit as st

from src.dados import ORIGEM_BANCO, carregar_dados
from src.filtros import aplicar_filtros, barra_lateral

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

# Prévia temporária do recorte — será substituída pelos KPIs, gráficos e abas nos próximos cards
st.subheader("Recorte selecionado")
st.write(f"{len(filtros['empresas'])} empresa(s) · exercícios de "
         f"{filtros['ano_inicio']} a {filtros['ano_fim']} · {len(integrado)} registros")
st.dataframe(integrado[["ticker", "empresa", "setor", "ano", "receita_liquida",
                        "lucro_liquido", "roe", "retorno_anual", "selic_media_pct"]],
             hide_index=True)

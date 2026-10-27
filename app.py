"""Plataforma Financeira Integrada — Tríade (BACEN + B3 + CVM)."""

import pandas as pd
import streamlit as st

from src.dados import ORIGEM_BANCO, carregar_dados

st.set_page_config(page_title="Tríade Financeira", page_icon="📊", layout="wide")

dados, origem, motivo = carregar_dados()

st.title("Plataforma Financeira Integrada — Tríade")
st.caption("Macroeconomia (BACEN) · Mercado (B3) · Balanços (CVM) — 2019 a 2023")

with st.sidebar:
    if origem == ORIGEM_BANCO:
        st.success(f"Fonte dos dados: {origem}")
    else:
        st.warning(f"Fonte dos dados: {origem}")
        st.caption(f"Banco indisponível ({motivo}); exibindo a cópia local dos dados.")

# Conferência temporária da carga — será substituída pelas abas nos próximos cards
st.subheader("Conferência da carga")
st.dataframe(
    pd.DataFrame({"tabela": list(dados), "linhas": [len(df) for df in dados.values()]}),
    hide_index=True,
)

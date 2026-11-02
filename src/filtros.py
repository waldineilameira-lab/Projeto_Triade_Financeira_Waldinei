"""Barra lateral: filtros cruzados com persistência em st.session_state."""

import pandas as pd
import streamlit as st

ANO_MIN, ANO_MAX = 2019, 2023


def _padroes(dim_empresa: pd.DataFrame) -> dict:
    """Valores iniciais dos filtros: todos os setores, todas as empresas, todo o período."""
    return {
        "f_setores": sorted(dim_empresa["setor"].unique()),
        "f_empresas": sorted(dim_empresa["ticker"]),
        "f_periodo": (ANO_MIN, ANO_MAX),
    }


def _empresas_dos_setores(dim_empresa: pd.DataFrame, setores: list) -> list:
    """Tickers que pertencem aos setores selecionados (filtro cruzado)."""
    return sorted(dim_empresa.loc[dim_empresa["setor"].isin(setores), "ticker"])


def _ao_mudar_setores(dim_empresa: pd.DataFrame) -> None:
    """Ao trocar os setores, seleciona automaticamente todas as empresas desses setores."""
    st.session_state["f_empresas"] = _empresas_dos_setores(dim_empresa, st.session_state["f_setores"])


def _resetar(dim_empresa: pd.DataFrame) -> None:
    """Botão de reset: devolve todos os filtros aos valores iniciais."""
    for chave, valor in _padroes(dim_empresa).items():
        st.session_state[chave] = valor


def barra_lateral(dim_empresa: pd.DataFrame) -> dict:
    """Desenha os filtros na barra lateral e devolve as seleções do usuário."""
    for chave, valor in _padroes(dim_empresa).items():
        st.session_state.setdefault(chave, valor)  # só na primeira execução da sessão

    nomes = dict(zip(dim_empresa["ticker"], dim_empresa["empresa"]))

    with st.sidebar:
        st.header("Filtros")
        st.multiselect(
            "Setores", options=sorted(dim_empresa["setor"].unique()), key="f_setores",
            on_change=_ao_mudar_setores, args=(dim_empresa,),
            help="Ao alterar os setores, a lista de empresas é atualizada automaticamente.",
        )
        st.multiselect(
            "Empresas", options=_empresas_dos_setores(dim_empresa, st.session_state["f_setores"]),
            key="f_empresas", format_func=lambda t: f"{t} — {nomes[t]}",
        )
        st.slider("Período (exercícios)", ANO_MIN, ANO_MAX, key="f_periodo")
        st.button("Resetar filtros", on_click=_resetar, args=(dim_empresa,),
                  use_container_width=True, type="secondary")

    return {
        "setores": st.session_state["f_setores"],
        "empresas": st.session_state["f_empresas"],
        "ano_inicio": st.session_state["f_periodo"][0],
        "ano_fim": st.session_state["f_periodo"][1],
    }


def aplicar_filtros(df: pd.DataFrame, filtros: dict, coluna_data: str | None = None) -> pd.DataFrame:
    """Aplica empresa e período a qualquer tabela (anual pela coluna 'ano' ou diária/mensal pela data)."""
    resultado = df
    if "ticker" in resultado.columns:
        resultado = resultado[resultado["ticker"].isin(filtros["empresas"])]
    if "ano" in resultado.columns:
        anos = resultado["ano"]
    elif coluna_data:
        anos = resultado[coluna_data].dt.year
    else:
        return resultado
    return resultado[anos.between(filtros["ano_inicio"], filtros["ano_fim"])]

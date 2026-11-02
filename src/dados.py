"""Camada de acesso a dados: Supabase (PostgreSQL) com contingência em CSV."""

from pathlib import Path

import pandas as pd
import streamlit as st

# Caminho relativo à raiz do projeto (funciona no computador e no Streamlit Cloud)
PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

TABELAS = [
    "dim_empresa",
    "fato_macro",
    "fato_macro_mensal",
    "fato_macro_anual",
    "fato_cotacoes",
    "fato_mercado_anual",
    "fato_contabil",
    "fato_indicadores_contabeis",
    "fato_anual_integrado",
]
COLUNAS_DATA = {
    "fato_macro": ["data"],
    "fato_macro_mensal": ["mes"],
    "fato_cotacoes": ["data"],
}
COLUNAS_TEXTO: dict = {"cnpj": "str", "cd_conta": "str"}

TTL_SEGUNDOS = 3600  # os dados são históricos (2019–2023): 1 hora de cache é suficiente
ORIGEM_BANCO = "Supabase (PostgreSQL)"
ORIGEM_CSV = "CSV local (contingência)"


def _ler_csv(nome: str) -> pd.DataFrame:
    """Lê uma tabela tratada de data/processed, com os mesmos tipos usados na carga do banco."""
    return pd.read_csv(
        PROC_DIR / f"{nome}.csv",
        parse_dates=COLUNAS_DATA.get(nome, []),
        dtype=COLUNAS_TEXTO,
    )


@st.cache_data(ttl=TTL_SEGUNDOS, show_spinner="Carregando dados...")
def carregar_dados() -> tuple[dict[str, pd.DataFrame], str, str]:
    """Carrega todas as tabelas do Supabase; se o banco falhar, usa os CSVs locais.

    Retorna (dicionário de DataFrames, origem dos dados, motivo da contingência).
    """
    try:
        conn = st.connection(
            "postgresql", type="sql", connect_args={"connect_timeout": 10}
        )
        dados = {
            nome: conn.query(f'SELECT * FROM "{nome}"', ttl=TTL_SEGUNDOS)
            for nome in TABELAS
        }
        return dados, ORIGEM_BANCO, ""
    except Exception as erro:  # noqa: BLE001 — qualquer falha do banco aciona a contingência
        dados = {nome: _ler_csv(nome) for nome in TABELAS}
        return dados, ORIGEM_CSV, type(erro).__name__

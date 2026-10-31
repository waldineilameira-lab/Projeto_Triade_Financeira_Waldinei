"""Plataforma Financeira Integrada — Tríade (BACEN + B3 + CVM)."""

import streamlit as st

from src.dados import ORIGEM_BANCO, carregar_dados
from src.filtros import aplicar_filtros, barra_lateral
from src.graficos import (
    grafico_base100,
    grafico_ebit_retorno,
    grafico_lucro_roe,
    grafico_macro,
    grafico_setor_selic,
)
from src.kpis import exibir_kpis
from src.narrativa import HISTORIAS, piramide

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

empresas, ano_ini, ano_fim = filtros["empresas"], filtros["ano_inicio"], filtros["ano_fim"]
anual = dados["fato_anual_integrado"]
integrado = aplicar_filtros(anual, filtros)

# KPIs: último exercício do período escolhido, comparado ao exercício anterior
st.subheader(f"Indicadores-chave — exercício de {ano_fim}")
exibir_kpis(dados["fato_macro_anual"], anual[anual["ticker"].isin(empresas)], ano_fim)

aba_macro, aba_balancos, aba_setores, aba_resiliencia, aba_dados = st.tabs([
    "Cenário macroeconômico",
    "P1 · Juros e balanços",
    "P2 · Setores × Selic",
    "P3/P4 · Câmbio e resiliência",
    "Dados e download",
])

with aba_macro:
    st.plotly_chart(grafico_macro(dados["fato_macro_mensal"], ano_ini, ano_fim))
    piramide(**HISTORIAS["macro"])

with aba_balancos:
    st.plotly_chart(grafico_lucro_roe(anual, empresas, ano_fim))
    piramide(**HISTORIAS["balancos"])

with aba_setores:
    st.plotly_chart(grafico_setor_selic(anual, empresas, ano_ini, ano_fim))
    st.plotly_chart(grafico_base100(dados["fato_cotacoes"], dados["dim_empresa"], empresas, ano_ini, ano_fim))
    piramide(**HISTORIAS["setores"])

with aba_resiliencia:
    st.plotly_chart(grafico_ebit_retorno(anual, empresas, ano_ini, ano_fim))
    st.caption("O Itaú não aparece neste gráfico: instituições financeiras não apresentam margem EBIT.")
    piramide(**HISTORIAS["resiliencia"])

with aba_dados:
    st.markdown(f"**Recorte atual:** {len(empresas)} empresa(s) · exercícios de {ano_ini} a {ano_fim} "
                f"· {len(integrado)} registros")
    tabela = integrado[["ticker", "empresa", "setor", "ano", "receita_liquida", "lucro_liquido",
                        "margem_ebit", "roe", "retorno_anual", "selic_media_pct", "ipca_ano_pct"]]
    st.dataframe(
        tabela, hide_index=True,
        column_config={
            "ticker": "Ticker", "empresa": "Empresa", "setor": "Setor",
            "ano": st.column_config.NumberColumn("Ano", format="%d"),
            "receita_liquida": st.column_config.NumberColumn("Receita líquida (R$)", format="localized"),
            "lucro_liquido": st.column_config.NumberColumn("Lucro líquido (R$)", format="localized"),
            "margem_ebit": st.column_config.NumberColumn("Margem EBIT", format="percent"),
            "roe": st.column_config.NumberColumn("ROE", format="percent"),
            "retorno_anual": st.column_config.NumberColumn("Retorno da ação", format="percent"),
            "selic_media_pct": st.column_config.NumberColumn("Selic média (%)", format="%.2f"),
            "ipca_ano_pct": st.column_config.NumberColumn("IPCA do ano (%)", format="%.2f"),
        },
    )
    st.download_button(
        "Baixar recorte em CSV",
        data=integrado.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name=f"triade_{ano_ini}_{ano_fim}.csv", mime="text/csv", type="primary",
        help="Separador ';' e vírgula decimal: abre direto no Excel em português.",
    )
    st.markdown("**Limitações da análise**")
    st.markdown(
        "- Associação estatística não implica causalidade.\n"
        "- Uma a duas empresas por setor: as conclusões valem para estas companhias, não para o setor.\n"
        "- Médias simples entre empresas; ROE sobre o PL do fim do exercício.\n"
        "- Itaú: margens, liquidez e dívida líquida não aplicáveis (instituição financeira).\n"
        "- Retorno de 2019 com base no 1º pregão do ano; retorno do ITUB4 em 2021 pode estar "
        "subestimado pela cisão da XP Inc.\n"
        "- Embraer: código histórico EMBR3 (atual EMBJ3)."
    )

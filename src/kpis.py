"""KPIs estratégicos da Linha 4 (st.metric) com deltas em relação ao exercício anterior."""

import pandas as pd
import streamlit as st

ANO_INICIAL_DADOS = 2019


def br(valor: float, casas: int = 1) -> str:
    """Formata números no padrão brasileiro: 1.234,5."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _sinal(valor: float) -> str:
    """Sinal explícito (o st.metric usa o '-' inicial para colorir o delta)."""
    return "+" if valor >= 0 else "-"


def _valor_do_ano(df: pd.DataFrame, ano: int, coluna: str) -> float | None:
    linha = df.loc[df["ano"] == ano, coluna]
    return None if linha.empty else float(linha.iloc[0])


def calcular_kpis(macro_anual: pd.DataFrame, anual: pd.DataFrame, ano: int) -> dict:
    """Calcula os 4 KPIs do ano escolhido e do ano anterior.

    anual: fato_anual_integrado filtrado pelas empresas selecionadas (todos os anos).
    """
    anterior = ano - 1
    nao_financeiras = anual[anual["tipo"] == "Não financeira"]
    return {
        "ano": ano,
        "tem_anterior": anterior >= ANO_INICIAL_DADOS,
        "selic": _valor_do_ano(macro_anual, ano, "selic_fim_ano_pct"),
        "selic_ant": _valor_do_ano(macro_anual, anterior, "selic_fim_ano_pct"),
        "ipca": _valor_do_ano(macro_anual, ano, "ipca_12m_dez_pct"),
        "ipca_ant": _valor_do_ano(macro_anual, anterior, "ipca_12m_dez_pct"),
        "tem_receita": not nao_financeiras.empty,
        "receita": nao_financeiras.loc[nao_financeiras["ano"] == ano, "receita_liquida"].sum(),
        "receita_ant": nao_financeiras.loc[nao_financeiras["ano"] == anterior, "receita_liquida"].sum(),
        "lucro": anual.loc[anual["ano"] == ano, "lucro_liquido"].sum(),
        "lucro_ant": anual.loc[anual["ano"] == anterior, "lucro_liquido"].sum(),
    }


def exibir_kpis(macro_anual: pd.DataFrame, anual: pd.DataFrame, ano: int) -> None:
    """Desenha os 4 KPIs estratégicos lado a lado."""
    k = calcular_kpis(macro_anual, anual, ano)
    ref = f"vs. {ano - 1}"

    d_selic = d_ipca = d_receita = d_lucro = None
    if k["tem_anterior"]:
        dif = k["selic"] - k["selic_ant"]
        d_selic = f"{_sinal(dif)}{br(abs(dif), 2)} p.p. {ref}"
        dif = k["ipca"] - k["ipca_ant"]
        d_ipca = f"{_sinal(dif)}{br(abs(dif), 2)} p.p. {ref}"
        if k["tem_receita"] and k["receita_ant"] > 0:
            var = (k["receita"] / k["receita_ant"] - 1) * 100
            d_receita = f"{_sinal(var)}{br(abs(var))}% {ref}"
        dif = (k["lucro"] - k["lucro_ant"]) / 1e9
        d_lucro = f"{_sinal(dif)}R$ {br(abs(dif))} bi {ref}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Selic Meta — fim de {ano}", f"{br(k['selic'], 2)}% a.a.", d_selic, delta_color="off", border=True,
              help="Meta da taxa Selic definida pelo Copom, vigente em 31/12 (BACEN, série 432).")
    c2.metric(f"IPCA 12 meses — dez/{ano}", f"{br(k['ipca'], 2)}%", d_ipca, delta_color="inverse",
              border=True,
              help="Inflação oficial acumulada em 12 meses (BACEN, série 13522). "
                   "Alta da inflação aparece em vermelho.")
    c3.metric(f"Receita da carteira — {ano}",
              f"R$ {br(k['receita'] / 1e9)} bi" if k["tem_receita"] else "N/A",
              d_receita, border=True,
              help="Soma da receita líquida das empresas não financeiras selecionadas (CVM). "
                   "O Itaú não entra na soma: sua receita de intermediação financeira não é comparável.")
    c4.metric(f"Lucro líquido da carteira — {ano}", f"R$ {br(k['lucro'] / 1e9)} bi", d_lucro,
              border=True,
              help="Soma do lucro líquido consolidado das empresas selecionadas (CVM).")

    if not k["tem_anterior"]:
        st.caption("Sem variação para 2019: o exercício de 2018 está fora do período analisado.")

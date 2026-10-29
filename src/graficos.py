"""Gráficos da Linha 4 em Plotly: preparação dos dados (pandas) separada do desenho."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.kpis import br

# Cor fixa por setor: a cor acompanha a entidade, nunca a posição no ranking,
# e não muda quando um filtro remove outros setores.
CORES_SETOR = {
    "Energia": "#3987e5",
    "Commodities Exportadoras": "#d95926",
    "Exportadoras Industriais": "#199e70",
    "Consumo/Varejo": "#c98500",
    "Bancos": "#d55181",
}
COR_SELIC, COR_IPCA, COR_DOLAR = "#3987e5", "#d95926", "#199e70"
TRACOS = ["solid", "dash"]  # 1ª e 2ª empresa de um mesmo setor


def _layout_padrao(fig: go.Figure, titulo: str, altura: int = 460) -> go.Figure:
    """Estilo comum: título, números no padrão brasileiro e legenda horizontal no topo."""
    fig.update_layout(
        title=titulo, height=altura, separators=",.", hovermode="x unified",
        legend={"orientation": "h", "yanchor": "top", "y": -0.12, "x": 0, "title": None},
        margin={"t": 70, "l": 10, "r": 10, "b": 10},
    )
    return fig


# ---------- Gráfico 1: multieixo macro-cambial ----------

def dados_macro(macro_mensal: pd.DataFrame, ano_inicio: int, ano_fim: int) -> pd.DataFrame:
    anos = macro_mensal["mes"].dt.year
    return macro_mensal[anos.between(ano_inicio, ano_fim)].sort_values("mes")


def grafico_macro(macro_mensal: pd.DataFrame, ano_inicio: int, ano_fim: int) -> go.Figure:
    """Selic e IPCA 12M (%) no painel superior; Dólar PTAX (R$) no inferior, mesmo eixo do tempo."""
    df = dados_macro(macro_mensal, ano_inicio, ano_fim)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        row_heights=[0.6, 0.4],
                        subplot_titles=("Juros e inflação (% a.a.)", "Dólar PTAX (R$ por US$)"))
    fig.add_trace(go.Scatter(x=df["mes"], y=df["selic_meta_pct"], name="Selic Meta",
                             line={"color": COR_SELIC, "width": 2},
                             hovertemplate="%{y:.2f}%"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["mes"], y=df["ipca_12m_pct"], name="IPCA 12 meses",
                             line={"color": COR_IPCA, "width": 2},
                             hovertemplate="%{y:.2f}%"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["mes"], y=df["ptax_media"], name="Dólar PTAX (média mensal)",
                             line={"color": COR_DOLAR, "width": 2},
                             hovertemplate="R$ %{y:.2f}"), row=2, col=1)
    fig.update_yaxes(title_text="%", row=1, col=1)
    fig.update_yaxes(title_text="R$", row=2, col=1)
    fig.update_xaxes(dtick="M6", tickformat="%b/%Y")
    return _layout_padrao(fig, "Selic, inflação e câmbio — evolução mensal", altura=560)


# ---------- Gráfico 2: Base 100 ----------

def dados_base100(cotacoes: pd.DataFrame, empresas: list, ano_inicio: int, ano_fim: int) -> pd.DataFrame:
    """Normaliza o fechamento ajustado de cada ação para 100 no primeiro pregão do período."""
    df = cotacoes[cotacoes["ticker"].isin(empresas)
                  & cotacoes["data"].dt.year.between(ano_inicio, ano_fim)].sort_values(["ticker", "data"])
    primeiro = df.groupby("ticker")["fechamento_ajustado"].transform("first")
    return df.assign(base100=df["fechamento_ajustado"] / primeiro * 100)


def grafico_base100(cotacoes: pd.DataFrame, dim_empresa: pd.DataFrame, empresas: list,
                    ano_inicio: int, ano_fim: int) -> go.Figure:
    df = dados_base100(cotacoes, empresas, ano_inicio, ano_fim)
    fig = go.Figure()
    for setor, grupo in dim_empresa[dim_empresa["ticker"].isin(empresas)].groupby("setor", sort=False):
        for i, ticker in enumerate(sorted(grupo["ticker"])):
            serie = df[df["ticker"] == ticker]
            fig.add_trace(go.Scatter(
                x=serie["data"], y=serie["base100"], name=f"{ticker} ({setor})",
                line={"color": CORES_SETOR[str(setor)], "width": 2, "dash": TRACOS[i % 2]},
                hovertemplate=f"{ticker}: " + "%{y:.1f}<extra></extra>",
            ))
    fig.add_hline(y=100, line={"color": "gray", "width": 1, "dash": "dot"})
    fig.update_yaxes(title_text=f"Índice (1º pregão de {ano_inicio} = 100)")
    fig = _layout_padrao(fig, "Desempenho comparado das ações — Base 100 (com proventos)")
    fig.update_layout(hovermode="x")
    return fig


# ---------- Gráfico 3: lucro líquido e ROE ----------

def dados_lucro_roe(anual: pd.DataFrame, empresas: list, ano: int) -> pd.DataFrame:
    df = anual[anual["ticker"].isin(empresas) & (anual["ano"] == ano)].copy()
    df["lucro_bi"] = df["lucro_liquido"] / 1e9
    df["rotulo_roe"] = df["roe"].map(lambda r: f"ROE {br(r * 100)}%")
    return df.sort_values("lucro_bi", ascending=False)


def grafico_lucro_roe(anual: pd.DataFrame, empresas: list, ano: int) -> go.Figure:
    df = dados_lucro_roe(anual, empresas, ano)
    fig = px.bar(df, x="ticker", y="lucro_bi", color="setor", text="rotulo_roe",
                 color_discrete_map=CORES_SETOR,
                 custom_data=["empresa", "roe"],
                 labels={"ticker": "Empresa", "lucro_bi": "Lucro líquido (R$ bi)", "setor": "Setor"})
    fig.update_traces(textposition="outside", cliponaxis=False,
                      hovertemplate="<b>%{customdata[0]}</b><br>Lucro: R$ %{y:.1f} bi"
                                    "<br>ROE: %{customdata[1]:.1%}<extra></extra>")
    fig.update_xaxes(categoryorder="array", categoryarray=df["ticker"].tolist())
    topo = max(df["lucro_bi"].max(), 0) * 1.15
    base = min(df["lucro_bi"].min(), 0) * 1.15
    fig.update_yaxes(range=[base, topo])
    fig.add_hline(y=0, line={"color": "gray", "width": 1})
    fig = _layout_padrao(fig, f"Lucro líquido e ROE por empresa — exercício de {ano}")
    fig.update_layout(hovermode="closest", bargap=0.35)
    return fig

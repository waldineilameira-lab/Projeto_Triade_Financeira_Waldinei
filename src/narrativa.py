"""Storytelling executivo: Pirâmide Invertida (Contexto → Insight → Ação) para cada aba."""

import streamlit as st

NOTA_PERIODO = (
    "Leitura referente ao período completo (2019–2023) e à carteira de 9 empresas; "
    "os gráficos acima reagem aos filtros."
)


def piramide(contexto: str, insight: str, acao: str) -> None:
    """Bloco padronizado de storytelling."""
    with st.container(border=True):
        st.markdown(f"**Contexto** — {contexto}")
        st.markdown(f"**Insight** — {insight}")
        st.markdown(f"**Ação** — {acao}")
        st.caption(NOTA_PERIODO)


HISTORIAS = {
    "macro": {
        "contexto": "A Selic saiu de 6,5% (início de 2019) para a mínima histórica de 2% na pandemia "
        "e subiu a 13,75% em 2022, o maior ciclo de aperto em duas décadas. "
        "O dólar subiu 29% em 2020.",
        "insight": "A inflação acelerou antes dos juros: em 2021 o IPCA passou de 10% com a Selic "
        "ainda abaixo disso, gerando juro real negativo (−5,0%). Em 2023 o juro real "
        "chegou a +8,3%.",
        "acao": "Acompanhar o juro real, e não só a Selic nominal, ao avaliar o custo do capital "
        "e a atratividade da renda variável.",
    },
    "balancos": {
        "contexto": "Com a Selic de 2,9% (2020) a 13,3% (2023), esperava-se alta das despesas "
        "financeiras das empresas não financeiras.",
        "insight": "Os dados contrariam a hipótese: a despesa financeira foi máxima em 2020 "
        "(R$ 115 bi), com o juro no piso, e menor em 2022–2023. A alavancagem média "
        "(Dívida Líquida/PL) caiu de 1,46 para 0,42. Explicação provável: dívidas em "
        "dólar e desalavancagem prévia.",
        "acao": "Separar a exposição à Selic da exposição cambial da dívida ao avaliar o risco "
        "de juros.",
    },
    "setores": {
        "contexto": "Entre 2022 e 2023 a Selic média ficou acima de 12% ao ano.",
        "insight": "Consumo/Varejo teve retorno médio negativo de 2020 a 2023; Energia (+62,5%) e "
        "Bancos (+42,3%) lideraram em 2023. A associação é consistente com a "
        "sensibilidade do consumo ao crédito — mas correlação não implica causalidade.",
        "acao": "Em ciclos de aperto monetário, tratar setores dependentes de crédito e consumo "
        "com cautela.",
    },
    "resiliencia": {
        "contexto": "Em 2020 o dólar subiu 29%; ao longo do período, as margens operacionais "
        "variaram fortemente entre setores.",
        "insight": "Exportadoras se protegeram no estresse cambial (VALE3 +70,9% e SUZB3 +47,5% "
        "em 2020), embora a Suzano tenha tido prejuízo contábil pela dívida em dólar. "
        "Energia combinou o maior ROE médio (28,3%), a maior margem EBIT (41,1%) e a "
        "menor volatilidade. A WEG teve margem moderada (~17%) e o maior retorno: o "
        "mercado precifica crescimento, não apenas margem.",
        "acao": "Combinar solidez contábil, exposição cambial e retorno ao comparar setores; "
        "margem alta isolada não garante retorno.",
    },
}

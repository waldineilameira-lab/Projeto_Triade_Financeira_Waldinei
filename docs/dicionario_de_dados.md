# Dicionário de Dados — Plataforma Financeira Integrada (Tríade)

Este documento descreve todas as tabelas tratadas da pasta `data/processed/`, geradas pelos notebooks `04_limpeza_tipagem.ipynb` e `05_modelagem_integracao.ipynb`.

## Convenções gerais

| Convenção | Regra |
|---|---|
| **Período** | 01/01/2019 a 31/12/2023 (exercícios fiscais de 2019 a 2023) |
| **Moeda** | Real (R$). Valores contábeis da CVM convertidos de milhares para reais (`ESCALA_MOEDA = MIL` × 1.000) |
| **Indicadores em fração** | Margens, ROE, retornos, volatilidade e crescimento: `0,15` = 15% |
| **Indicadores em pontos percentuais** | Colunas com sufixo `_pct` (dados macroeconômicos): `13,75` = 13,75% |
| **Sinal contábil** | Despesas aparecem com sinal negativo, como publicado pela CVM |
| **N/A — Itaú (ITUB4)** | Instituição financeira: EBIT, margens, liquidez corrente e dívida líquida não são aplicáveis e ficam vazios |
| **Tipos primitivos** | `str` (texto), `int64` (inteiro), `float64` (decimal), `datetime64` (data) |

## Modelo de dados

Constelação de fatos (variação do esquema estrela): a dimensão `dim_empresa` é compartilhada pelas tabelas de fatos por meio da chave `ticker`; a dimensão tempo é representada pelas colunas `data`, `mes` e `ano`.

| Tabela | Tipo | Granularidade (1 linha =) | Chave | Linhas |
|---|---|---|---|---|
| `dim_empresa` | Dimensão | 1 empresa | `ticker` | 9 |
| `fato_macro` | Fato | 1 série × 1 data | `serie`, `data` | 3.201 |
| `fato_macro_mensal` | Fato | 1 mês | `mes` | 60 |
| `fato_macro_anual` | Fato | 1 ano | `ano` | 5 |
| `fato_cotacoes` | Fato | 1 ação × 1 pregão | `ticker`, `data` | 11.169 |
| `fato_mercado_anual` | Fato | 1 ação × 1 ano | `ticker`, `ano` | 45 |
| `fato_contabil` | Fato | 1 conta × 1 empresa × 1 exercício | `ticker`, `ano`, `demonstrativo`, `cd_conta` | 9.894 |
| `fato_indicadores_contabeis` | Fato | 1 empresa × 1 exercício | `ticker`, `ano` | 45 |
| `fato_anual_integrado` | Fato integrado | 1 empresa × 1 exercício | `ticker`, `ano` | 45 |

---

## 1. `dim_empresa`

Cadastro das 9 companhias da carteira. **Fonte:** definição do projeto + CNPJ da base CVM.

| Campo | Tipo | Significado | Regra |
|---|---|---|---|
| `ticker` | str | Código de negociação na B3 | Código vigente no período analisado (Embraer: EMBR3; atual EMBJ3) |
| `empresa` | str | Nome resumido da companhia | Definido no projeto |
| `setor` | str | Grupo setorial de análise | Consumo/Varejo, Energia, Commodities Exportadoras, Exportadoras Industriais ou Bancos |
| `tipo` | str | Natureza contábil | `Financeira` (Itaú) ou `Não financeira` |
| `cnpj` | str | CNPJ da companhia (ponte entre B3 e CVM) | Extraído da base CVM |

## 2. `fato_macro`

Séries macroeconômicas no formato longo. **Fonte:** BACEN/SGS.

| Campo | Tipo | Significado | Regra |
|---|---|---|---|
| `data` | datetime64 | Data de referência da observação | Convertida de `dd/mm/aaaa` com formato explícito `%d/%m/%Y` |
| `serie` | str | Nome da série | `selic_meta` (SGS 432), `ipca_mensal` (433), `ipca_12m` (13522), `ptax_venda` (1) |
| `valor` | float64 | Valor da série | Selic em % a.a.; IPCA em %; PTAX em R$ por US$ |

## 3. `fato_macro_mensal`

Séries macro harmonizadas na frequência mensal (base do gráfico multieixo). **Fonte:** derivada de `fato_macro`.

| Campo | Tipo | Significado | Regra |
|---|---|---|---|
| `mes` | datetime64 | Mês de referência | Primeiro dia do mês |
| `selic_meta_pct` | float64 | Meta Selic vigente no fim do mês (% a.a.) | Último valor diário do mês |
| `ipca_mensal_pct` | float64 | Inflação do mês (%) | Valor mensal oficial |
| `ipca_12m_pct` | float64 | Inflação acumulada em 12 meses (%) | Valor mensal oficial |
| `ptax_media` | float64 | Dólar PTAX venda médio do mês (R$/US$) | Média dos dias úteis do mês |

## 4. `fato_macro_anual`

Indicadores macroeconômicos anuais. **Fonte:** derivada de `fato_macro`.

| Campo | Tipo | Significado | Regra |
|---|---|---|---|
| `ano` | int64 | Ano de referência | — |
| `selic_media_pct` | float64 | Selic média do ano (% a.a.) | Média da série diária corrida (ponderada pelo tempo de vigência) |
| `selic_fim_ano_pct` | float64 | Selic vigente em 31/12 (% a.a.) | Último valor do ano |
| `ipca_ano_pct` | float64 | Inflação acumulada no ano (%) | [Π(1 + IPCA mensal/100) − 1] × 100 |
| `ipca_12m_dez_pct` | float64 | IPCA 12 meses de dezembro (%) | Série oficial 13522; usada para validar `ipca_ano_pct` |
| `ptax_media` | float64 | Dólar médio do ano (R$/US$) | Média dos dias úteis |
| `ptax_fim_ano` | float64 | Dólar no último dia útil do ano (R$/US$) | Último valor do ano |
| `ptax_variacao_ano_pct` | float64 | Variação cambial no ano (%) | (PTAX final ÷ PTAX inicial − 1) × 100 |
| `juro_real_pct` | float64 | Juro real ex-post (% a.a.) | Equação de Fisher: [(1 + Selic média) ÷ (1 + IPCA do ano) − 1] × 100 |

## 5. `fato_cotacoes`

Cotações diárias das 9 ações. **Fonte:** B3 via yfinance (sufixo `.SA`).

| Campo | Tipo | Significado | Regra |
|---|---|---|---|
| `ticker` | str | Código da ação | Chave para `dim_empresa` |
| `data` | datetime64 | Data do pregão | 1.241 pregões por ativo |
| `abertura` | float64 | Preço de abertura (R$) | Nominal |
| `maxima` | float64 | Preço máximo do dia (R$) | Nominal |
| `minima` | float64 | Preço mínimo do dia (R$) | Nominal |
| `fechamento` | float64 | Preço de fechamento (R$) | Nominal; usado no volume financeiro |
| `fechamento_ajustado` | float64 | Fechamento ajustado por proventos e desdobramentos (R$) | Ajuste da fonte; usado em retornos e Base 100 |
| `volume_acoes` | int64 | Quantidade de ações negociadas no dia | — |
| `volume_financeiro` | float64 | Valor negociado no dia (R$) — estimativa | `fechamento` × `volume_acoes` |

## 6. `fato_mercado_anual`

Desempenho anual das ações. **Fonte:** derivada de `fato_cotacoes`.

| Campo | Tipo | Significado | Regra |
|---|---|---|---|
| `ticker` | str | Código da ação | — |
| `ano` | int64 | Ano de referência | — |
| `preco_fim` | float64 | Fechamento ajustado do último pregão do ano (R$) | — |
| `volume_financeiro_medio` | float64 | Volume financeiro médio diário (R$) | Média dos pregões do ano |
| `pregoes` | int64 | Número de pregões no ano | Contagem |
| `retorno_anual` | float64 | Retorno total da ação no ano (fração) | Preço final ÷ preço final do ano anterior − 1 (em 2019, base = 1º pregão do ano) |
| `volatilidade_anual` | float64 | Risco: volatilidade anualizada (fração) | Desvio-padrão dos retornos diários × √252 |

## 7. `fato_contabil`

Contas contábeis no formato longo. **Fonte:** CVM — DFP consolidada (DRE, BPA, BPP).

| Campo | Tipo | Significado | Regra |
|---|---|---|---|
| `ticker` | str | Código da ação | Associado pelo CNPJ |
| `cnpj` | str | CNPJ da companhia | — |
| `empresa` | str | Razão social na CVM | `DENOM_CIA` |
| `ano` | int64 | Exercício fiscal | Ano de `DT_FIM_EXERC` |
| `demonstrativo` | str | Demonstrativo de origem | `DRE`, `BPA` (Ativo) ou `BPP` (Passivo e PL) |
| `cd_conta` | str | Código da conta no plano padronizado da CVM | Lido como texto para preservar códigos como `3.10` |
| `ds_conta` | str | Descrição da conta | — |
| `valor_reais` | float64 | Valor da conta (R$) | `VL_CONTA` × 1.000; apenas exercício "ÚLTIMO" e versão mais recente |

## 8. `fato_indicadores_contabeis`

Contas selecionadas e indicadores por empresa e exercício. **Fonte:** derivada de `fato_contabil`.

### 8.1 Contas extraídas

| Campo | Tipo | Significado | Código CVM (não financeiras) | Código CVM (Itaú) |
|---|---|---|---|---|
| `receita_liquida` | float64 | Receita líquida de vendas e serviços (R$) | 3.01 | 3.01 (receitas da intermediação financeira) |
| `resultado_bruto` | float64 | Lucro bruto (R$) | 3.03 | N/A |
| `ebit` | float64 | Resultado antes do resultado financeiro e dos tributos (R$) | 3.05 | N/A |
| `despesas_financeiras` | float64 | Despesas financeiras — juros e encargos (R$, negativo) | 3.06.02 | N/A |
| `lucro_liquido` | float64 | Lucro líquido consolidado do período (R$) | 3.11 | 3.09 |
| `ativo_total` | float64 | Ativo total (R$) | 1 | 1 |
| `ativo_circulante` | float64 | Ativo de curto prazo (R$) | 1.01 | N/A |
| `caixa` | float64 | Caixa e equivalentes de caixa (R$) | 1.01.01 | N/A |
| `aplicacoes_financeiras` | float64 | Aplicações financeiras de curto prazo (R$) | 1.01.02 | N/A |
| `passivo_circulante` | float64 | Passivo de curto prazo (R$) | 2.01 | N/A |
| `emprestimos_cp` | float64 | Empréstimos e financiamentos de curto prazo (R$) | 2.01.04 | N/A |
| `emprestimos_lp` | float64 | Empréstimos e financiamentos de longo prazo (R$) | 2.02.01 | N/A |
| `patrimonio_liquido` | float64 | Patrimônio líquido consolidado (R$) | 2.03 | 2.08 |

### 8.2 Indicadores calculados

| Campo | Tipo | Significado financeiro | Regra de cálculo |
|---|---|---|---|
| `divida_bruta` | float64 | Endividamento total com empréstimos (R$) | `emprestimos_cp` + `emprestimos_lp` |
| `caixa_total` | float64 | Recursos disponíveis no curto prazo (R$) | `caixa` + `aplicacoes_financeiras` |
| `divida_liquida` | float64 | Dívida descontado o caixa (R$); negativo = caixa líquido | `divida_bruta` − `caixa_total` |
| `margem_bruta` | float64 | Quanto sobra da receita após o custo dos produtos (fração) | `resultado_bruto` ÷ `receita_liquida` |
| `margem_ebit` | float64 | Eficiência operacional (fração) | `ebit` ÷ `receita_liquida` |
| `margem_liquida` | float64 | Quanto da receita vira lucro (fração); N/A para o Itaú | `lucro_liquido` ÷ `receita_liquida` |
| `roe` | float64 | Retorno sobre o patrimônio do acionista (fração) | `lucro_liquido` ÷ `patrimonio_liquido` (PL do fim do exercício) |
| `liquidez_corrente` | float64 | Capacidade de pagar dívidas de curto prazo (vezes) | `ativo_circulante` ÷ `passivo_circulante` |
| `divida_liquida_pl` | float64 | Alavancagem financeira (vezes) | `divida_liquida` ÷ `patrimonio_liquido` |
| `crescimento_receita` | float64 | Variação da receita frente ao ano anterior (fração); vazio em 2019 | `receita_liquida` ÷ `receita_liquida` do ano anterior − 1 |

## 9. `fato_anual_integrado`

**Tabela central da aplicação:** 45 linhas (9 empresas × 5 exercícios) × 41 colunas, unindo as três fontes. Integridade dos JOINs garantida com `validate` (`one_to_one` / `many_to_one`).

| Bloco | Colunas | Origem |
|---|---|---|
| Identificação (5) | `ticker`, `empresa`, `setor`, `tipo`, `ano` | `dim_empresa` |
| Contábil (23) | as 13 contas e os 10 indicadores das seções 8.1 e 8.2 | CVM |
| Mercado (5) | `preco_fim`, `volume_financeiro_medio`, `pregoes`, `retorno_anual`, `volatilidade_anual` | B3 |
| Macroeconomia (8) | `selic_media_pct`, `selic_fim_ano_pct`, `ipca_ano_pct`, `ipca_12m_dez_pct`, `ptax_media`, `ptax_fim_ano`, `ptax_variacao_ano_pct`, `juro_real_pct` | BACEN |

Os campos têm o mesmo tipo, significado e regra descritos nas seções 4, 6 e 8.

**Valores vazios esperados:** 5 por coluna nos indicadores não aplicáveis ao Itaú; 9 em `crescimento_receita` (exercício de 2019, sem ano anterior).

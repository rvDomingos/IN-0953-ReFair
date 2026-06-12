# Organização de `documents/datasets/`

Dados do experimento ReFAIR × UStAI, separados por finalidade. Os **scripts** ficam em `documents/scripts/`.

## 📁 `essenciais/` — fontes e resultados canônicos
| Arquivo | O que é |
|---|---|
| `ustai-gabarito-completo` | **Ground truth** dos 3 estágios (domínio, ML task, atributos sensíveis) |
| `ustai-stories-para-refair` | **Entrada** do batch (texto original das 1260 US) |
| `equivalencia-ustai-synthetic` | Equivalência UStAI↔Synthetic (fonte do gabarito) |
| `refair-resultados-oficial` | **Rodada OFICIAL** (ReFAIR sem patch) — base dos números do relatório |
| `refair-resultados` | Rodada com patch (sub-experimento; usada na validação Windows) |

## 📁 `analises/` — datasets de prova/análise (gerados)
| Arquivo | O que é |
|---|---|
| `metricas-estagio1-por-dominio` · `metricas-estagio2-por-label` · `metricas-por-llm` | Métricas formais (F1-Score etc.) |
| `erro-end-to-end-causa` | Causa da falha por US (domínio/task/mapping) |
| `ustai-comparacao-refair-vs-gabarito` | Comparação 1-a-1, estágio a estágio |
| `ustai-matriz-confusao-dominio` | Matriz de confusão de domínio |
| `ustai-resumo-por-abstract` | Resumo por abstract (A1–A42) |
| `ustai-impacto-patch-glove` | ML task sem patch × com patch |
| `ustai-features-3fontes` | Features: ReFAIR × proxy × ontologia |
| `fabris-ttl-vs-refair-csv-dominios` | Proveniência Fabris (.ttl) × tabela do ReFAIR |
| `exemplos-us-por-dominio` | 1 US de exemplo por domínio |

## 📁 `referencia/` — material de origem
PDFs do dataset (`Synthetic-User-Stories.pdf`, `UStAI-annotated_V2.pdf`).

## 🐍 Scripts (`documents/scripts/`)
`calcular_metricas.py` · `analise_raiz_xgboost.py` · `comparar_plataformas.py` · `prototipo_embeddings.py` · `csv_para_xlsx.py`
Resolvem os caminhos sozinhos (leem de `essenciais/`, escrevem em `analises/`) — rodam de qualquer diretório.
Runners do ReFAIR (`run_refair_batch.py`, `gerar_resultado_oficial.py`) ficam em `ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/`.

> Documento mestre: [../RELATORIO-GERAL-experimento.md](../RELATORIO-GERAL-experimento.md).

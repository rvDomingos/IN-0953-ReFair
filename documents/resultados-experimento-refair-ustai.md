# Avaliação do ReFAIR sobre o dataset UStAI — Resultados

> Experimento: rodar a pipeline do ReFAIR (detecção de domínio → ML task → atributos
> sensíveis) sobre as user stories do UStAI e comparar, estágio a estágio, com um
> gabarito construído manualmente. Objetivo: medir o quanto o ReFAIR acerta em user
> stories **reais** e identificar onde/por que ele falha.

---

## 1. Objetivo

O ReFAIR recomenda **atributos sensíveis** (para fairness) a partir de uma user story,
em 3 estágios encadeados:

```
User Story ──(BERT+XGBoost)──► DOMÍNIO ──(GloVe+LinearSVC)──► ML TASK ──(domínio∩tarefa)──► ATRIBUTOS SENSÍVEIS
```

A pergunta de pesquisa: **o ReFAIR generaliza para user stories reais (UStAI), ou só
funciona no conjunto sintético em que foi treinado?**

---

## 2. Metodologia

### 2.1 Dados
- **UStAI:** 42 abstracts × 3 LLMs (Gemini 1.5, Llama 3.1 70b, O1-mini) × 10 user
  stories = **1260 user stories** (1258 após remover 2 ids duplicados).
- **Gabarito (ground truth) — 3 estágios**, em `documents/datasets/ustai-gabarito-completo.csv`:
  - *Domínio* (`equivalent_domain`) e *ML task* (`equivalent_ml_task_labels`):
    classificação manual por abstract, na taxonomia do ReFAIR (re-engenharia da
    ontologia do Fabris, 34 domínios), com nível de confiança (High/Medium/Low).
  - *Atributos sensíveis* (`sensitive_features_esperados`): derivados replicando a
    própria função `feature_extraction` do ReFAIR (interseção
    `features_da_tarefa ∩ features_do_domínio`), a partir do domínio + ML task do gabarito.

### 2.2 Execução do ReFAIR
- Pipeline rodada de verdade nas 1260 stories via `run_refair_batch.py`, gerando
  `documents/datasets/refair-resultados.csv`.
- **Ambiente reproduzido nas versões exatas** do `requirements.txt` (torch 2.0.0,
  transformers 4.27.1, xgboost 1.7.4, scikit-learn 1.2.2, gensim 4.3.1) →
  predições determinísticas, equivalentes ao ambiente original.

### 2.3 Ajustes aplicados
- **Patch do GloVe** no `getMLTask`: normaliza os tokens só na busca do GloVe
  (minúsculo, sem acento, sem pontuação; `real-time` → `real time`), elevando a
  cobertura de tokens de **78,8% → 99,2%**. Não altera o input do BERT (estágio 1).
- **Normalização de typos do próprio treino do ReFAIR** na comparação:
  `Demograpy`→Demography, `Psycology`→Psychology (senão contariam como erro indevido).

---

## 3. Resultados

### 3.1 Domínio (estágio 1) — acerto de **9,4%** (118/1258)

| Confiança do gabarito | Acerto |
|---|---|
| High   | 14,6% (109/748) |
| Medium | 1,5% (5/330) |
| Low    | 2,2% (4/180) |

**Teste decisivo (descarta bug):** o `getDomain` acerta **100% (200/200)** nas stories
de **treino** (sintéticas), mas **9,4%** no UStAI. Como acerta perfeitamente o treino,
ficam descartados bug de mapeamento de índice ou de carregamento dos modelos.

➡️ **Conclusão: o detector de domínio está superajustado (overfit) ao conjunto
sintético e não generaliza para user stories reais.**

#### Efeito "Biology" — top confusões (gabarito → ReFair)
O modelo colapsa domínios distintos em poucas classes dominantes
(**354 das 1258 stories foram para "Biology"**):

| Nº | gabarito → ReFair |
|---|---|
| 36 | Transportation → Biology |
| 34 | Economics → Biology |
| 32 | Information Systems → Biology |
| 27 | Psychology → Health |
| 27 | Health → Biology |
| 24 | Information Systems → Medicine |
| 22 | Psychology → Biology |
| 22 | Finance & Marketing → Biology |

Matriz completa em `documents/datasets/ustai-matriz-confusao-dominio.csv`.

### 3.2 ML task (estágio 2) — ReFAIR **zerou 42,5%** (535/1258)
- O gabarito tinha labels nas 1258 stories; o ReFAIR não produziu nenhuma ML task em
  535 delas.
- Das 723 comparáveis (não-vazias dos dois lados), **53,8%** têm overlap com o gabarito.
- Causa: o filtro `domínio→tarefa` (`getMLTask`) só mantém tarefas registradas para o
  domínio previsto. Como 8 domínios aceitam **uma única** tarefa, e o domínio em si já
  vem errado (§3.1), a interseção fica vazia → sem ML task.

### 3.3 Atributos sensíveis (estágio 3) — match exato **2,1%**
| | |
|---|---|
| Match exato | 2,1% (26/1258) |
| Overlap parcial | 32,4% (407/1258) |
| Ambos vazios | 4,0% (50/1258) |

Consequência direta da **propagação de erro**: domínio errado (§3.1) → ML task vazia
ou errada (§3.2) → atributos sensíveis errados.

### 3.4 Impacto do patch do GloVe
| | ML task vazia |
|---|---|
| SEM patch | 557 (44,3%) |
| COM patch | 535 (42,5%) |
| resgatadas (vazia→preenchida) | 162 |

O patch melhora a cobertura do GloVe (78,8%→99,2%) e **resgata 162 stories**, mas o
ganho **líquido é pequeno** (−22): mudar o vetor muda a predição, e ~140 stories que
eram preenchidas passam a cair fora do filtro do domínio. **Confirma que o gargalo
dominante não é o GloVe (estágio 2), e sim o domínio errado + o filtro (estágios 1–2).**

### 3.5 Causa-raiz: o detector de domínio decora o token na posição 3

A análise da árvore do XGBoost ([analise-raiz-xgboost.md](analise-raiz-xgboost.md)) mostra **por que** o
estágio 1 desaba. O `getDomain` passa pro XGBoost os **`input_ids`** do BERT — os **IDs de token por
posição**, **não** os embeddings. As 100 features são "qual token está na posição 0, 1, …, 99". A
**posição 3 (a palavra do papel) é a raiz de 2438 das 5092 árvores**.

| | Treino (sintético) | UStAI (real) |
|---|---|---|
| Papel na posição 3 | **é o nome do domínio** (Cardiology→"card", Transportation→"transportation") | papéis **genéricos** ("researcher", "data", "developer") |
| Pureza da posição 3 (papel → domínio) | **93,0%** | **47,5%** |
| Papel nunca visto no treino | — | **51,4%** das US |
| Acerto do "mapa decorado" no UStAI (papéis vistos) | — | **21,4%** |

> O modelo aprende a **forma** (qual token, em qual posição), não o **conteúdo** (qual domínio). No molde
> rígido do sintético o papel nomeia o domínio (decorável, 100%); no UStAI metade dos papéis é nova e o
> resto é ambíguo (9,4%). **Essa é a raiz dos 3 sintomas** — domínio errado, ML task vazia e features erradas.

---

## 4. Conclusão

1. **Causa-raiz — memoriza forma, não significado:** o detector de domínio é um XGBoost sobre
   `input_ids` posicionais; ele decora o token da posição 3 (o papel), que no sintético é o nome do
   domínio. Por isso 100% no treino e **9,4% no UStAI** (51,4% dos papéis nunca vistos). Detalhe e
   prova em [analise-raiz-xgboost.md](analise-raiz-xgboost.md).
2. **Propagação de erro:** como os 3 estágios são encadeados, o erro de domínio (90,6% das falhas)
   derruba a ML task (42,5% vazias) e, por consequência, os atributos sensíveis (2,1% exato) —
   justamente a saída útil da ferramenta.
3. **O patch do GloVe ajuda pouco** porque ataca um sintoma do estágio 2; o problema de
   raiz está no estágio 1 (domínio).

---

## 5. Artefatos gerados (`documents/datasets/`)

| Arquivo | Conteúdo |
|---|---|
| `ustai-gabarito-completo.csv/.xlsx` | Gabarito dos 3 estágios (domínio, ML task, atributos sensíveis) |
| `refair-resultados.csv/.xlsx` | Saída crua do ReFAIR por story |
| `ustai-comparacao-refair-vs-gabarito.csv/.xlsx` | Comparação 1-a-1, estágio a estágio |
| `ustai-matriz-confusao-dominio.csv/.xlsx` | Matriz de confusão de domínio (gabarito × ReFAIR) |
| `ustai-resumo-por-abstract.csv/.xlsx` | Resumo por abstract (A1–A42) |
| `ustai-impacto-patch-glove.csv/.xlsx` | ML task sem patch × com patch, por story |
| `refair-resultados-oficial.csv/.xlsx` | Rodada **oficial** (sem patch) — base dos números |
| `metricas-*.csv/.xlsx` | Métricas formais (estágio 1, estágio 2, por LLM, causa de erro) |

Docs de apoio: [metricas-formais-item-a.md](metricas-formais-item-a.md) · [analise-raiz-xgboost.md](analise-raiz-xgboost.md) · [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md)

Código: `run_refair_batch.py` + `gerar_resultado_oficial.py` (runners) · `calcular_metricas.py` · `analise_raiz_xgboost.py` · `comparar_plataformas.py` · patch em `REFAIR.py` (`_norm_token`).

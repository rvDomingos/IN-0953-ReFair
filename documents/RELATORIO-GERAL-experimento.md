# Relatório geral — Avaliação de validade externa do ReFAIR no UStAI

**Data:** 2026-06-12
**Projeto:** IN-0953-ReFair
**O que este doc é:** a **explicação final consolidada** do experimento, com rigor técnico — método, plataformas, resultados, causa-raiz (re-verificada) e extensão. Reúne e substitui a leitura dispersa dos docs de apoio (listados no fim).

---

## 0. Sumário executivo

Avaliamos o **ReFAIR** (recomendador de *sensitive features* para fairness, ICSE'24) em **user stories de contexto real** (dataset **UStAI**), como teste de **validade externa** — rodando a ferramenta **congelada, sem retreino**. O ReFAIR, que reporta F1 = 0,98 em domínio no seu conjunto sintético, **desaba para F1 = 0,125 (9,4% de acerto)** no UStAI. Abrindo a caixa-preta, **diagnosticamos a causa**: o detector de domínio aprende **padrões posicionais de token** (o molde "As a [papel], I want…"), não o **significado** da story. Um **estudo de ablação** (trocar a representação por embeddings) **quadruplica** o acerto (9,4% → 37%), confirmando a representação como causa-raiz.

| | Domínio (estágio 1) | ML task (estágio 2) | Features (estágio 3) |
|---|---|---|---|
| **F1-Score no UStAI** | **0,125** | 0,127 | 2,1% match exato |
| Referência *in-distribution* (paper) | 0,98 | 0,90 | — |
| ML task vazia | — | **42,5%** | — |

**Causa das falhas end-to-end:** 90,6% nascem no estágio 1 (domínio); 7,3% no estágio 2; 2,1% no mapping.

---

## 1. Problema, lacuna e perguntas de pesquisa

O ReFAIR recebe uma user story e recomenda **atributos sensíveis** a monitorar (idade, gênero, raça…), em 3 estágios encadeados:

```
US ─(BERT+XGBoost)→ DOMÍNIO ─(GloVe+LinearSVC)→ ML TASK ─(domínio∩tarefa)→ SENSITIVE FEATURES
```

**Lacuna:** o ReFAIR foi validado **só em user stories sintéticas**, geradas da própria ontologia, num molde fixo (template de Cohn). Os **próprios autores** declaram como limitação a dependência do template e dos dados sintéticos. **Nunca foi testado em user stories de contexto real.**

> **Nota metodológica (importante):** isto **não é "replicação"**. Replicação reproduziria os números do paper com o método original. Aqui fazemos **validade externa** (rodar a ferramenta inalterada em dados novos) + uma **extensão** (§7). A replicação da *alegação* do paper foi confirmada pelo sanity de 100% no treino (§4.1).

- **RQ1 (validade externa):** o ReFAIR generaliza para user stories de outra origem?
- **RQ2 (extensão):** a falha pode ser corrigida trocando a representação de entrada?

---

## 2. Materiais

| Material | Descrição |
|---|---|
| **UStAI** | 42 abstracts reais × 3 LLMs (Gemini 1.5, Llama 3.1 70b, O1-mini) × 10 US = **1260 user stories** (1258 após 2 ids duplicados). |
| **Ground truth** | Equivalência manual (`ustai-gabarito-completo.csv`): `equivalent_domain`, `equivalent_ml_task_labels`, `domain_confidence` + estágio 3 derivado da lógica do `feature_extraction`. |
| **ReFAIR** | Modelos do paper (XGBoost, LinearSVC, GloVe, BERT) — usados **congelados**. |
| **Taxonomia** | 34 domínios (ontologia de Fabris re-engenheirada) + 25 ML tasks (Duran-Silva). |

---

## 3. Método e plataformas (reprodutibilidade)

1. **Execução congelada:** as 1260 US passam pelo ReFAIR sem retreino (`run_refair_batch.py`). Princípio inegociável: UStAI é **só teste**.
2. **Ambiente nas versões exatas** do `requirements.txt` (torch 2.0.0, transformers 4.27.1, xgboost 1.7.4, sklearn 1.2.2, gensim 4.3.1) → predições determinísticas.
3. **Rodada oficial = sem patch.** O patch do GloVe (melhoria do estágio 2) é sub-experimento à parte; os números oficiais vêm do ReFAIR original (`refair-resultados-oficial.csv`).
4. **Métricas por estágio** (`calcular_metricas.py`): F1-Score, Hamming loss, Subset accuracy, precisão/revocação, estratificação por LLM e por confiança.

### 3.1 Validação cross-platform (macOS × Windows)

A inferência do ReFAIR é **determinística** (modelos congelados, sem aleatoriedade). Rodamos em **macOS/Py3.11** e **Windows/Py3.9** (`comparar_plataformas.py`): **predições idênticas** (0 divergências de domínio/ML task).

**Por quê idêntico:** o detector de domínio recebe **`input_ids` (inteiros)** → XGBoost (árvores) = **zero ponto flutuante** → bit-idêntico entre SO. O estágio 2 (GloVe→LinearSVC) tem decisão linear bem separada, robusta a arredondamento. → **Reprodutibilidade confirmada**; remove a ameaça de validade do ambiente.

---

## 4. Resultados

### 4.1 Estágio 1 — Domínio
Accuracy **9,4%** · **F1-Score 0,125** (sobre os 25 domínios cobertos; 9 dos 34 não têm US no UStAI). Sanity: o modelo acerta **100% no próprio treino** → descarta bug; é generalização que falha.

**Efeito de colapso:** 354/1258 US viram "Biology". Top confusões: Transportation→Biology (36), Economics→Biology (34), Information Systems→Biology (32)…

### 4.2 Estágio 2 — ML task (multi-label)
**F1-Score 0,127** · Hamming loss 0,222 · Subset accuracy 0,037 · **42,5% vazias**. O filtro domínio→tarefa, alimentado por um domínio errado e listas curtas (8 domínios aceitam 1 tarefa só), zera a maioria.

### 4.3 Estágio 3 — Sensitive features
Match exato **2,1%** · overlap parcial 32,4%. Consequência da propagação (domínio errado → features do domínio errado).

### 4.4 Por LLM
Ruim nos três (Llama levemente menos pior: acc 0,115 vs Gemini 0,081 / O1 0,086) → o problema é do ReFAIR, não de um gerador.

---

## 5. Causa-raiz (re-verificada com rigor)

O `getDomain` passa pro XGBoost os **`input_ids` do BERT** — os **IDs de token por posição**, **não** os embeddings. As 100 features são "qual token está na posição 0…99". Três provas **independentes e convergentes**:

**(a) A árvore.** A posição 3 (a palavra do papel em "As a [papel]…") é raiz de **2438 das 5092 árvores**; as posições 2-7 (o molde de abertura) concentram **78,4% do ganho** total.

**(b) Treino × UStAI.** No sintético o papel **é** o nome do domínio (Cardiology→"card", Transportation→"transportation"; pureza **93,0%**); no UStAI são papéis genéricos ("researcher", "data", "developer"; pureza **47,5%**), e **51,4% dos papéis nunca apareceram no treino**.

**(c) Importância por permutação (causal) — a prova definitiva.** Embaralhando colunas e medindo o colapso da acurácia (que é 100% no treino):

| Intervenção | Acurácia | Interpretação |
|---|---|---|
| baseline (nada) | 100,0% | — |
| embaralhar **só a posição 3** (papel) | **25,6%** | depende fortemente dela |
| embaralhar **posições 2-7** (molde) | **3,4%** | quase toda a decisão vem do molde |
| embaralhar **posição 40** (conteúdo) | 100,0% | conteúdo é **ignorado** |
| embaralhar **posições 40-60** (corpo) | 99,7% | conteúdo é **ignorado** |

> **Conclusão causal:** o modelo **ignora o conteúdo** da story e decide pelo **molde de abertura** ("As a [papel], I want"). No sintético o papel nomeia o domínio (decora → 100%); no UStAI o papel é novo/genérico → desaba (9,4%). **É a raiz dos 3 sintomas** (domínio errado → ML task vazia → features erradas). Reproduzível em [analise_raiz_xgboost.py](scripts/analise_raiz_xgboost.py).

---

## 6. Conclusão (RQ1)

O ReFAIR **não generaliza** para user stories de contexto real. A causa não é dificuldade intrínseca do UStAI, e sim uma **fragilidade de representação**: o detector de domínio aprende **forma** (token por posição), não **conteúdo** (significado). O erro **se propaga** pelos 3 estágios (90,6% das falhas nascem no estágio 1).

---

## 7. Extensão — corrigindo a representação (RQ2)

**Estudo de ablação controlado:** trocamos **uma única variável** — a entrada `input_ids` → **embeddings médios do BERT** — treinando no sintético e testando no UStAI *held-out* (`prototipo_embeddings.py`):

| Modelo | Acerto (UStAI) | F1-Score |
|---|---|---|
| ReFAIR original (XGBoost sobre `input_ids`) | 9,4% | 0,125 |
| **Protótipo (BERT mean-pool + LogReg)** | **37,0%** | **0,386** |

**4× melhor**, mudando só a representação. Isso **isola a representação como causa** (refuta "o UStAI é difícil demais") e indica o caminho do conserto. É **limite inferior** (BERT cru, 100 US/domínio); sentence-transformers + data augmentation + fine-tune/LLM tendem a ir além. Roteiro completo em [roadmap-80-porcento.md](roadmap-80-porcento.md).

---

## 8. Ameaças à validade

- Ground truth é a **própria equivalência** (não *gold standard* independente) → mitigar com **κ** + revisão do professor.
- **Domínio por abstract** (granularidade grossa).
- **Cobertura parcial:** 25 dos 34 domínios.
- **UStAI também é sintético** (gerado por LLM) → generalização comprovada é para outra **origem sintética**, não para US humanas.
- **Estágio 3 sem ground truth humano** ([estagio3-passo-a-passo.md](estagio3-passo-a-passo.md)).

---

## 9. O que falta

Estado em [o-que-falta.md](o-que-falta.md). Núcleo quantitativo fechado (métricas + rodada oficial + cross-platform). Falta: anotação humana do estágio 3 + painel + κ, limiar com o professor, e o texto final.

---

## 10. Índice de artefatos

**Dados/resultados (`documents/datasets/`):** `ustai-gabarito-completo`, `refair-resultados-oficial` (oficial), `refair-resultados` (com patch), `ustai-comparacao-refair-vs-gabarito`, `ustai-matriz-confusao-dominio`, `ustai-resumo-por-abstract`, `ustai-impacto-patch-glove`, `ustai-features-3fontes`, `fabris-ttl-vs-refair-csv-dominios`, `metricas-*`, `erro-end-to-end-causa`.

**Scripts:** `run_refair_batch.py`, `gerar_resultado_oficial.py` (refair-server) · `calcular_metricas.py`, `analise_raiz_xgboost.py`, `comparar_plataformas.py`, `prototipo_embeddings.py`, `csv_para_xlsx.py` (datasets).

**Docs de apoio:** [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md) · [metricas-formais-item-a.md](metricas-formais-item-a.md) · [analise-raiz-xgboost.md](analise-raiz-xgboost.md) · [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md) · [roadmap-80-porcento.md](roadmap-80-porcento.md) · [como-rodar-no-windows.md](como-rodar-no-windows.md) · [estagio3-passo-a-passo.md](estagio3-passo-a-passo.md) · [resumo-features-fabris-3fontes.md](resumo-features-fabris-3fontes.md) · [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md) · [plano-de-acao-refair.md](plano-de-acao-refair.md) · [o-que-falta.md](o-que-falta.md)

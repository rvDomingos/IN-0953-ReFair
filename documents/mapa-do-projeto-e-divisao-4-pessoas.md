# Mapa do projeto + divisão para 4 pessoas — IN-0953-ReFAIR

**Data:** 2026-06-15
**O que este doc é:** (1) o **mapa em bullets** de tudo que foi feito, (2) o que falta, e (3) a **divisão para 4 pessoas** (o que cada um domina/apresenta + as tarefas em aberto que ficam com cada um).
**Relatório final:** [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md) · **Índice:** [README.md](README.md)

> **Projeto em uma frase:** avaliamos o **ReFAIR** (recomendador de atributos sensíveis, ICSE'24) em user stories de contexto real (**UStAI**) — ele **colapsa** (F1 0,98 → 0,125), **descobrimos por quê** (decora a forma do token, não o significado) e **mostramos o conserto** (embeddings no domínio + reforma do ML task).

---

## PARTE 1 — Tudo que foi feito ✅

### 🏗️ Infra e reprodutibilidade
- ReFAIR colocado pra rodar: **CLI**, **app web** (Flask + Vue) e **Docker** (buildado e rodando).
- Ambiente nas **versões exatas** (torch 2.0.0, transformers 4.27.1, xgboost 1.7.4, sklearn 1.2.2, gensim 4.3.1).
- **Determinismo** confirmado: predições **idênticas** em macOS e Windows (inferência sem aleatoriedade).
- Runner em lote (`run_refair_batch.py`) processa as 1260 US de uma vez.

### 📊 Dataset e gabarito (ground truth)
- **Equivalência UStAI ↔ Synthetic** dos 34 domínios do ReFAIR (25 cobertos pelo UStAI, 9 sem US).
- **Gabarito manual dos 3 estágios** (domínio, ML task, atributos sensíveis) com nível de confiança.
- Divisão dos **179 roles** entre 4 pessoas para a anotação.
- **UStAI:** 1260 US = 42 abstracts reais × 3 LLMs (Gemini/Llama/O1) × 10 (1258 após 2 ids duplicados).

### 🔬 Experimento RQ1 — "o ReFAIR não generaliza"
- ReFAIR rodado **congelado** (sem retreino) nas 1260 US.
- **Métricas formais:** domínio **F1 0,125 (9,4%)**, ML task **F1 0,127**, features **2,1%** match exato (paper: 0,98 / 0,90).
- **Matriz de confusão:** colapso — **354/1258** US viram "Biology" (Transportation→Biology 36, Economics 34, Information Systems 32…).
- **Estratificação por LLM:** ruim nos três → o problema é do ReFAIR, não do gerador.
- **Decomposição end-to-end:** **90,6%** das falhas nascem no estágio 1 (domínio).
- Decisão metodológica: **rodada oficial = ReFAIR sem patch**; patch do GloVe é sub-experimento (não muda o veredito).

### 🧠 Causa-raiz (a parte forte)
- O `getDomain` entrega ao XGBoost os **`input_ids`** (token por posição), **não** embeddings → a etapa de significado do BERT **nunca acontece**.
- **Dump da árvore:** a **posição 3** (a palavra do papel) é raiz de **2438/5092** árvores.
- **Treino × UStAI:** no sintético o papel **é** o nome do domínio (pureza 93%); no UStAI é genérico (47%) e **51% dos papéis nunca foram vistos**.
- **Prova causal por permutação:** embaralhar a posição 3 → 99,5% **→ 25,3%**; embaralhar o **conteúdo** → 99,4% (**não muda**). O modelo **ignora o conteúdo e decide pelo molde**.
- Validação no **TTL do Fabris**: o mapa domínio→atributo está correto → o erro está confinado ao estágio 1.

### 🛠️ Extensão RQ2 — "dá pra consertar"
- **Estágio 1 (domínio):** `input_ids` → **embeddings do BERT** → **9,4% → 37,0%** (ablação limpa, 1 variável; parou de colapsar em Biology: 354→64).
- **Estágio 2 (ML task, "config D"):** **filtro soft** + classificador **OneVsRest** + **limiar** (GloVe, não embeddings) → **F1 0,132 → 0,283**, não-vazio 54% → 99,8%.
- **Ablação (isola cada ganho):** filtro soft **+0,11**, classificador +0,05, embeddings **−0,03** (pioram o ML task → removidos).
- **Vazamento corrigido:** limiar do ML task sintonizado num **split do sintético**, não no UStAI.
- Tudo **integrado** no `refair-server` (originais preservados como `_xgb`/`_glove`) e **validado no Docker**.

### ⚖️ Validade e entrega
- **[ameacas-a-validade.md](ameacas-a-validade.md):** 4 categorias (construto/interna/externa/conclusão) + status; **sem ameaças internas abertas**.
- **Desbalanceamento tratado:** acurácia ≈ macro (9,4 vs 11,1; 37,0 vs 37,5) → não distorce.
- **Gabarito colorido** por domínio (verde=correto / vermelho=errado).
- **Relatório final**, **índice de docs** e **apresentação (3 pessoas)** escritos.

---

## PARTE 2 — O que falta 🔴

- **Estágio 3:** anotação **humana** de atributos sensíveis (amostra ~100–150 US) + **painel de 3–4 avaliadores**.
- **Cohen's κ** nos estágios 1 e 2 (concordância entre anotadores) → mitiga "o gabarito é nosso".
- **Acordar o limiar "funciona/não funciona" com o professor** (antes de concluir).
- **McNemar + IC** nas comparações (original × extensão) — *recomendado*.
- **Investigar os 2 ids duplicados.**
- **Commit** final.

---

## PARTE 3 — Divisão para 4 pessoas

Cada pessoa **domina/apresenta** um bloco coerente **e** fica responsável pelas tarefas em aberto daquele bloco.

### 👤 Pessoa 1 — Contexto, ReFAIR e dataset
- **Apresenta:** o que é o ReFAIR (3 estágios, 2 classificadores + Fabris), a ontologia Fabris, o UStAI, como o gabarito foi construído.
- **Domina:** [refair-vetorizacao-e-defeito-do-parser.md](refair-vetorizacao-e-defeito-do-parser.md) (seção do que é o ReFAIR) · [equivalencia-dominios-ustai-synthetic.md](equivalencia-dominios-ustai-synthetic.md).
- **Tarefa aberta:** investigar e declarar os **2 ids duplicados**.

### 👤 Pessoa 2 — Experimento e métricas (RQ1)
- **Apresenta:** como rodamos (congelado, versões exatas, Docker), os resultados (0,98→0,125, ML task 42,5% vazia, features 2,1%), a **matriz de confusão** (colapso Biology) e o por-LLM.
- **Domina:** [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md) · [metricas-formais-item-a.md](metricas-formais-item-a.md).
- **Tarefa aberta:** rodar **McNemar + IC bootstrap** nas comparações.

### 👤 Pessoa 3 — Causa-raiz (técnico)
- **Apresenta:** tokenização × embeddings, o **defeito do parser**, o dump da árvore, e a **prova por permutação** (99,5%→25,3% vs conteúdo 99,4%).
- **Domina:** [analise-raiz-xgboost.md](analise-raiz-xgboost.md) · [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md) (versão didática).
- **Tarefa aberta:** preparar a figura/gráfico da permutação e do colapso para os slides.

### 👤 Pessoa 4 — Extensão (RQ2) e validade
- **Apresenta:** o conserto (domínio 9,4%→37%, ML task config D 0,283), a **ablação**, e as **ameaças à validade**.
- **Domina:** [passo-a-passo-extensao-37.md](passo-a-passo-extensao-37.md) · [ameacas-a-validade.md](ameacas-a-validade.md) · [roadmap-80-porcento.md](roadmap-80-porcento.md).
- **Tarefas abertas (as mais pesadas — pode puxar ajuda):** anotação humana do **estágio 3** + **painel**, **κ** dos estágios 1/2, e **acordar o limiar com o professor**.

### Cola da divisão
| Pessoa | Bloco | Doc principal | Tarefa aberta |
|---|---|---|---|
| **1** | Contexto / ReFAIR / dataset | equivalência + "o que é o ReFAIR" | 2 ids duplicados |
| **2** | Experimento / métricas (RQ1) | metricas-formais / resultados | McNemar + IC |
| **3** | Causa-raiz (técnico) | analise-raiz-xgboost | figuras dos slides |
| **4** | Extensão (RQ2) + validade | passo-a-passo-extensao + ameaças | estágio 3 + κ + limiar c/ professor |

> **Commit final:** responsável o dono do repositório (combinar entre os 4). Tudo versionável já está pronto; `venv_mac/` e arquivos grandes estão no `.gitignore`.

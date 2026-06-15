# Passo a passo — estender o ReFAIR e alcançar os 37% (4× o original)

**Data:** 2026-06-13
**O que este doc é:** o **passo a passo reproduzível**, a partir do estado atual da `main`, para sair dos **9,4%** do ReFAIR original e chegar aos **37,0% (F1 0,386)** de acerto de domínio no UStAI — trocando a **representação de entrada** (`input_ids` → **embeddings do BERT**). É a **Rota C / RQ2** ([roadmap-80-porcento.md](roadmap-80-porcento.md)).
**Confirmado na `main`:** rodado em 2026-06-13, ~53 s → **37,0%** (sanity de treino 99,8%).

> **Regra de ouro:** **nunca treinar no UStAI.** O UStAI é **só teste** (held-out). Treinamos no sintético do ReFAIR e testamos no UStAI. Quebrar isso invalida o experimento de validade externa.

---

## 0. Por que isso dá os 37%

O detector original entrega ao XGBoost os **`input_ids`** (token por posição) — ele decora "qual papel está na posição 3", não o significado (causa-raiz em [analise-raiz-xgboost.md](analise-raiz-xgboost.md)). A extensão muda **uma única variável**: em vez dos IDs crus, passa os **embeddings do BERT** (vetores de 768-dim que capturam significado). Aí "driver/route/traffic" cai **perto** de Transportation no espaço semântico, e o modelo **transfere** para US escritas de outro jeito.

```
ANTES : US → tokenizar → input_ids (forma)      → XGBoost      → 9,4%
DEPOIS: US → tokenizar → BERT → embeddings (significado) → LogReg → 37,0%
```

É um **estudo de ablação controlado**: mesma fonte de treino, mesma tarefa, mesmo teste — só a representação muda. Por isso o salto **prova** que a representação era a causa.

---

## 1. Pré-requisitos (já estão na `main`)

| Recurso | Caminho |
|---|---|
| Script da extensão | [documents/scripts/prototipo_embeddings.py](scripts/prototipo_embeddings.py) |
| venv com torch/transformers/sklearn | `ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/venv_mac/` |
| Treino (sintético do ReFAIR) | `ReFAIR/3. Source Code/ReFair/datasets/Synthetic User Stories.xlsx` |
| Teste (gabarito UStAI) | `documents/datasets/essenciais/ustai-gabarito-completo.csv` |

Sanity do ambiente (deve imprimir as 3 versões):
```bash
PY="ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/venv_mac/bin/python"
"$PY" -c "import torch,transformers,sklearn;print(torch.__version__,transformers.__version__,sklearn.__version__)"
```

---

## 2. Passo a passo para reproduzir os 37%

### Passo 1 — rodar a extensão
```bash
cd "/Users/romulodomingos/Documents/ProjetoFacul/IN-0953-ReFair"
PY="ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/venv_mac/bin/python"
"$PY" documents/scripts/prototipo_embeddings.py
```

### Passo 2 — saída esperada (real, da `main`)
```
treino: 3400 US, 34 domínios
embeddings do treino...
embeddings do UStAI...
treinando LogReg...
==================== RESULTADO ====================
  ReFAIR original (XGBoost sobre input_ids)  : 9,4%  (F1 0,125)
  PROTÓTIPO (BERT mean-pool + LogReg) no UStAI: 37.0%  (F1 0.386)
  (sanity: acerto no próprio treino = 99.8%)
===================================================
```
Pronto — **9,4% → 37,0%**, ~4×. O sanity de 99,8% no treino confirma que o modelo aprendeu (não é sorte).

---

## 3. O que o script faz por dentro (5 passos)

Tudo em [prototipo_embeddings.py](scripts/prototipo_embeddings.py). Os trechos que importam:

**(1) Carrega o BERT de verdade** (não só o tokenizador — é a etapa que o ReFAIR pulava):
```python
tok   = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased'); model.eval()
```

**(2) Vetoriza: texto → embedding 768-dim (mean-pooling com máscara):**
```python
h = model(**enc).last_hidden_state                  # [B,T,768] vetores por token
m = enc['attention_mask'].unsqueeze(-1).float()
emb = (h * m).sum(1) / m.sum(1).clamp(min=1)         # média só sobre tokens reais
```

**(3) Treino balanceado no sintético (~100 US por domínio, 34 domínios = 3400):**
```python
for d, g in train.groupby('dom'):
    parts.append(g.sample(min(100, len(g)), random_state=42))
```

**(4) UStAI como teste held-out (nunca entra no treino):**
```python
ustai = list(csv.DictReader(open('.../ustai-gabarito-completo.csv', ...)))
us_y  = [nd(r['equivalent_domain']) for r in ustai]    # rótulo verdadeiro
```

**(5) Classificador simples sobre os embeddings + métricas:**
```python
clf = LogisticRegression(max_iter=2000, C=1.0).fit(Xtr, ytr)
pred = clf.predict(Xus)
acc = accuracy_score(us_y, pred); f1 = f1_score(us_y, pred, average='macro', ...)
```

> Note os **seeds fixos** (`random/np/torch = 42`) → resultado **determinístico** e reproduzível.

---

## 4. Integração no ReFAIR — FEITA na `main` (estágio 1)

A extensão **já está integrada** no ReFAIR que você roda (o `refair-server`). Quando você roda a pipeline no UStAI, o `getDomain` agora decide por **significado** (embedding), e o estágio 2 mantém o patch do GloVe.

### Arquivos da integração (refair-server)
| Arquivo | Papel |
|---|---|
| `domain_embed.py` | vetorização BERT mean-pool (mesma lógica no treino e na inferência) |
| `treinar_dominio_embeddings.py` | treina e salva o classificador (rodar 1×) |
| `models/domain_embed_logreg.pkl` | o classificador treinado (207 KB, versionável) |
| `REFAIR.py` | `getDomain` agora usa embeddings; o original virou `getDomain_xgb` (fallback) |

### Como (re)treinar e rodar
```bash
cd "ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server"
venv_mac/bin/python treinar_dominio_embeddings.py          # 1) treina e salva o modelo
venv_mac/bin/python run_refair_batch.py \
    "../../../../../documents/datasets/essenciais/ustai-stories-para-refair.csv" \
    -o refair-resultados-extensao.csv                      # 2) roda o UStAI com a extensão
```

O `getDomain` novo:
```python
def getDomain(user_story):
    emb = embed([user_story])                       # significado (BERT), não input_ids
    return domain_embed_classifier.predict(emb)[0]
```

> O original foi **preservado** como `getDomain_xgb` — os números **oficiais** do estudo continuam vindo dele (e da branch `refair-antigo`); este `getDomain` é a **extensão**.

---

## 4b. Resultado da integração (verificado end-to-end na `main`, 1260 US)

Rodando a pipeline completa no UStAI **com a extensão**:

| Métrica | Original | **Extensão (BERT)** |
|---|---|---|
| **Domínio correto ("US validada")** | 118 (9,4%) | **466 (37,0%)** ↑ **+348 US** |
| Features — match exato | ~2,1% | **9,6%** |
| Features — overlap parcial | ~32,4% | **45,8%** |
| Colapso em "Biology" | 354 US | **64 US** (deixou de colapsar) |

> A detecção de domínio **quadruplicou** e parou de jogar tudo em "Biology" — as previsões se espalham realisticamente (information systems 185, health 148, finance & marketing 109, transportation 97…). A emenda do domínio **propaga** e melhora os atributos sensíveis (features).

---

## 4c. Estágio 2 (ML task) — também estendido (CONFIG D)

Diagnóstico: o classificador de ML task **nunca** previa vazio (0%); quem zerava era o **filtro domínio→tarefa duro** (interseção contra uma lista minúscula → 46% vazias). Config D = três mudanças:

1. **Filtro SOFT** (passo #1): se a interseção com o mapping zerar, mantém a previsão crua (não descarta tudo). **É o lever dominante (+0,11 de F1).**
2. **Classificador `OneVsRest(LogReg)`** no lugar do `LinearSVC LabelPowerset` — dá probabilidade (+0,05 de F1).
3. **Limiar ajustável** (passo #3), **sintonizado num split de validação do sintético** (sem olhar o UStAI → saiu 0,3).
4. **Entrada continua GloVe** (não embeddings) — a ablação (§4d) mostrou que embeddings **pioram** o ML task.

### Arquivos (refair-server)
| Arquivo | Papel |
|---|---|
| `treinar_mltask_glove.py` | treina GloVe-média + OneVsRest, alvo de `Keyword labelled.xlsx`, limiar no sintético |
| `models/mltask_glove_ovr.pkl` | classificador + `MultiLabelBinarizer` + limiar (0,3) |
| `REFAIR.py` | `getMLTask` = GloVe + OneVsRest + filtro soft; o original virou `getMLTask_glove`; `feature_extraction` ignora features `NaN` |

```bash
venv_mac/bin/python treinar_mltask_glove.py     # treina o estágio 2 (1×, ~10s, sem BERT)
```

### Resultado end-to-end (1260 US, estágio 1 + 2) — **sem vazamento**
| Métrica | Original | **Extensão (config D)** |
|---|---|---|
| Domínio correto | 9,4% | **37,0%** |
| **ML task F1** | 0,132 | **0,283** (~2,1×) |
| ML task não-vazio | 54% | **99,8%** |
| Features — match exato | ~2,1% | **20,9%** (~10×) |
| Features — overlap | ~32,4% | **84,3%** |

### 4d. Por que GloVe e não embeddings no estágio 2 (ablação — ameaça #6)
Segurando o domínio constante e variando uma coisa por vez (medido no UStAI/OOD):

| Δ F1 | Mudança |
|---|---|
| **+0,11** | filtro **soft** (lever dominante) |
| +0,05 | classificador LabelPowerset → OneVsRest |
| **−0,03 a −0,04** | GloVe → **embeddings** (pioram!) |

> No ML task o GloVe **generaliza melhor** que o mean-pool do BERT: a tarefa depende de palavras-chave de ação ("classify", "predict", "summarize") que o vetor de palavra capta direto — a média do BERT borra esse sinal. (No **domínio** é o contrário: embedding ganha.) Por isso a arquitetura final é **embeddings no domínio + GloVe no ML task**.
> Ressalva remanescente: o gabarito de ML task tem listas longas/permissivas → limita a precision; vale alinhar a granularidade com o professor.

---

## 5. Como passar de 37% rumo a 80% (próximos degraus)

O 37% é um **limite inferior** (BERT cru, 100 US/domínio). Em ordem de impacto/esforço ([roadmap-80-porcento.md](roadmap-80-porcento.md)):

| Degrau | O que muda | Expectativa |
|---|---|---|
| **a. sentence-transformers** | trocar `bert-base` mean-pool por `all-mpnet-base-v2` / `all-MiniLM-L6-v2` (feitos p/ frase) | passa de 37% |
| **b. data augmentation** | variar os papéis no treino ("driver", "commuter"…), parafrasear, remover o papel | média-alta |
| **c. fine-tune** | treinar um transformer ponta-a-ponta p/ domínio | alta |
| **d. LLM zero/few-shot** | dar story + lista de 34 domínios a um LLM classificar | **alta (provável ≥80%)** |

O degrau **(a)** é o mais barato: troca só a linha do encoder. Tudo o mais (treino balanceado, teste held-out, métricas) já está pronto no script.

---

## 6. Medir honesto (checklist)

- [ ] UStAI **só como teste** — nunca no `fit`.
- [ ] Split treino/validação **apenas** dentro do sintético, se for ajustar hiperparâmetros.
- [ ] Reportar **F1-Score** + accuracy (como em [calcular_metricas.py](scripts/calcular_metricas.py)).
- [ ] Guardar o **sanity de treino** (deve ser alto) para mostrar que o modelo aprendeu.
- [ ] Deixar claro que é **extensão/ablação**, não replicação — os números oficiais do ReFAIR vêm do modelo **congelado**.

---

## Arquivos relacionados
- [roadmap-80-porcento.md](roadmap-80-porcento.md) (o plano completo) · [analise-raiz-xgboost.md](analise-raiz-xgboost.md) (por que 9,4%) · [refair-vetorizacao-e-defeito-do-parser.md](refair-vetorizacao-e-defeito-do-parser.md) (tokenização × embedding) · [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md) (§7 extensão)
- Script: [scripts/prototipo_embeddings.py](scripts/prototipo_embeddings.py)

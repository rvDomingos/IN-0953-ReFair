# Roadmap — como chegar a ≥80% de acerto de domínio no UStAI

**Data:** 2026-06-12
**O que este doc é:** o plano técnico para melhorar a **generalização** do detector de domínio do ReFAIR, partindo do diagnóstico de causa-raiz ([analise-raiz-xgboost.md](analise-raiz-xgboost.md)). É a **Rota C** (extensão metodológica) do [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md).

> **Regra de ouro:** **NÃO treinar no UStAI.** "Chegar a 80% no UStAI" = melhorar a generalização (treinar em outra fonte, testar no UStAI *held-out*). Treinar no UStAI destrói o experimento de validade externa.

---

## O diagnóstico (de onde partimos)

O detector de domínio é um XGBoost sobre `input_ids` (IDs de token por posição). Ele **decora o token na posição 3** (a palavra do papel), que no sintético **é o nome do domínio** (pureza 93%) e no UStAI é genérico/novo (pureza 47,5%; **51,4% dos papéis nunca vistos**). Resultado: **100% no treino, 9,4% no UStAI**. A correção é trocar **forma** por **significado**.

---

## Os passos (em ordem de impacto)

### Passo 1 — Trocar a ENTRADA: `input_ids` → embeddings semânticos ⭐
O maior lever. Em vez de "token na posição N", usar o **significado** da story inteira:
- **Embeddings do BERT** (média dos vetores / `[CLS]`, 768-dim), ou
- **sentence-transformers** (`all-mpnet-base-v2`, `all-MiniLM-L6-v2`) — feitos p/ similaridade semântica, melhor transferência.
- Classificador simples em cima (LogReg / SVM / XGBoost).

Por quê: "driver + car + traffic" cai **perto** de "transportation" no espaço semântico. Sai de "decorar palavra" para "entender assunto".

> **Protótipo medido (BERT mean-pool + LogReg, treino no sintético, teste no UStAI):**
> **37,0% de acerto (F1 0,386)** — vs **9,4% (F1 0,125)** do original. **4× melhor**, só trocando a entrada.
> Sanity: 99,8% no próprio treino (aprendeu) — e generaliza pro UStAI muito melhor que o XGBoost-sobre-input_ids.
> *(É um **limite inferior**: BERT mean-pool não é fine-tuned p/ frases e treinamos com só 100 US/domínio. sentence-transformers + mais dados tende a ir bem além.)*

### Passo 2 — Consertar os DADOS de treino (tirar a muleta do papel)
Mesmo com embeddings, o sintético envieса (papel = nome do domínio). Para forçar o uso do **conteúdo**:
- **Data augmentation:** parafrasear; **variar os papéis** ("transportation researcher" → "driver", "commuter", "logistics manager"); remover/reordenar o papel.
- Adicionar stories **mais diversas/reais** ao treino — de **outras** fontes, **nunca** UStAI.

### Passo 3 — Modelo mais forte
- **Fine-tune** de um transformer (RoBERTa/BERT) ponta a ponta para classificar domínio (em vez de classificador raso sobre features congeladas), **ou**
- **LLM zero-shot/few-shot:** dar a story + a lista dos 34 domínios para um LLM classificar. **Provavelmente o caminho mais rápido para ≥80%** em stories reais (entende semântica, sem treino) — porém muda a arquitetura do ReFAIR e adiciona custo/latência.

### Passo 4 — Estágio 2/3 (secundário)
Domínio é **90,6%** das falhas → conserta ele primeiro. Depois: revisar o filtro domínio→tarefa e trocar a média de GloVe (estágio 2) por embeddings também.

### Passo 5 — Medir honesto
- UStAI **só como teste** (held-out); split treino/validação só nos dados de treino melhorados.
- Reusar [datasets/calcular_metricas.py](datasets/calcular_metricas.py) para reportar F1-Score / accuracy no UStAI.

---

## Expectativa realista

| Abordagem | Esforço | Resultado / chance de ~80% |
|---|---|---|
| BERT-média + LogReg (treino atual) | baixo | **medido: 37,0%** (4× o original) — limite inferior |
| sentence-transformers + classificador | médio | média (deve passar bem de 37%) |
| + data augmentation (variar papéis) | médio | média-alta |
| Fine-tune transformer + dados aumentados | alto | média-alta |
| LLM zero-shot | baixo | **alta** (provável ≥80%) |

> Não há garantia de 80% sem rodar — 80% **fora da distribuição** é ambicioso. Mas qualquer um desses passos sai de "decorar forma" para "entender significado", que é o conserto correto. O número do protótipo (Passo 1) dá a primeira evidência concreta de quanto a representação semântica recupera.

---

## Como isso entra no trabalho

Vira uma **2ª RQ** (Rota C), complementando a 1ª (validade externa):
- **RQ1 (feito):** o ReFAIR generaliza? **Não** — 9,4% no UStAI, por decorar a forma.
- **RQ2 (este roadmap):** dá para consertar trocando a representação? Em quanto melhora?

Isso transforma "o ReFAIR vai mal" em **"diagnosticamos a causa e mostramos o caminho da correção"** — contribuição bem mais forte.

---

## Arquivos relacionados
- [analise-raiz-xgboost.md](analise-raiz-xgboost.md) (diagnóstico) · [metricas-formais-item-a.md](metricas-formais-item-a.md) · [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md) · [o-que-falta.md](o-que-falta.md)
- Protótipo: [datasets/prototipo_embeddings.py](datasets/prototipo_embeddings.py)

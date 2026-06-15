# Vetorização do BERT, classificação e o defeito do parser do ReFAIR

**Data:** 2026-06-13
**O que este doc é:** a explicação **técnica e autocontida** de (1) como o BERT transforma texto em números, (2) a diferença entre **tokenização** e **vetorização (embeddings)**, (3) **o defeito do parser** do detector de domínio do ReFAIR — com o **código real**, a **saída real** e (4) o **TTL do Fabris**, mostrando como domínio é um **nome** e a task é um **número/ID**.
**Reproduzir:** [scripts/analise_raiz_xgboost.py](scripts/analise_raiz_xgboost.py) (venv do ReFAIR).
**Doc irmão (a prova causal completa):** [analise-raiz-xgboost.md](analise-raiz-xgboost.md).

---

## 1. Como o BERT transforma texto em números — duas etapas distintas

O BERT tem **duas etapas bem separadas**. Confundi-las é exatamente o defeito do ReFAIR.

### Etapa 1 — Tokenização (texto → IDs de token)
O tokenizador quebra a frase em *tokens* (pedaços de palavra) e troca cada um pelo seu **índice no vocabulário** (`input_ids`). É uma **tabela de consulta**: `palavra → número`. **Não há significado** nesse número — é só um endereço. "driver" é o ID 4062 por estar na linha 4062 do vocabulário, não porque "dirige".

```
"As a driver, I want…"  ──tokenizador──▶  [101, 2004, 1037, 4062, 1010, 1045, 2215, …]
                                            [CLS]  as    a    driver  ,    i    want
```

### Etapa 2 — Vetorização / embeddings (IDs → significado)
Os `input_ids` passam pela **rede neural** do BERT, que devolve, para cada token, um **vetor de 768 dimensões** (o *embedding*) que **codifica o significado no contexto**. Aqui sim "driver", "car", "traffic" caem **próximos** no espaço — e "driver" perto de "commuter", "rider", etc.

```
[101, 2004, 1037, 4062, …]  ──rede BERT──▶  matriz (100 × 768) de vetores de significado
                                            (ex.: média → 1 vetor de 768-dim por story)
```

> **Resumo:** `input_ids` = **forma** (qual token, em que posição). `embeddings` = **significado**. Um classificador que quer entender *assunto* precisa dos **embeddings**.

---

## 2. O DEFEITO do parser: o ReFAIR para na Etapa 1

O `getDomain` ([REFAIR.py:33-41](../ReFAIR/3.%20Source%20Code/ReFair/REFAIR.py#L33-L41)) tokeniza e entrega os **`input_ids` crus** ao XGBoost — **a Etapa 2 (a rede BERT que daria significado) nunca é chamada**:

```python
def getDomain(user_story):
    tokenized_data = domain_tokenizer([user_story], padding='max_length',
                                      max_length=100, truncation=True)
    traindata = []
    for msg in tokenized_data['input_ids']:        # <-- input_ids = IDs de token (Etapa 1)
        traindata.append(msg)                      #     a rede BERT (Etapa 2) NÃO é usada
    traindata = pd.DataFrame(traindata)
    traindata.columns = traindata.columns.astype(str)   # 100 colunas: "0","1",…,"99" = POSIÇÕES
    predict = domain_classifier.predict(traindata)      # XGBoost decide sobre POSIÇÕES de token
    return dataset["Domain"].unique()[predict[0]]
```

O BERT é usado **só como tokenizador**. As 100 *features* que chegam ao XGBoost são literalmente *"qual ID de token está na posição 0, 1, …, 99"*. O classificador nunca vê o **significado** — só **números de vocabulário posicionais**, cuja grandeza é arbitrária (comparar "ID 4062 < 2474" não quer dizer nada).

---

## 3. O parser em ação — entrada e SAÍDA reais

User story claramente de **Transportation**:

> *"As a driver, I want the app to suggest the fastest route so that I save time in traffic."*

**O que o parser entrega ao XGBoost (`input_ids`, 12 primeiras posições):**

| Posição | Token | input_id |
|---|---|---|
| 0 | `[CLS]` | 101 |
| 1 | `as` | 2004 |
| 2 | `a` | 1037 |
| **3** | **`driver`** | **4062** |
| 4 | `,` | 1010 |
| 5 | `i` | 1045 |
| 6 | `want` | 2215 |
| 7 | `the` | 1996 |
| 8 | `app` | 10439 |
| 9 | `to` | 2000 |
| 10 | `suggest` | 6592 |
| 11 | `the` | 1996 |

**Saída do ReFAIR:** `Domínio previsto = News` ❌ (esperado: **Transportation**).

Por quê erra: a feature decisiva é a **posição 3** (`driver`, id 4062). No treino, nenhuma US de Transportation tinha "driver" na posição 3 (lá o papel é "transportation researcher" → token "transportation"). Como o ID 4062 não casa com o que o modelo decorou, ele cai num ramo arbitrário → "News".

**O que SERIA o embedding (a Etapa 2 ignorada):**
```
shape por token: (1, 100, 768)
vetor médio (768-dim), 6 primeiros valores: [0.180, -0.052, 0.808, 0.003, 0.072, -0.428]
```
Nesse espaço de 768 dimensões "driver/route/traffic" ficaria perto de "Transportation" — e o acerto sobe (protótipo: **9,4% → 37%**, ver [roadmap-80-porcento.md](roadmap-80-porcento.md)).

---

## 4. A classificação: XGBoost sobre posições de token

O classificador de domínio é um **XGBoost** com **5092 árvores**. Cada nó pergunta *"o ID do token na posição N é menor que V?"*. Dump real da árvore 0:

```
0:[7<2474] yes=1,no=2,missing=1          ← "ID do token na posição 7 < 2474?"
	1:[1<1041] yes=3,no=4,missing=3
		3:[5<5352] ...
		4:[3<15056] ...                  ← posição 3 = o papel
	2:[2<2183] ...
```

**Posições usadas como raiz (top 5 de 5092 árvores):** posição **3 → 2438 árvores**, posição 4 → 733, posição 5 → 497, posição 2 → 451, posição 6 → 218. Ou seja, a decisão gira em torno do **molde de abertura** "As **a** [papel], **I want to**…" (posições 2-7), e principalmente do **papel (posição 3)**.

**Prova causal (permutação, no treino — baseline 99,5%):**

| Embaralhar… | Acerto | Lê-se |
|---|---|---|
| nada (baseline) | 99,5% | — |
| **só a posição 3** (papel) | **25,3%** | a decisão depende dela |
| molde (posições 2-7) | 3,3% | quase tudo vem do molde |
| **conteúdo** (posições 40-60) | **99,4%** | o conteúdo é **ignorado** |

> Embaralhar o conteúdo **não muda nada** → o modelo **decide pela forma, não pelo significado**. Detalhe completo em [analise-raiz-xgboost.md](analise-raiz-xgboost.md).

---

## 5. O TTL do Fabris — domínio é NOME, task é NÚMERO/ID

O estágio 3 (atributos sensíveis) vem da **ontologia Fabris** (`fairness_databriefs_alpha_v01.ttl`, **226 data briefs**). Cada brief liga um dataset real a um **domínio**, uma **task** e um **atributo sensível**. Bloco real:

```turtle
fdo:ChicagoRidesharing a dcat:Dataset ;
    dcterms:title "Chicago Ridesharing" ;
    fdo:domain fdo:transportation ;        # DOMÍNIO = NOME (URI textual)
    fdo:sensitiveFeature "geography" ;      # ATRIBUTO  = string
    fdo:task fdo:222 .                       # TASK     = NÚMERO/ID
```

Repare na codificação **mista**, que é o ponto da sua pergunta "nome = número ou id":

| Campo | Como é codificado | Exemplo |
|---|---|---|
| **Domínio** | **NOME** (URI textual) | `fdo:transportation`, `fdo:cardiology`, `fdo:law` |
| **Task** | **NÚMERO / ID** (URI numérico) | `fdo:222`, `fdo:192`, `fdo:13` |
| Atributo sensível | string literal | `"geography"`, `"gender"`, `"race"` |

E o **número da task** é resolvido para um nome num bloco separado do mesmo TTL:

```turtle
fdo:222 a fdo:Task ;
    fdo:taskName "fair pricing evaluation ..." .
fdo:192 a fdo:Task ;
    fdo:taskName "fair matching ..." .
```

> Então: `fdo:transportation` é o **nome** do domínio; `fdo:222` é o **id numérico** que aponta para a task "fair pricing evaluation". O `transporte` (transportation) é um **nome**, não um número — quem é número é a **task**.

### 5.1 Isso bate com o que o ReFAIR carrega
Agregando os briefs de `fdo:transportation` (Chicago Ridesharing, NYC Taxi, Ride-hailing App, Seoul Bike, Shanghai Taxi, Equitable School Access), os atributos não-vazios são **geography (3×)** e **race (1×)** — **exatamente** o `domains-features-mapping.csv` do ReFAIR:

```csv
Domain,Feature
transportation,geography
transportation,race
```

> **Consequência para o diagnóstico:** o mapa domínio→atributo (estágio 3) está **correto e fiel ao TTL**. Logo, quando o atributo final sai errado, é porque **o domínio chegou errado do estágio 1** — não por falha da ontologia. O defeito está **confinado ao parser/classificador de domínio** (§2-4).

### 5.2 Há ainda um segundo "nome = número" — dentro do classificador
Além do TTL, o próprio `getDomain` faz um mapeamento **número → nome**: o XGBoost devolve um **índice inteiro**, traduzido para o nome do domínio por `dataset["Domain"].unique()[predict[0]]` (a posição do domínio na ordem de aparição do dataset de treino). Ou seja, "domínio 0" = primeiro domínio do arquivo, etc.

---

## 6. Conclusão

| | Forma (o que o ReFAIR usa) | Significado (o que deveria usar) |
|---|---|---|
| Representação | `input_ids` — token por posição | embeddings BERT (768-dim) |
| Feature decisiva | posição 3 (o papel) | o assunto da story inteira |
| Treino | papel = nome do domínio → decora → 99,5% | — |
| UStAI | papel novo/genérico → desaba → **9,4%** | protótipo: **37%** |

O **defeito do parser** é entregar ao classificador a **forma tokenizada** em vez do **significado vetorizado**. Funciona no molde rígido do sintético e desaba em user stories reais — e os erros de ML task e de atributo sensível **descem todos desta raiz**.

---

## Arquivos relacionados
- [analise-raiz-xgboost.md](analise-raiz-xgboost.md) (prova causal + dumps) · [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md) (ELI5) · [roadmap-80-porcento.md](roadmap-80-porcento.md) · [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md)
- Script: [scripts/analise_raiz_xgboost.py](scripts/analise_raiz_xgboost.py) · TTL: `ReFAIR/1. Starting Assets/Fabris Ontology Reenginering/fairness_databriefs_alpha_v01.ttl`

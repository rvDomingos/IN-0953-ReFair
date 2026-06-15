# Análise da raiz do classificador de domínio — por que o ReFAIR decora (e onde está o erro)

**Data:** 2026-06-13 (re-investigação com rigor — todos os números abaixo foram **regerados** nesta data)
**O que este doc é:** a prova técnica, com **o código do parser**, o **dump real da árvore**, a **prova causal por permutação** e os **dados sobre todas as US** (treino × UStAI), de que o detector de domínio do ReFAIR **decide pelo token na posição 3 (a palavra do papel)** em vez do significado. É a causa-raiz dos 9,4% de acerto.
**Reproduzir:** [scripts/analise_raiz_xgboost.py](scripts/analise_raiz_xgboost.py) — rodar com o venv do ReFAIR:
```bash
"ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/venv_mac/bin/python" \
    documents/scripts/analise_raiz_xgboost.py
```
**Versão simples (ELI5):** [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md).

---

## 1. ONDE está o erro: o parser de entrada do classificador

O erro **não** está nos pesos do modelo nem na ontologia — está em **o que** é dado ao classificador. Veja o `getDomain` real ([REFAIR.py:33-41](../ReFAIR/3.%20Source%20Code/ReFair/REFAIR.py#L33-L41)):

```python
def getDomain(user_story):
    tokenized_data = domain_tokenizer([user_story], padding='max_length',
                                      max_length=100, truncation=True)
    traindata = []
    for msg in tokenized_data['input_ids']:      # <-- input_ids, NÃO embeddings
        traindata.append(msg)
    traindata = pd.DataFrame(traindata)
    traindata.columns = traindata.columns.astype(str)   # colunas "0".."99" = posições
    predict = domain_classifier.predict(traindata)
    return dataset["Domain"].unique()[predict[0]]
```

O que entra no XGBoost é `tokenized_data['input_ids']`: os **IDs de token por posição**, **não** os vetores de significado (embeddings) do BERT. Ou seja, as 100 features do modelo são literalmente *"qual ID de token está na posição 0, 1, …, 99"*.

| Posição | 0 | 1 | 2 | **3** | 4 | … |
|---|---|---|---|---|---|---|
| Token | `[CLS]` | `as` | `a` | **papel** | … | … |

> O BERT aqui é usado só como **tokenizador** (texto → IDs). O passo que daria *significado* — passar os IDs pela rede e pegar os embeddings — **nunca acontece**. O XGBoost recebe números de vocabulário crus, posicionais. **É esse o defeito do parser.**

---

## 2. A árvore que o XGBoost faz (dump REAL, regerado)

Saída de `booster.get_dump()[0]` — primeira de **5092** árvores:

```
0:[7<2474] yes=1,no=2,missing=1
	1:[1<1041] yes=3,no=4,missing=3
		3:[5<5352] yes=7,no=8,missing=7
			7:leaf=0.0776080936
			8:leaf=0.530275285
		4:[3<15056] yes=9,no=10,missing=9
			9:leaf=-0.0222107917
			10:leaf=0.0625508651
	2:[2<2183] yes=5,no=6,missing=5
		5:leaf=0.78779304
		6:[2<10285] yes=11,no=12,missing=11
			11:leaf=0.00727293128
			12:leaf=0.213115379
```

- `[N<V]` = *"o ID do token na **posição N** é menor que **V**?"*. O `V` é um **índice de vocabulário** — **não tem sentido de grandeza** (comparar IDs de token é arbitrário; é o sintoma do parser errado).
- `leaf` = contribuição de score; o domínio final é o `argmax` da soma das 5092 árvores.

### Posições usadas como RAIZ das 5092 árvores (top 10)

| Posição (token) | Nº de árvores com essa raiz |
|---|---|
| **3 (o papel)** | **2438** |
| 4 | 733 |
| 5 | 497 |
| 2 | 451 |
| 6 | 218 |
| 21 | 93 |
| 9 | 89 |
| 7 | 77 |
| 8 | 64 |
| 25 | 53 |

→ Quase **metade** das árvores decide na primeira pergunta pela **posição 3 (o papel)**; o resto são as palavras fixas do molde "As **a** … **I want to**" (posições 2,4,5,6). O modelo inteiro gira em torno do **molde**, não do conteúdo.

```python
roots = clf.get_booster().trees_to_dataframe()
roots = roots[roots['Node'] == 0]          # nó-raiz de cada árvore
Counter(roots['Feature']).most_common(10)  # -> posição '3' domina
```

---

## 3. TREINO (sintético): a posição 3 É o nome do domínio

Token na posição 3 (papel) por domínio, sobre **todas** as ~365 US de cada um (top 3). Repare que **o papel quase sempre nomeia o domínio**:

| Domínio | Token pos.3 mais comum (contagem) |
|---|---|
| Biology | bio(90), of(70), computational(66) |
| Cardiology | **card**(360) |
| Computer Networks | network(331), computer(25) |
| Computer Vision | computer(356), vision(7) |
| Demography | **demo**(350) |
| Dermatology | **der**(360) |
| Economics | **economist**(362) |
| Education | **educator**(322), education(25) |
| Endocrinology | **end**(359) |
| Finance & Marketing | market(194), financial(85), marketing(54) |
| Health | healthcare(269), public(52), health(33) |
| Information Systems | information(250), it(104) |
| Law | legal(211), lawyer(144) |
| Library | **librarian**(355) |
| Linguistics | **linguist**(346) |
| Literature | literary(304), literature(45) |
| Medicine | medical(331), physician(21) |
| Movies | movie(232), filmmaker(71), film(49) |
| Music | music(300), musician(57) |
| Nephrology | **ne**(359) |
| News | journalist(195), news(163) |
| Pediatrics | **pediatric**(358) |
| Pharmacology | ph(326), pharmaceutical(30) |
| Plant Science | plant(344), botanist(15) |
| Political Science | **political**(360) |
| Psychology | **psychologist**(350) |
| Radiology | **radio**(359) |
| Social Media | social(360) |
| Social Networks | social(343), network(15) |
| Social Work | social(356), worker(5) |
| Sociology | **sociologist**(360) |
| Sport | sports(353), coach(7) |
| Transportation | **transportation**(355), traffic(4) |
| Urban Studies | urban(359), planner(5) |

> Cada domínio tem **um papel dominante que é o próprio nome do domínio**. Decorar "token na posição 3 → domínio" funciona **quase perfeito** aqui.

---

## 4. UStAI (nosso): a posição 3 são papéis genéricos e repetidos

As mesmas palavras ("researcher", "data", "developer", "user", "patient") aparecem em **vários** domínios — nenhum papel "nomeia" o domínio:

| Domínio | Token pos.3 mais comum (contagem) |
|---|---|
| Cardiology | researcher(4), data(4), healthcare(3) |
| Computer Networks | cyber(5), security(4), data(3) |
| Computer Vision | researcher(10), developer(8), user(8) |
| Demography | economic(4), researcher(4), data(4) |
| Economics | researcher(12), data(9), freelance(9) |
| Endocrinology | person(6), healthcare(5), researcher(3) |
| Finance & Marketing | data(8), business(6), credit(5) |
| Health | healthcare(9), patient(8), data(8) |
| Information Systems | developer(20), customer(13), researcher(12) |
| Law | law(4), data(3), researcher(2) |
| Library | researcher(6), developer(4), research(3) |
| Linguistics | social(4), data(4), researcher(3) |
| Medicine | healthcare(4), researcher(4), medical(3) |
| Music | music(16), data(2), play(2) |
| News | news(6), journalist(5), researcher(4) |
| Pediatrics | researcher(5), developer(4), parent(3) |
| Pharmacology | pharmaceutical(4), ne(3), data(3) |
| Political Science | military(5), cyber(2), defense(2) |
| Psychology | researcher(14), data(12), healthcare(7) |
| Radiology | radio(5), patient(5), healthcare(5) |
| Social Media | social(5), researcher(4), content(3) |
| Social Networks | social(9), user(7), security(6) |
| Social Work | public(7), community(5), researcher(5) |
| Sport | fantasy(16), sports(3), casual(2) |
| **Transportation** | data(11), researcher(10), **driver(9)** |

> "researcher" e "data" aparecem em **quase todos** os domínios. "driver" (Transportation) aparece em só **9 das 120** US. Não há como decorar "posição 3 → domínio" aqui.

---

## 5. A prova em números (regerada)

### 5.1 Pureza da posição 3 (se você SÓ soubesse o papel, acertaria o domínio?)

| Dataset | Pureza | Significa |
|---|---|---|
| **Treino** | **93,0%** | o papel quase **define** o domínio → dá pra decorar |
| **UStAI** | **47,5%** | o papel **não** define o domínio → não dá pra decorar |

### 5.2 O "mapa decorado" do treino aplicado ao UStAI

Construímos o mapa `token da posição 3 → domínio majoritário` a partir do **treino** e aplicamos no **UStAI**:

| Métrica | Valor |
|---|---|
| US do UStAI cujo papel (token pos.3) **nunca apareceu no treino** | **648/1260 = 51,4%** |
| Acerto do mapa mesmo entre os 612 papéis "vistos" | **131/612 = 21,4%** |

> **Metade das nossas US tem um papel que o modelo nunca viu** → cai no default. E mesmo onde o papel é conhecido, o mapa decorado **erra ~79% das vezes**, porque o mesmo papel aparece em domínios diferentes.

### 5.3 Sobreposição de papéis entre domínios

| Dataset | Papéis que caem em >1 domínio |
|---|---|
| Treino | 22,3% (31/139) |
| UStAI | 35,5% (81/228) |

---

## 5.4 A PROVA CAUSAL — importância por permutação

As seções anteriores são *correlação*. Esta é a **prova causal** de que a decisão sai da posição 3 e **não** do conteúdo. Método: medir o acerto no treino, depois **embaralhar** grupos de posições entre as linhas (quebrando o vínculo daquela posição com o rótulo, mantendo a distribuição) e remedir.

```python
def perm_acc(cols, seed=42):
    rng = np.random.default_rng(seed)
    Xp = X.copy()                      # X = matriz input_ids (N,100) do treino
    for c in cols:
        Xp[:, c] = Xp[rng.permutation(len(Xp)), c]   # embaralha a posição c
    return acc(Xp)                     # acc() = mesmo caminho do getDomain
```

| Experimento | Acerto no treino |
|---|---|
| baseline (nada embaralhado) | **99,5%** |
| embaralha **SÓ a posição 3** (o papel) | **25,3%** |
| embaralha o **molde** (posições 2-7: "a … I want to") | **3,3%** |
| embaralha o **conteúdo** (posições 40-60) | **99,4%** (inalterado) |

**Leitura:**
- Tirar o vínculo da **posição 3** derruba o acerto de 99,5% → **25,3%**: o modelo perde sua principal feature de decisão.
- Embaralhar o **conteúdo** da story (posições 40-60) **não muda nada** (99,4%): **o modelo já ignorava o conteúdo.**
- Embaralhar o molde inteiro o destrói (3,3%): ele depende **inteiramente** da forma fixa.

> Conclusão causal: **o classificador decide pela posição do papel no molde, não pelo significado da user story.** É exatamente o que o parser da seção 1 alimenta nele.

---

## 6. Validação com o TTL do Fabris (estágio 3) — para situar onde o erro NÃO está

O estágio 3 (atributos sensíveis) vem da **ontologia Fabris** (`fairness_databriefs_alpha_v01.ttl`, **226 data briefs**). Cada brief liga **domínio → atributo sensível**. Exemplo real (bloco completo do TTL):

```turtle
fdo:ChicagoRidesharing a dcat:Dataset ;
    dcterms:title "Chicago Ridesharing" ;
    dcterms:description "... ridesharing trips reported to the City of Chicago ..." ;
    fdo:domain fdo:transportation ;
    fdo:sensitiveFeature "geography" ;
    fdo:task fdo:222 .
```

Agregando todos os briefs de `fdo:transportation` (Chicago Ridesharing, Equitable School Access, NYC Taxi, Ride-hailing App, Seoul Bike, Shanghai Taxi) os atributos não-vazios são **geography (3×)** e **race (1×)**. E é **exatamente** isso que o ReFAIR carrega em `domains-features-mapping.csv`:

```csv
Domain,Feature
transportation,geography
transportation,race
```

> **Por que isso importa para o diagnóstico:** o mapeamento domínio→atributo do estágio 3 está **correto** e fiel ao Fabris. Logo, quando o estágio 3 erra o atributo sensível, é porque **recebeu o domínio errado do estágio 1** — não porque a ontologia ou o CSV estejam errados. Isto confina o defeito **ao parser/classificador de domínio** (seções 1-5) e descarta o estágio 3 como culpado. (Bate com a decomposição de falhas: **90,6% nascem no estágio 1**.)

---

## 7. Qual seria a árvore CORRETA

O problema **não é a árvore — é a entrada** (`input_ids` posicionais). Nenhuma árvore generaliza sobre "qual token está em qual lugar". A correção é trocar a **representação**:

**(a) Por significado, independente de posição:**
```
Raiz: a US menciona {car, driver, traffic, road, transport}?
 ├─sim→ Transportation
 └─não→ menciona {patient, diagnosis, clinical, disease}?
         ├─sim→ Health / Medicine
         └─não→ menciona {price, market, customer, revenue}?
                 ├─sim→ Finance & Marketing
                 └─não→ …
```
Não importa **onde** a palavra aparece nem o **número** do ID — importa o **conceito**.

**(b) O ideal (o que "XGBoost+BERT" deveria ser):** usar os **embeddings** do BERT (vetor `[CLS]` ou média) como entrada — fazendo aquele passo que o parser pula. Aí "driver", "car", "transportation researcher" ficam **próximos** no espaço e o modelo **transfere** pra US escritas de outro jeito. (Protótipo medido: **9,4% → 37%**, ver [roadmap-80-porcento.md](roadmap-80-porcento.md).)

---

## 8. Conclusão

```
ONDE   : o parser do getDomain entrega input_ids (token por posição), não embeddings.
COMO   : a posição 3 (o papel) vira a feature de decisão (raiz de 2438/5092 árvores).
PROVA  : embaralhar a posição 3 -> 99,5%→25,3% ; embaralhar o conteúdo -> 99,4% (nada).
TREINO : papel = nome do domínio (pureza 93%)            -> decora -> 99,5%
UStAI  : papel genérico/novo (pureza 47%, 51% nunca vistos) -> sem decorar -> 9,4%
FABRIS : o mapa domínio→atributo (estágio 3) está correto -> o erro é só no estágio 1.
```

O detector de domínio do ReFAIR **aprende a forma (qual token, em qual posição), não o conteúdo**. Funciona no molde rígido do sintético e **desaba** em US reais. Os outros sintomas (ML task vazia, features erradas) **descem todos desta raiz**.

---

## Arquivos relacionados
- [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md) (ELI5) · [metricas-formais-item-a.md](metricas-formais-item-a.md) · [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md) · [roadmap-80-porcento.md](roadmap-80-porcento.md) · [o-que-falta.md](o-que-falta.md)
- Script (reproduz tudo acima): [scripts/analise_raiz_xgboost.py](scripts/analise_raiz_xgboost.py)
- TTL do Fabris: `ReFAIR/1. Starting Assets/Fabris Ontology Reenginering/fairness_databriefs_alpha_v01.ttl`

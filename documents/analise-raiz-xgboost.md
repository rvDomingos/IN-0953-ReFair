# Análise da raiz do classificador de domínio — por que o ReFAIR decora

**Data:** 2026-06-12
**O que este doc é:** a prova técnica, com dump da árvore e dados sobre **todas** as US (treino × UStAI), de que o detector de domínio do ReFAIR **decora o token na posição 3 (a palavra do papel)** em vez de entender o significado. É a causa-raiz dos 9,4% de acerto.
**Reproduzir:** [scripts/analise_raiz_xgboost.py](scripts/analise_raiz_xgboost.py) (precisa do venv do ReFAIR — xgboost/transformers).
**Versão simples (ELI5):** [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md).

---

## 1. Como o modelo enxerga a frase

`getDomain` ([REFAIR.py:33-41](../ReFAIR/3.%20Source%20Code/ReFair/REFAIR.py#L33-L41)) passa pro XGBoost os **`input_ids`** do BERT — os **IDs de token por posição** (não os embeddings). As 100 features são "qual token está na posição 0, 1, …, 99".

| Posição | 0 | 1 | 2 | **3** | 4 | … |
|---|---|---|---|---|---|---|
| Token | `[CLS]` | `as` | `a` | **papel** | … | … |

A **posição 3 é a palavra do papel** ("As a **driver**…").

---

## 2. A árvore que o XGBoost faz (dump real da árvore 0, de 5092)

```
0:[f7 < 2474]              ← raiz: token na posição 7 tem ID < 2474?
   ├─sim→ 1:[f1 < 1041]
   │       ├─sim→ 3:[f5 < 5352]
   │       │       ├─sim→ leaf = +0.078
   │       │       └─não→ leaf = +0.530
   │       └─não→ 4:[f3 < 15056]
   │               ├─sim→ leaf = −0.022
   │               └─não→ leaf = +0.063
   └─não→ 2:[f2 < 2183]
           ├─sim→ leaf = +0.788
           └─não→ 6:[f2 < 10285]
                   ├─sim→ leaf = +0.007
                   └─não→ leaf = +0.213
```

- `fN` = ID do token na **posição N**; o número após `<` é um **limiar de ID de token** (índice no vocabulário, **sem significado de grandeza**).
- `leaf` = contribuição de score; são **5092 árvores** (80 rodadas × ~38 classes) e o domínio é o `argmax` da soma.

### Posições usadas como RAIZ (top 10)

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

→ A **posição 3 (papel)** domina; o resto são as palavras fixas do molde "As a … I want" (posições 2,4,5,6).

---

## 3. TREINO (sintético): a posição 3 É o nome do domínio

Token na posição 3 (papel), por domínio — **todas as ~365 US de cada um**. Repare que **o papel quase sempre nomeia o domínio**:

| Domínio | Token pos.3 mais comum (contagem) |
|---|---|
| Biology | bio(90), of(70), computational(66), biologist(27) |
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
| Political Science | political(360) |
| Psychology | **psychologist**(350) |
| Radiology | **radio**(359) |
| Social Media | social(360) |
| Social Networks | social(343), network(15) |
| Social Work | social(356), worker(5) |
| Sociology | **sociologist**(360) |
| Sport | sports(353), coach(7) |
| Transportation | **transportation**(355), traffic(4) |
| Urban Studies | urban(359), planner(5) |

> Cada domínio tem **um papel dominante que é o próprio nome do domínio**. Memorizar "token na posição 3 → domínio" **funciona quase perfeito** aqui.

---

## 4. UStAI (nosso): a posição 3 são papéis genéricos e repetidos

As mesmas palavras ("researcher", "data", "developer", "user", "patient") aparecem em **vários** domínios — nenhum papel "nomeia" o domínio:

| Domínio | Token pos.3 mais comum (contagem) |
|---|---|
| Cardiology | researcher(4), data(4), healthcare(3), patient(3) |
| Computer Networks | cyber(5), security(4), data(3), researcher(3) |
| Computer Vision | researcher(10), developer(8), user(8) |
| Demography | economic(4), researcher(4), data(4) |
| Economics | researcher(12), data(9), freelance(9), client(9) |
| Endocrinology | person(6), healthcare(5), researcher(3) |
| Finance & Marketing | data(8), business(6), credit(5), financial(5) |
| Health | healthcare(9), patient(8), data(8) |
| Information Systems | developer(20), customer(13), researcher(12) |
| Law | law(4), data(3), researcher(2) |
| Library | researcher(6), developer(4), librarian(3) |
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
| **Transportation** | data(11), researcher(10), **driver(9)**, city(7) |

> "researcher" e "data" aparecem em **quase todos** os domínios. "driver" (Transportation) só **9 das 120**. Não há como decorar "posição 3 → domínio" aqui.

---

## 5. A prova em números

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

> Tradução: **metade das nossas US tem um papel que o modelo nunca viu** (ele não tem ideia do que fazer → cai no default "Biology"). E mesmo onde o papel é conhecido, o mapa decorado **erra 79% das vezes**, porque o mesmo papel aparece em domínios diferentes.

### 5.3 Sobreposição de papéis entre domínios

| Dataset | Papéis que caem em >1 domínio |
|---|---|
| Treino | 22,3% |
| UStAI | 35,5% |

---

## 6. Qual seria a árvore CORRETA

O problema **não é a árvore — é a entrada** (`input_ids` posicionais). Nenhuma árvore generaliza sobre "qual token está em qual lugar". A correção é trocar a **representação**:

**(a) Por significado, independente de posição** (ex.: presença de palavras-chave):
```
Raiz: a US menciona {car, driver, traffic, road, transport}?
 ├─sim→ Transportation
 └─não→ menciona {patient, diagnosis, clinical, disease}?
         ├─sim→ Health / Medicine
         └─não→ menciona {price, market, customer, revenue}?
                 ├─sim→ Finance & Marketing
                 └─não→ …
```
Não importa **onde** a palavra aparece nem o **número** do ID — importa o **conceito**. "driver", "car", "traffic" → Transportation, em qualquer posição.

**(b) O ideal (o que "XGBoost+BERT" deveria ser):** usar os **embeddings do BERT** (vetor `[CLS]` ou média) como entrada. Nesse espaço "driver", "car", "transportation researcher" ficam **próximos** → o modelo aprende "esta região de significado = Transportation" e **transfere** pra US escritas de outro jeito.

---

## 7. Conclusão

```
ENTRADA: input_ids (token por posição)  →  posição 3 = o papel
TREINO : papel = nome do domínio (pureza 93%)  →  decora  →  100%
UStAI  : papel genérico/novo (pureza 47%, 51% nunca vistos)  →  sem o que decorar  →  9,4%
```

O detector de domínio do ReFAIR **aprende a forma (qual token, em qual posição), não o conteúdo (qual domínio)**. Funciona no molde rígido do sintético e **desaba** em US reais. Os outros sintomas (ML task vazia, features erradas) **descem todos desta raiz** (90,6% das falhas nascem no estágio 1).

---

## Arquivos relacionados
- [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md) (versão ELI5) · [metricas-formais-item-a.md](metricas-formais-item-a.md) · [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md) · [o-que-falta.md](o-que-falta.md)
- Script: [scripts/analise_raiz_xgboost.py](scripts/analise_raiz_xgboost.py)

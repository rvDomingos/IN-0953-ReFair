# Apresentação ReFAIR × UStAI — roteiro para 3 apresentadores

**Data:** 2026-06-13
**Duração-alvo:** ~18 min (3 × ~6 min) + perguntas.
**Base:** o **artigo do ReFAIR** — *"ReFAIR: Toward a Context-Aware Recommender for Fairness Requirements Engineering"* (Ferrara et al., **ICSE'24**) — e nossos resultados em [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md), [analise-raiz-xgboost.md](analise-raiz-xgboost.md) e [refair-vetorizacao-e-defeito-do-parser.md](refair-vetorizacao-e-defeito-do-parser.md).

> **Divisão pedida:**
> **P1 — Como o ReFAIR funciona e o que ele faz** (a partir do artigo).
> **P2 — Ontologia e datasets, com as métricas (UStAI × ReFAIR).**
> **P3 — Parte técnica: como o ReFAIR funciona por dentro hoje (vetorização, parser, defeito).**
>
> Dica: **um número por slide.** Não leiam o slide — contem a história. Negrito = não pode faltar.

---

## 🎤 Participante 1 — O que o artigo propõe: o que é e o que faz o ReFAIR (~6 min) · slides 1-5

**Slide 1 — Capa**
- Título do artigo: *"ReFAIR: Toward a Context-Aware Recommender for Fairness Requirements Engineering"* — Ferrara et al., **ICSE 2024**. Nomes da equipe.

**Slide 2 — A motivação do artigo**
- *Fala (palavras do artigo):* "O ReFAIR foi proposto para **assistir cientistas de dados e engenheiros de software a construir soluções de ML justas**. Sistemas de ML podem discriminar por idade, gênero, raça — os **atributos sensíveis**. O artigo defende tratar isso **cedo, na engenharia de requisitos**, e não depois do dano."

**Slide 3 — O que o ReFAIR faz (a tese do artigo)**
- *Fala:* "A ideia central, segundo o artigo: **analisar uma user story** — o 'Como [papel], quero [ação] para [objetivo]' — para **identificar o domínio da aplicação e as tarefas de ML**, e a partir disso **recomendar os atributos sensíveis** que importam naquele contexto. É um **recomendador *context-aware*** de requisitos de fairness."

**Slide 4 — A arquitetura do artigo: 2 módulos de ML + 1 mapeamento**
- Mostrar o diagrama (figura `approach` do repositório):
```
                ┌─ Single Label Classifier (XGBoost) ─▶ DOMÍNIO
User Story ─────┤                                                  ┐
                └─ Multi Label Classifier (LinearSVC LP) ─▶ ML TASKS ┘
                                                                   │
                              mapeamento (ontologia Fabris) ───────▶ ATRIBUTOS SENSÍVEIS
```
- *Fala (termos do artigo):* "São **dois classificadores**: um **Single Label Classifier** que detecta o **domínio**, e um **Multi Label Classifier** que detecta as **tarefas de ML**. Com o par (domínio, tarefa), o ReFAIR consulta um **mapeamento construído a partir da literatura** — a ontologia de **Fabris** — e devolve os **atributos sensíveis**."

**Slide 5 — Como foi treinado e a lacuna (handoff)**
- *Fala:* "Pra treinar, os autores **criaram um dataset sintético** de user stories de ML, num molde fixo (template de Cohn), e treinaram um **XGBoost** (domínio) e um **Linear SVC Label Powerset** (tarefas). No paper, o domínio atinge **F1 ≈ 0,98**. **Mas** — e os próprios autores citam isso como limitação — a validação foi **só com stories sintéticas**. Nunca em stories **reais**. Daí nossas perguntas: **(RQ1)** generaliza? **(RQ2)** dá pra consertar? — [P2] mostra os dados e os números."
- *Números:* **2 classificadores** + mapeamento Fabris · treino **sintético** · **F1 0,98** (domínio, no paper) · validado **só no sintético** (a lacuna).

---

## 🎤 Participante 2 — Ontologia, datasets e métricas (~6 min) · slides 6-12

**Slide 6 — A ontologia Fabris (a base do estágio 3, ref. [1] do artigo)**
- *Fala:* "O 'conhecimento' que vira atributo sensível vem da ontologia de **Fabris et al. (2022), 'Algorithmic fairness datasets: the story so far'** — a referência [1] do ReFAIR. São **226 fichas (data briefs)** de datasets reais de fairness; cada uma liga **domínio → tarefa → atributo sensível**."
- Mostrar uma ficha real:
```turtle
fdo:ChicagoRidesharing a dcat:Dataset ;
    fdo:domain fdo:transportation ;     # domínio = NOME
    fdo:sensitiveFeature "geography" ;
    fdo:task fdo:222 .                    # task = NÚMERO/ID -> "fair pricing evaluation"
```
- *Fala:* "Note a codificação: **domínio é um nome** (`transportation`), **tarefa é um número** (`fdo:222`). Disso o ReFAIR monta a tabela `transportation → geography, race`. **Essa tabela está correta**, fiel à ontologia."

**Slide 7 — O vocabulário de tarefas (ref. [2] do artigo)**
- *Fala:* "As 25 tarefas de ML vêm de um segundo recurso citado no artigo: o **vocabulário controlado de IA de Duran-Silva et al.** Então o ReFAIR combina **duas bases da literatura**: Fabris (domínios+atributos) e Duran-Silva (tarefas)."

**Slide 8 — Os datasets: ReFAIR (sintético) × UStAI (real)**
- Tabela:

| | ReFAIR (treino do artigo) | **UStAI** (nosso teste) |
|---|---|---|
| Origem | gerado da própria ontologia | **42 abstracts de papers reais** |
| Como | molde fixo (template de Cohn) | **3 LLMs** (Gemini, Llama, O1) |
| Volume | ~12 mil US | **1260 user stories** |

- *Fala:* "O treino do ReFAIR é sintético e padronizado. Testamos com o **UStAI**: 1260 stories de **3 LLMs** a partir de **42 abstracts reais**. Origem diferente = teste de generalização legítimo."

**Slide 9 — Como medimos (rigor)**
- *Fala:* "Fizemos um **gabarito manual** dos 3 estágios e rodamos o ReFAIR **congelado, sem retreino** — UStAI é **só teste** — nas **versões exatas** das libs (determinístico). Rodamos em **macOS e Windows**: **idêntico**."

**Slide 10 — O resultado principal (o choque)**
- Barras: **0,98 → 0,125**.
- *Fala:* "A promessa do artigo era F1 0,98. No UStAI, o domínio cai pra **F1 0,125 — 9,4% de acerto**. Não é uma queda, é um **colapso**."

**Slide 11 — As métricas por estágio**
- Tabela:

| Estágio | Métrica no UStAI | Referência do paper |
|---|---|---|
| 1 — Domínio | **F1 0,125 (9,4%)** | 0,98 |
| 2 — ML task | F1 0,127 · **42,5% vazias** | 0,90 |
| 3 — Atributos | **2,1%** match exato | — |

- *Fala:* "Piora a cada estágio: quase **metade** fica **sem nenhuma ML task** e os atributos acertam só **2%**. Ruim nos **3 LLMs** igualmente → o problema é do ReFAIR, não do gerador. **354 stories** caem todas em 'Biology'."

**Slide 12 — Mas ele acerta às vezes! (handoff)**
- *Fala:* "Importante ser justo: das 1258, **118 (9,4%) acertaram o domínio**. Exemplo real do UStAI que o ReFAIR **acertou** — inclusive os atributos **exatos**:"
```
US (A6US6O1): "As a user experience designer, I want the ADAS to provide
               clear feedback to drivers, so that users understand..."
ReFAIR → domínio: Transportation ✓ | atributos: geography, race ✓ (= gabarito)
```
- *Fala:* "Então ele **não está 100% quebrado** — ele acerta em **casos específicos**. A pergunta de ouro é: **por que acerta nuns e desaba na maioria?** — [P3] abre a caixa-preta e mostra o padrão."
- *Números:* **226** fichas Fabris · **1260** US · **9,4%** domínio · **42,5%** ML task vazia · **118 acertos**.

---

## 🎤 Participante 3 — Como o ReFAIR funciona por dentro, e o defeito (~6 min) · slides 13-18

**Slide 13 — Texto vira número: as 2 etapas do BERT**
- *Fala:* "Pro modelo entender texto, o BERT faz **duas coisas**. **(1) Tokeniza:** troca cada palavra por um número de dicionário — `driver` vira o id 4062. É só um **endereço**, sem significado. **(2) Vetoriza:** passa esses números pela rede neural e gera **embeddings** — vetores de 768 números que **capturam o significado**. É no embedding que 'driver', 'car' e 'traffic' ficam **perto**."

**Slide 14 — O defeito: o ReFAIR para na etapa 1**
- Mostrar o código real do `getDomain`:
```python
tokenized_data = domain_tokenizer([user_story], ...)
for msg in tokenized_data['input_ids']:    # <-- usa os IDs crus (etapa 1)
    traindata.append(msg)                  #     a rede BERT (embedding) NUNCA é chamada
predict = domain_classifier.predict(traindata)
```
- *Fala:* "Aqui está o defeito. O ReFAIR usa o BERT **só como tokenizador** e joga os **IDs crus** no XGBoost. **A etapa que daria significado nunca acontece.** O modelo decide por *'qual número de token está em qual posição'* — a **forma**, não o **sentido**."

**Slide 15 — O acerto e o erro têm a MESMA causa (o ponto-chave)**
- Tabela de contraste (dois casos reais do UStAI):

| User story (real) | Papel (posição 3) | ReFAIR | Por quê |
|---|---|---|---|
| *"As a **Healthcare Administrator**, I want to evaluate…"* | `healthcare` | **Health ✓** | no treino, "healthcare" = Health (decorado) |
| *"As a **driver**, I want a car that uses AI… in traffic"* | `driver` | **News ✗** | "driver" nunca foi papel de transporte no treino |

- *Fala:* "Esse é o coração. O ReFAIR **acerta quando, por sorte, o papel da story real é o mesmo que ele decorou** — 'healthcare' → Health. E **erra quando o papel é novo** — 'driver', que ele nunca viu em transporte, vai parar em 'News'. **Mesmo mecanismo, resultados opostos**: ele lê a palavra do papel, não o assunto."

**Slide 16 — A prova causal (permutação)**
- Tabela:

| Embaralhar… | Acerto no treino |
|---|---|
| nada | **99,5%** |
| **só a posição 3** (o papel) | **25,3%** |
| o conteúdo da story | **99,4%** (não muda) |

- *Fala:* "Provamos: embaralhar **só o papel** derruba de ~100% pra **25%**; embaralhar o **conteúdo** **não muda nada**. Ou seja: **o modelo ignora o conteúdo e decide pelo molde**. No treino, o papel **é** o nome do domínio; no UStAI, **51% dos papéis ele nunca viu**."

**Slide 17 — A correção (extensão / RQ2)**
- Barras: 9,4% → **37%**.
- *Fala:* "Pra confirmar que a culpa é da **representação**, mudamos **uma coisa só**: trocamos os IDs de token pelos **embeddings** (a etapa pulada). O acerto **quadruplicou: 9,4% → 37%**. Mesmo dataset, mesma tarefa. Isso **prova** que era a representação."

**Slide 18 — Conclusão e contribuição**
- *Fala:* "Fechando: **(1)** o ReFAIR, como está no artigo, **não generaliza** pra user stories reais; **(2)** descobrimos **por quê** — decora a **forma** (token por posição), não o **significado**, e por isso só acerta quando o papel coincide; **(3)** mostramos o **caminho do conserto**. Resultado negativo **bem fundamentado**, com diagnóstico e remediação. Limitações honestas: nosso gabarito (vamos medir κ), o UStAI ainda é gerado por LLM, e o estágio 3 precisa de anotação humana. **Obrigado!**"
- *Números:* `healthcare`→Health ✓ vs `driver`→News ✗ · posição 3: **99,5%→25,3%** · conteúdo **99,4%** · **51%** papéis nunca vistos · **9,4%→37% (4×)**.

---

## Apêndice — perguntas prováveis e respostas curtas

| Pergunta | Resposta de bolso |
|---|---|
| "Isso é replicação?" | Não — é **validade externa** (ferramenta inalterada em dados novos) + **extensão**. A alegação do paper a gente confirmou pelo **99,5% no treino**. |
| "Mostra uma US que ele acertou." | `A6US6O1` (Transportation, atributos exatos `geography, race`) e `A5US10Ll` ("Healthcare Administrator" → Health). Acerta quando o papel coincide com o molde. |
| "Por que não retreinar no UStAI?" | Destruiria o teste de generalização — UStAI é **só teste**. |
| "37% ainda é baixo." | É **limite inferior** (BERT cru, pouca amostra). O ponto é o **4×** com uma mudança só. |
| "O gabarito não é enviesado?" | Por isso vamos medir **κ** e submeter ao professor. |
| "Por que cai tudo em 'Biology'?" | É a classe 'default' da árvore quando os IDs de token não batem com o decorado. |
| "A ontologia está errada?" | Não — `transportation→geography,race` bate com o TTL de Fabris. O erro é só no **estágio 1**. |

---

## Divisão rápida (cola)

| Participante | Bloco | Slides | Mensagem-chave |
|---|---|---|---|
| **1** | O artigo: o que é/faz | 1-5 | "Recomendador *context-aware*: 2 classificadores + Fabris; promete 0,98, só testado no sintético" |
| **2** | Ontologia, datasets, métricas | 6-12 | "1260 US reais; colapsa 0,98→0,125; mas acerta 118 — por quê?" |
| **3** | Técnica + defeito | 13-18 | "Lê a forma do token, não o significado: acerta quando o papel coincide, e a correção quadruplica" |

---

## Material de apoio
- **Visão geral:** [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md)
- **Técnico (P3):** [refair-vetorizacao-e-defeito-do-parser.md](refair-vetorizacao-e-defeito-do-parser.md) · [analise-raiz-xgboost.md](analise-raiz-xgboost.md)
- **ELI5:** [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md)
- **Métricas (P2):** [metricas-formais-item-a.md](metricas-formais-item-a.md) · [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md)
- **Correção (P3 slide 17):** [roadmap-80-porcento.md](roadmap-80-porcento.md)
- **Artigo / repositório:** README do ReFAIR · refs [1] Fabris et al. 2022 · [2] Duran-Silva et al. 2021

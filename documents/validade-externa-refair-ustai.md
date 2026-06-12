# Validade Externa do ReFAIR — Plano de Análise com o Dataset UStAI

**Data:** 2026-05-21
**Projeto:** IN-0953-ReFair
**O que este documento é:** o detalhamento operacional da **Rota A** levantada em [analise-replicacao-novo-dataset.md](analise-replicacao-novo-dataset.md) (Seção 5.1 — "Estudo de Caso de Validade Externa"). Aqui a rota deixa de ser uma ideia e vira um **plano executável**, ancorado em um dataset concreto — o **UStAI** — e na equivalência que já construímos.

---

## 1. Pergunta de pesquisa

> **RQ principal:** *"O ReFAIR funciona para dados que nunca viu?"*

Em termos técnicos: o ReFAIR é treinado sobre o dataset **Synthetic User Stories**. A pergunta é se ele **generaliza** — se, aplicado a user stories de **outra origem e outra distribuição** (o UStAI), ele continua classificando domínio e ML task corretamente e recomendando *sensitive features* coerentes.

Sub-perguntas, uma por estágio da pipeline:

- **RQ1 — Domínio.** O classificador de domínio acerta o domínio de aplicação de US que não vieram da ontologia de treino?
- **RQ2 — ML task.** O classificador multi-label de ML tasks acerta o conjunto de tasks de US escritas em linguagem de negócio?
- **RQ3 — Sensitive features.** As *sensitive features* recomendadas no fim da pipeline fazem sentido para o contexto real de cada US?

## 2. A ideia em uma frase

Pegar o **UStAI** (nunca usado no treino), passar suas user stories pelo **ReFAIR já treinado e congelado** (sem retreino, como caixa-preta) e **comparar a saída de cada estágio com um *ground truth***. A distância entre o que o ReFAIR prevê e o *ground truth* é a medida da generalização.

> **Princípio inegociável:** o ReFAIR **não é retreinado** com o UStAI. Treina-se (ou usam-se os pesos do paper) **só** no dataset Synthetic; o UStAI é **exclusivamente teste**. Retreinar no UStAI destruiria o experimento — deixaria de ser um teste de dados "nunca vistos".

## 3. Por que o UStAI serve para este teste

Dataset **UStAI** — `Asma/UStAI` no Hugging Face (`https://huggingface.co/datasets/Asma/UStAI`), licença Apache 2.0.

| Característica | Por que importa para o nosso teste |
|---|---|
| **Público e citável** | Reprodutibilidade — qualquer um pode rebaixar o dataset e conferir. |
| **Semissintético** | 1260 user stories geradas por **3 LLMs** (Gemini 1.5 Flash, Llama 3.1 70b, O1-mini) a partir de **42 abstracts de papers reais** de sistemas de IA/ML. |
| **Mesmo gênero do alvo do ReFAIR** | São US de sistemas de IA — exatamente o tipo de entrada que o ReFAIR espera. |
| **Já vem anotado** | Tem colunas de análise — `Implied ethical needs`, `Non-Functional Requirements` e ~13 colunas de qualidade de US. |
| **É *out-of-distribution*** | As US do UStAI **não** foram geradas a partir dos 34 domínios nem do dicionário de ML do ReFAIR. Origem diferente = teste de generalização **legítimo**. |

> **Ressalva honesta sobre o "out-of-distribution".** UStAI e Synthetic são **ambos** conjuntos de US geradas por LLM. UStAI é uma distribuição **diferente** (origem em abstracts reais, outros LLMs, linguagem mais de negócio), mas **não** é um dataset 100% humano. A conclusão correta do estudo é "o ReFAIR generaliza para US de **outra origem sintética**" — não "generaliza para US humanas". É uma limitação a declarar, não a esconder (ver Seção 9).

## 4. O ativo que já temos: a equivalência pronta

O passo mais caro de um estudo de validade externa — **construir o *ground truth*** — **já está feito** para os dois primeiros estágios. A equivalência em [equivalencia-dominios-ustai-synthetic.md](equivalencia-dominios-ustai-synthetic.md) / [equivalencia-ustai-synthetic.csv](datasets/equivalencia-ustai-synthetic.csv) fornece, para **cada uma das 1260 US**:

| Coluna da equivalência | Serve como |
|---|---|
| `equivalent_domain` | **Ground truth do Estágio 1** — 1 dos 34 domínios do ReFAIR |
| `equivalent_ml_task_labels` | **Ground truth do Estágio 2** — conjunto **multi-label** de labels de ML task (dos 25 do ReFAIR) |
| `equivalent_ml_task` | ML task *fine-grained* âncora (apoio à interpretação) |
| `domain_confidence` | Permite estratificar a avaliação por confiança do *ground truth* |

> **Consequência:** a Rota A deixa de ser um estudo **puramente qualitativo** (como descrito na Seção 5.1 da análise original) e passa a ser **quantitativa** para RQ1 e RQ2 — temos rótulos de referência para comparar. Esse é o maior salto de qualidade desta versão do plano.

## 5. Os três estágios do ReFAIR e como avaliar cada um

A pipeline do ReFAIR tem três estágios. Avaliamos **cada um separadamente** — isso permite saber **onde** o ReFAIR falha, não só **se** falha.

### 5.1. Estágio 1 — Classificador de domínio (single-label)

- **Entrada:** texto bruto da US.
- **Saída do ReFAIR:** 1 domínio (de 34).
- **Ground truth:** `equivalent_domain` da equivalência.
- **Tarefa:** classificação **single-label**.
- **Métricas:** Accuracy, F1-Score, precisão/revocação por classe, **matriz de confusão**.
- **Ressalva:** o UStAI cobre **25 dos 34** domínios. Os 9 domínios sem US no UStAI **não podem ser testados** — declarar isso e reportar métricas só sobre os 25 cobertos.

### 5.2. Estágio 2 — Classificador de ML task (multi-label)

- **Entrada:** texto bruto da US.
- **Saída do ReFAIR:** **conjunto** de labels de ML task (classificação multi-label — Linear SVC + Label Powerset).
- **Ground truth:** `equivalent_ml_task_labels` da equivalência (conjunto de labels dos 25 de alto nível).
- **Tarefa:** classificação **multi-label**.
- **Métricas:** F1-Score, **Hamming loss**, **Subset accuracy** (exact-match), precisão/revocação por label.
- **Comparação-chave:** confrontar com o F1 reportado no paper original (≈90% com `Label Powerset + GloVe + LSVC`, *in-distribution*). Uma queda grande no UStAI = ReFAIR não generaliza na RQ2.

### 5.3. Estágio 3 — Recomendação de *sensitive features*

- **Entrada:** o par `(domínio, tasks)` previsto pelos estágios 1 e 2.
- **Saída do ReFAIR:** *sensitive features* recomendadas, **consultadas no mapping** `(domínio × task) → sensitive features`.
- **Ground truth:** **não existe pronto** — ver Seção 6. Avaliação **híbrida** (quantitativa parcial + painel de especialistas).
- **Métricas:** Precision@k / cobertura contra anotação manual de uma amostra; notas do painel (utilidade, correção, falsos positivos); coerência com a coluna `Implied ethical needs`.

### Análise de erros end-to-end

Como avaliamos os três estágios separadamente, quando a recomendação final do Estágio 3 for ruim conseguimos **decompor a causa**: erro de domínio (Estágio 1), erro de task (Estágio 2) ou limitação do próprio *mapping*. Essa decomposição é, por si só, uma contribuição do trabalho.

## 6. A ressalva crítica: `Implied ethical needs` ≠ `sensitive features`

Esta é a parte que **exige mais cuidado** e que precisa estar clara para o professor.

- O ReFAIR recomenda **sensitive features** = **atributos protegidos** que devem ser checados quanto a viés: *gender, age, race/ethnicity, religion, disability, sexual orientation, socioeconomic status*, etc.
- A coluna **`Implied ethical needs`** do UStAI traz **princípios éticos** (são 71 valores distintos): *Non-maleficence (Safety), Privacy, Sustainability, Beneficence, Responsibility*, etc. — vocabulário de **ética de IA**, não de atributos demográficos.

**São construtos diferentes.** `Privacy`, `Safety` e `Sustainability` não correspondem a nenhum atributo protegido. Logo, **`Implied ethical needs` não é um *ground truth* direto** para o Estágio 3.

Como usar a coluna mesmo assim, de forma honesta:

1. **Como filtro de relevância.** Princípios ligados a equidade (*Justice, Fairness, Non-discrimination, Inclusiveness* — quando presentes) marcam as US em que o ReFAIR **deveria** recomendar *sensitive features* não-triviais. US cujo princípio é apenas `Privacy`/`Safety` são casos em que a recomendação de *sensitive features* é menos central.
2. **Como verificação de coerência.** Cruzar: quando `Implied ethical needs` aponta justiça/inclusão, a recomendação do ReFAIR é compatível?
3. **O *ground truth* real do Estágio 3 deve ser construído.** O caminho rigoroso é **anotar manualmente as *sensitive features*** de uma **amostra estratificada** de US do UStAI, usando o texto e o `role_shorten` (o papel frequentemente nomeia o grupo — ex.: *"visually impaired person"* → `disability`). Essa anotação, somada ao painel de especialistas, dá a avaliação do Estágio 3.

> **Resumo:** Estágios 1 e 2 têm avaliação **quantitativa forte** (ground truth pronto). Estágio 3 é o **elo mais fraco** para métricas exatas — fica **híbrido** (amostra anotada + painel + coerência com `Implied ethical needs`). Isso deve ser dito explicitamente no relatório.

## 7. Pipeline de execução (passo a passo)

**Preparação**

1. **Baixar o UStAI** da Hugging Face em CSV completo (1260 linhas, **todas** as colunas, incluindo `Implied ethical needs`). Preferir o CSV da HF à extração do PDF — é mais limpo e traz todas as colunas.
2. **Obter o ReFAIR treinado:** usar os pesos/modelos do paper original (pasta `ReFAIR/` do projeto) **ou** retreinar **apenas no dataset Synthetic**. Em nenhuma hipótese treinar no UStAI.
3. **Consolidar o *ground truth*:** juntar (`join` pela coluna `id`) o UStAI com [equivalencia-ustai-synthetic.csv](datasets/equivalencia-ustai-synthetic.csv) → tabela única com texto da US + `equivalent_domain` + `equivalent_ml_task_labels` + `Implied ethical needs`.
4. **Garantir o mesmo pré-processamento/embedding** que o ReFAIR usou no treino (mesmo tokenizador, mesmo modelo de embedding) — senão a comparação é injusta.

**Execução (ReFAIR congelado)**

5. Passar as 1260 US (texto bruto) pelo **classificador de domínio** → predição de domínio por US.
6. Passar as 1260 US pelo **classificador multi-label de ML task** → conjunto de tasks por US.
7. Para cada US, consultar o ***mapping*** `(domínio × task) → sensitive features` → recomendação final.

**Avaliação**

8. **Estágio 1:** predição vs `equivalent_domain` → Accuracy, F1-Score, matriz de confusão (25 domínios cobertos).
9. **Estágio 2:** predição vs `equivalent_ml_task_labels` → F1-Score, Hamming loss, Subset accuracy.
10. **Estágio 3:** anotar manualmente *sensitive features* de uma amostra estratificada (~100–150 US, balanceada por domínio e por `domain_confidence`); painel de 3–4 pessoas avalia utilidade/correção; cruzar com `Implied ethical needs`.
11. **Análise de erros:** para cada falha do Estágio 3, classificar a causa (domínio / task / mapping).
12. **Estratificar tudo** por `domain_confidence` (High/Medium/Low) e por LLM gerador — verifica se o ReFAIR vai pior nos casos de baixa confiança ou em algum LLM.

## 8. Métricas e critério de "funciona"

| Estágio | Métricas | Referência de comparação |
|---|---|---|
| 1 — Domínio | Accuracy, F1-Score, confusão | F1 *in-distribution* do paper (XGBoost) |
| 2 — ML task | F1-Score, Hamming loss, Subset accuracy | ≈90% F1 do paper (LP+GloVe+LSVC) |
| 3 — Sensitive features | Precision@k, cobertura, notas do painel, coerência | Anotação manual da amostra |

**Critério de decisão.** O ReFAIR "generaliza bem" se as métricas no UStAI ficarem **próximas** das *in-distribution* do paper; "generaliza mal" se houver **queda acentuada**. O limiar exato (ex.: queda de F1 > 15–20 pontos) deve ser **acordado com o professor antes** de rodar — para não parecer escolhido depois do resultado.

## 9. Ameaças à validade (a declarar no relatório)

- **O *ground truth* dos Estágios 1 e 2 é a nossa própria equivalência.** Foi construído por análise temática dos 42 abstracts — é defensável, mas **não é um *gold standard* independente**. Mitigação: ter **2+ anotadores** revisando uma amostra e medir **concordância** (Cohen's κ); submeter uma amostra ao professor.
- **Domínio fixado por *abstract*.** A equivalência atribui 1 domínio por abstract (todas as 30 US do abstract herdam). É uma granularidade grossa — US "fora do tema" mantêm o domínio do abstract.
- **Cobertura parcial:** 25 dos 34 domínios; 9 domínios não são testados.
- **`Implied ethical needs` ≠ `sensitive features`** (Seção 6) — Estágio 3 sem *ground truth* exato.
- **UStAI também é sintético** (Seção 3) — a generalização comprovada é para outra origem **sintética**, não para US humanas.
- **Labels multi-label herdadas da `task augmentation mapping`** do ReFAIR — o *ground truth* do Estágio 2 carrega as escolhas dessa tabela.
- **Risco de *mismatch* de pré-processamento** entre treino (Synthetic) e teste (UStAI) — controlar no passo 4.

## 10. Checklist do que é preciso ter

- [ ] Repositório ReFAIR + modelos treinados (ou pipeline de treino só no Synthetic)
- [ ] *Mapping* `(domínio × task) → sensitive features` do ReFAIR
- [ ] UStAI em CSV completo (Hugging Face)
- [x] Equivalência UStAI ↔ Synthetic (domínio + ML task multi-label) — **já feita**
- [ ] Anotação manual de *sensitive features* de uma amostra estratificada do UStAI
- [ ] Painel de 3–4 avaliadores (equipe / professor)
- [ ] Limiar de "funciona / não funciona" acordado com o professor

## 11. Resultado esperado e contribuição

Independentemente de o ReFAIR generalizar bem ou mal, o trabalho entrega uma **contribuição científica válida**:

- Se **generaliza bem:** evidência de que o ReFAIR é robusto fora da sua distribuição de treino — reforça o método.
- Se **generaliza mal:** mapeamos **onde** quebra (qual estágio, quais domínios, quais LLMs) — diagnóstico útil para evoluir o ReFAIR.

A pergunta *"o ReFAIR funciona para dados que nunca viu?"* é respondida com **métricas por estágio + análise de erros**, e não com uma replicação forçada. Isso resolve, com honestidade, o impasse levantado na análise de viabilidade: usamos o dataset novo **onde ele é adequado** (teste de generalização) em vez de fingir uma replicação que ele não suporta.

---

## Relação com os outros documentos do projeto

- [analise-replicacao-novo-dataset.md](analise-replicacao-novo-dataset.md) — por que a replicação fiel não é viável e por que a validade externa é a saída. **Este documento executa a Rota A de lá.**
- [equivalencia-dominios-ustai-synthetic.md](equivalencia-dominios-ustai-synthetic.md) — o *ground truth* de domínio e ML task usado aqui.
- Combinar com a **Rota C** (extensão metodológica) da análise original transforma o trabalho em duas RQs: *validade externa* (este plano) + *extensão metodológica* (combinações de embedding × classificador não testadas pelos autores).

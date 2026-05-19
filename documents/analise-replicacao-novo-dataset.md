# Análise de Viabilidade — Replicação do ReFAIR com Novo Dataset

**Data:** 2026-05-18
**Contexto:** Reunião com o professor prevista para amanhã. Objetivo do documento: explicar, com fundamentação técnica, por que o novo dataset (apenas user stories) **não permite uma replicação fiel do ReFAIR** e propor uma alternativa diferente da que a equipe levantou.

---

## 1. Como o ReFAIR funciona (visão rápida para fundamentar o argumento)

O ReFAIR é uma pipeline com **três artefatos rotulados** que precisam existir juntos para o método funcionar:

1. **Dicionário de 34 domínios de aplicação** (Estudos Urbanos, Saúde, Educação, etc.) — origem: ontologia de Fabris et al. (2022).
2. **Dicionário de tasks de ML** (classificação, regressão, clustering, NLP, …) — origem: vocabulário controlado de Duran-Silva et al. (2021).
3. **Mapeamento `(domínio × task) → sensitive features`** — construído manualmente a partir da literatura.

As **user stories sintéticas** existem **apenas como veículo** para treinar dois classificadores supervisionados sobre esses três artefatos:

- **Single-Label Classifier (XGB):** US → domínio.
- **Multi-Label Classifier (Linear SVC com Label Powerset):** US → tasks de ML.

Por fim, o módulo de _Features Extraction_ consulta o mapping e retorna as sensitive features. Sem domínio e sem task detectados, o último passo não tem o que consultar.

> **Implicação chave:** o ground truth do ReFAIR não está nas user stories — está nos dicionários e no mapping. As user stories são apenas a superfície linguística que liga uma entrada textual a um par `(domínio, task)` rotulado.

---

## 2. A pergunta da equipe: "dá pra rodar só com as user stories?"

**Resposta curta: não, não na forma de replicação.**

**Por quê:**

- As US sintéticas do ReFAIR foram **geradas a partir dos 34 domínios e do dicionário de ML**. Cada US já carrega, por construção, um rótulo de domínio e um conjunto de tasks. É **dataset rotulado**, não texto livre.
- O novo dataset que recebemos é **apenas o texto** das user stories. Sem os rótulos de domínio e de task, **não temos como treinar nem avaliar** os dois classificadores do ReFAIR.
- Mesmo que rotulássemos manualmente, **não há garantia** de que as US do novo dataset:
  - cubram os 34 domínios da ontologia de Fabris (provavelmente cobrem 1 só),
  - mencionem tasks de ML (US de negócio normalmente não falam de classificação/regressão explicitamente),
  - tenham conexão com o mapping de sensitive features (que é específico para pares domínio×task de ML).
- Em outras palavras: **não dá para "pular a etapa"** dos dicionários e do mapping, porque eles **são** o ReFAIR. Sem eles, o que sobra (rodar classificadores em texto) não é mais ReFAIR — é um classificador de texto qualquer.

---

## 3. Por que o novo dataset **não atende aos parâmetros de replicação**

Argumentos a apresentar ao professor (em ordem de força):

### 3.1. Ausência do oráculo (ground truth)
- O oráculo do ReFAIR são os pares `(domínio, task)` atribuídos às US **na geração**.
- As US do novo dataset **não foram geradas a partir dos 34 domínios** nem do dicionário de ML — logo, **não existe oráculo compatível**.
- Datasets públicos de US **rotuladas com domínio + tasks de ML** são **raros ou inexistentes**. Construir um manualmente exigiria expertise em fairness ML e levaria meses.

### 3.2. Mismatch de domínio
- Se as US novas são de um único contexto de aplicação (ex.: um sistema específico), elas cobrem **1 domínio**, não 34. O classificador de domínio do ReFAIR **não tem o que fazer** — vai prever sempre a mesma classe, ou pior, classes erradas porque o vocabulário não bate.

### 3.3. Mismatch de tasks de ML
- User stories de negócio raramente são escritas em termos de ML ("o sistema deve classificar…", "predizer…"). Se as US novas são funcionais/de produto, **não há sinal textual** para o classificador multi-label de tasks.
- **Classificar tasks de ML em US que não falam de ML não é possível** — é tentar prever um rótulo que **não está no input**.

### 3.4. Sensitive features dependem do mapping
- Mesmo que conseguíssemos forçar uma classificação, as sensitive features só existem **para pares domínio×task presentes no mapping**. Se cair fora, o ReFAIR não tem recomendação a fazer.

**Conclusão técnica:** replicar o ReFAIR com este dataset **viola três dos quatro pilares do método** (oráculo, dicionário de domínios, dicionário de tasks). O que restaria seria um experimento sem validade interna.

---

## 4. Análise crítica da proposta atual da equipe

A equipe propôs:

| # | Proposta | Avaliação |
|---|----------|-----------|
| 1 | Usar apenas um domínio (ex.: Estudos Urbanos), eliminando o classificador de domínio | Resolve o problema dos 34 domínios, **mas** ao remover o classificador deixamos de replicar metade do ReFAIR. Vira um "ReFAIR reduzido". |
| 2 | Substituir BERT por BERTimbau (PT-BR) | Faz sentido **se** as US estiverem em português. É uma adaptação razoável, não uma replicação. |
| 3 | Usar 2–3 algoritmos (Decision Tree, Logistic Regression) em vez de todos | Reduz custo, mas perde a comparação ampla que era um dos resultados do paper original. |
| 4 | Random Forest no lugar do XGBoost | Trocar XGBoost por Random Forest é defensável (são modelos comparáveis), mas **não resolve o problema central**, que é a falta de rótulos. |

**Limitação fundamental que a proposta da equipe não endereça:** mesmo com 1 domínio, BERTimbau e Random Forest, **ainda precisamos rotular as US com tasks de ML**. Se as US não falam de ML, esse rótulo não existe — e o classificador multi-label fica sem dado de treino. A proposta **mascara o problema, mas não o resolve**.

---

## 5. Proposta alternativa ( para levar amanhã)

> **Tese a defender:** "Após analisar o novo dataset, concluímos que ele **não corresponde aos parâmetros necessários** para replicar o ReFAIR no contexto original. Em vez de uma replicação artificial, propomos um **estudo de caso de validade externa** — usar o novo dataset como entrada para o ReFAIR já treinado e medir qualitativamente a qualidade das recomendações."

### 5.1. Estudo de Caso de Validade Externa (sem retreino)

Em vez de retreinar o ReFAIR com um dataset inadequado, **usamos o ReFAIR já treinado** (com os pesos e modelos do paper original) **como caixa-preta** e fazemos:

1. **Entrada:** as US do novo dataset (sem rótulo).
2. **Saída:** as sensitive features que o ReFAIR recomenda.
3. **Avaliação:** painel de especialistas (3–4 pessoas da equipe / professor) avalia, por amostragem, se as recomendações **fazem sentido** para aquele contexto. Métricas qualitativas: precisão percebida, utilidade, falsos positivos.

**Vantagens:**
- **Não precisa de oráculo** — a avaliação é human-in-the-loop.
- **Mantém o ReFAIR íntegro** — não distorcemos o método para caber no dado.
- **Contribuição científica diferente e válida:** "avaliamos a validade externa do ReFAIR aplicando-o a US fora da distribuição de treino".
- Replica o **espírito** do ReFAIR (recomendar sensitive features) sem fingir replicar o que não dá.

**Desvantagens / o que admitir:**
- Não há métrica numérica como F1.
- Resultado é descritivo, não estatístico.

### 5.2. Variação opcional: baseline LLM zero-shot

Como **comparativo extra** (não substitui o ReFAIR), rodar a mesma tarefa com um LLM zero-shot (Claude/GPT) recebendo o mapping de sensitive features como contexto e a US como entrada. Compara-se qualitativamente:

- ReFAIR (clássico) **vs.** LLM zero-shot

Isso dá um segundo eixo de discussão e mostra que **pensamos no problema além da replicação mecânica**.

### 5.3. Extensão metodológica do estudo original (sem depender do dataset novo)

> **Quando essa rota faz sentido:** se decidirmos **não usar o dataset novo** para o experimento principal (porque ele não permite replicação fiel — ver seção 3) e ao invés disso **estender o trabalho original** sobre o dataset sintético já rotulado.

A ideia é manter o pipeline do ReFAIR e **preencher lacunas que os próprios autores deixaram**, propondo combinações de embedding × classificador que não foram avaliadas no paper. É uma contribuição do tipo "ablation / extension study".

#### O que se varia

**Variação 1 — Embeddings não testados pelos autores**

Os autores testaram: `TF-IDF`, `BERT`, `Word2Vec`, `FastText`, `GloVe`. Adicionar:

- **RoBERTa** — versão melhorada do BERT, treinada com mais dados e sem o NSP.
- **sentence-transformers** (ex.: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`) — desenhados para similaridade semântica de frases, que é exatamente o caso de US.
- **GPT embeddings** (ex.: `text-embedding-3-small` via API da OpenAI) — estado-da-arte em embeddings, ainda não usado no domínio de fairness requirements.

**Variação 2 — Classificadores de domínio (RQ1)**

Os autores varreram 25 algoritmos via LazyPredict e o XGBoost venceu. Testar alternativas modernas que não estavam no LazyPredict (ou que valem refinamento dedicado):

- **LightGBM** — alternativa direta ao XGBoost, tipicamente mais rápida.
- **CatBoost** — outro gradient boosting robusto, lida bem com features categóricas.

**Variação 3 — Classificadores de tarefa ML (RQ2)**

A combinação vencedora foi `Label Powerset + GloVe + LSVC` (≈90% F1). Combinações não exploradas:

- **BERT + Label Powerset + LSVC** — os autores testaram BERT e testaram LP+LSVC, mas **não cruzaram** as duas escolhas.
- **RoBERTa + Label Powerset + Random Forest** — embedding mais forte + classificador multi-label diferente.

#### Por que essa variação é defensável

- **Usa o dataset original rotulado** — não tem o problema do oráculo ausente que afeta o dataset novo (seção 3.1).
- **Contribuição clara para o paper:** "preenchemos lacunas combinatórias do estudo original, identificando se há combinações superiores às reportadas pelos autores".
- Mantém RQ1 e RQ2 originais, só amplia o grid de hiperparâmetros/modelos.
- Resultado é **numérico e comparável** (F1, acurácia) — diferente da abordagem qualitativa da seção 5.1.

#### Limitações honestas

- **Não usa o dataset novo** — se o professor insistir que o dataset novo precisa entrar no experimento, essa rota sozinha não atende.
- Pode acabar virando um estudo de **engenharia** (rodar mais modelos) em vez de uma **contribuição conceitual** — depende de como narrarmos os resultados.
- Custo computacional dos embeddings mais pesados (GPT embeddings tem custo de API; RoBERTa exige GPU para tempo aceitável).

#### Combinação possível

A seção 5.1 (estudo de caso com dataset novo) e a seção 5.3 (extensão metodológica com dataset original) **não são mutuamente exclusivas**. Podem virar **duas RQs novas** do nosso trabalho:

- **RQ-nossa-1 (extensão):** combinações não testadas superam o estado-da-arte do paper original no dataset sintético?
- **RQ-nossa-2 (validade externa):** o ReFAIR generaliza para US fora do domínio de treino (dataset novo)?

Isso fica mais robusto que escolher só um caminho.

---

## 6. Roteiro sugerido para a conversa com o professor

1. Mostrar a análise do dataset novo (seção 3) — **fazer o que ele pediu** primeiro.
2. Concluir, com base em 3 pilares quebrados, que **a replicação não é viável** com o dataset novo.
3. Apresentar a proposta da equipe (seção 4) e ser **honestos** sobre a limitação dela.
4. Apresentar **três rotas alternativas** que sustentam um trabalho científico defensável:
   - **Rota A — Estudo de caso de validade externa (seção 5.1):** ReFAIR já treinado aplicado ao dataset novo, avaliação qualitativa por especialistas.
   - **Rota B — Baseline LLM zero-shot (seção 5.2):** comparativo extra usando LLM com o mapping como contexto.
   - **Rota C — Extensão metodológica (seção 5.3):** rodar combinações de embedding × classificador não testadas pelos autores **sobre o dataset original sintético**.
5. Sugerir, se possível, **combinar Rota A + Rota C** como duas RQs do nosso trabalho (validade externa + extensão metodológica).
6. Pedir alinhamento do professor sobre o escopo final.

---

## 7. Riscos e contingência

- Se o professor insistir na replicação: aceitar a versão reduzida da equipe **deixando registrado em ata** que o resultado terá validade interna limitada por causa do dataset.
- Se ele topar o estudo de caso: já temos como começar — só precisamos do ReFAIR rodando e das US do dataset novo passando pela pipeline.

---

## Referências do projeto original

- Fabris, A. et al. (2022). *Algorithmic fairness datasets: the story so far*. Data Mining and Knowledge Discovery, 36(6), 2074-2152.
- Duran-Silva, N. et al. (2021). *A controlled vocabulary for research and innovation in the field of AI*.
- Repositório ReFAIR original: pasta `ReFAIR/` neste projeto.

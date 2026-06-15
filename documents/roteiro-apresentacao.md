# Roteiro de apresentação — ReFAIR × UStAI (4 participantes)

**Duração-alvo:** ~20 min (4 × ~5 min) + perguntas.
**Estrutura:** cada participante tem um bloco fechado, com slides, fala (notas) e os números-chave. Termina com handoff pro próximo.
**Fonte dos números:** [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md).

> Dica geral: **um número por slide**. Não leiam o slide — contem a história. Os números em **negrito** são os que não podem faltar.

---

## Participante 1 — Contexto e Problema (~4-5 min) · slides 1-4

**Slide 1 — Capa**
- Título: *"O ReFAIR funciona fora do laboratório? Avaliação de validade externa em user stories reais"*. Nomes da equipe.

**Slide 2 — O problema**
- *Fala:* "Sistemas de ML podem discriminar pessoas — por idade, gênero, raça. Esses são os **atributos sensíveis**. O ideal é pensar neles **cedo**, na engenharia de requisitos, não depois do estrago."

**Slide 3 — O que é o ReFAIR**
- Mostrar a pipeline: `User Story → Domínio → ML Task → Atributos sensíveis`.
- *Fala:* "Dada uma user story, o ReFAIR diz quais atributos sensíveis monitorar. No artigo dele (ICSE'24), ele reporta **F1 = 0,98** na detecção de domínio."

**Slide 4 — A lacuna e as perguntas (handoff)**
- *Fala:* "Mas ele foi validado **só com user stories sintéticas**, num molde fixo — limitação que os **próprios autores** citam. Nossa pergunta: **e com user stories reais?** Daí as duas RQs: **(RQ1)** ele generaliza? **(RQ2)** dá pra consertar? — Passo pra [Participante 2] falar de como testamos."

> Números: **F1 0,98** (promessa do paper); **sintético only** (a lacuna).

---

## Participante 2 — Método e Plataformas (~5 min) · slides 5-8

**Slide 5 — O dataset UStAI**
- *Fala:* "Pegamos o **UStAI**: **1260 user stories** geradas por **3 LLMs** (Gemini, Llama, O1) a partir de **42 abstracts de papers reais**. Origem diferente = teste de generalização legítimo."

**Slide 6 — O gabarito (ground truth)**
- *Fala:* "Construímos manualmente o **gabarito dos 3 estágios** — domínio, ML task e atributos sensíveis correto de cada US — com nível de confiança. É a régua de comparação."

**Slide 7 — Como testamos (rigor)**
- *Fala:* "Rodamos o ReFAIR **congelado, sem retreino** — UStAI é só teste. Nas **versões exatas** das bibliotecas (pra ser determinístico). E medimos **estágio por estágio**."

**Slide 8 — Reprodutibilidade (handoff)**
- *Fala:* "Rodamos em **macOS e Windows** e deu **idêntico** — porque a inferência é determinística (o detector de domínio roda sobre números inteiros). Isso blinda os resultados. — [Participante 3], o que esses testes mostraram?"

> Números: **1260 US**, **3 LLMs**, **congelado**, **macOS = Windows** (0 divergências).

---

## Participante 3 — Resultados (~5 min) · slides 9-12

**Slide 9 — O resultado principal**
- Gráfico de barras: **0,98 → 0,125**.
- *Fala:* "O ReFAIR promete F1 0,98. No UStAI, a detecção de domínio cai pra **F1 0,125 — 9,4% de acerto**. Não é uma queda, é um **colapso**."

**Slide 10 — Por estágio**
- Tabela: Domínio **9,4%** · ML task **42,5% vazias** · Features **2,1%** match exato.
- *Fala:* "E piora a cada estágio: quase metade das US fica **sem nenhuma ML task**, e os atributos sensíveis acertam só 2%."

**Slide 11 — O colapso e os LLMs**
- Matriz de confusão (destacar a coluna "Biology").
- *Fala:* "O modelo joga **354 US em 'Biology'** — domínios totalmente diferentes na mesma caixa. E é ruim **nos 3 LLMs** igualmente — então o problema é do ReFAIR, não do gerador."

**Slide 12 — De onde vêm as falhas (handoff)**
- Pizza: **90,6%** estágio 1.
- *Fala:* "Decompondo: **90,6% das falhas nascem no estágio 1, o domínio**. Os outros estágios só herdam o erro. Então a pergunta é: **por que o domínio erra tanto?** — [Participante 4] abre a caixa-preta."

> Números: **0,98→0,125** · **9,4%** · **42,5% vazias** · **354→Biology** · **90,6%**.

---

## Participante 4 — Causa-raiz, Extensão e Conclusão (~5 min) · slides 13-17

**Slide 13 — A causa-raiz**
- Mostrar: a frase "As a **[papel]**, I want…" com a **posição 3** destacada.
- *Fala:* "O detector de domínio não lê o **significado** — ele recebe os **IDs de token por posição**. E a feature mais importante é a **posição 3: a palavra do papel**."

**Slide 14 — A prova (a parte forte)**
- Tabela da permutação: posição 3 → **25,3%** · conteúdo → **99,4%**.
- *Fala:* "Provamos assim: se a gente embaralha **só o papel**, o acerto despenca de ~100% pra **25%**. Se embaralha o **conteúdo** da story, **não muda nada** (99,4%). Ou seja: **o modelo ignora o conteúdo e decide pelo molde**. No treino, o papel **é** o nome do domínio (Transportation→'transportation'); no UStAI, **51% dos papéis ele nunca viu** ('driver', 'parent'…). Por isso decora e não generaliza."

**Slide 15 — A correção (extensão / RQ2)**
- Barras: 9,4% → **37%**.
- *Fala:* "Pra confirmar que a culpa é da representação, mudamos **só uma coisa**: trocamos os IDs de token por **embeddings semânticos**. O acerto **quadruplicou: 9,4% → 37%**. Mesmo dataset, mesma tarefa — só a representação. Isso **prova** que a representação era o problema."

**Slide 16 — Conclusão e contribuição**
- *Fala:* "Então: **(1)** o ReFAIR não generaliza pra US reais; **(2)** descobrimos **por quê** — ele decora forma, não significado; **(3)** mostramos o **caminho do conserto**. É um resultado negativo **bem fundamentado** + um **diagnóstico com remediação**."

**Slide 17 — Limitações e próximos passos**
- *Fala:* "Limitações honestas: o gabarito é nosso (vamos medir concordância), o UStAI ainda é gerado por LLM, e o estágio 3 precisa de anotação humana. Próximo passo: empurrar a correção (sentence-transformers, LLM) rumo a 80%. **Obrigado!**"

> Números: **posição 3** · **25,3% vs 99,4%** (permutação) · **51% papéis nunca vistos** · **9,4%→37% (4×)**.

---

## Apêndice — perguntas prováveis e respostas curtas

| Pergunta | Resposta de bolso |
|---|---|
| "Isso é replicação?" | Não — é **validade externa** (ferramenta inalterada em dados novos) + **extensão**. A replicação da alegação do paper a gente confirmou pelo 100% no treino. |
| "Por que não retreinar no UStAI?" | Destruiria o teste de generalização — UStAI tem que ser **só teste**. |
| "37% ainda é baixo." | É **limite inferior** (BERT cru, pouca amostra). O ponto é o **4×** com uma mudança só — prova a causa. sentence-transformers/LLM vão além. |
| "O gabarito não é enviesado?" | Por isso vamos medir **concordância entre anotadores (κ)** e submeter ao professor. |
| "Por que cai tudo em 'Biology'?" | É a classe 'default' da árvore quando os IDs de token não batem com o que ela decorou. |

---

## Divisão rápida (cola)

| Participante | Bloco | Slides | Mensagem-chave |
|---|---|---|---|
| **1** | Contexto/Problema | 1-4 | "ReFAIR promete 0,98, mas só foi testado no sintético" |
| **2** | Método/Plataformas | 5-8 | "Testamos com 1260 US reais, congelado, reprodutível" |
| **3** | Resultados | 9-12 | "Colapsa: 0,98→0,125, e 90% da culpa é o domínio" |
| **4** | Causa-raiz/Extensão | 13-17 | "Decora o molde, não o sentido — e a correção quadruplica" |

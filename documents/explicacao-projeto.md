# Explicação do projeto — ReFAIR × UStAI (IN-0953)

**Resumo de uma página** do estudo, nos tópicos da entrega (contexto, problema, solução, replicação, resultados, conclusões, trabalhos relacionados). Versão completa em [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md).

---

## Contexto
Sistemas de ML podem discriminar pessoas por atributos sensíveis (idade, gênero, raça). O ideal é tratar isso cedo, na **engenharia de requisitos**. O **ReFAIR** (Ferrara et al., ICSE'24) é uma ferramenta que, a partir de uma *user story*, recomenda os atributos sensíveis a monitorar, em **3 estágios**: domínio → tarefa de ML → atributos sensíveis.

## Problema
O ReFAIR foi validado **apenas com user stories sintéticas**, geradas da própria ontologia num molde fixo — limitação que os próprios autores citam. Nunca foi testado em user stories de **contexto real**. Nossa pergunta: ele **generaliza**? (RQ1) E, se falhar, **dá para consertar**? (RQ2)

## Solução avaliada
A solução é o próprio ReFAIR: **dois classificadores** (domínio via BERT+XGBoost; tarefa via GloVe+LinearSVC) + um **mapeamento da ontologia de Fabris** para os atributos sensíveis. No paper, reporta **F1 ≈ 0,98** (domínio).

## Como foi replicada / avaliada
Rodamos o ReFAIR **congelado, sem retreino**, sobre o dataset **UStAI** (1260 user stories = 42 abstracts reais × 3 LLMs × 10), comparando estágio a estágio com um **gabarito construído manualmente**. Tudo nas **versões exatas** das bibliotecas e empacotado em **Docker** (replicação determinística; resultado idêntico em macOS e Windows).

## Resultados
O ReFAIR **colapsa** fora do laboratório: domínio **F1 0,98 → 0,125 (9,4%)**, e 354 user stories caem todas em "Biology". **90,6% das falhas nascem no estágio 1**. Abrindo a caixa-preta, descobrimos a **causa-raiz**: o detector entrega ao classificador os IDs de token por **posição** (não o significado) e decide pela palavra do papel na **posição 3** — provado por **permutação** (embaralhar o papel: 99,5% → 25,3%; embaralhar o conteúdo: 99,4%, não muda). Como **extensão**, trocamos a representação do domínio por **embeddings** (9,4% → **37%**) e reformamos o estágio 2 (F1 0,13 → **0,28**).

## Principais conclusões / lições
1. Alto desempenho *in-distribution* **não garante** generalização.
2. O ReFAIR **decora a forma**, não o significado.
3. O defeito está na **representação de entrada** — e trocá-la **quadruplica** o acerto.
4. Validade externa exige dados de **outra origem** — e ainda assim o UStAI é gerado por LLM (não humano), uma **limitação honesta**.

## Trabalhos relacionados
ReFAIR (Ferrara et al., ICSE'24); ontologia de fairness de **Fabris et al., 2022** (*Algorithmic fairness datasets: the story so far*); vocabulário de tarefas de IA de **Duran-Silva et al., 2021**; literatura de *fairness-aware ML* e *fairness em engenharia de requisitos*.

---

*Documentos relacionados: [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md) (completo) · [analise-raiz-xgboost.md](analise-raiz-xgboost.md) (causa-raiz) · [passo-a-passo-extensao-37.md](passo-a-passo-extensao-37.md) (extensão) · [ameacas-a-validade.md](ameacas-a-validade.md) (validade) · [apresentacao-3-pessoas.md](apresentacao-3-pessoas.md).*

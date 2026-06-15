# Ameaças à validade — ReFAIR × UStAI (e a extensão)

**Data:** 2026-06-14
**O que este doc é:** a análise completa de **ameaças à validade** do estudo, pelas quatro categorias clássicas (construto, interna, externa, conclusão) + reprodutibilidade. Cada ameaça vem com **gravidade**, **status** (mitigada / aberta) e **mitigação**.
**Por que separado:** o estudo tem **duas perguntas com perfis de risco diferentes** — a **RQ1** (mostrar que o ReFAIR não generaliza) é robusta; a **RQ2** (a extensão por embeddings) tem ameaças mais sérias que precisam ser declaradas.
**Docs relacionados:** [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md) · [analise-raiz-xgboost.md](analise-raiz-xgboost.md) · [passo-a-passo-extensao-37.md](passo-a-passo-extensao-37.md).

---

## 0. Mapa de gravidade (visão rápida)

| # | Ameaça | Categoria | Afeta | Gravidade | Status |
|---|---|---|---|---|---|
| 1 | Gabarito é a nossa própria equivalência | Construto | RQ1+RQ2 | Alta | aberta (κ planejado) |
| 2 | Gabarito de ML task é permissivo | Construto | RQ1+RQ2 | Alta | aberta |
| 3 | Domínio anotado por abstract | Construto | RQ1+RQ2 | Média | aberta |
| 4 | Estágio 3 derivado do mapping | Construto | RQ1+RQ2 | Média | aberta |
| 5 | Limiar do estágio 2 ajustado no teste | Interna | RQ2 | Alta | **mitigada** (re-sintonizado no sintético) |
| 6 | Estágio 2 mudou várias coisas juntas | Interna | RQ2 | Média-alta | **mitigada** (ablação isolou cada uma) |
| 7 | Causa-raiz (posição 3) | Interna | RQ1 | Baixa | **mitigada** (permutação) |
| 8 | Ablação do domínio (1 variável) | Interna | RQ2 | Baixa | **mitigada** |
| 9 | UStAI também é gerado por LLM | Externa | RQ1+RQ2 | Alta | declarada |
| 10 | Cobertura parcial (25/34 domínios) | Externa | RQ1+RQ2 | Média | declarada |
| 11 | Poucos abstracts/geradores | Externa | RQ1+RQ2 | Média | declarada |
| 12 | Específico à versão do ReFAIR | Externa | RQ1 | Baixa | declarada |
| 13 | Sem teste de significância / IC | Conclusão | RQ1+RQ2 | Média | aberta |
| 14 | Suporte pequeno por classe | Conclusão | RQ1+RQ2 | Média | declarada |
| 15 | Desbalanceamento de classes | Conclusão | RQ1+RQ2 | Baixa | **mitigada** (micro≈macro) |
| 16 | Determinismo / reprodutibilidade | Reprodutib. | RQ1+RQ2 | Baixa | **mitigada** |

---

## 1. Validade de construto — *estamos medindo o que pensamos medir?*

**1.1 Gabarito é a nossa própria equivalência (Alta).**
A "verdade" usada nas métricas é a equivalência domínio/tarefa/atributo que **nós** construímos (`ustai-gabarito-completo.csv`), não um padrão-ouro independente. Risco de subjetividade e de circularidade (rotular a favor do que esperamos).
→ *Mitigação:* medir **concordância entre anotadores (Cohen's κ)** com um segundo anotador e revisão do professor; já registramos `domain_confidence` por item.

**1.2 Gabarito de ML task é permissivo (Alta).**
A verdade do estágio 2 é uma **lista longa** de tarefas plausíveis por abstract. Isso **infla o denominador do recall** e **limita a precision** — é parte do motivo de o F1 do ML task parecer baixo (0,27) mesmo quando as previsões são razoáveis.
→ *Mitigação:* definir com o professor um critério objetivo de "tarefa correta" (p.ex. top-k, ou só a tarefa principal).

**1.3 Domínio anotado por abstract, não por US (Média).**
Atribuímos **um domínio por abstract**, herdado pelas 10 US geradas. Mas US do mesmo abstract podem legitimamente pertencer a domínios diferentes → a "verdade" pode estar grossa demais.
→ *Mitigação:* anotar no nível da **US individual**.

**1.4 Estágio 3 derivado da lógica do mapping (Média).**
Os atributos sensíveis "esperados" saem da **regra de cruzamento domínio∩tarefa** (a mesma lógica do ReFAIR), não de anotação humana. Comparar o ReFAIR com um alvo derivado da própria lógica é parcialmente circular.
→ *Mitigação:* anotação humana **independente** do estágio 3 ([estagio3-passo-a-passo.md](estagio3-passo-a-passo.md)).

---

## 2. Validade interna — *as relações causais se sustentam?*

**2.1 (RQ2) Limiar do estágio 2 ajustado no conjunto de teste (Alta — ✅ corrigida).**
Originalmente o limiar 0,15 foi escolhido **varrendo valores no próprio UStAI** (vazamento → F1 otimista, 0,268).
→ *Corrigido:* o limiar passou a ser sintonizado num **split de validação do sintético** (80/20, held-out do treino), maximizando o micro-F1 ali; o UStAI é rodado **uma única vez** com esse valor. O limiar honesto saiu **0,45** (alto, porque o classificador é confiante in-distribution) e o **F1 do UStAI ficou 0,243** (vs 0,268 com vazamento). Reprodutível em `treinar_mltask_embeddings.py`. (O domínio nunca teve esse problema — não ajustamos nada nele no UStAI.)

**2.2 (RQ2) O estágio 2 mudou várias coisas ao mesmo tempo (Média-alta — ✅ mitigada por ablação).**
Fizemos a **ablação variável-a-variável** (domínio constante, medida no UStAI), isolando cada contribuição ao F1:

| Δ F1 | Mudança |
|---|---|
| **+0,11** | filtro **soft** (lever dominante) |
| +0,05 | classificador LabelPowerset → OneVsRest |
| **−0,03 a −0,04** | GloVe → embeddings (**pioram** o ML task) |

> Conclusão: o ganho do estágio 2 vem do **filtro soft + classificador**, **não** dos embeddings — que na verdade atrapalham aqui. Por isso adotamos o **config D** (GloVe + OneVsRest + soft, F1 **0,283**) e **removemos os embeddings do estágio 2** (ficam só no domínio). A atribuição agora é limpa.

**2.3 (RQ1) Causa-raiz "decora a posição 3" (Baixa — mitigada). ✅**
Não é só correlação: a **importância por permutação** é causal — embaralhar a posição 3 derruba o acerto (99,5%→25,3%) e embaralhar o conteúdo não muda nada (99,4%). Ver [analise-raiz-xgboost.md](analise-raiz-xgboost.md).

**2.4 (RQ2) Ablação do domínio mudou uma só variável (Baixa — mitigada). ✅**
A extensão do domínio trocou **apenas** a entrada (input_ids→embeddings), mesmo treino, mesmo teste, sem ajuste no UStAI → a atribuição causal (representação era a culpa) é **válida**. Salto 9,4%→37%.

---

## 3. Validade externa — *os resultados generalizam?*

**3.1 O UStAI também é gerado por LLM (Alta — a ameaça-mãe).**
Provamos que o ReFAIR falha numa **origem sintética diferente** (Gemini 1.5, Llama 3.1, O1-mini a partir de abstracts reais) — **não** necessariamente em user stories **escritas por humanos** em contexto real. O mesmo vale para o 37% da extensão: validado só sobre esse conjunto gerado por LLM.
→ *Mitigação:* validar num conjunto de US **humanas** (de projetos reais), ainda que pequeno.

**3.2 Cobertura parcial dos domínios (Média).**
25 dos 34 domínios aparecem no UStAI; **9 não têm nenhuma US** → não foram avaliados. As conclusões valem para a parte coberta.

**3.3 Poucos abstracts e geradores específicos (Média).**
42 abstracts, 3 LLMs num momento específico, com um prompt específico. Outros modelos/prompts podem produzir distribuições diferentes.

**3.4 Específico à versão do ReFAIR (Baixa).**
As conclusões valem para os **modelos liberados** do paper (XGBoost/LinearSVC/GloVe/BERT do repositório).

---

## 4. Validade de conclusão — *a estatística sustenta as afirmações?*

**4.1 Sem teste de significância nem intervalo de confiança (Média — aberta).**
Reportamos 9,4% vs 37,0% (domínio) e 0,13 vs 0,27 (ML task) sem **IC** nem **teste de McNemar** para a comparação pareada original×extensão (mesmas US).
→ *Mitigação:* adicionar **McNemar** (comparação pareada) e **IC bootstrap** nas acurácias/F1.

**4.2 Suporte pequeno por classe (Média).**
Domínios com 29-30 US → estimativas por domínio **ruidosas**; cuidado ao ler números por domínio isoladamente.

**4.3 Desbalanceamento de classes (Baixa — mitigada). ✅**
O UStAI é desbalanceado (120 US no maior domínio, 29 no menor). Mas **acurácia (micro) ≈ média por domínio (macro)**: 9,4% vs 11,1% (original) e 37,0% vs 37,5% (extensão) → o desempenho está **espalhado**, nenhuma classe grande distorce o número. Além disso, o "F1-Score" que reportamos **já é macro** (corrige o desbalanceamento). E a comparação original×extensão é imune (mesmo conjunto de teste).

**4.4 Determinismo (Baixa — mitigada). ✅**
Inferência sem aleatoriedade; predições **idênticas** em macOS e Windows → variância de execução ≈ 0.

---

## 5. Reprodutibilidade / confiabilidade

| Item | Situação |
|---|---|
| Versões fixadas (torch 2.0.0, transformers 4.27.1, xgboost 1.7.4, sklearn 1.2.2) | ✅ |
| Inferência determinística, macOS = Windows (0 divergências) | ✅ |
| Seeds fixos no treino da extensão (42) | ✅ |
| Scripts e modelos versionados | ✅ |
| **Fragilidade:** modelo `.pkl` treinado em Py 3.11, container Docker em Py 3.9 | funcionou, mas re-treinar no ambiente-alvo é mais seguro |

---

## 6. Resumo honesto (RQ1 × RQ2)

- **RQ1 — "o ReFAIR não generaliza para US de outra origem": forte.** Ferramenta congelada, inferência determinística e reprodutível, e causa-raiz **provada por permutação**. Ressalva principal: o UStAI ainda é sintético (origem LLM), então a generalização comprovada é para **outra origem sintética**, não para US humanas.

- **RQ2 — "a representação conserta": defensável.** O ganho do **domínio** (9,4%→37%) é uma **ablação limpa** (uma variável, sem ajuste no teste). No **ML task** (config D, F1 **0,283**), o vazamento do limiar foi **corrigido** (§2.1) e a contribuição de cada mudança foi **isolada por ablação** (§2.2): o ganho vem do **filtro soft + classificador**, não dos embeddings (que pioravam e foram removidos do estágio 2). Sem ameaças internas abertas.

---

## 7. Ações pendentes (para fechar as ameaças abertas)

1. **κ entre anotadores** + revisão do professor (cobre 1.1, 1.3).
2. **Critério objetivo de ML task correta** com o professor (cobre 1.2).
3. **Anotação humana do estágio 3** (cobre 1.4).
4. ~~Re-sintonizar o limiar do estágio 2 num split do sintético~~ ✅ **feito** (limiar 0,45, F1 honesto 0,243).
5. **McNemar + IC bootstrap** nas comparações (cobre 4.1).
6. (Opcional) validar num conjunto pequeno de **US humanas reais** (cobre 3.1).

---

## Arquivos relacionados
- [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md) (§8 aponta para cá) · [analise-raiz-xgboost.md](analise-raiz-xgboost.md) · [passo-a-passo-extensao-37.md](passo-a-passo-extensao-37.md) · [o-que-falta.md](o-que-falta.md) · [estagio3-passo-a-passo.md](estagio3-passo-a-passo.md)

# O que falta — Experimento ReFAIR × UStAI e entrega do projeto

**Data:** 2026-06-12
**Base:** checklist (Seção 10) e métricas (Seção 8) do [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md).
**O que este doc é:** o estado atual do experimento e a lista **completa e priorizada** do que falta para **fechar o experimento** e **entregar o projeto**.

---

## 📍 Resumo do progresso (bater o olho)

| Bloco | Estado |
|---|---|
| **A — Métricas formais** (F1-Score, Hamming, subset, por LLM, causa de erro) | ✅ **Feito** |
| **B — Rodada oficial sem patch + decisão patched×unpatched** | ✅ **Feito** |
| **C — Validação cross-platform (Windows)** | 🟡 **Scripts prontos, falta rodar no Windows** |
| **D — Estágio 3 (anotação humana + painel + κ)** | 🔴 **Falta** (precisa de pessoas) |
| **E — Limpeza: 2 ids duplicados + README dos artefatos** | 🔴 **Falta** (rápido) |
| **Decisão com o professor — limiar "funciona/não funciona"** | 🔴 **Falta** (combinar) |
| **Relatório final** | 🔴 **Falta** (escrever) |

**Em uma frase:** o **núcleo quantitativo está fechado** (A+B); falta **validar no Windows** (C — só executar), a **avaliação humana do estágio 3** (D), pequenas **limpezas** (E), **combinar o limiar com o professor** e **escrever o relatório**.

---

## ✅ Já está pronto

- ReFAIR rodado **congelado** (sem retreino) nas 1260 US — princípio inegociável respeitado.
- Ground truth dos estágios 1 e 2 (equivalência) + **estágio 3 derivado** da lógica do `feature_extraction` (proxy).
- **Estágio 1:** accuracy (9,4%) + **matriz de confusão** + estratificação por `domain_confidence`.
- **Estágio 2:** taxa de ML task vazia (42,5%) + overlap (53,8%).
- Comparação 1-a-1, resumo por abstract, impacto do patch do GloVe.
- Rascunho de resultados ([resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md)).
- Ambiente reproduzido nas versões exatas do `requirements.txt` + runner em lote (`run_refair_batch.py`) + patch do GloVe.
- Sanity check forte: `getDomain` acerta **100% (200/200)** nas stories de treino → descarta bug de mapeamento/carregamento.

---

## 🔴 Falta no EXPERIMENTO

### A) Métricas e análises automatizáveis (dá pra fazer agora — sklearn já instalado) ✅ FEITO

> ✅ **Concluído.** Resultados em [metricas-formais-item-a.md](metricas-formais-item-a.md); script reproduzível em [datasets/calcular_metricas.py](datasets/calcular_metricas.py). Resumo: domínio F1-Score **0,125** / ML task F1-Score **0,127** (vs ~0,98 e ~0,90 do paper); **90,6% das falhas nascem no estágio 1 (domínio)**; desempenho igualmente ruim nos 3 LLMs.

- [x] **Métricas formais do Estágio 1**: accuracy 0,094, F1-Score 0,125 + precisão/revocação/F1 por domínio (25 cobertos).
- [x] **Métricas formais do Estágio 2**: F1-Score 0,127, Hamming loss 0,223, Subset accuracy 0,039 + precisão/revocação por label.
- [x] **Estratificação por LLM** (Gemini × Llama × O1) nos estágios 1 e 2.
- [x] **Análise de erros end-to-end formal** (causa: domínio / task / mapping) — 90,6% / 7,0% / 2,4%.
- [x] **Métricas só sobre os 25 domínios cobertos** (9 dos 34 declarados como não testados).

### B) Decisões metodológicas a tomar (antes de fechar os números)

- [x] **Definido: rodada oficial = ReFAIR ORIGINAL (sem patch).** ✅
  O plano testa o ReFAIR **como caixa-preta congelada** (Seção 2). Gerado [datasets/refair-resultados-oficial.csv](datasets/refair-resultados-oficial.csv) (via `gerar_resultado_oficial.py`), e as métricas canônicas (`metricas-*.csv`) agora vêm dele.
  - **Resultado:** oficial × com patch ficou **praticamente idêntico** — domínio F1-Score **0,125** (igual, o patch não toca o estágio 1); ML task F1-Score **0,127** nos dois. O patch só muda casas decimais (ML task vazia 557→535; subset 0,037→0,039). **Conclusão: o patch não altera o veredito.**
  - O patch fica registrado como **sub-experimento de melhoria** (ver `ustai-impacto-patch-glove.csv`).
- [ ] **Acordar com o professor o limiar "funciona/não funciona"** *antes* de concluir (Seção 8) — para não parecer escolhido depois do resultado.

### C) Validação de reprodutibilidade / cross-platform (Windows) — 🟡 scripts prontos, falta executar

> Rodamos no **macOS + Python 3.11**. O ambiente original do ReFAIR é **Windows + Python 3.9**. Diferenças de SO / builds de BERT, XGBoost e GloVe podem, em princípio, deslocar predições. Validar que a saída é a mesma entre plataformas.
> 📋 **Tudo pronto pra executar:** passo a passo em [como-rodar-no-windows.md](como-rodar-no-windows.md); scripts versionados `gerar_resultado_oficial.py` (refair-server) e `comparar_plataformas.py` (documents/datasets).

- [ ] **Rodar `run_refair_batch.py` no Windows / Python 3.9** → gera `refair-resultados-windows.csv` (passo 4 do guia).
- [ ] **Rodar `comparar_plataformas.py`** → confere diff de domínio e ML task contra o macOS (idealmente **0 / 0**). Se divergir, ele gera `diferencas-plataformas.csv`; quantificar e declarar como ameaça à validade.
- [ ] **Confirmar o mesmo GloVe** (`glove.6B.100d.txt`) e o mesmo `bert-base-uncased` nas duas máquinas.
- [ ] **Registrar no relatório o ambiente de execução** (SO, versão do Python, versões das libs).
- [ ] *(Opcional, mais robusto)* rodar via **Docker** (`docker-compose.yml`) para eliminar a variável SO.

### D) Itens que precisam de pessoas (não automatizável)

> 📋 **Passo a passo detalhado deste item:** [estagio3-passo-a-passo.md](estagio3-passo-a-passo.md) — fluxo completo (amostra → anotação → κ → métricas → painel), com scripts prontos, para a pessoa responsável não se perder.
> 📊 **Contexto das features:** [resumo-features-fabris-3fontes.md](resumo-features-fabris-3fontes.md) — por que o `.ttl` do Fabris não vira ground truth melhor.

- [ ] **Estágio 3 rigoroso** — o plano diz que **não há ground truth pronto** (Seção 6):
  anotação **manual** de *sensitive features* de uma **amostra estratificada** (~100–150 US, balanceada por domínio e `domain_confidence`).
  > O gabarito do estágio 3 que geramos é um *proxy* (derivado do código), serve de apoio, **não substitui** a anotação manual.
- [ ] **Painel de 3–4 avaliadores** (equipe/professor) para utilidade/correção/falsos-positivos do estágio 3.
- [ ] **Concordância entre anotadores (Cohen's κ)** numa amostra do gabarito (estágios 1 e 2) — mitigação de ameaça à validade (Seção 9).
- [ ] **Coerência com `Implied ethical needs`** do UStAI (uso honesto da coluna, Seção 6) — cruzamento qualitativo.

### E) Limpeza de dados / consistência

- [ ] **Resolver os 2 ids duplicados** do UStAI (caíram de 1260 → 1258 na junção) — investigar e declarar.
- [ ] **Versionar os artefatos** com um pequeno README explicando cada CSV/XLSX gerado.

---

## 📦 Falta para ENTREGAR o projeto

- [ ] **Relatório final** consolidado no formato que o professor pede — incorporar as métricas formais, figuras (matriz de confusão, per-LLM), ameaças à validade (Seção 9), ambiente de execução e conclusão. (O `.md` atual é rascunho de resultados.)
- [ ] **(Opcional) Rota C** — extensão metodológica: testar outros embeddings (RoBERTa, sentence-transformers) como 2ª RQ. Só se quiserem ampliar o escopo.
- [ ] **Commit/empacotamento** no git: relatório + planilhas versionáveis + código + patch (`venv_mac/` e arquivos grandes já cobertos pelo `.gitignore`).

---

## 🎯 Ordem sugerida

1. ✅ **Métricas formais** estágios 1 e 2 + estratificação por LLM — FEITO ([metricas-formais-item-a.md](metricas-formais-item-a.md)).
2. ✅ **Decidido patched × unpatched** + gerado `refair-resultados-oficial.csv` (sem patch) — FEITO.
3. **(próximo)** **Validação cross-platform (Windows)** — re-rodar o batch lá e diffar com o macOS.
4. Preparar **amostra estratificada (~120 US) + template de anotação** do estágio 3.
5. Acordar **limiar com o professor** e rodar o **painel** + **κ**.
6. Escrever **relatório final** com tudo.
7. **Commit** final.

---

## ✔️ Definição de "experimento concluído"

O experimento está fechado quando:
- ✅ Estágios 1 e 2 têm **métricas formais** (F1-Score/Hamming/subset), estratificadas por confiança **e por LLM**, sobre os 25 domínios cobertos. **(feito — A)**
- ✅ A rodada **oficial (sem patch)** está definida e os números do relatório vêm dela; o patch está reportado como melhoria à parte. **(feito — B)**
- 🟡 As predições foram **validadas entre macOS e Windows** (ou rodadas via Docker), com o ambiente registrado. **(scripts prontos — C)**
- 🔴 O **estágio 3** tem ao menos a **amostra anotada + painel** (avaliação híbrida, como o plano prevê). **(falta — D)**
- 🔴 As **ameaças à validade** estão declaradas no relatório. **(ao escrever o relatório)**

---

## Ameaças à validade a declarar (lembrete — Seção 9 do plano)

- Ground truth dos estágios 1 e 2 é a **própria equivalência** (não é *gold standard* independente) → mitigar com κ + revisão do professor.
- **Domínio fixado por abstract** (granularidade grossa; US "fora do tema" herdam o domínio).
- **Cobertura parcial:** 25 dos 34 domínios; 9 não testados.
- **`Implied ethical needs` ≠ `sensitive features`** → estágio 3 sem ground truth exato.
- **UStAI também é sintético** → generalização comprovada é para outra origem **sintética**, não para US humanas.
- **Ambiente de execução diferente do original** (macOS/Py3.11 × Windows/Py3.9) → mitigar com a validação cross-platform da Seção C.
- Risco de *mismatch* de pré-processamento treino × teste (controlado: mesmas versões + mesmo tokenizador; o patch do GloVe, se usado, deve ser declarado).

# O que falta — Experimento ReFAIR × UStAI e entrega do projeto

**Data:** 2026-06-09
**Base:** checklist (Seção 10) e métricas (Seção 8) do [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md).
**O que este doc é:** o estado atual do experimento e a lista priorizada do que falta para **fechar o experimento** e **entregar o projeto**.

---

## ✅ Já está pronto

- ReFAIR rodado **congelado** (sem retreino) nas 1260 US — princípio inegociável respeitado.
- Ground truth dos estágios 1 e 2 (equivalência) + **estágio 3 derivado** da lógica do `feature_extraction` (proxy).
- **Estágio 1:** accuracy (9,4%) + **matriz de confusão** + estratificação por `domain_confidence`.
- **Estágio 2:** taxa de ML task vazia (42,5%) + overlap (53,8%).
- Comparação 1-a-1, resumo por abstract, impacto do patch do GloVe.
- Rascunho de resultados ([resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md)).
- Ambiente reproduzido nas versões exatas do `requirements.txt` + runner em lote (`run_refair_batch.py`) + patch do GloVe.

---

## 🔴 Falta no EXPERIMENTO

### A) Automatizável (dá pra fazer agora — sklearn já instalado)

- [ ] **Métricas formais do Estágio 1** (o plano pede, só tenho accuracy + confusão):
  Macro-F1, Weighted-F1, precisão/revocação por domínio — **restrito aos 25 domínios cobertos** pelo UStAI.
- [ ] **Métricas formais do Estágio 2** (hoje só tenho "overlap", fraco p/ multi-label):
  Micro-F1, Macro-F1, **Hamming loss**, **Subset accuracy (exact-match)**, precisão/revocação por label.
- [ ] **Estratificação por LLM** (Gemini 1.5 × Llama 3.1 × O1-mini) nos estágios 1 e 2 — o plano pede explicitamente (Seção 7, passo 12).
- [ ] **Análise de erros end-to-end formal:** por US, classificar a causa da falha do estágio 3 (erro de domínio / erro de task / limitação do mapping).

### B) Precisa de pessoas (não automatizável)

- [ ] **Estágio 3 rigoroso** — o plano diz que **não há ground truth pronto** (Seção 6):
  anotação **manual** de *sensitive features* de uma **amostra estratificada** (~100–150 US, balanceada por domínio e `domain_confidence`).
  > O gabarito do estágio 3 que geramos é um *proxy* (derivado do código), serve de apoio, **não substitui** a anotação manual.
- [ ] **Painel de 3–4 avaliadores** (equipe/professor) para utilidade/correção/falsos-positivos do estágio 3.
- [ ] **Concordância entre anotadores (Cohen's κ)** numa amostra do gabarito (estágios 1 e 2) — mitigação de ameaça à validade (Seção 9).
- [ ] **Limiar "funciona/não funciona" acordado com o professor** *antes* de concluir (Seção 8) — para não parecer escolhido depois do resultado.
- [ ] **Coerência com `Implied ethical needs`** do UStAI (uso honesto da coluna, Seção 6) — cruzamento qualitativo.

---

## 📦 Falta para ENTREGAR o projeto

- [ ] **Relatório final** consolidado no formato que o professor pede — incorporar as métricas formais, figuras (matriz de confusão, per-LLM), ameaças à validade (Seção 9) e conclusão. (O `.md` atual é rascunho de resultados.)
- [ ] **(Opcional) Rota C** — extensão metodológica: testar outros embeddings (RoBERTa, sentence-transformers) como 2ª RQ. Só se quiserem ampliar o escopo.
- [ ] **Commit/empacotamento** no git: relatório + planilhas versionáveis + código + patch (`venv_mac/` e arquivos grandes já cobertos pelo `.gitignore`).

---

## 🎯 Ordem sugerida

1. **(agora)** Métricas formais estágios 1 e 2 + estratificação por LLM → fecha o grosso quantitativo.
2. Preparar **amostra estratificada (~120 US) + template de anotação** do estágio 3.
3. Acordar **limiar com o professor** e rodar o **painel** + **κ**.
4. Escrever **relatório final** com tudo.
5. **Commit** final.

---

## Ameaças à validade a declarar (lembrete — Seção 9 do plano)

- Ground truth dos estágios 1 e 2 é a **própria equivalência** (não é *gold standard* independente) → mitigar com κ + revisão do professor.
- **Domínio fixado por abstract** (granularidade grossa; US "fora do tema" herdam o domínio).
- **Cobertura parcial:** 25 dos 34 domínios; 9 não testados.
- **`Implied ethical needs` ≠ `sensitive features`** → estágio 3 sem ground truth exato.
- **UStAI também é sintético** → generalização comprovada é para outra origem **sintética**, não para US humanas.
- Risco de *mismatch* de pré-processamento treino × teste (controlado: mesmas versões + mesmo tokenizador).

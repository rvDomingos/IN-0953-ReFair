# O que falta — Experimento ReFAIR × UStAI e entrega do projeto

**Data:** 2026-06-09
**Base:** checklist (Seção 10) e métricas (Seção 8) do [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md).
**O que este doc é:** o estado atual do experimento e a lista **completa e priorizada** do que falta para **fechar o experimento** e **entregar o projeto**.

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

### A) Métricas e análises automatizáveis (dá pra fazer agora — sklearn já instalado)

- [ ] **Métricas formais do Estágio 1** (o plano pede, só tenho accuracy + confusão):
  F1-Score, precisão/revocação por domínio — **restrito aos 25 domínios cobertos** pelo UStAI.
- [ ] **Métricas formais do Estágio 2** (hoje só tenho "overlap", fraco p/ multi-label):
  F1-Score, **Hamming loss**, **Subset accuracy (exact-match)**, precisão/revocação por label.
- [ ] **Estratificação por LLM** (Gemini 1.5 × Llama 3.1 × O1-mini) nos estágios 1 e 2 — o plano pede explicitamente (Seção 7, passo 12).
- [ ] **Análise de erros end-to-end formal:** por US, classificar a causa da falha do estágio 3 (erro de domínio / erro de task / limitação do mapping).
- [ ] **Métricas só sobre os 25 domínios cobertos** (declarar que 9 dos 34 não têm US no UStAI e não são testados).

### B) Decisões metodológicas a tomar (antes de fechar os números)

- [ ] **Definir qual é a rodada "oficial": com ou sem o patch do GloVe.**
  O plano testa o ReFAIR **como caixa-preta congelada** (Seção 2). O patch **modifica** o estágio 2. Decisão recomendada:
  - **Números oficiais de validade externa = ReFAIR ORIGINAL (sem patch).**
  - O patch entra como **sub-experimento de melhoria** ("e se corrigirmos o GloVe?").
  > ⚠️ Hoje o `refair-resultados.csv` está **com patch**. Os domínios são idênticos (o patch só toca o estágio 2), mas as **ML tasks/features oficiais** precisam vir da versão **sem** patch (já temos os dados em `ustai-impacto-patch-glove.csv`, coluna `*_SEM_patch`). Gerar um `refair-resultados-oficial.csv` sem patch para os números do relatório.
- [ ] **Acordar com o professor o limiar "funciona/não funciona"** *antes* de concluir (Seção 8) — para não parecer escolhido depois do resultado.

### C) Validação de reprodutibilidade / cross-platform (Windows) ⭐ novo

> Rodamos no **macOS + Python 3.11** com as libs recém-instaladas. O ambiente original do ReFAIR é **Windows + Python 3.9** (o `env/` empacotado no repo). Diferenças de SO / builds de BERT, XGBoost e GloVe podem, em princípio, deslocar algumas predições. Para os números entrarem no relatório com segurança, validar que a saída é a mesma entre plataformas.

- [ ] **Re-rodar o `run_refair_batch.py` no ambiente original (Windows / Python 3.9)** e comparar `refair-resultados.csv` com o gerado no macOS.
- [ ] **Conferir igualdade das predições** (domínio e ML task) entre macOS e Windows — idealmente diff = 0; se houver divergência, quantificar e declarar como ameaça à validade.
- [ ] **Confirmar o mesmo GloVe** (`glove.6B.100d.txt`) e o mesmo `bert-base-uncased` (mesmo hash/origem) nas duas máquinas.
- [ ] **Registrar no relatório o ambiente de execução** (SO, versão do Python, versões das libs) — exigência de reprodutibilidade.
- [ ] *(Opcional, mais robusto)* rodar via **Docker** (`docker-compose.yml` do projeto) para um ambiente único e reprodutível, eliminando a variável SO.

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

1. **(agora)** Métricas formais estágios 1 e 2 + estratificação por LLM → fecha o grosso quantitativo.
2. **Decidir patched × unpatched** e gerar o `refair-resultados-oficial.csv` (sem patch).
3. **Validação cross-platform (Windows)** — re-rodar o batch lá e diffar com o macOS.
4. Preparar **amostra estratificada (~120 US) + template de anotação** do estágio 3.
5. Acordar **limiar com o professor** e rodar o **painel** + **κ**.
6. Escrever **relatório final** com tudo.
7. **Commit** final.

---

## ✔️ Definição de "experimento concluído"

O experimento está fechado quando:
- Estágios 1 e 2 têm **métricas formais** (F1/Hamming/subset), estratificadas por confiança **e por LLM**, sobre os 25 domínios cobertos.
- A rodada **oficial (sem patch)** está definida e os números do relatório vêm dela; o patch está reportado como melhoria à parte.
- As predições foram **validadas entre macOS e Windows** (ou rodadas via Docker), com o ambiente registrado.
- O **estágio 3** tem ao menos a **amostra anotada + painel** (avaliação híbrida, como o plano prevê).
- As **ameaças à validade** estão declaradas no relatório.

---

## Ameaças à validade a declarar (lembrete — Seção 9 do plano)

- Ground truth dos estágios 1 e 2 é a **própria equivalência** (não é *gold standard* independente) → mitigar com κ + revisão do professor.
- **Domínio fixado por abstract** (granularidade grossa; US "fora do tema" herdam o domínio).
- **Cobertura parcial:** 25 dos 34 domínios; 9 não testados.
- **`Implied ethical needs` ≠ `sensitive features`** → estágio 3 sem ground truth exato.
- **UStAI também é sintético** → generalização comprovada é para outra origem **sintética**, não para US humanas.
- **Ambiente de execução diferente do original** (macOS/Py3.11 × Windows/Py3.9) → mitigar com a validação cross-platform da Seção C.
- Risco de *mismatch* de pré-processamento treino × teste (controlado: mesmas versões + mesmo tokenizador; o patch do GloVe, se usado, deve ser declarado).

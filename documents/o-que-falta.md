# O que falta — entrega do projeto ReFAIR × UStAI

**Data:** 2026-06-15 (atualizado após a extensão RQ2 e a análise de validade)
**O que este doc é:** o estado **atual** e a lista priorizada do que falta para **entregar**. Visão consolidada em [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md).

---

## Resumo (bater o olho)

| Bloco | Estado |
|---|---|
| **A — Métricas formais** (F1, Hamming, subset, por LLM, causa de erro) | Feito |
| **B — Rodada oficial sem patch + decisão patched×unpatched** | Feito |
| **Causa-raiz** (parser/posição-3, prova por permutação) | Feito |
| **RQ2 — Extensão** (domínio embeddings 37% + ML task config D 0,283 + ablação) | Feito |
| **Ameaças à validade** (doc dedicado, vazamento corrigido) | Feito |
| **Reprodutibilidade** (Docker rodando + determinismo macOS=Windows) | Feito |
| **C — Validação nativa no Windows** (opcional, Docker já cobre) | Opcional |
| **D — Estágio 3: anotação humana + painel + κ** | Falta (precisa de pessoas) |
| **Significância estatística** (McNemar + IC) | Recomendado |
| **2 ids duplicados** | Falta (rápido) |
| **Acordar limiar com o professor** | Falta (combinar) |
| **Relatório final + commit** | Relatório pronto; falta o commit |

**Em uma frase:** o **núcleo quantitativo (RQ1 + RQ2) está fechado e defensável**; falta a **avaliação humana** (κ + painel do estágio 3), **combinar o limiar com o professor**, pequenas limpezas, e o **commit**.

---

## Já está pronto

**Experimento (RQ1 — o ReFAIR não generaliza):**
- ReFAIR rodado **congelado** nas 1260 US; ground truth dos 3 estágios.
- Métricas formais: domínio **F1 0,125 (9,4%)**, ML task **F1 0,127**, features 2,1%; **90,6% das falhas nascem no estágio 1**; igualmente ruim nos 3 LLMs.
- **Causa-raiz provada** (parser entrega `input_ids`; decide pela posição 3; **permutação causal**: 99,5%→25,3% ao embaralhar o papel, conteúdo 99,4% inalterado).
- Rodada **oficial sem patch** definida; patch é sub-experimento (não muda o veredito).

**Extensão (RQ2 — dá pra consertar):**
- **Domínio:** embeddings do BERT → **9,4% → 37,0%** (ablação limpa, sem ajuste no teste).
- **ML task (config D):** GloVe + OneVsRest + filtro soft + limiar → **F1 0,132 → 0,283**, não-vazio 54%→99,8%.
- **Ablação (ameaça #6):** isolou cada contribuição (filtro soft +0,11; classificador +0,05; embeddings −0,03 → removidos do estágio 2).
- **Vazamento do limiar corrigido** (sintonizado no sintético, não no UStAI).
- Integrado no `refair-server` e **validado no Docker** (frontend funcional).

**Infra/docs:**
- Ambiente nas versões exatas; **Docker buildado e rodando**; determinismo macOS=Windows.
- [ameacas-a-validade.md](ameacas-a-validade.md), gabaritos coloridos por domínio, README dos datasets.

---

## Falta de verdade

### 1. Avaliação humana do estágio 3 (precisa de pessoas) — maior item aberto
Passo a passo em [estagio3-passo-a-passo.md](estagio3-passo-a-passo.md).
- [ ] Anotação **manual** de *sensitive features* numa amostra estratificada (~100–150 US).
- [ ] **Painel de 3–4 avaliadores** (utilidade/correção/falsos-positivos).
- [ ] **Cohen's κ** numa amostra do gabarito (estágios 1 e 2) → mitiga a ameaça de "gabarito é nosso".

### 2. Decisão com o professor
- [ ] Acordar o **limiar "funciona/não funciona"** *antes* de concluir (para não parecer escolhido depois).
- [ ] Alinhar a **granularidade do gabarito de ML task** (listas longas limitam a precision).

### 3. Limpezas / rigor
- [ ] Investigar e declarar os **2 ids duplicados** (1260 → 1258).
- [ ] *(Recomendado)* **McNemar + IC bootstrap** nas comparações (original×extensão) — fecha a ameaça de conclusão.

### 4. Opcional
- [ ] Validação **nativa no Windows** (o Docker já elimina a variável SO).
- [ ] Rumo a ≥80%: sentence-transformers / augmentation / LLM ([roadmap-80-porcento.md](roadmap-80-porcento.md)).

---

## Para ENTREGAR
- [x] **Relatório final** consolidado → [RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md) (atualizado com RQ1 + RQ2 + ameaças).
- [x] **Apresentação** → [apresentacao-3-pessoas.md](apresentacao-3-pessoas.md).
- [ ] **Commit/empacotamento** no git (o usuário faz): relatório + scripts + modelos da extensão + planilhas (`venv_mac/` e arquivos grandes já no `.gitignore`).

---

## Definição de "concluído"
- Estágios 1 e 2 com métricas formais, por LLM, nos 25 domínios cobertos.
- Rodada oficial (sem patch) definida; causa-raiz provada.
- RQ2 (extensão) medida, com ablação e sem vazamento; ameaças declaradas.
- Reprodutibilidade (Docker + determinismo).
- Estágio 3 com amostra anotada + painel + κ. **(falta — precisa de pessoas)**
- Limiar acordado com o professor.

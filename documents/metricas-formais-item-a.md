# Métricas formais (Item A) — ReFAIR × UStAI

**Data:** 2026-06-11
**O que este doc é:** os resultados quantitativos formais do experimento (Item A do [o-que-falta.md](o-que-falta.md)) — F1 por estágio, estratificação por LLM e análise de causa dos erros. Inclui como reproduzir e por que rodar no Windows precisa de cuidado.

> Gerado por [scripts/calcular_metricas.py](scripts/calcular_metricas.py) sobre a **rodada oficial** `refair-resultados-oficial.csv` (1258 US, **ReFAIR original, SEM patch** — item B) × `ustai-gabarito-completo.csv`.
> A rodada **com patch** dá números praticamente idênticos (ver Seção 5b); o patch **não altera o veredito**.

---

## 1. Estágio 1 — Domínio (single-label)

| Métrica | Valor | Referência *in-distribution* (paper) |
|---|---|---|
| **Accuracy** | **0,094** | — |
| **F1-Score** | **0,125** | **F1 = 0,98** (XGBoost) |

> **F1-Score** = média do F1 sobre as classes (cada domínio pesa igual). Sobre os **25 domínios cobertos** pelo UStAI (9 dos 34 não têm US e não são testados — declarar no relatório). Detalhe (precisão/revocação/F1) por domínio em [datasets/analises/metricas-estagio1-por-dominio.csv](datasets/analises/metricas-estagio1-por-dominio.csv).

**Leitura:** queda de ~0,98 → ~0,13 de F1. O classificador de domínio **não generaliza** para fora do conjunto sintético de treino.

---

## 2. Estágio 2 — ML task (multi-label)

| Métrica | Valor | Referência *in-distribution* (paper) |
|---|---|---|
| **F1-Score** | **0,127** | **F1 ≈ 0,90** (LP + GloVe + LSVC) |
| **Hamming loss** | 0,222 | 0,05 (paper) |
| **Subset accuracy** (exact-match) | **0,037** | |

> **F1-Score** multi-label (micro). Detalhe (precisão/revocação/F1) por label em [datasets/analises/metricas-estagio2-por-label.csv](datasets/analises/metricas-estagio2-por-label.csv).

**Leitura:** mesma história — queda de ~0,90 → ~0,13 de F1, Hamming loss 4× pior. Some-se a isso que o ReFAIR **zerou a ML task em 42,5%** das US.

---

## 3. Estratificação por LLM

| LLM | Acc domínio | F1-Score domínio | F1-Score task | Subset task | ML task vazias |
|---|---|---|---|---|---|
| **Llama 3.1** | **0,115** | 0,136 | 0,113 | 0,050 | 183/419 |
| O1-mini | 0,086 | 0,120 | 0,126 | 0,021 | 180/420 |
| Gemini 1.5 | 0,081 | 0,110 | 0,141 | 0,041 | 194/419 |

**Leitura:** desempenho **igualmente ruim nos três LLMs** (Llama um pouco menos pior). Ou seja, o problema **não é de um gerador específico** — é do ReFAIR não generalizar. Arquivo: [datasets/analises/metricas-por-llm.csv](datasets/analises/metricas-por-llm.csv).

---

## 4. Análise de erros end-to-end — qual estágio causa a falha?

| Causa | US | % |
|---|---|---|
| **Erro de DOMÍNIO (estágio 1)** | 1140 | **90,6%** |
| Domínio ok, erro/vazio de ML task (estágio 2) | 92 | 7,3% |
| Domínio e task ok → diferença vem do mapping (estágio 3) | 26 | 2,1% |

**Leitura — a conclusão mais importante do trabalho:** **90,6% das falhas nascem no estágio 1 (domínio).** Os estágios 2 e 3 quase nunca são a causa-raiz; eles herdam o erro de domínio (**propagação**). Por US em [datasets/analises/erro-end-to-end-causa.csv](datasets/analises/erro-end-to-end-causa.csv).

---

## 5. Conclusão

Comparando com o paper (*in-distribution*: domínio F1 0,98, ML task F1 0,90), o ReFAIR **despenca para ~0,13 de F1 nos dois estágios** quando exposto ao UStAI. O gargalo é o **classificador de domínio** (90,6% das falhas), e o erro **se propaga** para tarefa e features. O comportamento é consistente nos 3 LLMs. → **O ReFAIR não generaliza para user stories de outra origem.**

---

## 5b. Oficial (sem patch) × Com patch (item B)

A rodada **oficial** é o ReFAIR **original (sem patch)** — caixa-preta congelada. O patch do GloVe é um sub-experimento de melhoria. Comparação:

| | Domínio F1 | ML task F1 | Hamming | Subset | ML task vazias |
|---|---|---|---|---|---|
| **Oficial (sem patch)** | 0,125 | 0,127 | 0,222 | 0,037 | 557 |
| Com patch | 0,125 | 0,127 | 0,223 | 0,039 | 535 |

**O patch não altera o veredito** — o F1 é idêntico; muda só casa decimal (22 ML tasks a menos vazias). O domínio (estágio 1) é igual nos dois porque o patch só toca o estágio 2. Por isso os números do relatório vêm da rodada **oficial**.

---

## 6. Como reproduzir

```bash
cd documents/datasets
# precisa de scikit-learn (já está no venv do ReFAIR)
python calcular_metricas.py                          # oficial (sem patch) — padrão
python calcular_metricas.py refair-resultados.csv    # com patch (comparação)
```

Gera 4 CSVs: `metricas-estagio1-por-dominio`, `metricas-estagio2-por-label`, `metricas-por-llm`, `erro-end-to-end-causa`.

---

## 7. Sobre "deu o mesmo resultado no Windows" — leia com atenção

Há **dois tipos de script** e isso muda tudo:

| Script | O que faz | Rodar no Windows e dar igual significa… |
|---|---|---|
| **`run_refair_batch.py`** | Roda os **modelos do ReFAIR** (BERT+XGBoost, GloVe+LSVC) nas 1260 US → gera `refair-resultados.csv` | **Validação real**: as predições são iguais entre SO (resultado ideal!) |
| **`analisar_resultados.py` / `calcular_metricas.py`** | Só **lê um CSV** e compara com o gabarito (pós-processamento, sem modelo) | **Não valida nada**: se leu o mesmo CSV, o resultado é idêntico **por construção** |

**O que provavelmente aconteceu:** você rodou `analisar_resultados.py` apontando para o `refair-resultados.csv` que **veio do macOS** (está versionado no repo). Aí dar `9,4%` igual é **esperado e trivial** — você re-analisou o mesmo arquivo, não rodou o ReFAIR no Windows.

### Como fazer a validação cross-platform de verdade
1. No Windows, rodar **o batch** (não a análise):
   ```bat
   python run_refair_batch.py "..\..\..\..\documents\datasets\ustai-stories-para-refair.csv" -o "..\..\..\..\documents\datasets\refair-resultados-windows.csv"
   ```
2. **Diffar** o arquivo do Windows contra o do macOS (comando na Seção 5 do [como-rodar-no-windows.md](como-rodar-no-windows.md)):
   ```bat
   python -c "import csv; a={r['id']:r for r in csv.DictReader(open('refair-resultados.csv',encoding='utf-8'))}; b={r['id']:r for r in csv.DictReader(open('refair-resultados-windows.csv',encoding='utf-8'))}; ids=set(a)&set(b); print('dom dif:', sum(a[i]['refair_domain']!=b[i]['refair_domain'] for i in ids)); print('task dif:', sum(a[i]['refair_ml_tasks']!=b[i]['refair_ml_tasks'] for i in ids))"
   ```
3. Resultado esperado: **`dom dif: 0` e `task dif: 0`** → aí sim está provado que o ReFAIR dá o mesmo resultado nos dois SO (modelos determinísticos). **Esse é o "faltou algo"**: gerar o `refair-resultados-windows.csv` com o batch e diffar.

> **Resumo:** "deu igual" só vale como reprodutibilidade se você **re-gerou** o `refair-resultados-windows.csv` com `run_refair_batch.py`. Se só rodou a análise no CSV do macOS, ainda falta rodar o batch no Windows.

---

## Arquivos relacionados
- [o-que-falta.md](o-que-falta.md) (Item A) · [como-rodar-no-windows.md](como-rodar-no-windows.md) · [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md)

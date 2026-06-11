# Estágio 3 — Passo a passo da avaliação (anotação humana)

**Data:** 2026-06-11
**Para quem:** a pessoa responsável por concluir o **Item D** do [o-que-falta.md](o-que-falta.md) — a avaliação rigorosa do Estágio 3 (recomendação de *sensitive features*).
**Por que existe:** o Estágio 3 **não tem ground truth pronto**. Nem o código (`feature_extraction`) nem a ontologia do Fabris (`.ttl`) substituem uma anotação **humana** das user stories do UStAI (ver [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md), Seção 6, e [resumo-features-fabris-3fontes.md](resumo-features-fabris-3fontes.md)).

> **Objetivo final:** ter uma tabela em que cada US tem suas *sensitive features* **anotadas por humanos**, comparar com o que o ReFAIR recomendou, e reportar métricas + notas de um painel. Tudo declarado com honestidade.

---

## Visão geral (o fluxo inteiro)

```
1. Montar amostra estratificada (~120 US)
2. Preparar a planilha de anotação (vocabulário fechado)
3. 2+ pessoas anotam INDEPENDENTE
4. Medir concordância (Cohen's κ)
5. Reconciliar divergências -> ground truth consolidado
6. Comparar ReFAIR × ground truth (métricas)
7. Painel (3-4 pessoas) dá notas qualitativas
8. Coerência com 'Implied ethical needs'
9. Escrever a seção do relatório
```

Tempo estimado: **1 a 2 dias** de trabalho de anotação para 2 pessoas + meio dia de consolidação.

---

## Pré-requisitos (arquivos que você vai usar)

| Arquivo | Para quê |
|---|---|
| `documents/datasets/ustai-gabarito-completo.csv` | tem `id`, `User Story`, `role_shorten`, `equivalent_domain`, `domain_confidence` |
| `documents/datasets/refair-resultados.csv` | o que o ReFAIR recomendou (`refair_features`) — para o passo 6 |
| UStAI completo (Hugging Face) | a coluna `Implied ethical needs` — para o passo 8 |

---

## Passo 1 — Montar a amostra estratificada (~120 US)

**Por quê:** anotar 1260 à mão é inviável. Uma amostra **balanceada** dá métricas válidas sem anotar tudo.

**Como balancear:** por **domínio** (do gabarito) e por **confiança** (`High`/`Medium`/`Low`). Meta: ~120 US, cobrindo os 25 domínios, com presença das 3 confianças.

**Script pronto** (salve como `montar_amostra.py` em `documents/datasets/` e rode `python montar_amostra.py`):

```python
import csv, random
random.seed(42)                      # reprodutível
rows=list(csv.DictReader(open('ustai-gabarito-completo.csv',encoding='utf-8-sig')))
from collections import defaultdict
buckets=defaultdict(list)
for r in rows:
    buckets[(r['equivalent_domain'].strip(), r['domain_confidence'].strip())].append(r)
amostra=[]
for k,v in buckets.items():
    random.shuffle(v)
    amostra += v[:max(1, round(len(v)*0.10))]   # ~10% de cada estrato, mínimo 1
cols=['id','User Story','role_shorten','equivalent_domain','domain_confidence']
with open('estagio3-amostra-para-anotar.csv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f); w.writerow(cols+['features_anotador_A','features_anotador_B','observacoes'])
    for r in amostra:
        w.writerow([r['id'],r['User Story'],r['role_shorten'],r['equivalent_domain'],r['domain_confidence'],'','',''])
print('amostra:', len(amostra), 'US -> estagio3-amostra-para-anotar.csv')
```

> Saída: `estagio3-amostra-para-anotar.csv` com colunas vazias `features_anotador_A` e `features_anotador_B` para preencher.

---

## Passo 2 — Preparar a planilha e o vocabulário fechado

**Regra de ouro:** anotadores **não inventam** nomes de features. Usam um **vocabulário fechado** (senão a comparação vira bagunça). Vocabulário sugerido (atributos protegidos clássicos):

```
age, gender, sex, race, ethnicity, nationality, geography, religion,
disability, sexual orientation, skin tone, language, age group,
socioeconomic status, education, marital status, pregnancy/maternity,
political affiliation, none
```

- Pode-se **adaptar** essa lista com o professor antes de começar — mas **fixe-a antes** de anotar.
- `none` = "esta US não envolve nenhum atributo sensível" (caso legítimo, não deixar em branco).
- Separar múltiplas features por `;` (ex.: `age; gender; disability`).

---

## Passo 3 — Protocolo de anotação (o que olhar em cada US)

Para cada user story, o anotador pergunta: **"se este sistema de ML fosse construído, quais atributos de pessoas poderiam gerar viés/injustiça e precisam ser monitorados?"**

Pistas concretas:
1. **O papel (`role_shorten`)** muitas vezes nomeia o grupo — ex.: *"visually impaired person"* → `disability`; *"elderly patient"* → `age`.
2. **O texto da US** — menção a pacientes, clientes, estudantes, motoristas → pensar em quais demografias são relevantes naquele contexto.
3. **O domínio** ajuda a calibrar — saúde puxa `age`/`sex`; crédito puxa `age`/`gender`/`race`; etc.
4. Se a US é puramente técnica e **não envolve pessoas** → `none`.

> ⚠️ Anotar pelo **contexto real da US**, **não** pelo que o ReFAIR respondeu. O anotador **não deve ver** a saída do ReFAIR nesta fase (senão enviesa).

---

## Passo 4 — Anotação independente (2+ pessoas)

- **No mínimo 2 anotadores**, cada um preenche sua coluna (`features_anotador_A`, `features_anotador_B`) **sem ver a do outro**.
- Trabalhar em cópias separadas e juntar depois, ou esconder a coluna do outro.
- Isso é o que permite medir **concordância** (passo 5) — exigência de validade (Seção 9 do plano).

---

## Passo 5 — Medir concordância (Cohen's κ)

**Por quê:** mostra que o ground truth não é "achismo de uma pessoa". κ > 0,6 = concordância boa; > 0,8 = ótima.

**Como (multi-label → por feature):** trata-se cada feature do vocabulário como um rótulo binário (presente/ausente) e calcula κ médio. Script (salve como `kappa.py`):

```python
import csv
from sklearn.metrics import cohen_kappa_score
VOCAB=['age','gender','sex','race','ethnicity','nationality','geography','religion',
       'disability','sexual orientation','skin tone','language','socioeconomic status',
       'education','marital status','political affiliation','none']
rows=[r for r in csv.DictReader(open('estagio3-amostra-para-anotar.csv',encoding='utf-8'))
      if r['features_anotador_A'].strip() and r['features_anotador_B'].strip()]
def vec(s):
    fs=set(x.strip().lower() for x in s.split(';'))
    return [1 if f in fs else 0 for f in VOCAB]
import statistics
kappas=[]
for j,feat in enumerate(VOCAB):
    a=[vec(r['features_anotador_A'])[j] for r in rows]
    b=[vec(r['features_anotador_B'])[j] for r in rows]
    if len(set(a))>1 or len(set(b))>1:
        kappas.append(cohen_kappa_score(a,b))
print(f'κ médio (por feature): {statistics.mean(kappas):.3f}  sobre {len(rows)} US anotadas')
```

> Se κ ficar baixo (< 0,5): revisar o protocolo/vocabulário com a equipe e re-anotar uma parte. Documentar isso é honesto, não é erro.

---

## Passo 6 — Consolidar o ground truth e comparar com o ReFAIR

1. **Reconciliar divergências:** onde A e B diferem, os dois (ou o professor) decidem a feature final → coluna `features_ground_truth`.
2. **Comparar** com `refair_features` (de `refair-resultados.csv`), juntando por `id`. Métricas multi-label:
   - **Precision / Recall / F1** (por US e médias)
   - **Subset accuracy** (acerto exato do conjunto)
   - **Falsos positivos** (ReFAIR sugeriu e não devia) e **falsos negativos** (devia e não sugeriu)

> Reaproveite a lógica do `analisar_resultados.py` (em [como-rodar-no-windows.md](como-rodar-no-windows.md)) trocando o gabarito proxy pelo `features_ground_truth`.

---

## Passo 7 — Painel de avaliação (3–4 pessoas)

Para uma amostra menor (~30–40 US), o painel dá **notas qualitativas** que as métricas não capturam:

| Critério | Escala |
|---|---|
| **Utilidade** da recomendação | 1–5 |
| **Correção** (as features fazem sentido?) | 1–5 |
| **Falsos positivos** (sugeriu lixo?) | contagem |
| **Falsos negativos** (faltou algo óbvio?) | contagem |

Cada avaliador preenche separado; reportar média + desvio. Inclua o **professor** se possível.

---

## Passo 8 — Coerência com `Implied ethical needs`

> ⚠️ **`Implied ethical needs` ≠ `sensitive features`** (Seção 6 do plano). Não é ground truth direto — é vocabulário de ética (Privacy, Safety…), não de atributos demográficos.

Uso honesto:
- **Filtro de relevância:** US cujo princípio ético é justiça/inclusão/não-discriminação são as em que o ReFAIR **deveria** recomendar features não-triviais. US só de `Privacy`/`Safety` são casos onde features são menos centrais.
- **Verificação cruzada:** quando o princípio aponta justiça/inclusão, a recomendação do ReFAIR foi compatível?

Reporte como análise **qualitativa de apoio**, não como métrica.

---

## Passo 9 — Escrever a seção do relatório

Itens obrigatórios a registrar:
- Tamanho e critério da amostra estratificada.
- Vocabulário fechado usado.
- Nº de anotadores + **κ** (concordância).
- Métricas ReFAIR × ground truth (P/R/F1/subset).
- Notas do painel.
- Análise de erros end-to-end: quando a feature final está errada, a causa foi **domínio** (Estágio 1), **tarefa** (Estágio 2) ou **mapping**? (lembrar: 9,4% de acerto de domínio → a maioria dos erros do Estágio 3 é **propagação**).
- **Ameaças à validade** (amostra parcial, ground truth próprio, UStAI sintético, `Implied ethical needs` ≠ features).

---

## ✔️ Checklist do Item D

- [ ] Amostra estratificada gerada (~120 US) — `estagio3-amostra-para-anotar.csv`
- [ ] Vocabulário fechado acordado com o professor
- [ ] Anotação independente por 2+ pessoas
- [ ] κ calculado e aceitável (ou re-anotação documentada)
- [ ] Ground truth consolidado (`features_ground_truth`)
- [ ] Métricas ReFAIR × ground truth (P/R/F1/subset)
- [ ] Painel de 3–4 pessoas com notas
- [ ] Coerência com `Implied ethical needs` (qualitativo)
- [ ] Seção do relatório escrita + ameaças à validade

---

## Arquivos relacionados
- [o-que-falta.md](o-que-falta.md) (Item D) · [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md) (Seções 5.3, 6, 10) · [resumo-features-fabris-3fontes.md](resumo-features-fabris-3fontes.md) · [como-rodar-no-windows.md](como-rodar-no-windows.md)

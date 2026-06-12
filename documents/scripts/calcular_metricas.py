#!/usr/bin/env python3
"""Item A — métricas formais do experimento ReFAIR × UStAI.

Lê o gabarito + a saída do ReFAIR e calcula:
  - Estágio 1 (domínio): accuracy, F1-Score, precisão/revocação/F1 por domínio (25 cobertos).
  - Estágio 2 (ML task, multi-label): F1-Score, Hamming loss, Subset accuracy, precisão/revocação por label.
  - Estratificação por LLM (Gemini/Llama/O1).
  - Análise de erros end-to-end: causa da falha (domínio / task / mapping).

Requer scikit-learn. Lê de documents/datasets/essenciais/, escreve em .../analises/.
Rodar de qualquer lugar:  python documents/scripts/calcular_metricas.py
"""
import csv, re, sys, os
from pathlib import Path
from collections import defaultdict, Counter
from sklearn.metrics import (precision_recall_fscore_support, f1_score,
                             accuracy_score, hamming_loss)
from sklearn.preprocessing import MultiLabelBinarizer

DATA = Path(__file__).resolve().parent.parent / 'datasets'   # documents/datasets
ESS, ANA = DATA / 'essenciais', DATA / 'analises'
def _ess(name):  # resolve nome -> essenciais (ou caminho dado, se existir)
    return name if os.path.exists(name) else str(ESS / name)

GAB = str(ESS / 'ustai-gabarito-completo.csv')
# OFICIAL = sem patch (caixa-preta). Passe outro arquivo como argumento p/ comparar
# (ex.: refair-resultados.csv = com patch; refair-resultados-windows.csv = validação Windows).
RES = _ess(sys.argv[1]) if len(sys.argv) > 1 else str(ESS / 'refair-resultados-oficial.csv')
print(f"[fonte: {RES}]")

FIX = {'demograpy': 'demography', 'psycology': 'psychology'}
nd = lambda s: (lambda x: FIX.get(x, x))(s.strip().lower())
toset = lambda s: set(x.strip().lower() for x in s.split(';') if x.strip())
LLM = {'Ge': 'Gemini 1.5', 'Ll': 'Llama 3.1', 'O1': 'O1-mini'}
def llm_of(i):
    m = re.match(r'A\d+US\d+(.+)$', i); return LLM.get(m.group(1), '?') if m else '?'

gab = {r['id']: r for r in csv.DictReader(open(GAB, encoding='utf-8-sig'))}
res = {r['id']: r for r in csv.DictReader(open(RES, encoding='utf-8'))}
ids = [i for i in gab if i in res]
print(f"== {len(ids)} stories ==\n")

# ---------------- ESTÁGIO 1: domínio (single-label) ----------------
y_true = [nd(gab[i]['equivalent_domain']) for i in ids]
y_pred = [nd(res[i]['refair_domain']) for i in ids]
covered = sorted(set(y_true))                      # 25 domínios cobertos pelo UStAI
acc = accuracy_score(y_true, y_pred)
# F1-Score = média do F1 sobre as classes (cada domínio pesa igual)
f1s = f1_score(y_true, y_pred, labels=covered, average='macro', zero_division=0)
print("ESTÁGIO 1 — DOMÍNIO")
print(f"  Accuracy : {acc:.3f}")
print(f"  F1-Score : {f1s:.3f}")
print(f"  (sobre {len(covered)} domínios cobertos; 9 dos 34 não têm US no UStAI)\n")
p, r, f, sup = precision_recall_fscore_support(y_true, y_pred, labels=covered, zero_division=0)
with open(ANA / 'metricas-estagio1-por-dominio.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh); w.writerow(['dominio', 'precision', 'recall', 'f1_score', 'support'])
    for d, pp, rr, ff, ss in zip(covered, p, r, f, sup):
        w.writerow([d, f'{pp:.3f}', f'{rr:.3f}', f'{ff:.3f}', ss])
    w.writerow(['GERAL', f'{p.mean():.3f}', f'{r.mean():.3f}', f'{f1s:.3f}', sum(sup)])

# ---------------- ESTÁGIO 2: ML task (multi-label) ----------------
yt = [toset(gab[i]['equivalent_ml_task_labels']) for i in ids]
yp = [toset(res[i]['refair_ml_tasks']) for i in ids]
mlb = MultiLabelBinarizer()
mlb.fit(yt + yp)
T = mlb.transform(yt); P = mlb.transform(yp)
f1s2 = f1_score(T, P, average='micro', zero_division=0)   # F1-Score multi-label (micro)
ham = hamming_loss(T, P)
subset = accuracy_score(T, P)                      # exact-match do conjunto
print("ESTÁGIO 2 — ML TASK (multi-label)")
print(f"  F1-Score        : {f1s2:.3f}")
print(f"  Hamming loss    : {ham:.3f}")
print(f"  Subset accuracy : {subset:.3f}  (exact-match)\n")
pp, rr, ff, ss = precision_recall_fscore_support(T, P, average=None, zero_division=0)
with open(ANA / 'metricas-estagio2-por-label.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh); w.writerow(['ml_task', 'precision', 'recall', 'f1_score', 'support'])
    for lab, a, b, c, d in zip(mlb.classes_, pp, rr, ff, ss):
        w.writerow([lab, f'{a:.3f}', f'{b:.3f}', f'{c:.3f}', d])

# ---------------- ESTRATIFICAÇÃO POR LLM ----------------
print("POR LLM (estágio 1 acc / F1-Score  |  estágio 2 F1-Score / Subset)")
rows_llm = []
for code, name in LLM.items():
    sub = [i for i in ids if llm_of(i) == name]
    yt1 = [nd(gab[i]['equivalent_domain']) for i in sub]
    yp1 = [nd(res[i]['refair_domain']) for i in sub]
    a1 = accuracy_score(yt1, yp1)
    f1d = f1_score(yt1, yp1, labels=sorted(set(yt1)), average='macro', zero_division=0)
    T2 = mlb.transform([toset(gab[i]['equivalent_ml_task_labels']) for i in sub])
    P2 = mlb.transform([toset(res[i]['refair_ml_tasks']) for i in sub])
    mi = f1_score(T2, P2, average='micro', zero_division=0)
    su = accuracy_score(T2, P2)
    vazio = sum(res[i]['ml_task_vazio'] == 'Sim' for i in sub)
    print(f"  {name:11s}: acc {a1:.3f} / F1 {f1d:.3f}  |  F1 {mi:.3f} / subset {su:.3f}  (vazias {vazio}/{len(sub)})")
    rows_llm.append([name, len(sub), f'{a1:.3f}', f'{f1d:.3f}', f'{mi:.3f}', f'{su:.3f}', vazio])
with open(ANA / 'metricas-por-llm.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh); w.writerow(['llm', 'n', 'dom_accuracy', 'dom_f1_score', 'mltask_f1_score', 'mltask_subset', 'mltask_vazias'])
    w.writerows(rows_llm)

# ---------------- ERRO END-TO-END: causa ----------------
causa = Counter()
with open(ANA / 'erro-end-to-end-causa.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh); w.writerow(['id', 'dom_ok', 'mltask_ok', 'causa_provavel'])
    for i in ids:
        dom_ok = nd(res[i]['refair_domain']) == nd(gab[i]['equivalent_domain'])
        ml_ok = bool(toset(res[i]['refair_ml_tasks']) & toset(gab[i]['equivalent_ml_task_labels']))
        if not dom_ok:
            c = 'erro de DOMINIO (estagio 1)'
        elif not ml_ok:
            c = 'dominio ok, erro/vazio de ML TASK (estagio 2)'
        else:
            c = 'dominio e task ok -> diferenca vem do MAPPING (estagio 3)'
        causa[c] += 1
        w.writerow([i, 'Sim' if dom_ok else 'Nao', 'Sim' if ml_ok else 'Nao', c])
print("\nCAUSA da falha end-to-end:")
for c, n in causa.most_common():
    print(f"  {n:4d} ({100*n/len(ids):4.1f}%)  {c}")
print("\n-> CSVs gerados: metricas-estagio1-por-dominio, metricas-estagio2-por-label, metricas-por-llm, erro-end-to-end-causa")

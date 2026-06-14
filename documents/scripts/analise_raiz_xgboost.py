#!/usr/bin/env python3
"""Análise da raiz do classificador de DOMÍNIO do ReFAIR (XGBoost sobre input_ids).

Prova, com dados, por que o detector de domínio acerta ~100% no treino (sintético)
e 9,4% no UStAI: ele decide pelo TOKEN na posição 3 (a palavra do papel da US),
em vez do significado da frase.

Três evidências independentes e convergentes:
  (A) DUMP da árvore + posições usadas como raiz -> a posição 3 domina.
  (B) PUREZA / TRANSFER / SOBREPOSIÇÃO da posição 3 (treino x UStAI).
  (C) IMPORTÂNCIA POR PERMUTAÇÃO (prova causal): embaralhar só a posição 3
      derruba o acerto; embaralhar o CONTEÚDO não muda nada.

Requer o venv do ReFAIR (xgboost 1.7.4, transformers 4.27.1, sklearn 1.2.2, pandas).
Rodar com:
  "ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/venv_mac/bin/python" \\
      documents/scripts/analise_raiz_xgboost.py
"""
import warnings; warnings.filterwarnings('ignore')
import pickle, csv
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from transformers import BertTokenizer

ROOT = '/Users/romulodomingos/Documents/ProjetoFacul/IN-0953-ReFair/'
SRC = ROOT + 'ReFAIR/3. Source Code/ReFair/'
SEED = 42

tok = BertTokenizer.from_pretrained('bert-base-uncased')


def pos3_token(text):
    ids = tok([str(text)], padding='max_length', max_length=100, truncation=True)['input_ids'][0]
    return tok.convert_ids_to_tokens([ids[3]])[0], ids[3]


def input_ids_matrix(texts):
    """Reproduz EXATAMENTE o pré-processamento do getDomain() do ReFAIR."""
    enc = tok(list(texts), padding='max_length', max_length=100, truncation=True)
    return np.array(enc['input_ids'])          # (N, 100) IDs de token por posição


# ---------- modelo + dados ----------
clf = pickle.load(open(SRC + 'models/XGBClassifier.pkl', 'rb'))
booster = clf.get_booster()

ds = pd.read_excel(SRC + 'datasets/Synthetic User Stories.xlsx')   # treino sintético
ds = ds[['Domain', 'User Story']].dropna()
DOM_UNIQUE = ds['Domain'].unique()                                 # mapa índice->domínio (== getDomain)
ustai = list(csv.DictReader(open(
    ROOT + 'documents/datasets/essenciais/ustai-gabarito-completo.csv', encoding='utf-8-sig')))


def predict_domains(Xmat):
    """Mesmo caminho do getDomain: DataFrame de input_ids -> predict -> nome do domínio."""
    df = pd.DataFrame(Xmat); df.columns = df.columns.astype(str)
    pred = clf.predict(df)
    return [DOM_UNIQUE[p] for p in pred]


# ================================================================
# (A) DUMP DA ÁRVORE + POSIÇÕES USADAS COMO RAIZ
# ================================================================
print("=" * 70)
print("(A) ÁRVORE 0 (dump cru, 1 de %d) — fN = ID do token na posição N" % len(booster.get_dump()))
print("=" * 70)
print(booster.get_dump()[0])
roots = booster.trees_to_dataframe()
roots = roots[roots['Node'] == 0]
print("=== POSIÇÕES usadas como RAIZ das %d árvores (top 10) ===" % len(roots))
for f, c in Counter(roots['Feature']).most_common(10):
    print(f"  posição {str(f):>4s}: raiz de {c} árvores")

# ================================================================
# (B) PUREZA / TRANSFER / SOBREPOSIÇÃO da posição 3
# ================================================================
tr_pos3 = defaultdict(Counter)
for _, r in ds.iterrows():
    t, _ = pos3_token(r['User Story'])
    tr_pos3[r['Domain'].strip()][t] += 1
us_pos3 = defaultdict(Counter)
for r in ustai:
    t, _ = pos3_token(r['User Story'])
    us_pos3[r['equivalent_domain'].strip()][t] += 1

print("\n" + "=" * 70)
print("(B) Token na posição 3 (o papel) por domínio")
print("=" * 70)
print("--- TREINO (top 3 por domínio) ---")
for d in sorted(tr_pos3):
    top = ', '.join(f"{w}({n})" for w, n in tr_pos3[d].most_common(3))
    print(f"  {d:22s} [{sum(tr_pos3[d].values())} US]: {top}")
print("--- UStAI (top 3 por domínio) ---")
for d in sorted(us_pos3):
    top = ', '.join(f"{w}({n})" for w, n in us_pos3[d].most_common(3))
    print(f"  {d:22s} [{sum(us_pos3[d].values())} US]: {top}")


def purity(pos3_map):
    tok2dom = defaultdict(Counter)
    for dom, cnt in pos3_map.items():
        for t, n in cnt.items():
            tok2dom[t][dom] += n
    total = correct = 0
    for t, doms in tok2dom.items():
        total += sum(doms.values()); correct += doms.most_common(1)[0][1]
    return correct / total, tok2dom


tr_pur, tr_map = purity(tr_pos3)
us_pur, _ = purity(us_pos3)
print("\n=== PUREZA da posição 3 (só o papel -> acerta o domínio?) ===")
print(f"  TREINO : {100*tr_pur:.1f}%  (o papel quase DEFINE o domínio -> dá pra decorar)")
print(f"  UStAI  : {100*us_pur:.1f}%  (o papel NÃO define o domínio -> não dá pra decorar)")

tok2dom_train = {t: doms.most_common(1)[0][0] for t, doms in tr_map.items()}
seen = unseen = hit = 0
for r in ustai:
    t, _ = pos3_token(r['User Story'])
    real = r['equivalent_domain'].strip()
    if t in tok2dom_train:
        seen += 1; hit += (tok2dom_train[t] == real)
    else:
        unseen += 1
N = len(ustai)
print("\n=== 'Mapa decorado' (papel->domínio do TREINO) aplicado ao UStAI ===")
print(f"  papel (pos.3) NUNCA visto no treino : {unseen}/{N} = {100*unseen/N:.1f}%")
print(f"  acerto mesmo entre os {seen} vistos  : {hit}/{seen} = {100*hit/max(seen,1):.1f}%")


def shared(pos3_map):
    tokdoms = defaultdict(set)
    for dom, cnt in pos3_map.items():
        for t in cnt: tokdoms[t].add(dom)
    return sum(len(ds) > 1 for ds in tokdoms.values()), len(tokdoms)


tr_m, tr_t = shared(tr_pos3); us_m, us_t = shared(us_pos3)
print("\n=== SOBREPOSIÇÃO: papéis (pos.3) que caem em >1 domínio ===")
print(f"  TREINO : {tr_m}/{tr_t} = {100*tr_m/tr_t:.1f}%")
print(f"  UStAI  : {us_m}/{us_t} = {100*us_m/us_t:.1f}%")

# ================================================================
# (C) IMPORTÂNCIA POR PERMUTAÇÃO — a prova CAUSAL
#     Embaralha grupos de posições no TREINO e remede o acerto.
#     Se embaralhar a posição 3 derruba o acerto, é ela que decide.
# ================================================================
print("\n" + "=" * 70)
print("(C) IMPORTÂNCIA POR PERMUTAÇÃO (prova causal) — medida no TREINO")
print("=" * 70)
X = input_ids_matrix(ds['User Story'])
y = ds['Domain'].tolist()


def acc(Xmat):
    pred = predict_domains(Xmat)
    return float(np.mean([p == t for p, t in zip(pred, y)]))


def perm_acc(cols, seed=SEED):
    """Embaralha cada coluna de 'cols' entre as linhas (mantém a distribuição, quebra o vínculo)."""
    rng = np.random.default_rng(seed)
    Xp = X.copy()
    for c in cols:
        Xp[:, c] = Xp[rng.permutation(len(Xp)), c]
    return acc(Xp)


base = acc(X)
exp = [
    ("baseline (nada embaralhado)", base),
    ("embaralha SÓ a posição 3 (o papel)", perm_acc([3])),
    ("embaralha o MOLDE (posições 2-7: 'a … I want to')", perm_acc(list(range(2, 8)))),
    ("embaralha o CONTEÚDO (posições 40-60)", perm_acc(list(range(40, 61)))),
]
print(f"{'experimento':<52s} acerto no treino")
for name, a in exp:
    print(f"  {name:<50s} {100*a:5.1f}%")
print("\nLeitura: embaralhar a posição 3 DESABA o acerto (o modelo perde sua")
print("feature de decisão); embaralhar o conteúdo NÃO muda nada (o modelo já o")
print("ignorava). => a decisão é causada pela posição 3, não pelo significado.")

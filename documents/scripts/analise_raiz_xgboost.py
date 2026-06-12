#!/usr/bin/env python3
"""Análise da raiz do classificador de domínio do ReFAIR (XGBoost sobre input_ids).

Mostra, com dados, por que o modelo acerta 100% no treino (sintético) e 9,4% no
UStAI: ele decora o TOKEN na posição 3 (a palavra do papel), em vez do significado.

Compara a posição 3 entre TODAS as US do treino e TODAS as do UStAI.

Requer: xgboost, transformers, pandas (venv do ReFAIR). Rodar de documents/datasets/.
"""
import warnings; warnings.filterwarnings('ignore')
import pickle, csv
from collections import Counter, defaultdict
import pandas as pd
from transformers import BertTokenizer

ROOT = '/Users/romulodomingos/Documents/ProjetoFacul/IN-0953-ReFair/'
SRC = ROOT + 'ReFAIR/3. Source Code/ReFair/'

tok = BertTokenizer.from_pretrained('bert-base-uncased')

def pos3_token(text):
    ids = tok([str(text)], padding='max_length', max_length=100, truncation=True)['input_ids'][0]
    return tok.convert_ids_to_tokens([ids[3]])[0], ids[3]

# ---------- 1) DUMP DA ÁRVORE + FEATURES RAIZ ----------
clf = pickle.load(open(SRC + 'models/XGBClassifier.pkl', 'rb'))
booster = clf.get_booster()
print("=== ÁRVORE 0 (dump cru, 1 de 5092) ===")
print(booster.get_dump()[0])
roots = booster.trees_to_dataframe()
roots = roots[roots['Node'] == 0]
print("=== POSIÇÕES usadas como RAIZ (top 10) ===")
for f, c in Counter(roots['Feature']).most_common(10):
    print(f"  posição {f}: raiz de {c} árvores")

# ---------- 2) carregar treino + UStAI ----------
train = pd.read_excel(SRC + 'datasets/Synthetic User Stories.xlsx')
train = train[['Domain', 'User Story']].dropna()
ustai = list(csv.DictReader(open(ROOT + 'documents/datasets/essenciais/ustai-gabarito-completo.csv', encoding='utf-8-sig')))

tr_pos3 = defaultdict(Counter)   # domínio -> Counter(token)
for _, r in train.iterrows():
    t, _ = pos3_token(r['User Story'])
    tr_pos3[r['Domain'].strip()][t] += 1
us_pos3 = defaultdict(Counter)
for r in ustai:
    t, _ = pos3_token(r['User Story'])
    us_pos3[r['equivalent_domain'].strip()][t] += 1

print("\n=== TREINO: token na posição 3 (papel) por domínio — top 4 ===")
for d in sorted(tr_pos3):
    top = ', '.join(f"{w}({n})" for w, n in tr_pos3[d].most_common(4))
    print(f"  {d:22s} [{sum(tr_pos3[d].values())} US]: {top}")

print("\n=== UStAI: token na posição 3 (papel) por domínio — top 4 ===")
for d in sorted(us_pos3):
    top = ', '.join(f"{w}({n})" for w, n in us_pos3[d].most_common(4))
    print(f"  {d:22s} [{sum(us_pos3[d].values())} US]: {top}")

# ---------- 3) PUREZA: posição 3 prevê o domínio? ----------
def purity(pos3_map):
    # constrói token -> domínio majoritário e mede acerto
    tok2dom = defaultdict(Counter)
    for dom, cnt in pos3_map.items():
        for t, n in cnt.items():
            tok2dom[t][dom] += n
    total = correct = 0
    for t, doms in tok2dom.items():
        n = sum(doms.values()); maj = doms.most_common(1)[0][1]
        total += n; correct += maj
    return correct / total, tok2dom

tr_pur, tr_map = purity(tr_pos3)
us_pur, _ = purity(us_pos3)
print(f"\n=== PUREZA da posição 3 (se você SÓ soubesse o token do papel, acertaria o domínio?) ===")
print(f"  TREINO : {100*tr_pur:.1f}%   (posição 3 quase DEFINE o domínio -> dá pra decorar)")
print(f"  UStAI  : {100*us_pur:.1f}%   (posição 3 NÃO define o domínio -> não dá pra decorar)")

# ---------- 4) TRANSFER: o mapa decorado no treino funciona no UStAI? ----------
# mapa token->domínio majoritário aprendido no TREINO, aplicado ao UStAI
tok2dom_train = {t: doms.most_common(1)[0][0] for t, doms in tr_map.items()}
seen = unseen = hit = 0
for r in ustai:
    t, _ = pos3_token(r['User Story'])
    real = r['equivalent_domain'].strip()
    if t in tok2dom_train:
        seen += 1
        if tok2dom_train[t] == real: hit += 1
    else:
        unseen += 1
N = len(ustai)
print(f"\n=== O 'mapa decorado' (posição 3 -> domínio, aprendido no treino) no UStAI ===")
print(f"  US do UStAI cujo papel (token pos.3) NUNCA apareceu no treino: {unseen}/{N} = {100*unseen/N:.1f}%")
print(f"  Mesmo entre os {seen} 'vistos', acerto do mapa: {hit}/{seen} = {100*hit/max(seen,1):.1f}%")

# ---------- 5) SOBREPOSIÇÃO entre domínios ----------
def shared(pos3_map):
    tokdoms = defaultdict(set)
    for dom, cnt in pos3_map.items():
        for t in cnt: tokdoms[t].add(dom)
    multi = sum(1 for t, ds in tokdoms.items() if len(ds) > 1)
    return multi, len(tokdoms)
tr_m, tr_tot = shared(tr_pos3); us_m, us_tot = shared(us_pos3)
print(f"\n=== SOBREPOSIÇÃO: tokens de papel (pos.3) que caem em >1 domínio ===")
print(f"  TREINO : {tr_m}/{tr_tot} = {100*tr_m/tr_tot:.1f}% dos papéis são ambíguos")
print(f"  UStAI  : {us_m}/{us_tot} = {100*us_m/us_tot:.1f}% dos papéis são ambíguos")

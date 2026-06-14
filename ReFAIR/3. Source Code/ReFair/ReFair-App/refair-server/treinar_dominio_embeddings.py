#!/usr/bin/env python3
"""Treina o detector de dominio da EXTENSAO (BERT mean-pool + LogReg) e salva o
modelo em models/domain_embed_logreg.pkl, usado pelo getDomain do REFAIR.py.

Treina SO no sintetico do ReFAIR (balanceado ~100 US/dominio). O UStAI continua
sendo apenas teste — este script nao o toca.

Rodar (uma vez, e sempre que quiser re-treinar):
    cd refair-server
    venv_mac/bin/python treinar_dominio_embeddings.py      # macOS
    env\\Scripts\\python treinar_dominio_embeddings.py       # Windows
"""
import pickle
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from domain_embed import embed, canon_domain

BASE = Path(__file__).resolve().parent
OUT = BASE / "models" / "domain_embed_logreg.pkl"

print("carregando treino (sintetico)...")
ds = pd.read_excel(BASE / "datasets" / "Synthetic User Stories.xlsx")[["Domain", "User Story"]].dropna()
ds["dom"] = ds["Domain"].map(canon_domain)

# amostra balanceada: ate 100 US por dominio (seed fixo -> reproduzivel)
parts = [g.sample(min(100, len(g)), random_state=42) for _, g in ds.groupby("dom")]
tr = pd.concat(parts)
print(f"treino: {len(tr)} US, {tr['dom'].nunique()} dominios")

print("gerando embeddings do BERT...")
X = embed(list(tr["User Story"]))
y = list(tr["dom"])

print("treinando LogisticRegression...")
clf = LogisticRegression(max_iter=2000, C=1.0)
clf.fit(X, y)

acc_tr = accuracy_score(y, clf.predict(X))
print(f"sanity (acerto no proprio treino): {100*acc_tr:.1f}%")

OUT.parent.mkdir(exist_ok=True)
with open(OUT, "wb") as f:
    pickle.dump(clf, f)
print(f"modelo salvo em: {OUT}")

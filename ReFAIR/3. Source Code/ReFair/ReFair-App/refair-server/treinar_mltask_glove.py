#!/usr/bin/env python3
"""Treina o detector de ML TASK da extensao — CONFIG D: GloVe-media + OneVsRest(LogReg)
+ limiar sintonizado no sintetico. Salva models/mltask_glove_ovr.pkl.

Por que GloVe (e nao embeddings do BERT) no estagio 2: a ablacao (ameaca #6) mostrou
que, para ML task, o GloVe GENERALIZA MELHOR que o mean-pool do BERT no UStAI
(F1 0,283 vs 0,243) — a tarefa depende de palavras-chave de acao ("classify",
"predict", "summarize") que o vetor de palavra capta direto. (No DOMINIO o embedding
ganha; por isso o getDomain continua com embeddings.)

Mesmo ALVO (Y) do modelo original (Keyword labelled.xlsx). So muda o classificador
(LabelPowerset->OneVsRest, p/ ter probabilidade e limiar) e o filtro (duro->soft,
aplicado no getMLTask). Treina so no sintetico; UStAI continua sendo teste.

Rodar:
    cd refair-server
    venv_mac/bin/python treinar_mltask_glove.py
"""
import pickle
import re
import unicodedata
from pathlib import Path

import gensim
import numpy as np
import pandas as pd
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

BASE = Path(__file__).resolve().parent
KEYWORDS = BASE.parents[2] / "2. Tasks Detection" / "Keyword labelled.xlsx"
OUT = BASE / "models" / "mltask_glove_ovr.pkl"

print("carregando GloVe...")
glove = gensim.models.KeyedVectors.load_word2vec_format(
    str(BASE / "models" / "glove.6B.100d.txt"), binary=False, no_header=True)


def _norm_token(word):                      # identico ao usado no getMLTask (inferencia)
    word = unicodedata.normalize('NFKD', word.lower())
    word = ''.join(c for c in word if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9']", '', word)


def glove_avg(text):
    words = str(text).replace('-', ' ').replace('/', ' ').split()
    vecs = [glove[t] for w in words if (t := _norm_token(w)) and t in glove]
    return np.array(sum(vecs) / len(vecs) if vecs else [0.0] * 100)


def micro_f1(yt, yp):
    yt = yt.astype(bool); yp = yp.astype(bool)
    tp = int((yt & yp).sum()); fp = int((~yt & yp).sum()); fn = int((yt & ~yp).sum())
    P = tp / (tp + fp) if tp + fp else 0.0
    R = tp / (tp + fn) if tp + fn else 0.0
    return 2 * P * R / (P + R) if P + R else 0.0


print("construindo alvo Y (tarefa fina -> categorias grossas)...")
ds = pd.read_excel(BASE / "datasets" / "Synthetic User Stories.xlsx")
labels = pd.read_excel(KEYWORDS, header=None)
labels[2] = labels[2].apply(lambda x: str(x).lower())
labels["C"] = [[str(l).lower() for l in r[3:] if isinstance(l, str)] for _, r in labels.iterrows()]
target = []
for _, row in ds.iterrows():
    m = labels[labels[2] == str(row["Machine Learning Task"]).lower()]["C"].values
    target.append(m[0] if len(m) else [])
mlb = MultiLabelBinarizer()
y = mlb.fit_transform(target)
print(f"treino: {len(ds)} US, {len(mlb.classes_)} categorias")

print("gerando features GloVe-media...")
X = np.vstack([glove_avg(s) for s in ds["User Story"]])


def build():
    return make_pipeline(StandardScaler(),
                         OneVsRestClassifier(LogisticRegression(max_iter=2000, C=1.0)))


# limiar sem vazamento: sintonizado num split de validacao do SINTETICO (80/20)
Xtr, Xval, ytr, yval = train_test_split(X, y, test_size=0.2, random_state=42)
sel = build(); sel.fit(Xtr, ytr); Pval = sel.predict_proba(Xval)
THRESHOLD = max([round(0.05 * k, 2) for k in range(1, 11)],
                key=lambda t: micro_f1(yval, (Pval >= t).astype(int)))
print(f"limiar escolhido na validacao: {THRESHOLD}")

print("re-treinando em 100% do sintetico...")
clf = build(); clf.fit(X, y)

OUT.parent.mkdir(exist_ok=True)
with open(OUT, "wb") as f:
    pickle.dump({"clf": clf, "mlb": mlb, "threshold": THRESHOLD}, f)
print(f"modelo salvo em: {OUT}  (threshold={THRESHOLD})")

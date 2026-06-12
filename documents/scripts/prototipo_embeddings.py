#!/usr/bin/env python3
"""Protótipo (Rota C): trocar input_ids por EMBEDDINGS do BERT no detector de domínio.

Compara com o ReFAIR original (9,4% no UStAI). Treina no sintético, testa no UStAI
(held-out — nunca treinado nele). Mede quanto a representação semântica recupera.

BERT-base mean-pooling é um LIMITE INFERIOR (não é fine-tuned p/ frases);
sentence-transformers tende a ir melhor.
"""
import warnings; warnings.filterwarnings('ignore')
import csv, random
import numpy as np
import torch
import pandas as pd
from transformers import BertTokenizer, BertModel
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

random.seed(42); np.random.seed(42); torch.manual_seed(42)
ROOT = '/Users/romulodomingos/Documents/ProjetoFacul/IN-0953-ReFair/'
SRC = ROOT + 'ReFAIR/3. Source Code/ReFair/'
FIX = {'demograpy': 'demography', 'psycology': 'psychology'}
nd = lambda s: FIX.get(s.strip().lower(), s.strip().lower())

print("carregando BERT...")
tok = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased'); model.eval()

@torch.no_grad()
def embed(texts, bs=32):
    out = []
    for i in range(0, len(texts), bs):
        batch = [str(t) for t in texts[i:i+bs]]
        enc = tok(batch, padding='max_length', max_length=100, truncation=True, return_tensors='pt')
        h = model(**enc).last_hidden_state                 # [B,T,768]
        m = enc['attention_mask'].unsqueeze(-1).float()
        emb = (h * m).sum(1) / m.sum(1).clamp(min=1)        # mean-pool
        out.append(emb.numpy())
        if (i // bs) % 20 == 0:
            print(f"  embed {i+len(batch)}/{len(texts)}")
    return np.vstack(out)

# ---- treino: amostra balanceada do sintético (~100/domínio) ----
train = pd.read_excel(SRC + 'datasets/Synthetic User Stories.xlsx')[['Domain', 'User Story']].dropna()
train['dom'] = train['Domain'].map(nd)
parts = []
for d, g in train.groupby('dom'):
    parts.append(g.sample(min(100, len(g)), random_state=42))
tr = pd.concat(parts)
print(f"treino: {len(tr)} US, {tr['dom'].nunique()} domínios")

# ---- UStAI (teste held-out) ----
ustai = list(csv.DictReader(open(ROOT + 'documents/datasets/essenciais/ustai-gabarito-completo.csv', encoding='utf-8-sig')))
us_text = [r['User Story'] for r in ustai]
us_y = [nd(r['equivalent_domain']) for r in ustai]

print("\nembeddings do treino...")
Xtr = embed(list(tr['User Story'])); ytr = list(tr['dom'])
print("embeddings do UStAI...")
Xus = embed(us_text)

print("\ntreinando LogReg...")
clf = LogisticRegression(max_iter=2000, C=1.0)
clf.fit(Xtr, ytr)
pred = clf.predict(Xus)

covered = sorted(set(us_y))
acc = accuracy_score(us_y, pred)
f1 = f1_score(us_y, pred, labels=covered, average='macro', zero_division=0)
# acerto no próprio treino (sanity)
acc_tr = accuracy_score(ytr, clf.predict(Xtr))

print("\n==================== RESULTADO ====================")
print(f"  ReFAIR original (XGBoost sobre input_ids)  : 9,4%  (F1 0,125)")
print(f"  PROTÓTIPO (BERT mean-pool + LogReg) no UStAI: {100*acc:.1f}%  (F1 {f1:.3f})")
print(f"  (sanity: acerto no próprio treino = {100*acc_tr:.1f}%)")
print("===================================================")

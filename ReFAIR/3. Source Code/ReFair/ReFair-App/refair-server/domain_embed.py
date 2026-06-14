"""Vetorizacao semantica (BERT mean-pool) para o detector de dominio — extensao RQ2.

Mesma logica de embedding usada no TREINO (treinar_dominio_embeddings.py) e na
INFERENCIA (getDomain em REFAIR.py). Manter num so lugar evita divergencia entre
o que o classificador aprendeu e o que recebe em producao.

Substitui a representacao 'input_ids por posicao' (que decorava o papel na pos.3,
~9,4% no UStAI) pelo SIGNIFICADO da story (embedding 768-dim, ~37% no UStAI).
"""
import numpy as np
import torch
from transformers import BertTokenizer, BertModel

_tok = BertTokenizer.from_pretrained('bert-base-uncased')
_model = BertModel.from_pretrained('bert-base-uncased')
_model.eval()


@torch.no_grad()
def embed(texts, bs=32):
    """texto(s) -> matriz (N, 768) de embeddings (mean-pool mascarado do BERT)."""
    out = []
    for i in range(0, len(texts), bs):
        batch = [str(t) for t in texts[i:i + bs]]
        enc = _tok(batch, padding='max_length', max_length=100,
                   truncation=True, return_tensors='pt')
        h = _model(**enc).last_hidden_state              # [B, T, 768]
        m = enc['attention_mask'].unsqueeze(-1).float()
        emb = (h * m).sum(1) / m.sum(1).clamp(min=1)     # media so sobre tokens reais
        out.append(emb.numpy())
    return np.vstack(out)


def canon_domain(d):
    """Normaliza o rotulo de dominio: corrige typos do dataset e usa Title Case
    (mesmo formato do gabarito; o downstream compara com .lower())."""
    d = ' '.join(str(d).split()).strip().lower()
    d = {'demograpy': 'demography', 'psycology': 'psychology'}.get(d, d)
    return d.title()

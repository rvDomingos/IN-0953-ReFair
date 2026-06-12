#!/usr/bin/env python3
"""Item B — gera a rodada OFICIAL do ReFAIR (SEM o patch do GloVe).

O estudo de validade externa testa o ReFAIR como CAIXA-PRETA congelada. O patch
do GloVe modifica o estágio 2, então os números oficiais devem vir do ReFAIR
ORIGINAL. O patch fica como sub-experimento de melhoria à parte.

Como o patch só toca o getMLTask (estágio 2), os DOMÍNIOS (estágio 1) são
idênticos — reaproveitamos os domínios já calculados em refair-resultados.csv e
recomputamos só ML task (versão original, sem normalização) + features.

Saída: refair-resultados-oficial.csv (mesmas colunas de refair-resultados.csv).
Rodar (em refair-server, venv ativo):
    python gerar_resultado_oficial.py
"""
import csv
import pandas as pd
import REFAIR

ENTRADA = '../../../../documents/datasets/refair-resultados.csv'   # rodada COM patch (p/ reaproveitar domínio + texto)
SAIDA   = '../../../../documents/datasets/refair-resultados-oficial.csv'


def getMLTask_original(user_story, domain):
    """getMLTask como no código ORIGINAL do paper: split puro, sem normalizar tokens."""
    words = user_story.split()
    vecs = [REFAIR.glove_vectors[w] for w in words if w in REFAIR.glove_vectors]
    vec = (sum(vecs) / len(vecs)) if vecs else [0] * 100
    td = pd.DataFrame([vec]); td.columns = td.columns.astype(str)
    out = []
    for p in REFAIR.mlb.inverse_transform(REFAIR.lsvc.predict(td.values))[0]:
        for idx in REFAIR.domain_task_mapping.index:
            if (REFAIR.domain_task_mapping['Domain'][idx].lower() == domain.lower()
                    and REFAIR.domain_task_mapping['Task'][idx].lower() == p.lower()):
                out.append(p)
    return out


rows = list(csv.DictReader(open(ENTRADA, encoding='utf-8')))
print(f"Recomputando ML task + features SEM patch para {len(rows)} stories...")
out = []
n_vazio = 0
for i, r in enumerate(rows):
    story = r['User Story']
    domain = r['refair_domain']          # idêntico com/sem patch (patch não toca estágio 1)
    ml = getMLTask_original(story, domain) if domain else []
    feats = REFAIR.feature_extraction(domain, ml) if domain else {}
    union, seen = [], set()
    for fs in feats.values():
        for f in fs:
            if f not in seen:
                seen.add(f); union.append(f)
    por_task = ' | '.join(f"{t}: {', '.join(fs) if fs else '—'}" for t, fs in feats.items())
    if not ml:
        n_vazio += 1
    out.append({
        'id': r['id'], 'User Story': story, 'refair_domain': domain,
        'refair_ml_tasks': '; '.join(ml), 'refair_features': '; '.join(union),
        'refair_features_por_task': por_task,
        'ml_task_vazio': 'Sim' if not ml else 'Não', 'erro': '',
    })
    if (i + 1) % 200 == 0:
        print(f"  {i+1}/{len(rows)}")

cols = ['id', 'User Story', 'refair_domain', 'refair_ml_tasks', 'refair_features',
        'refair_features_por_task', 'ml_task_vazio', 'erro']
with open(SAIDA, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
print(f"\nOK -> {SAIDA}")
print(f"  ML task VAZIO (sem patch): {n_vazio}/{len(rows)}")

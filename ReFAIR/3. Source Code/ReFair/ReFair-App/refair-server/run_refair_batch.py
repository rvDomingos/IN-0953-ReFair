#!/usr/bin/env python3
"""Roda a pipeline do ReFAIR (domínio -> ML task -> atributos sensíveis) em LOTE,
sobre um arquivo de user stories, e exporta um CSV com o resultado de cada story.

Pra que serve: o front do ReFair analisa 1 story por vez (clique a clique). Este
script processa as 1260 de uma vez, gerando o arquivo que a comparação com o
gabarito espera.

COMO RODAR (na máquina onde o ReFair funciona — Windows / Python 3.9 / venv 'env'):
    cd refair-server
    env\\Scripts\\activate            # (Windows)   ou   source env/bin/activate
    python run_refair_batch.py "..\\..\\..\\..\\documents\\datasets\\ustai-stories-para-refair.csv"

O arquivo de entrada precisa ter as colunas 'User Story' e (opcional) 'id'.
Use o TEXTO ORIGINAL das stories — o patch do getMLTask já normaliza pro GloVe,
e o getDomain (BERT) deve receber o texto intacto.

Saída: refair-resultados.csv  (mesmo diretório), com as colunas:
    id, User Story, refair_domain, refair_ml_tasks, refair_features,
    refair_features_por_task, ml_task_vazio, erro
"""
import sys
import csv
import argparse
from pathlib import Path

import pandas as pd

from REFAIR import getDomain, getMLTask, feature_extraction


def carregar(path):
    path = Path(path)
    if path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    if "User Story" not in df.columns:
        raise SystemExit(f'ERRO: o arquivo {path} não tem coluna "User Story". '
                         f'Colunas encontradas: {list(df.columns)}')
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", help="CSV/XLSX com colunas 'User Story' e (opcional) 'id'")
    ap.add_argument("-o", "--saida", default="refair-resultados.csv")
    args = ap.parse_args()

    df = carregar(args.entrada)
    total = len(df)
    print(f"Processando {total} user stories de {args.entrada} ...")

    linhas = []
    for i, row in df.iterrows():
        story = str(row["User Story"]).strip()
        sid = str(row["id"]).strip() if "id" in df.columns and pd.notna(row.get("id")) else f"row{i+1}"

        domain = ml_tasks = features = None
        erro = ""
        try:
            domain = getDomain(story)
            ml_tasks = getMLTask(story, domain)
            features = feature_extraction(domain, ml_tasks)
        except Exception as e:           # uma story problemática não derruba o lote
            erro = f"{type(e).__name__}: {e}"

        # união dos atributos sensíveis (o que o front mostra agregado)
        union, seen = [], set()
        if features:
            for feats in features.values():
                for f in feats:
                    if f not in seen:
                        seen.add(f); union.append(f)
        por_task = ""
        if features:
            por_task = " | ".join(
                f"{t}: {', '.join(fs) if fs else '—'}" for t, fs in features.items()
            )

        linhas.append({
            "id": sid,
            "User Story": story,
            "refair_domain": domain or "",
            "refair_ml_tasks": "; ".join(ml_tasks) if ml_tasks else "",
            "refair_features": "; ".join(union),
            "refair_features_por_task": por_task,
            "ml_task_vazio": "Sim" if (not ml_tasks and not erro) else "Não",
            "erro": erro,
        })

        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(f"  {i+1}/{total}")

    cols = ["id", "User Story", "refair_domain", "refair_ml_tasks",
            "refair_features", "refair_features_por_task", "ml_task_vazio", "erro"]
    with open(args.saida, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(linhas)

    n_vazio = sum(1 for l in linhas if l["ml_task_vazio"] == "Sim")
    n_erro = sum(1 for l in linhas if l["erro"])
    print(f"\nOK -> {args.saida}")
    print(f"  stories processadas : {total}")
    print(f"  ML task VAZIO       : {n_vazio}")
    print(f"  erros               : {n_erro}")


if __name__ == "__main__":
    main()

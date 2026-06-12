#!/usr/bin/env python3
"""Compara a saída do ReFAIR entre duas plataformas (ex.: Windows x macOS).

Valida reprodutibilidade: as predições de domínio e ML task devem ser IGUAIS
entre sistemas operacionais (modelos determinísticos). Diferença = 0 é o ideal.

Pós-processamento puro (só CSV, sem libs de ML) — roda em qualquer máquina.

Uso (a partir de documents/datasets/):
    python comparar_plataformas.py                                  # usa os 2 arquivos padrão
    python comparar_plataformas.py refair-resultados-windows.csv refair-resultados.csv

Padrão: compara refair-resultados-windows.csv (A) contra refair-resultados.csv (B, macOS).
Os dois precisam vir do MESMO script (run_refair_batch.py, que usa o REFAIR.py COM patch).
Gera também 'diferencas-plataformas.csv' com as linhas que divergem (se houver).
"""
import csv
import sys

A = sys.argv[1] if len(sys.argv) > 1 else 'refair-resultados-windows.csv'
B = sys.argv[2] if len(sys.argv) > 2 else 'refair-resultados.csv'


def carregar(path):
    try:
        return {r['id']: r for r in csv.DictReader(open(path, encoding='utf-8'))}
    except FileNotFoundError:
        sys.exit(f'ERRO: arquivo nao encontrado: {path}\n'
                 f'Rode antes o run_refair_batch.py para gerar "{path}".')


a = carregar(A)
b = carregar(B)
ids = sorted(set(a) & set(b))
print(f'Comparando:\n  A = {A}  ({len(a)} linhas)\n  B = {B}  ({len(b)} linhas)')
print(f'  ids em comum: {len(ids)}')
if set(a) ^ set(b):
    print(f'  AVISO: {len(set(a) ^ set(b))} ids existem so em um dos arquivos')

dom_dif = []
task_dif = []
for i in ids:
    if a[i]['refair_domain'].strip() != b[i]['refair_domain'].strip():
        dom_dif.append(i)
    if a[i]['refair_ml_tasks'].strip() != b[i]['refair_ml_tasks'].strip():
        task_dif.append(i)

print('\n=== RESULTADO ===')
print(f'divergencias de DOMINIO : {len(dom_dif)}')
print(f'divergencias de ML TASK : {len(task_dif)}')

if not dom_dif and not task_dif:
    print('\nIDENTICO entre as plataformas -> reprodutibilidade confirmada.')
else:
    print('\nHA DIVERGENCIAS -> registrar como ameaca a validade no relatorio.')
    with open('diferencas-plataformas.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'campo', 'valor_A', 'valor_B'])
        for i in dom_dif:
            w.writerow([i, 'refair_domain', a[i]['refair_domain'], b[i]['refair_domain']])
        for i in task_dif:
            w.writerow([i, 'refair_ml_tasks', a[i]['refair_ml_tasks'], b[i]['refair_ml_tasks']])
    print('  -> detalhes em diferencas-plataformas.csv')
    print('\n  Primeiras divergencias de dominio:')
    for i in dom_dif[:8]:
        print(f'    {i}: A={a[i]["refair_domain"]!r}  B={b[i]["refair_domain"]!r}')

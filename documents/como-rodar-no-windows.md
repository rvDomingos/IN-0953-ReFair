# Como rodar o experimento ReFAIR × UStAI no Windows

**Data:** 2026-06-09
**Objetivo:** rodar **todo** o pipeline do experimento no **Windows** (ambiente original do ReFAIR — Python 3.9): setup do ambiente, execução do ReFAIR em lote sobre as 1260 user stories, geração das planilhas de análise e a **validação cross-platform** (conferir que o resultado bate com o do macOS).

> Por que Windows: a rodada de referência foi feita no macOS (Python 3.11). O ReFAIR foi desenvolvido/treinado no Windows (Python 3.9). Reproduzir aqui confirma que as predições não dependem do SO — exigência de reprodutibilidade (ver [o-que-falta.md](o-que-falta.md), Seção C).

---

## 0. Pré-requisitos

- **Windows 10/11**, com **PowerShell** ou **Prompt de Comando (cmd)**.
- **Python 3.9 (64-bit)** — *não* use 3.10+, as libs do `requirements.txt` (torch 2.0.0, sklearn 1.2.2…) não têm wheel pras versões novas.
  - Baixar em [python.org/downloads](https://www.python.org/downloads/release/python-3913/) → marcar **"Add python.exe to PATH"** na instalação.
  - Conferir: `py -3.9 --version` deve mostrar `Python 3.9.x`.
- **Git** ([git-scm.com](https://git-scm.com/download/win)).
- **~5 GB** livres (modelos + dependências).
- **Internet** na primeira execução (baixa o BERT `bert-base-uncased`, ~250 MB).
- **Habilitar caminhos longos** (o projeto tem pastas com espaços e nomes longos):
  - PowerShell **como Administrador**:
    ```powershell
    New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
    ```

---

## 1. Obter o repositório e o GloVe

```bat
git clone <url-do-repo> IN-0953-ReFair
cd IN-0953-ReFair
git pull
```

> ⚠️ **Garanta que o `REFAIR.py` é o patcheado** (com a função `_norm_token`) e que o `run_refair_batch.py` está presente em `refair-server`. Se clonou/puxou do mesmo repo, já vem.

O modelo **GloVe** (~347 MB) não fica no Git. Baixe e coloque em `models/`:

```bat
cd "ReFAIR\3. Source Code\ReFair\ReFair-App\refair-server\models"
curl -L -o glove.6B.zip https://nlp.stanford.edu/data/glove.6B.zip
tar -xf glove.6B.zip glove.6B.100d.txt
del glove.6B.zip
cd ..\..\..\..\..\..\..
```

> `curl` e `tar` já vêm no Windows 10/11. Se preferir, baixe pelo navegador e extraia o `glove.6B.100d.txt` manualmente para a pasta `models`.

Confirme que existem também os pickles: `models\XGBClassifier.pkl`, `models\LinearSVC_LabelPowerset.pkl`, `models\multilabel.pkl`.

---

## 2. Criar o ambiente Python (venv próprio)

> **Não use** a pasta `env/` que vem no repo — ela é um venv do autor original (aponta para `C:\Users\carmi\...`) e não funciona na sua máquina.

Na pasta `refair-server`:

```bat
cd "ReFAIR\3. Source Code\ReFair\ReFair-App\refair-server"
py -3.9 -m venv venv_win
venv_win\Scripts\activate
python -m pip install --upgrade pip
```

Instale as dependências **nas versões exatas** (cria/atualiza o `requirements.txt` com este conteúdo se o seu estiver incompleto):

```txt
flask==2.3.2
flask-cors==4.0.0
werkzeug==2.3.6
pandas==1.5.3
numpy==1.24.2
scipy==1.10.1
scikit-learn==1.2.2
scikit-multilearn==0.2.0
xgboost==1.7.4
transformers==4.27.1
tokenizers==0.13.2
huggingface-hub==0.13.2
torch==2.0.0
gensim==4.3.1
openpyxl==3.1.2
```

```bat
pip install -r requirements.txt
```

> As versões fixas são **obrigatórias**: os `.pkl` foram salvos com sklearn 1.2.2 / xgboost 1.7.4 e podem não carregar em versões diferentes.

---

## 3. Sanity check (modelos carregam?)

```bat
python -c "import warnings; warnings.filterwarnings('ignore'); import pickle; [print('OK', f) for f in ['models/XGBClassifier.pkl','models/LinearSVC_LabelPowerset.pkl','models/multilabel.pkl'] if pickle.load(open(f,'rb')) is not None]; import REFAIR; print('REFAIR OK')"
```

Esperado: três `OK ...` e `REFAIR OK` (na primeira vez baixa o `bert-base-uncased`).

Opcional — confirme que o modelo acerta as stories de **treino** (deve dar ~100%):

```bat
python -c "import warnings; warnings.filterwarnings('ignore'); import pandas as pd, REFAIR; d=pd.read_excel('datasets/Synthetic User Stories.xlsx').sample(50, random_state=1); ok=sum(str(REFAIR.getDomain(str(r['User Story']))).lower()==str(r['Domain']).lower() for _,r in d.iterrows()); print(f'treino: {ok}/50')"
```

---

## 4. Rodar o ReFAIR em lote (as 1260 user stories)

Com o venv ativo, ainda em `refair-server`:

```bat
python run_refair_batch.py "..\..\..\..\documents\datasets\ustai-stories-para-refair.csv" -o "..\..\..\..\documents\datasets\refair-resultados-windows.csv"
```

> Use o **texto original** (`ustai-stories-para-refair.csv`) — o patch do GloVe já normaliza no estágio 2 e o BERT (estágio 1) deve receber o texto intacto. **Não** use o `glove-clean`.

Saída esperada ao final:
```
OK -> ...\refair-resultados-windows.csv
  stories processadas : 1260
  ML task VAZIO       : 535
  erros               : 0
```

Colunas do CSV: `id, User Story, refair_domain, refair_ml_tasks, refair_features, refair_features_por_task, ml_task_vazio, erro`.

> ⏱️ Demora alguns minutos (carrega GloVe de 347 MB + roda BERT/XGBoost/LSVC em 1260 stories).

---

## 5. Validação cross-platform (o ponto principal de rodar no Windows)

Compare o resultado do Windows com o do macOS (`refair-resultados.csv`). Idealmente **zero divergências** em domínio e ML task:

```bat
python -c "import csv; a={r['id']:r for r in csv.DictReader(open('../../../../documents/datasets/refair-resultados.csv',encoding='utf-8'))}; b={r['id']:r for r in csv.DictReader(open('../../../../documents/datasets/refair-resultados-windows.csv',encoding='utf-8'))}; ids=set(a)&set(b); dd=sum(a[i]['refair_domain']!=b[i]['refair_domain'] for i in ids); dt=sum(a[i]['refair_ml_tasks']!=b[i]['refair_ml_tasks'] for i in ids); print(f'comparadas: {len(ids)}'); print(f'divergencias de DOMINIO: {dd}'); print(f'divergencias de ML TASK: {dt}')"
```

- **`divergencias de DOMINIO: 0` e `ML TASK: 0`** → as predições são iguais entre SO; pode usar qualquer rodada como oficial.
- **Se houver divergências** → quantifique, registre **quais** stories e declare como ameaça à validade no relatório (provável causa: builds diferentes de torch/BLAS produzindo arredondamentos distintos).

> Registre no relatório o **ambiente** das duas rodadas (SO, Python, versões das libs) — exigência de reprodutibilidade.

---

## 6. (Opcional) Gerar as planilhas de análise no Windows

A análise (comparação com o gabarito, matriz de confusão, etc.) é **pós-processamento puro** (sem libs de ML) e roda igual em qualquer SO. Para reproduzir no Windows, salve o script abaixo como `analisar_resultados.py` em `documents\datasets\` e rode com `python analisar_resultados.py`:

```python
import csv
from collections import Counter, defaultdict
RES='refair-resultados-windows.csv'   # ou refair-resultados.csv
GAB='ustai-gabarito-completo.csv'
res={r['id']:r for r in csv.DictReader(open(RES,encoding='utf-8'))}
gab={r['id']:r for r in csv.DictReader(open(GAB,encoding='utf-8-sig'))}
FIX={'demograpy':'demography','psycology':'psychology'}
nd=lambda s:(lambda x:FIX.get(x,x))(s.strip().lower())
ids=[i for i in gab if i in res]
ok=sum(nd(res[i]['refair_domain'])==nd(gab[i]['equivalent_domain']) for i in ids)
vazio=sum(res[i]['ml_task_vazio']=='Sim' for i in ids)
print(f'stories: {len(ids)}')
print(f'DOMINIO acerto: {ok}/{len(ids)} = {100*ok/len(ids):.1f}%')
print(f'ML task vazia : {vazio}/{len(ids)} = {100*vazio/len(ids):.1f}%')
# matriz de confusao (long)
conf=Counter((gab[i]['equivalent_domain'].strip(), res[i]['refair_domain'].strip()) for i in ids if nd(res[i]['refair_domain'])!=nd(gab[i]['equivalent_domain']))
print('\nTop confusoes (gabarito -> refair):')
for (g,r),c in conf.most_common(10): print(f'  {c:3d}  {g} -> {r}')
```

> O pipeline completo de análise (comparação 1-a-1, matriz de confusão em formato planilha, resumo por abstract, impacto do patch) já está versionado em `documents/datasets/` — esses arquivos são gerados a partir do `refair-resultados.csv` e independem do SO.

---

## 7. (Alternativa) Rodar via Docker — ambiente único, sem instalar nada

Se quiser eliminar a variável "SO/versão de lib", use o Docker que já vem no projeto (ver [plano-de-acao-refair.md](plano-de-acao-refair.md), Seção 6):

```bat
cd "ReFAIR\3. Source Code\ReFair"
docker compose build
docker compose up -d
```

Depois copie o `run_refair_batch.py` e os dados para dentro do container e rode lá. Isso dá o ambiente mais reprodutível possível (mesma imagem em qualquer máquina).

---

## 8. Problemas comuns no Windows

| Sintoma | Causa / Correção |
|---|---|
| `pip` falha ao ler `requirements.txt` | O arquivo original do `ReFair/` está em **UTF-16**. Reescreva em **UTF-8 sem BOM** (ou use o bloco da Seção 2). |
| `ModuleNotFoundError` ao rodar o batch | venv não ativado. Rode `venv_win\Scripts\activate` antes. |
| `FileNotFoundError: glove.6B.100d.txt` | GloVe não está em `refair-server\models\`. Ver Seção 1. |
| `torch` não instala | Confirme **Python 3.9 64-bit**. Em 3.10+/32-bit não há wheel do torch 2.0.0. |
| Erro de caminho longo / "path too long" | Habilite `LongPathsEnabled` (Seção 0) e evite clonar o repo muito fundo (ex.: clone em `C:\refair`). |
| `InconsistentVersionWarning` ao carregar `.pkl` | Versões de sklearn/xgboost diferentes das fixadas. Reinstale **exatamente** as da Seção 2. |
| Acentos quebrados no CSV | Abra/leia sempre com `encoding='utf-8'` (ou `utf-8-sig` para o gabarito). |
| Caminho relativo do `-o` não encontrado | O `cwd` precisa ser `refair-server`. Use caminhos **absolutos** se tiver dúvida. |

---

## Resumo do fluxo

```
1. Python 3.9 + git + GloVe em models/
2. venv_win + pip install (versões fixas)
3. sanity check (modelos carregam, treino ~100%)
4. python run_refair_batch.py ... -o refair-resultados-windows.csv
5. diff vs refair-resultados.csv (macOS)  ← validação cross-platform
6. (opcional) analisar_resultados.py
```

Arquivos relacionados: [o-que-falta.md](o-que-falta.md) · [plano-de-acao-refair.md](plano-de-acao-refair.md) · [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md) · [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md)

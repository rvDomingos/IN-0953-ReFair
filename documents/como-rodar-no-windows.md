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
python run_refair_batch.py "..\..\..\..\documents\datasets\essenciais\ustai-stories-para-refair.csv" -o "..\..\..\..\documents\datasets\essenciais\refair-resultados-windows.csv"
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
> Este arquivo sai **com patch** do GloVe (o `REFAIR.py` está patcheado). É esse que entra na validação cross-platform do passo 5.

### 4b. (Opcional) Gerar a rodada OFICIAL (sem patch) — item B

A rodada **oficial** do experimento é o ReFAIR **original, sem o patch** (caixa-preta). Para regenerá-la no Windows, ainda em `refair-server`:

```bat
python gerar_resultado_oficial.py
```

> Gera `..\..\..\..\documents\datasets\refair-resultados-oficial.csv`. Ele reaproveita os domínios (idênticos com/sem patch) e recomputa só ML task/features na versão original. É a partir dele que saem os números oficiais do relatório (ver [metricas-formais-item-a.md](metricas-formais-item-a.md)).

---

## 5. Validação cross-platform (o ponto principal de rodar no Windows)

Já existe um script versionado para isso: **[scripts/comparar_plataformas.py](scripts/comparar_plataformas.py)**. Ele compara o `refair-resultados-windows.csv` (gerado no passo 4) contra o `refair-resultados.csv` (rodada do macOS, já no repo) e reporta as divergências.

```bat
cd "..\..\..\..\documents\scripts"
python comparar_plataformas.py
```

> ⚠️ Compare contra **`refair-resultados.csv`** (não o `-oficial`): os dois saem do mesmo `run_refair_batch.py` (que usa o `REFAIR.py` **com patch**). O **domínio é idêntico com/sem patch**, então é a comparação certa para reprodutibilidade.

Saída esperada:
```
=== RESULTADO ===
divergencias de DOMINIO : 0
divergencias de ML TASK : 0

IDENTICO entre as plataformas -> reprodutibilidade confirmada.
```

- **`DOMINIO: 0` e `ML TASK: 0`** → predições iguais entre SO; reprodutibilidade confirmada.
- **Se houver divergências** → o script gera `diferencas-plataformas.csv` com as linhas; quantifique e declare como ameaça à validade no relatório (provável causa: builds diferentes de torch/BLAS).

> Registre no relatório o **ambiente** das duas rodadas (SO, Python, versões das libs) — exigência de reprodutibilidade.

---

## 6. (Opcional) Recalcular as métricas no Windows

A análise é **pós-processamento puro** (só precisa de `scikit-learn`, sem torch/transformers) e roda igual em qualquer SO. Os scripts **já estão versionados** em `documents\datasets\` — não precisa colar código. Do diretório `documents\datasets\`:

```bat
cd "<raiz-do-projeto>\documents\scripts"

REM métricas formais (F1-Score, Hamming, subset, por LLM) — usa a rodada OFICIAL por padrao
python calcular_metricas.py

REM para conferir a rodada COM patch:
python calcular_metricas.py refair-resultados.csv
```

> `calcular_metricas.py` precisa de `scikit-learn` — rode com o mesmo `venv_win` do passo 2 (que já tem). Gera `metricas-estagio1-por-dominio.csv`, `metricas-estagio2-por-label.csv`, `metricas-por-llm.csv`, `erro-end-to-end-causa.csv`.

> O restante das planilhas (comparação 1-a-1, matriz de confusão, resumo por abstract, impacto do patch, 3 fontes de features) **já está versionado** em `documents/datasets/` e independe do SO — não precisa regerar.

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
4. python run_refair_batch.py ... -o refair-resultados-windows.csv   (com patch)
   (opcional 4b) python gerar_resultado_oficial.py                    (rodada oficial, sem patch)
5. cd documents\scripts  &&  python comparar_plataformas.py           ← validação cross-platform
6. (opcional) python calcular_metricas.py                             (recalcular F1-Score etc.)
```

> Scripts usados: `run_refair_batch.py` e `gerar_resultado_oficial.py` (em `refair-server`); `comparar_plataformas.py` e `calcular_metricas.py` (em `documents\scripts\`).

Arquivos relacionados: [o-que-falta.md](o-que-falta.md) · [metricas-formais-item-a.md](metricas-formais-item-a.md) · [plano-de-acao-refair.md](plano-de-acao-refair.md) · [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md) · [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md)

# Plano de Ação — Colocar o ReFAIR para Rodar

**Data:** 2026-05-19
**Objetivo:** documentar, passo a passo, o que o ReFAIR é, como o repositório está estruturado, **quais ajustes de código/ambiente são necessários** para executá-lo localmente (CLI e App Web), e como validar o funcionamento ponta a ponta.

Este documento complementa [`analise-replicacao-novo-dataset.md`](./analise-replicacao-novo-dataset.md), que discute a viabilidade científica da replicação com um novo dataset. Aqui o foco é puramente operacional: **fazer o sistema original rodar**.

---

## 1. O que é o ReFAIR (resumo técnico do artigo)

> Fonte: Ferrara et al., *"ReFAIR: Toward a Context-Aware Recommender for Fairness Requirements Engineering"*, ICSE '24, Lisboa.

### 1.1. Problema que o ReFAIR resolve

Sistemas baseados em Machine Learning podem aprender e reproduzir **vieses históricos** presentes nos dados, levando a decisões injustas (crédito, contratação, saúde, etc.). A literatura de *software fairness* responde a isso majoritariamente em **estágios tardios** do ciclo de vida — pré-processamento, balanceamento, mitigação de viés no modelo treinado.

O ReFAIR ataca o problema **antes**: ainda na fase de **engenharia de requisitos**. A pergunta central é "**dadas as user stories de um sistema ML, quais atributos sensíveis o time precisa monitorar desde o início?**". Sensitive features dependem fortemente do contexto: idade é sensível em saúde e crédito, mas não em controle industrial; geografia é sensível em política e marketing, mas inofensiva em biologia molecular. Logo, o recomendador precisa ser **ciente do domínio** e **ciente da tarefa de ML** envolvida.

### 1.2. Arquitetura da pipeline

O ReFAIR é uma pipeline com três etapas encadeadas, alimentadas por três artefatos rotulados:

```
User Story (texto)
        │
        ▼
┌──────────────────┐
│  Pré-processamento│  →  word embeddings (BERT, GloVe, etc.)
└──────────────────┘
        │
        ├─────────────────────────┐
        ▼                         ▼
┌──────────────────┐    ┌──────────────────────────┐
│ Domain Classifier│    │  ML Task Classifier      │
│ (single-label,   │    │  (multi-label,           │
│  XGBoost+BERT)   │    │   Label Powerset + LSVC) │
└──────────────────┘    └──────────────────────────┘
        │                         │
        ▼                         ▼
   Domínio                Lista de tasks ML
        │                         │
        └────────────┬────────────┘
                     ▼
        ┌────────────────────────────┐
        │  Feature Recommendation    │
        │  (interseção entre         │
        │   features sensíveis do    │
        │   domínio e das tasks)     │
        └────────────────────────────┘
                     │
                     ▼
            Sensitive Features
            recomendadas para
            aquela US
```

**Artefatos rotulados que sustentam tudo:**

| Artefato | Origem | Conteúdo |
|---|---|---|
| **Ontologia de domínios** (34 domínios fairness-críticos) | Fabris et al. (2022), `domains.json` | Lista canônica de domínios + features sensíveis típicas. |
| **Dicionário de tasks de ML** (25 tasks de alto nível + 457 técnicas) | Duran-Silva et al. (2021), `AI vocabulary.xlsx` | Tasks como "classification", "clustering", "regression", "NLP", etc. |
| **Mapping `(domínio × task) → sensitive features`** | Construído manualmente pelos autores | Núcleo do recomendador: dado o par detectado, devolve features sensíveis. |

### 1.3. Dataset e modelos

- **Dataset sintético:** 12.401 user stories cobrindo 34 domínios, geradas pelos autores via ChatGPT (GPT-3.5) usando o cruzamento entre domínios e dicionário de tasks, e validadas em duas rodadas (interna + survey externo com 150 praticantes via Prolific).
- **Domain Classifier (RQ1):** **XGBoost + BERT** → **F1 = 0,98** em 10-fold CV (vencedor entre 125 combinações de embedding × classificador).
- **ML Task Classifier (RQ2):** **Label Powerset + Linear SVC + GloVe (100d)** → **F1 ≈ 0,90, Hamming Loss = 0,05** (vencedor entre 90 combinações de técnica multi-label × embedding × classificador base).
- **Avaliação final (RQ3):** distância MoJo entre features recomendadas e oráculo = **0,04** (≈ 4% de divergência). Em **97% das US** o recomendador foi *perfect-match*.

### 1.4. Saída concreta para o engenheiro

Para uma US do tipo:

> *"As a marketer, I want to use nearest neighbor search to identify customers with similar preferences or behaviors, so that I can provide personalized marketing messages and improve customer engagement."*

O ReFAIR responde:

- **Domínio:** `Finance & Marketing`
- **Tasks:** `Anomaly Detection`, `Clustering`, `Representation Learning`
- **Sensitive Features sugeridas:** `activity, age, gender, geography, sex, race`

Ou seja: antes mesmo de o time decidir qual modelo usar, o ReFAIR já levanta a bandeira de que **idade, gênero, raça, geografia, atividade e sexo** precisam entrar na análise de fairness daquele projeto.

---

## 2. Estrutura do repositório

```
IN-0953-ReFair/
├── README.md
├── ReFair.zip                          # backup do conteúdo (95 MB)
├── documents/
│   ├── analise-replicacao-novo-dataset.md
│   └── plano-de-acao-refair.md         # ← este arquivo
└── ReFAIR/                              # código do paper (replication package)
    ├── README.md
    ├── Technical_Report.ipynb
    ├── 1. Starting Assets/              # ontologia Fabris + dicionário Duran-Silva
    │   ├── Fabris Ontology Reenginering/
    │   └── ML Keyword Dictionary/
    ├── 2. Synthetic User Stories/       # dataset + validação
    │   ├── Synthetic User Stories.xlsx
    │   ├── Dictionaries/
    │   └── Dataset validation/Dataset_Validation.ipynb
    ├── 3. Source Code/                  # núcleo do projeto
    │   ├── 1. Domain Detection/         # notebook + dados de RQ1
    │   ├── 2. Tasks Detection/          # notebook + dados de RQ2
    │   ├── 3. Features Extraction/      # notebook do mapping
    │   └── ReFair/                      # ★ aplicação executável
    │       ├── REFAIR.py                # CLI principal
    │       ├── Dockerfile
    │       ├── docker-compose.yml
    │       ├── requirements.txt         # ⚠️ UTF-16 (ver §3.1)
    │       ├── datasets/                # CSVs do mapping + xlsx das US
    │       ├── models/                  # .pkl treinados (sem glove)
    │       └── ReFair-App/              # versão web (Flask + Vue)
    │           ├── refair-server/       # backend Flask
    │           └── refair-client/       # frontend Vue 3 + Vite
    └── 4. Experimental Results/         # reprodução de experimentos RQ1/RQ2/RQ3
```

**O que importa para "rodar":** apenas `ReFAIR/3. Source Code/ReFair/`. As outras pastas são insumos do paper (replicação, notebooks, resultados).

---

## 3. Problemas atuais que **impedem** a execução

Levantamento feito a partir da leitura do código e arquivos do repositório. Cada item abaixo está bloqueando ou degradando a execução:

### 3.1. `requirements.txt` em UTF-16 LE com BOM

- **Sintoma:** `pip install -r requirements.txt` falha em macOS/Linux com erro de parsing — pip não decodifica UTF-16.
- **Confirmado por:** `file requirements.txt` → `Unicode text, UTF-16, little-endian text, with CRLF line terminators`.
- **Causa:** arquivo gerado em Windows com `>` do PowerShell (que escreve UTF-16 por padrão).
- **Correção:** reescrever em UTF-8 sem BOM (ver §4.2).

### 3.2. Modelo GloVe ausente (~331 MB)

- **Sintoma:** `REFAIR.py` quebra na linha 21 com `FileNotFoundError: models/glove.6B.100d.txt`.
- **Causa:** o arquivo é grande demais para versionar no Git (foi `.gitignore`-ado pelo autor original) e precisa ser baixado manualmente.
- **Fonte:** [https://nlp.stanford.edu/projects/glove/](https://nlp.stanford.edu/projects/glove/) ou [Kaggle (`danielwillgeorge/glove6b100dtxt`)](https://www.kaggle.com/datasets/danielwillgeorge/glove6b100dtxt).

### 3.3. Virtualenv do Windows commitado no repositório

- **Sintoma:** `ReFair-App/refair-server/env/` contém `python.exe`, `pip.exe`, scripts `.bat` e `.ps1` — só funcionam em Windows.
- **`pyvenv.cfg`** referencia `C:\Users\carmi\...` — caminho do autor original do paper.
- **Correção:** ignorar/remover essa pasta e criar venv local (ver §4.3).

### 3.4. Port mismatch entre frontend Vue e backend Flask

- **Frontend** (`refair-client/src/components/refair.vue:130`):
  ```js
  const server = "http://localhost:5001"
  ```
- **Backend** (`refair-server/app.py:144`):
  ```python
  app.run()   # default: porta 5000
  ```
- **Sintoma:** o navegador faz requisição para `:5001`, Flask escuta em `:5000`, todas as chamadas `axios.post` falham.
- **Correção:** alinhar — recomendação: subir Flask em 5001 (ver §4.5).

### 3.5. `requirements.txt` do `refair-server` está incompleto

- **Conteúdo atual:**
  ```
  flask
  werkzeug
  flask_cors
  pandas
  numpy
  scipy
  xgboost
  transformers
  gensim
  ```
- **Faltam:** `scikit-learn`, `scikit-multilearn`, `openpyxl` (para ler o xlsx), `torch` (dependência do `transformers`).
- **Sem versões fixadas** → pode pegar versões incompatíveis (ex.: `scikit-learn 1.4` quebra `.pkl` salvos com `1.2.2`).

### 3.6. Pickle dos modelos preso à versão exata do scikit-learn / XGBoost

- Os `.pkl` foram gerados em `scikit-learn==1.2.2` e `xgboost==1.7.4`.
- Carregar em versões diferentes pode lançar `InconsistentVersionWarning` ou `AttributeError` em internals.
- **Correção:** fixar as versões originais (ver `requirements.txt` reescrito em §4.2).

### 3.7. Caminhos relativos em `REFAIR.py`

- O script usa `"datasets/..."` e `"models/..."` **sem âncora absoluta**.
- Só roda se o `cwd` for exatamente `ReFAIR/3. Source Code/ReFair/`.
- **Correção sugerida:** usar `pathlib.Path(__file__).parent` (ver §5.1).

### 3.8. Modelo BERT baixado em runtime (sem cache local)

- `BertTokenizer.from_pretrained('bert-base-uncased')` faz download no primeiro uso (~250 MB).
- **Requer internet** na primeira execução, e cache vai para `~/.cache/huggingface/`.
- Em ambientes offline / CI sem acesso a HF, é necessário pré-baixar (ver §4.4).

### 3.9. `fasttext==0.9.2` quebra no `pip install` em algumas plataformas

- Já tratado no `Dockerfile` (linha 16: `sed -i 's/fasttext==0.9.2/fasttext-wheel/g'`), mas **não está tratado fora do Docker**.
- O `requirements.txt` original tem só `fasttext-wheel` (sem versão), então localmente isso é OK *desde que o arquivo seja salvo em UTF-8*.

### 3.10. Pequenos issues de código

- `REFAIR.py` chama `getDomain(user_story)` **quatro vezes** no `main` (linhas 96–100). Cada chamada re-tokeniza com BERT e roda o XGBoost. Funcional, mas ineficiente.
- O mesmo vale para `getMLTask`.
- `app.py` em `homepage()` é OK, mas `refair_app.py` é um arquivo Flask **duplicado e incompleto** (rota `/refair` em vez de `/analyzeStory`). Aparenta ser versão antiga; pode ser deletado para evitar confusão.

### 3.11. Dataset `Synthetic User Stories.xlsx` é carregado só para extrair `dataset["Domain"].unique()`

- `REFAIR.py` carrega 12k linhas de Excel só para mapear índice → nome de domínio na linha 37:
  ```python
  return dataset["Domain"].unique()[predict[0]]
  ```
- Custo de I/O desnecessário. Poderia ser um JSON estático com 34 entradas. **Não bloqueia execução**, mas é melhoria fácil.

---

## 4. Passo a passo — Setup do ambiente

Duas rotas disponíveis. **Recomendação: Rota A (Docker)** para ambiente reprodutível. Use a Rota B (venv local) se quiser desenvolver/depurar no editor.

### 4.1. Pré-requisitos

- Python **3.9** (não use 3.10+, várias libs do `requirements.txt` quebram).
- Git.
- ~5 GB livres em disco (modelos + dependências).
- **Para a Rota A:** Docker + Docker Compose.
- **Para o App Web:** Node.js 18+ e npm.
- Acesso à internet na **primeira** execução (BERT + GloVe).

### 4.2. Ajuste obrigatório no `requirements.txt` (UTF-16 → UTF-8)

Recriar o arquivo `ReFAIR/3. Source Code/ReFair/requirements.txt` com o conteúdo abaixo (UTF-8, sem BOM):

```txt
asttokens==2.2.1
backcall==0.2.0
certifi==2022.12.7
charset-normalizer==3.1.0
click==8.1.3
colorama==0.4.6
comm==0.1.2
contourpy==1.0.7
cycler==0.11.0
debugpy==1.6.6
decorator==5.1.1
et-xmlfile==1.1.0
executing==1.2.0
fasttext-wheel
filelock==3.10.0
fonttools==4.39.3
gensim==4.3.1
huggingface-hub==0.13.2
idna==3.4
importlib-metadata==6.1.0
importlib-resources==5.12.0
ipykernel==6.21.3
ipython==8.11.0
jedi==0.18.2
Jinja2==3.1.2
joblib==1.2.0
jupyter_client==8.0.3
jupyter_core==5.3.0
kiwisolver==1.4.4
lazypredict==0.2.12
lightgbm==3.3.5
MarkupSafe==2.1.2
matplotlib==3.7.1
matplotlib-inline==0.1.6
mpmath==1.3.0
nest-asyncio==1.5.6
networkx==3.0
numpy==1.24.2
openpyxl==3.1.2
packaging==23.0
pandas==1.5.3
parso==0.8.3
pickleshare==0.7.5
Pillow==9.4.0
platformdirs==3.1.1
prompt-toolkit==3.0.38
psutil==5.9.4
pure-eval==0.2.2
pybind11==2.10.4
Pygments==2.14.0
pyparsing==3.0.9
python-dateutil==2.8.2
pytz==2022.7.1
PyYAML==6.0
pyzmq==25.0.1
regex==2022.10.31
requests==2.28.2
scikit-learn==1.2.2
scikit-multilearn==0.2.0
scipy==1.10.1
six==1.16.0
smart-open==6.3.0
stack-data==0.6.2
sympy==1.11.1
threadpoolctl==3.1.0
tokenizers==0.13.2
torch==2.0.0
torchaudio==2.0.1
torchvision==0.15.1
tornado==6.2
tqdm==4.65.0
traitlets==5.9.0
transformers==4.27.1
typing_extensions==4.5.0
urllib3==1.26.15
wcwidth==0.2.6
xgboost==1.7.4
zipp==3.15.0
flask==2.3.2
flask-cors==4.0.0
werkzeug==2.3.6
```

Comando para reescrever no terminal (a partir da raiz do projeto):

```bash
iconv -f UTF-16LE -t UTF-8 \
  "ReFAIR/3. Source Code/ReFair/requirements.txt" \
  | sed '1s/^\xEF\xBB\xBF//' \
  > /tmp/req.utf8.txt \
  && mv /tmp/req.utf8.txt "ReFAIR/3. Source Code/ReFair/requirements.txt"
```

Ou simplesmente substitua o conteúdo pelo bloco acima usando um editor.

### 4.3. Remover o venv Windows abandonado

```bash
rm -rf "ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/env"
```

Adicionar ao `.gitignore` do projeto (raiz):

```
# Python
.venv/
venv/
env/
__pycache__/
*.pyc

# Modelos grandes
ReFAIR/3. Source Code/ReFair/models/glove.6B.100d.txt
ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/models/glove.6B.100d.txt

# Node
node_modules/
dist/

# OS
.DS_Store
```

### 4.4. Baixar o GloVe 100d

```bash
cd "ReFAIR/3. Source Code/ReFair/models"
curl -L -o glove.6B.zip https://nlp.stanford.edu/data/glove.6B.zip
unzip -p glove.6B.zip glove.6B.100d.txt > glove.6B.100d.txt
rm glove.6B.zip
cd -
```

Copie também para o backend Flask (mesmo arquivo, caminho diferente):

```bash
cp "ReFAIR/3. Source Code/ReFair/models/glove.6B.100d.txt" \
   "ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/models/glove.6B.100d.txt"
```

### 4.5. Corrigir o port mismatch (frontend ↔ backend)

**Opção escolhida:** rodar Flask em 5001 (não alterar Vue).

Editar `ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/app.py`, última linha:

```python
# antes
if __name__ == '__main__':
    app.run()

# depois
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
```

(`host='0.0.0.0'` é importante para Docker; localmente é redundante mas inofensivo.)

### 4.6. Reforçar o `requirements.txt` do `refair-server`

Substituir `ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/requirements.txt` por:

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
torch==2.0.0
gensim==4.3.1
openpyxl==3.1.2
```

---

## 5. Ajustes de código (opcionais mas recomendados)

### 5.1. Tornar `REFAIR.py` independente do `cwd`

No topo do `ReFAIR/3. Source Code/ReFair/REFAIR.py`, trocar caminhos relativos por caminhos resolvidos a partir do arquivo:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASETS = BASE_DIR / "datasets"
MODELS = BASE_DIR / "models"

dataset = pd.read_excel(DATASETS / "Synthetic User Stories.xlsx")
domain_task_mapping = pd.read_csv(DATASETS / "domains-tasks-mapping.csv")
domains_mapping = pd.read_csv(DATASETS / "domains-features-mapping.csv")
tasks_mapping = pd.read_csv(DATASETS / "tasks-features-mapping.csv")

with open(MODELS / "XGBClassifier.pkl", "rb") as f:
    domain_classifier = pickle.load(f)

glove_vectors = gensim.models.KeyedVectors.load_word2vec_format(
    str(MODELS / "glove.6B.100d.txt"), binary=False, no_header=True
)

with open(MODELS / "multilabel.pkl", "rb") as f:
    mlb = pickle.load(f)

with open(MODELS / "LinearSVC_LabelPowerset.pkl", "rb") as f:
    lsvc = pickle.load(f)
```

Aplicar o mesmo padrão no `refair-server/REFAIR.py`.

### 5.2. Evitar chamadas redundantes a `getDomain` / `getMLTask` no `main`

Substituir o bloco final do CLI por:

```python
if __name__ == '__main__':
    print('*** REFAIR started ***')

    if len(sys.argv) < 2:
        print('Usage: python REFAIR.py "<your user story>"')
        sys.exit(1)

    user_story = sys.argv[1]
    domain = getDomain(user_story)
    ml_tasks = getMLTask(user_story, domain)
    features = feature_extraction(domain, ml_tasks)

    print(f"Domain identified: {domain}")
    print(f"Machine Learning task(s) identified: {ml_tasks}")
    for task in ml_tasks:
        print(f"Domain: {domain} - Task: {task} - Sensitive Features: {features[task]}")

    print('*** REFAIR ended ***')
```

Reduz o tempo de uma chamada CLI de ~4x para 1x.

### 5.3. Remover `refair_app.py` duplicado

`refair-server/refair_app.py` é uma versão antiga do Flask app (rota `/refair`) que **não bate com o que o frontend chama** (`/analyzeStory`, `/storiesload`, `/reportStory`, `/reportStories`). Manter só `app.py` evita confusão de qual arquivo subir.

```bash
rm "ReFAIR/3. Source Code/ReFair/ReFair-App/refair-server/refair_app.py"
```

### 5.4. (Opcional) Cache do BERT para uso offline

```python
import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"   # depois do primeiro download
```

E pré-baixar manualmente:

```bash
python -c "from transformers import BertTokenizer; BertTokenizer.from_pretrained('bert-base-uncased')"
```

---

## 6. Execução — Rota A (Docker, recomendado)

### 6.1. Preparar o ambiente

Já feito nos passos §4.2, §4.3, §4.4 acima (`requirements.txt` em UTF-8, GloVe baixado, venv Windows removido).

### 6.2. Build do container

```bash
cd "ReFAIR/3. Source Code/ReFair"
docker compose build
```

Tempo esperado: 8–15 minutos na primeira vez (instala torch + transformers).

### 6.3. Subir o container interativo

```bash
docker compose up -d
docker exec -it refair_python bash
```

### 6.4. Rodar o CLI

Dentro do container:

```bash
python REFAIR.py "As a marketer, I want to use nearest neighbor search to identify customers with similar preferences or behaviors, so that I can provide personalized marketing messages and improve customer engagement."
```

**Saída esperada:**

```
*** REFAIR started ***
Domain identified: Finance & Marketing
Machine Learning task identified: ['anomaly detection', 'clustering', 'representation learning']
Domain: Finance & Marketing - Task: anomaly detection - Sensitive Features: [...]
Domain: Finance & Marketing - Task: clustering - Sensitive Features: [...]
Domain: Finance & Marketing - Task: representation learning - Sensitive Features: [...]
*** REFAIR ended ***
```

### 6.5. Rodar o App Web (Flask + Vue)

**Backend** (dentro do container, ou em terminal separado se rodar fora):

```bash
cd ReFair-App/refair-server
pip install -r requirements.txt
python app.py
# Flask agora escuta em http://0.0.0.0:5001
```

**Frontend** (fora do Docker, no host — precisa Node.js):

```bash
cd "ReFAIR/3. Source Code/ReFair/ReFair-App/refair-client"
npm install
npm run dev
# Vite serve em http://localhost:5173
```

Abrir `http://localhost:5173` no navegador. Upload de um `.xlsx` com uma coluna `User Story` → clicar **Load** → **Analyze** em uma linha → modal mostra domínio, tasks, features e gráfico de barras.

---

## 7. Execução — Rota B (venv local, sem Docker)

### 7.1. Criar venv com Python 3.9

```bash
cd "ReFAIR/3. Source Code/ReFair"
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 7.2. Instalar dependências

```bash
pip install -r requirements.txt
```

**Se** `fasttext-wheel` falhar no macOS Apple Silicon, removê-lo do requirements (ele não é usado pelo `REFAIR.py`; está só no notebook de RQ2).

### 7.3. Rodar o CLI

```bash
python REFAIR.py "your user story here"
```

### 7.4. Rodar o backend Flask

```bash
cd ReFair-App/refair-server
pip install -r requirements.txt   # mesmo venv, dependências extras
python app.py
```

### 7.5. Rodar o frontend Vue

(Em outro terminal, fora do venv Python.)

```bash
cd "ReFAIR/3. Source Code/ReFair/ReFair-App/refair-client"
npm install
npm run dev
```

---

## 8. Teste de fumaça (smoke test)

Para confirmar que tudo está conectado corretamente, rodar **na ordem**:

1. **CLI isolado** (sem rede após primeira execução):
   ```bash
   python REFAIR.py "As a doctor, I want to predict cancer recurrence from patient genomic data."
   ```
   Esperado: domínio `oncology`/`healthcare`, tasks incluindo `classification`, features incluindo `age`, `gender`, possivelmente `ethnicity`/`race`.

2. **Backend isolado** (curl direto):
   ```bash
   curl -X POST http://localhost:5001/analyzeStory \
     -F "story=As a hiring manager, I want to rank candidates based on their CVs."
   ```
   Esperado: JSON com `domain`, `tasks`, `tasks_features`, `features_counts`.

3. **Frontend ↔ Backend:** upload de um xlsx com 2–3 stories, clicar em **Analyze** em uma → modal abre com gráfico de barras.

4. **Report download:** clicar em **Report** após Load → baixa `report.json` com a análise de todas as stories.

---

## 9. Resumo das mudanças no código (checklist)

| Onde | O quê | Crítico? |
|---|---|---|
| `requirements.txt` (raiz do ReFair/) | Reescrever em UTF-8 sem BOM + adicionar `flask`/`flask-cors`/`werkzeug` | **Sim** |
| `refair-server/requirements.txt` | Expandir com versões fixadas | **Sim** |
| `models/glove.6B.100d.txt` | Baixar (~331 MB) e colocar em `models/` **e** em `refair-server/models/` | **Sim** |
| `refair-server/env/` | Remover (venv Windows abandonado) | **Sim** |
| `refair-server/app.py` | `app.run(host='0.0.0.0', port=5001)` | **Sim** |
| `.gitignore` (raiz do projeto) | Adicionar (criar se não existir) `.venv/`, `env/`, modelos grandes | Sim |
| `REFAIR.py` (CLI e server) | Usar `pathlib.Path(__file__).parent` para caminhos | Recomendado |
| `REFAIR.py` (CLI) | Evitar chamar `getDomain`/`getMLTask` 4× no `main` | Recomendado |
| `refair-server/refair_app.py` | Remover (arquivo duplicado/antigo) | Recomendado |

---

## 10. Limitações conhecidas (a observar durante uso)

Reproduzido do paper original (seção 6 do artigo) e relevante para entender resultados:

- **Formato de US:** ReFAIR foi treinado para US no template de Cohn ("As a X, I want Y, so that Z"). US fora desse padrão degradam performance.
- **Idioma:** modelo treinado em **inglês**. US em PT-BR vão produzir embeddings ruins (BERT-base-uncased é inglês; GloVe 6B é inglês).
- **Cobertura de domínios:** apenas 34 domínios da ontologia de Fabris. Domínios fora dessa lista serão **forçadamente** classificados no mais próximo (e a recomendação pode não fazer sentido).
- **Cobertura de tasks:** se a US **não menciona nenhum termo de ML**, o classificador multi-label tende a devolver uma lista vazia ou tasks genéricas — comportamento esperado, não bug.
- **Fairness contextual fora do mapping:** features sensíveis específicas de leis/regulações locais (LGPD, GDPR, normas setoriais) **não** aparecem no mapping de Fabris e portanto **nunca** serão recomendadas. Os próprios autores destacam isso como limitação na seção 6 do paper.

---

## 11. Próximos passos sugeridos (depois de ter o sistema rodando)

Em ordem de complexidade crescente:

1. **Smoke test** com 5–10 US do nosso domínio de interesse → ver se o classificador "se vira" ou cai sempre na mesma classe.
2. **Decidir a rota científica** discutida em [`analise-replicacao-novo-dataset.md`](./analise-replicacao-novo-dataset.md) — Rota A (validade externa), Rota C (extensão metodológica) ou combinação.
3. Se Rota C: replicar os notebooks de `3. Source Code/1. Domain Detection/` e `2. Tasks Detection/` com embeddings adicionais (RoBERTa, sentence-transformers).
4. Se Rota A: empacotar um script `batch_refair.py` que recebe um xlsx do dataset novo, roda o ReFAIR sobre todas as US e gera um CSV com `story, domain_predicted, tasks_predicted, features_recommended` para o painel de avaliação manual.

---

## 12. Referências

- **Paper original:** Ferrara, C., Casillo, F., Gravino, C., De Lucia, A., Palomba, F. (2024). *ReFAIR: Toward a Context-Aware Recommender for Fairness Requirements Engineering.* ICSE '24, Lisboa.
- **Replication package:** Zenodo DOI [10.5281/zenodo.10470916](https://doi.org/10.5281/zenodo.10470916).
- **Ontologia de domínios:** Fabris, A. et al. (2022). *Algorithmic fairness datasets: the story so far.* DMKD 36(6).
- **Dicionário de tasks ML:** Duran-Silva, N. et al. (2021). *A controlled vocabulary for research and innovation in the field of AI.*
- **GloVe vectors:** [https://nlp.stanford.edu/projects/glove/](https://nlp.stanford.edu/projects/glove/)
- **BERT base uncased:** [https://huggingface.co/bert-base-uncased](https://huggingface.co/bert-base-uncased)

# ReFAIR — Setup cross-platform

Instruções para rodar o ReFAIR em **macOS, Linux e Windows**. Três rotas: Docker (recomendado), venv local e App Web (Flask + Vue).

Para entender o que o sistema faz por dentro e a justificativa de cada ajuste, ver [`../../documents/plano-de-acao-refair.md`](../../../documents/plano-de-acao-refair.md).

---

## 0. Pré-requisitos comuns

- **Python 3.9** (não use 3.10+, várias libs travam).
- **Git**.
- **~5 GB livres** em disco.
- **Internet** na primeira execução (BERT ~250 MB + GloVe ~331 MB extraído).
- Para o App Web: **Node.js 18+** e npm.
- Para a rota Docker: **Docker Desktop** (macOS/Windows) ou **Docker Engine + Compose** (Linux).

> Todos os comandos abaixo assumem que você está em `ReFAIR/3. Source Code/ReFair/`.

---

## 1. Baixar o modelo GloVe (todas as rotas precisam)

O `glove.6B.100d.txt` (~331 MB) **não está no git**. Baixar antes de qualquer execução.

### macOS / Linux

```bash
./scripts/download_glove.sh
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\download_glove.ps1
```

O script copia o arquivo para os **dois** locais que o código usa:
- `models/glove.6B.100d.txt` (CLI)
- `ReFair-App/refair-server/models/glove.6B.100d.txt` (API)

---

## 2. Rota A — Docker (recomendado)

Ambiente reprodutível, igual em Mac/Win/Linux. Não precisa instalar Python no host.

```bash
docker compose build         # ~8–15 min na primeira vez
docker compose up -d         # sobe a API Flask em http://localhost:5001
```

### Usar a API

```bash
curl -X POST http://localhost:5001/analyzeStory \
  -F "story=As a marketer, I want to use nearest neighbor search to identify customers with similar preferences."
```

### Usar o CLI dentro do container

```bash
docker compose exec refair bash -c \
  "cd /app && python REFAIR.py 'As a doctor, I want to predict cancer recurrence from genomic data.'"
```

### Parar / remover

```bash
docker compose down          # para o container
docker compose down -v       # para e apaga o volume de cache do HuggingFace
```

---

## 3. Rota B — venv local

### macOS / Linux

```bash
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -3.9 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> Se você usar `cmd.exe` em vez de PowerShell, ative com `.\.venv\Scripts\activate.bat`.

### Rodar o CLI

```bash
python REFAIR.py "As a hiring manager, I want to rank candidates based on their CVs."
```

Saída esperada (exemplo):

```
*** REFAIR started ***
Domain identified: Hiring
Machine Learning task(s) identified: ['classification', 'ranking']
Domain: Hiring - Task: classification - Sensitive Features: [...]
Domain: Hiring - Task: ranking - Sensitive Features: [...]
*** REFAIR ended ***
```

> **macOS Apple Silicon:** se `fasttext-wheel` falhar no `pip install`, remova essa linha de `requirements.txt`. Ela só é usada nos notebooks de experimentação (RQ2), o `REFAIR.py` em produção não precisa dela.

---

## 4. App Web (Flask + Vue)

### Backend (Flask)

Reaproveita o venv da §3 (ou rode dentro do Docker, que já sobe a API automaticamente).

```bash
cd ReFair-App/refair-server
pip install -r requirements.txt    # se não usou o requirements raiz
python app.py
# API escutando em http://localhost:5001
```

### Frontend (Vue 3 + Vite)

Em outro terminal:

```bash
cd ReFair-App/refair-client
npm install
npm run dev
# Frontend em http://localhost:5173
```

Abrir `http://localhost:5173` no navegador. Subir um `.xlsx` com uma única coluna `User Story` → **Load** → **Analyze**.

---

## 5. Smoke test

Após instalar, valide a pipeline ponta a ponta:

| # | Teste | Esperado |
|---|---|---|
| 1 | `python REFAIR.py "As a doctor, I want to predict cancer recurrence from genomic data."` | Domínio `oncology`/`healthcare`, tasks com `classification`, features com `age`, `gender`, `ethnicity`. |
| 2 | `curl -X POST http://localhost:5001/analyzeStory -F "story=..."` | JSON com `domain`, `tasks`, `tasks_features`, `features_counts`. |
| 3 | Upload xlsx no frontend → **Analyze** | Modal abre com domínio, tasks, features e gráfico de barras. |

---

## 6. Troubleshooting

| Sintoma | Causa | Correção |
|---|---|---|
| `pip` reclama de encoding ao instalar | `requirements.txt` foi reaberto/salvo como UTF-16 (Windows Notepad) | Salvar como UTF-8 sem BOM (VS Code: "Save with Encoding → UTF-8"). |
| `FileNotFoundError: models/glove.6B.100d.txt` | GloVe não baixado | Rodar `scripts/download_glove.sh` (ou `.ps1`). |
| `Connection refused` no frontend | API não está em 5001 | Confirmar `app.py` termina com `app.run(host='0.0.0.0', port=5001)`. |
| `InconsistentVersionWarning` ao carregar `.pkl` | scikit-learn/xgboost diferente do que treinou os modelos | Usar exatamente `scikit-learn==1.2.2` e `xgboost==1.7.4` (já fixado nos requirements). |
| `OSError: We couldn't connect to ...huggingface.co` | Sem internet no primeiro run | Conectar à internet uma vez para o BERT cachear, ou pré-baixar com `python -c "from transformers import BertTokenizer; BertTokenizer.from_pretrained('bert-base-uncased')"`. |
| Linhas com `\r` causando erro em scripts `.sh` | Git checkout em Windows convertendo para CRLF | O `.gitattributes` na raiz força LF em `.sh`/`.py`. Rodar `git add --renormalize .` se já tiver checkout. |
| `port is already allocated` | Porta 5001 ocupada | `docker compose down` ou trocar o mapeamento em `docker-compose.yml`. |

---

## 7. Estrutura dos arquivos editados nesta rodada de fixes

```
.gitignore                       ← novo, na raiz do projeto
.gitattributes                   ← novo, força LF cross-platform
ReFAIR/3. Source Code/ReFair/
├── requirements.txt             ← reescrito em UTF-8 + flask/cors/werkzeug
├── Dockerfile                   ← multistage-ready, instala ambos requirements, pre-baixa BERT
├── docker-compose.yml           ← porta 5001, volume hf-cache, service único
├── REFAIR.py                    ← paths via pathlib, main deduplicado
├── SETUP.md                     ← este arquivo
├── scripts/
│   ├── download_glove.sh        ← novo, macOS/Linux
│   └── download_glove.ps1       ← novo, Windows
└── ReFair-App/refair-server/
    ├── app.py                   ← Flask agora em 0.0.0.0:5001
    ├── REFAIR.py                ← paths via pathlib
    └── requirements.txt         ← expandido com versões fixadas
```

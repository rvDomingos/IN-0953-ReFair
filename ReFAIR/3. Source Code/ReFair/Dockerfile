FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TRANSFORMERS_OFFLINE=0 \
    HF_HOME=/root/.cache/huggingface

WORKDIR /app

# Build tools needed for some wheels (xgboost, scipy, fasttext-wheel, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        g++ \
        curl \
        unzip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first to leverage Docker layer cache
COPY requirements.txt ./requirements.txt
COPY ReFair-App/refair-server/requirements.txt ./refair-server-requirements.txt

RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip install -r refair-server-requirements.txt

# Pre-download the BERT tokenizer AND model used by REFAIR.py (extensao: getDomain
# usa embeddings via BertModel) so containers run offline-ready
RUN python -c "from transformers import BertTokenizer, BertModel; BertTokenizer.from_pretrained('bert-base-uncased'); BertModel.from_pretrained('bert-base-uncased')"

# Copy source last (changes here don't bust the deps layer)
COPY . .

# Flask API (single-service deployment uses this)
EXPOSE 5001
# Optional: Jupyter for the analysis notebooks
EXPOSE 8888

# Default command: start the Flask API. Override with `docker compose run` to use the CLI.
WORKDIR /app/ReFair-App/refair-server
CMD ["python", "app.py"]

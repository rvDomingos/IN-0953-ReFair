FROM python:3.9-slim

WORKDIR /app

# Instala compiladores essenciais do Linux
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia os requisitos
COPY requirements.txt .

# O PULO DO GATO: Lê o requirements.txt e substitui a linha do fasttext 
# pela versão pré-compilada antes do pip tentar instalar
RUN sed -i 's/fasttext==0.9.2/fasttext-wheel/g' requirements.txt

# Atualiza o pip e instala as dependências
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe as portas do Jupyter e do servidor Flask
EXPOSE 8888 5000

CMD ["/bin/bash"]
import pickle
import re
import unicodedata
from pathlib import Path

import gensim
import pandas as pd
from transformers import BertTokenizer

from domain_embed import embed   # extensao RQ2: vetorizacao semantica do dominio

BASE_DIR = Path(__file__).resolve().parent
DATASETS = BASE_DIR / "datasets"
MODELS = BASE_DIR / "models"

dataset = pd.read_excel(DATASETS / "Synthetic User Stories.xlsx")
domain_task_mapping = pd.read_csv(DATASETS / "domains-tasks-mapping.csv")
domains_mapping = pd.read_csv(DATASETS / "domains-features-mapping.csv")
tasks_mapping = pd.read_csv(DATASETS / "tasks-features-mapping.csv")

domain_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
with open(MODELS / "XGBClassifier.pkl", "rb") as f:
    domain_classifier = pickle.load(f)          # original (input_ids) — mantido p/ fallback

# extensao RQ2: classificador de dominio sobre EMBEDDINGS do BERT (treinado por
# treinar_dominio_embeddings.py). Substitui o getDomain original no pipeline.
with open(MODELS / "domain_embed_logreg.pkl", "rb") as f:
    domain_embed_classifier = pickle.load(f)

# extensao estagio 2 (CONFIG D): ML task = GloVe-media + OneVsRest + limiar + filtro
# soft (treinar_mltask_glove.py). A ablacao (ameaca #6) mostrou que GloVe generaliza
# melhor que embeddings no ML task (F1 0,283 vs 0,243) — embeddings ficam so no dominio.
with open(MODELS / "mltask_glove_ovr.pkl", "rb") as f:
    _mlt = pickle.load(f)
    mltask_classifier = _mlt["clf"]
    mltask_mlb = _mlt["mlb"]
    mltask_threshold = _mlt["threshold"]

glove_vectors = gensim.models.KeyedVectors.load_word2vec_format(
    str(MODELS / "glove.6B.100d.txt"), binary=False, no_header=True
)

with open(MODELS / "multilabel.pkl", "rb") as f:
    mlb = pickle.load(f)

with open(MODELS / "LinearSVC_LabelPowerset.pkl", "rb") as f:
    lsvc = pickle.load(f)


def getDomain(user_story):
    # EXTENSAO RQ2: decide pelo SIGNIFICADO (embedding do BERT), nao pela posicao
    # do token. Recupera de ~9,4% para ~37% de acerto de dominio no UStAI.
    emb = embed([user_story])
    return domain_embed_classifier.predict(emb)[0]


def getDomain_xgb(user_story):
    # ORIGINAL do ReFAIR (input_ids por posicao) — preservado p/ comparacao/fallback.
    tokenized_data = domain_tokenizer([user_story], padding='max_length', max_length=100, truncation=True)
    traindata = []
    for msg in tokenized_data['input_ids']:
        traindata.append(msg)
    traindata = pd.DataFrame(traindata)
    traindata.columns = traindata.columns.astype(str)
    predict = domain_classifier.predict(traindata)
    return dataset["Domain"].unique()[predict[0]]


def _norm_token(word):
    # normaliza só p/ casar no GloVe (6B é minúsculo, sem acento/pontuacao):
    # lower + remove acento + tira pontuacao das bordas. Nao altera o texto
    # original (que tambem alimenta o getDomain/BERT) — so o lookup do GloVe.
    word = unicodedata.normalize('NFKD', word.lower())
    word = ''.join(c for c in word if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9']", '', word)


def _allowed_tasks(domain):
    # tarefas plausiveis p/ o dominio, segundo o mapping (Fabris/literatura)
    return set(
        domain_task_mapping['Task'][i].lower()
        for i in domain_task_mapping.index
        if domain_task_mapping['Domain'][i].lower() == str(domain).lower()
    )


def _glove_avg(user_story):
    words = user_story.replace('-', ' ').replace('/', ' ').split()
    vecs = []
    for word in words:
        token = _norm_token(word)
        if token and token in glove_vectors:
            vecs.append(glove_vectors[token])
    return sum(vecs) / len(vecs) if vecs else [0] * 100


def getMLTask(user_story, domain):
    # EXTENSAO estagio 2 (CONFIG D): GloVe-media -> OneVsRest(LogReg) com LIMIAR
    # ajustavel; filtro dominio->tarefa SOFT — se a intersecao zerar, mantem a
    # previsao crua (evita os ~46% de saidas vazias do filtro DURO original).
    # F1 no UStAI: 0,13 -> 0,283. GloVe generaliza melhor que embeddings aqui (ablacao #6).
    feat = pd.DataFrame([_glove_avg(user_story)])
    feat.columns = feat.columns.astype(str)
    proba = mltask_classifier.predict_proba(feat.values)[0]
    raw = [mltask_mlb.classes_[j] for j in range(len(proba)) if proba[j] >= mltask_threshold]
    allowed = _allowed_tasks(domain)
    filtered = [t for t in raw if t.lower() in allowed]
    return filtered if filtered else raw


def getMLTask_glove(user_story, domain):
    # ORIGINAL (GloVe-media + LinearSVC LabelPowerset + filtro DURO) — preservado.
    traindata = []
    for msg in [user_story]:
        words = msg.replace('-', ' ').replace('/', ' ').split()
        vecs = []
        for word in words:
            token = _norm_token(word)
            if token and token in glove_vectors:
                vecs.append(glove_vectors[token])
        if vecs:
            vec_avg = sum(vecs) / len(vecs)
        else:
            vec_avg = [0] * 100
        traindata.append(vec_avg)
    traindata = pd.DataFrame(traindata)
    traindata.columns = traindata.columns.astype(str)
    output = []
    for prediction in mlb.inverse_transform(lsvc.predict(traindata.values))[0]:
        for index in domain_task_mapping.index:
            if (domain_task_mapping['Domain'][index].lower() == domain.lower()
                    and domain_task_mapping['Task'][index].lower() == prediction.lower()):
                output.append(prediction)
    return output


def intersection(lst1, lst2):
    return [value for value in lst1 if value in lst2]


def feature_extraction(domain, mltasks):
    out_features = {}

    domain_features = []
    for index in domains_mapping.index:
        feat = domains_mapping['Feature'][index]
        if domains_mapping['Domain'][index].lower() == domain.lower() and isinstance(feat, str):
            domain_features.append(feat)

    for task in mltasks:
        tmp = []
        for index in tasks_mapping.index:
            feat = tasks_mapping['Feature'][index]
            if tasks_mapping['Task'][index].lower() == task.lower() and isinstance(feat, str):
                tmp.append(feat)
        out_features[task] = intersection(tmp, domain_features)

    return out_features


def refair(user_story):
    print('*** REFAIR started ***')

    domain = getDomain(user_story)
    ml_tasks = getMLTask(user_story, domain)
    features = feature_extraction(domain, ml_tasks)

    print(f"Domain identified: {domain}")
    print(f"Machine Learning task(s) identified: {ml_tasks}")
    for task in ml_tasks:
        print(f"Domain: {domain} - Task: {task} - Sensitive Features: {features[task]}")

    print('*** REFAIR ended ***')

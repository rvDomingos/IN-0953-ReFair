import pickle
import re
import unicodedata
from pathlib import Path

import gensim
import pandas as pd
from transformers import BertTokenizer

BASE_DIR = Path(__file__).resolve().parent
DATASETS = BASE_DIR / "datasets"
MODELS = BASE_DIR / "models"

dataset = pd.read_excel(DATASETS / "Synthetic User Stories.xlsx")
domain_task_mapping = pd.read_csv(DATASETS / "domains-tasks-mapping.csv")
domains_mapping = pd.read_csv(DATASETS / "domains-features-mapping.csv")
tasks_mapping = pd.read_csv(DATASETS / "tasks-features-mapping.csv")

domain_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
with open(MODELS / "XGBClassifier.pkl", "rb") as f:
    domain_classifier = pickle.load(f)

glove_vectors = gensim.models.KeyedVectors.load_word2vec_format(
    str(MODELS / "glove.6B.100d.txt"), binary=False, no_header=True
)

with open(MODELS / "multilabel.pkl", "rb") as f:
    mlb = pickle.load(f)

with open(MODELS / "LinearSVC_LabelPowerset.pkl", "rb") as f:
    lsvc = pickle.load(f)


def getDomain(user_story):
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


def getMLTask(user_story, domain):
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
        if domains_mapping['Domain'][index].lower() == domain.lower():
            domain_features.append(domains_mapping['Feature'][index])

    for task in mltasks:
        tmp = []
        for index in tasks_mapping.index:
            if tasks_mapping['Task'][index].lower() == task.lower():
                tmp.append(tasks_mapping['Feature'][index])
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

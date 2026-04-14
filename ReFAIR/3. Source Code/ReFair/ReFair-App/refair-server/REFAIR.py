import pandas as pd
import sys
import numpy as np
import xgboost as xgb
from transformers import BertTokenizer
import pickle
import gensim

dataset = pd.read_excel("./datasets/Synthetic User Stories.xlsx")
domain_task_mapping = pd.read_csv("./datasets/domains-tasks-mapping.csv")
domains_mapping = pd.read_csv("./datasets/domains-features-mapping.csv")
tasks_mapping = pd.read_csv("./datasets/tasks-features-mapping.csv")

# Loading domain tokenizer and classifier
domain_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
with open('./models/XGBClassifier.pkl', 'rb') as f:
    domain_classifier= pickle.load(f)


# Loading MLTask tokenizer, model and multilabeler.
glove_vectors = gensim.models.KeyedVectors.load_word2vec_format('./models/glove.6B.100d.txt',binary=False, no_header=True)

with open('./models/multilabel.pkl', 'rb') as f:
    mlb= pickle.load(f)

with open('./models/LinearSVC_LabelPowerset.pkl', 'rb') as f:
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

def getMLTask(user_story, domain):
    traindata = []
    for msg in [user_story]:
        words = msg.split()
        vecs = []
        for word in words:
            if word in glove_vectors:
                vecs.append(glove_vectors[word])
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
            
            if domain_task_mapping['Domain'][index].lower() == domain.lower()  and  domain_task_mapping['Task'][index].lower()  == prediction.lower():
                
                output.append(prediction)
                
    return output



def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3



def feature_extraction(domain, mltasks):
    
    out_features = {}

    #Domain detection
    domain_features = []
    for index in domains_mapping.index:
        if domains_mapping['Domain'][index].lower() == domain.lower():
            domain_features.append(domains_mapping['Feature'][index])

    #Tasks detection
    for task in mltasks:
        tmp = []
        for index in tasks_mapping.index:
            if tasks_mapping['Task'][index].lower() == task.lower():
                tmp.append(tasks_mapping['Feature'][index])
        out_features[task] = intersection(tmp, domain_features)

    return out_features


def refair(user_story):
    print('*** REFAIR started ***')

    print("Domain identified: " + getDomain(user_story))
    print("Machine Learning task identified: " + str(getMLTask(user_story, getDomain(user_story))))

    output = feature_extraction(getDomain(user_story), getMLTask(user_story, getDomain(user_story)))
    for task in getMLTask(user_story, getDomain(user_story)):
        print("Domain: {} - Task: {} - Sensitive Features: {}".format(getDomain(user_story), task, output[task]))

    print('*** REFAIR ended ***')
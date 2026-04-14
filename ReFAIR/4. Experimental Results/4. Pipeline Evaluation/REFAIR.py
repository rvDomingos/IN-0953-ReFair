import pandas as pd
import sys
import numpy as np
import xgboost as xgb
from transformers import BertTokenizer
import pickle
import gensim
import csv

dataset = pd.read_excel("datasets/Synthetic User Stories.xlsx")
domain_task_mapping = pd.read_csv("datasets/domains-tasks-mapping.csv")
domains_mapping = pd.read_csv("datasets/domains-features-mapping.csv")
tasks_mapping = pd.read_csv("datasets/tasks-features-mapping.csv")

oracle = pd.read_csv("datasets/oracle.csv", sep=";")

# Loading domain tokenizer and classifier
domain_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
with open('models/XGBClassifier.pkl', 'rb') as f:
    domain_classifier= pickle.load(f)


# Loading MLTask tokenizer, model and multilabeler.
glove_vectors = gensim.models.KeyedVectors.load_word2vec_format('models/glove.6B.100d.txt',binary=False, no_header=True)

with open('models/multilabel.pkl', 'rb') as f:
    mlb= pickle.load(f)

with open('models/LinearSVC_LabelPowerset.pkl', 'rb') as f:
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

def getMLTask(user_story,domain):
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
            if isinstance(domain_task_mapping['Task'][index], str):
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




if __name__ == '__main__':
    
    #   ideal_predictions =[]

    #   tasks = ["classification", "regression", "ranking", "matching", "risk assessment", "representation learning", "clustering", "anomaly detection", "districting", "task assignment", "spatio-temporal process learning", "graph diffusion", "graph augmentation", "resource allocation", "subset selection", "data summarization", "graph mining", "pricing", "advertising", "entity resolution", "sentiment analysis", "bias detection in word embeddings", "bias detection in language models", "machine translation", "speech recognition", "other"]

    #   for index, row in oracle.iterrows():
         
    #       print("{}-{}".format(index, row['User Story']))
    #       out_tasks = []
    #       for task in tasks:
        
    #          if row[task] == 1:
                
    #                for index in domain_task_mapping.index:
                    
    #                   if isinstance(domain_task_mapping['Task'][index], str):
    #                        if domain_task_mapping['Domain'][index].lower() == row['Oracle Domain'].lower()  and  domain_task_mapping['Task'][index].lower()  == task.lower():
    #                           out_tasks.append(task)
                    
    #       ideal_predictions.append([row['User Story'], row['Oracle Domain'], out_tasks])
         
     
    #   with open("predictions/oracle-predictions.csv", "w", newline="") as f:
          
    #        writer = csv.writer(f)
    #        writer.writerows(ideal_predictions)


    # #output = feature_extraction(getDomain(user_story), getMLTask(user_story, getDomain(user_story)))
    #   print('*** REFAIR started ***')
    #   refair_predictions =[]
    #   i = 0
    #   for user_story in dataset['User Story']:
    #       print("{}-{}".format(i, user_story))
    #       refair_predictions.append([user_story, getDomain(user_story), getMLTask(user_story, getDomain(user_story))])
    #       i = i + 1

   
    #   with open("predictions/refair-predictions.csv", "w", newline="") as f:
    #      writer = csv.writer(f, delimiter = ";")
    #      writer.writerows(refair_predictions)
    #   print('*** REFAIR ended ***')
     
    oracle_predictions = pd.read_excel("predictions/oracle-predictions.xlsx")
    refair_predictions = pd.read_excel("predictions/refair-predictions.xlsx")
    
    correct_domains = 0
    wrong_domains = 0
    
    refair_void_predictions=0
    correctly_refair_void_predictions=0
    oracle_void_predictions=0

    matching_tasks_predictions = 0

    correct_tasks = 0
    wrong_tasks = 0
    missing_tasks = 0
    partialy_correct_stories = 0
    completely_wrong_stories = 0
    partial_check = False
    
    for index in oracle_predictions['Story'].index:
        if oracle_predictions['Domain'][index] == refair_predictions['Domain'][index]:
            correct_domains = correct_domains + 1
            refair_tasks = str(refair_predictions['Tasks'][index]).split(',')
            oracle_tasks = str(oracle_predictions['Tasks'][index]).split(',')
        
            if str(refair_predictions['Tasks'][index]).split(',') == ['nan']:
                refair_void_predictions = refair_void_predictions + 1
                if str(oracle_predictions['Tasks'][index]).split(',') == ['nan']:
                    correctly_refair_void_predictions=correctly_refair_void_predictions + 1
            else:
                if refair_tasks == oracle_tasks :
                    matching_tasks_predictions = matching_tasks_predictions + 1
                    correct_tasks  = correct_tasks + len(refair_tasks)
                else:
                    for task in refair_tasks:
                        if task in oracle_tasks:   
                            correct_tasks = correct_tasks + 1
                            partial_check = True
                        
                        else:
                            wrong_tasks = wrong_tasks + 1
                    if partial_check: partialy_correct_stories = partialy_correct_stories + 1
                    else: completely_wrong_stories = completely_wrong_stories + 1
                    for task in oracle_tasks:
                        if task not in refair_tasks:   
                            missing_tasks = missing_tasks + 1
                
                partial_check = False

        else:
            wrong_domains = wrong_domains + 1
            
       


        if str(oracle_predictions['Tasks'][index]).split(',') == ['nan']:
            oracle_void_predictions = oracle_void_predictions + 1


    print("Wrong domains : {}".format(wrong_domains))
    
    print("\n")
    print("Correct domains : {}".format(correct_domains))
   
    print("Following Statistics are true only in case of correct domain prediction")
    print("ReFair tasks void predictions : {}".format(refair_void_predictions))
    print("Correctly ReFair tasks void predictions : {}".format(correctly_refair_void_predictions))
    
    print("Wrongly ReFair tasks void predictions : {}".format(refair_void_predictions  - correctly_refair_void_predictions))

    print("Perfect matching among ReFair and Oracle on tasks predicted when prediction is not void: {}".format(matching_tasks_predictions))

    print("ReFair provide partially correct tasks predictions for : {} stories".format(partialy_correct_stories))
    print("ReFair provide completely wrong tasks predictions for : {} stories".format(completely_wrong_stories))

    print("\n")
    print("Tasks correctly predicted by ReFair when prediction is not void: {}".format(correct_tasks))
    print("Tasks wrongly predicted by ReFair when prediction is not void: {}".format(wrong_tasks))
    
    

    print("\n")
    print("Oracle tasks void predictions : {}".format(oracle_void_predictions))
    print("Oracle tasks not predicted by ReFair: {}".format(missing_tasks))

    
    # print('*** REFAIR ended ***')
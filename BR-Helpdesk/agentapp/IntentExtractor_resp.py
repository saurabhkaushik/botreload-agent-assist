from gensim.models.word2vec import Word2Vec 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.pipeline import Pipeline
import re 
import numpy as np
from pandas_ml import ConfusionMatrix 
from sklearn.metrics import  f1_score, precision_score, recall_score
import csv
from collections import defaultdict
from agentapp.model_select import get_model, getTrainingModel, getResponseModel
from agentapp.tickets_learner import tickets_learner
from flask import current_app
import logging
#from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
import nltk
nltk.download('stopwords')
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from agentapp.tickets_learner import tickets_learner
import pickle
from agentapp.TfidfVectorizer import TfidfEmbeddingVectorizer, MeanEmbeddingVectorizer

class IntentExtractor_resp(object): 
    

    def prepareTrainingData(self, cust_id):
        logging.info("\n"+"################# Preparing Training Data - Response #########################"+"\n")
        self.X, self.y = [], []
        
        tickets_learn = tickets_learner()
        ticket_data = tickets_learn.getResponseData(cust_id=cust_id)
    
        xX = []
        yY = []
        for linestms in ticket_data:           
            for linestm in linestms:
                xX.append(preprocess(str(linestm['tags'])).strip().split())
                yY.append(linestm['res_category'].strip())
        self.X = xX
        self.y = yY
        
        self.X, self.y = np.array(self.X, dtype=object), np.array(self.y, dtype=object)
        logging.info ("Total Training Examples : %s" % len(self.y))

            
    def startTrainingProcess(self, cust_id):
        logging.info("\n"+"################# Starting Training Processing ################################"+"\n")
        self.model = Word2Vec(self.X, size=100, window=5, min_count=1, workers=2)
        self.model.wv.index2word
        w2v = {w: vec for w, vec in zip(self.model.wv.index2word, self.model.wv.syn0)}
        self.etree_w2v_tfidf = Pipeline([("word2vec vectorizer", MeanEmbeddingVectorizer(w2v)), 
                        ("extra trees", ExtraTreesClassifier(n_estimators=200))])
        self.etree_w2v_tfidf.fit(self.X, self.y)
        
        logging.info ("Total Training Samples : %s" % len(self.y))
        
    def getPredictedIntent(self, textinput, cust_id): 
        logging.info("\n"+"################# Starting Prediction Process ################################"+"\n")
        self.test_X = []
        self.test_X.append(preprocess(textinput).split())
        self.predicted = []
        try:
            self.predicted = self.etree_w2v_tfidf.predict(self.test_X) 
        except ValueError as err: 
            logging.error(str(err))
        return self.predicted

def preprocess(sentence):
    sentence = sentence.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(sentence)
    filtered_words = [w for w in tokens if not w in stopwords.words('english')]
    return " ".join(filtered_words)
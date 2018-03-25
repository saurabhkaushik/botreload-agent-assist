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

import logging

logger = logging.getLogger('br-srv-app')

TRAIN_SET_PATH = 'input/hd_training_data.csv'
TEST_SET_PATH = 'input/hd_training_data.csv'
txt_modelfile = 'input/hd_trained.model.bin'

class TfidfEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.word2weight = None
        self.dim = len(word2vec.items())
        
    def fit(self, X, y):
        tfidf = TfidfVectorizer(analyzer=lambda x: x)
        tfidf.fit(X)
        max_idf = max(tfidf.idf_)
        self.word2weight = defaultdict(
            lambda: max_idf, 
            [(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])
    
        return self
    
    def transform(self, X):
        return np.array([
                np.mean([self.word2vec[w] * self.word2weight[w]
                         for w in words if w in self.word2vec] or
                        [np.zeros(self.dim)], axis=0)
                for words in X
            ])

class IntentExtractor(object): 
    
    def prepareTrainingData(self):
        logger.info("\n"+"################# Preparing Training Data ################################"+"\n")
        self.X, self.y = [], []
        # Read CSV for Input and Output Columns 
        with open(TRAIN_SET_PATH, 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
            
        for linestm in train_list:
            linestm[1] = re.sub('["]', '', linestm[1])    
            logger.info (linestm[0] + ', ' + linestm[1] + "  =>  " + linestm[2])
        
        self.X = [(item[0] + ', ' + item[1]).split() for item in train_list]
        self.y = [item[2] for item in train_list]
        
        self.X, self.y = np.array(self.X, dtype=object), np.array(self.y, dtype=object)
        logger.info ("Total Training Examples : %s" % len(self.y))
        
    def prepareTestingData(self):
        logger.info("\n"+"################# Preparing Testing Data ################################"+"\n")
        self.test_X, self.test_y = [], []
        # Read CSV for Input and Output Columns 
        with open(TEST_SET_PATH, 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            self.train_list = list(reader)
            
        for linestm in self.train_list:
            linestm[1] = re.sub('["]', '', linestm[1])    
            logger.info (linestm[0], "  =>  " + linestm[1])
        
        self.test_X = [item[0].split() for item in self.train_list]
        self.test_y = [item[1] for item in self.train_list]
        
        self.X, self.y = np.array(self.X), np.array(self.y)
        logger.info ("Total Testing Examples : %s" % len(self.y))
    
    def startTrainingProcess(self):
        logger.info("\n"+"################# Starting Training Processing ################################"+"\n")
        self.model = Word2Vec(self.X, size=100, window=5, min_count=1, workers=2)
        self.model.wv.index2word
        w2v = {w: vec for w, vec in zip(self.model.wv.index2word, self.model.wv.syn0)}
        self.etree_w2v_tfidf = Pipeline([("word2vec vectorizer", TfidfEmbeddingVectorizer(w2v)), 
                        ("extra trees", ExtraTreesClassifier(n_estimators=200))])
        self.etree_w2v_tfidf.fit(self.X, self.y)
        logger.info ("Total Training Samples : %s" % len(self.y))

    def startTestingProcess(self): 
        logger.info("\n"+"################# Starting Testing Process ################################"+"\n")
        self.predicted = self.etree_w2v_tfidf.predict(self.test_X)
        for input_data, output_data in zip(self.train_list, self.predicted) :
            logger.info (input_data[0] + "  =>  " + output_data)
            
    def getIntentForText(self, textinput): 
        logger.info("\n"+"################# Starting Testing Process ################################"+"\n")
        self.test_X = []
        self.test_X.append(textinput.split())
        logger.info(self.test_X)
        self.predicted = self.etree_w2v_tfidf.predict(self.test_X) 
        self.predicted_prob = self.etree_w2v_tfidf.predict_proba(self.test_X)  
        self.y_predict_dic = dict(zip(self.etree_w2v_tfidf.classes_, self.predicted_prob[0]))
        logger.info('Predicted Sorted Dictionary : ' + str(self.y_predict_dic))
        return self.y_predict_dic
    
    def createConfusionMatrix(self):
        logger.info("\n"+"################# Evaluating Model Performance ################################"+"\n")
        logger.info("Mean: \n" + np.mean(self.test_y == self.predicted))
        
        cm = ConfusionMatrix(self.test_y, self.predicted)
        logger.info("Confusion Matrix: \n" , cm)
        cm.plot()
        
        logger.info("f1_score : " + f1_score(self.test_y, self.predicted, average="macro"))
        logger.info("precision_score : " + precision_score(self.test_y, self.predicted, average="macro"))
        logger.info("recall_score : " + recall_score(self.test_y, self.predicted, average="macro")) 
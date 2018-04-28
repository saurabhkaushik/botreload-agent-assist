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
        logging.info("\n"+"################# Preparing Training Data ################################"+"\n")
        self.X, self.y = [], []
        # Read CSV for Input and Output Columns 
        with open(current_app.config['TRAIN_SET_PATH'], 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
            
        for linestm in train_list:
            linestm[1] = re.sub('["]', '', linestm[1])    
            logging.debug (linestm[0] + ', ' + linestm[1] + "  =>  " + linestm[2])
        
        self.X = [(preprocess(item[0]).strip() + ' ' + preprocess(item[1]).strip()).split() for item in train_list]
        self.y = [item[2].strip() for item in train_list]
        
        self.X, self.y = np.array(self.X, dtype=object), np.array(self.y, dtype=object)
        logging.info ("Total Training Examples : %s" % len(self.y))
        
    def prepareTrainingData_ds(self):
        logging.info("\n"+"################# Preparing Training Data ################################"+"\n")
        self.X, self.y = [], []
        
        tickets_learn = tickets_learner()
        ticket_data = tickets_learn.getTrainingData()
    
        xX = []
        yY = []
        for linestms in ticket_data:           
            for linestm in linestms:
                logging.debug (linestm['tags'] + " =>  " + linestm['response'])
                xX.append(preprocess(linestm['tags']).strip().split())
                yY.append(linestm['response'].strip())
        self.X = xX
        self.y = yY
        
        self.X, self.y = np.array(self.X, dtype=object), np.array(self.y, dtype=object)
        logging.info ("Total Training Examples : %s" % len(self.y))
            
    def startTrainingProcess(self):
        logging.info("\n"+"################# Starting Training Processing ################################"+"\n")
        self.model = Word2Vec(self.X, size=100, window=5, min_count=1, workers=2)
        self.model.wv.index2word
        w2v = {w: vec for w, vec in zip(self.model.wv.index2word, self.model.wv.syn0)}
        self.etree_w2v_tfidf = Pipeline([("word2vec vectorizer", TfidfEmbeddingVectorizer(w2v)), 
                        ("extra trees", ExtraTreesClassifier(n_estimators=200))])
        '''self.etree_w2v_tfidf = Pipeline([("word2vec vectorizer", TfidfEmbeddingVectorizer(w2v)), 
                        ("MultinomialNB", MultinomialNB())])
        self.etree_w2v_tfidf = Pipeline([("word2vec vectorizer", TfidfEmbeddingVectorizer(w2v)), 
                        ("SVC", SVC(kernel='linear', probability=True))])'''
        self.etree_w2v_tfidf.fit(self.X, self.y)
        logging.info ("Total Training Samples : %s" % len(self.y))
        
    def getIntentForText(self, textinput): 
        logging.info("\n"+"################# Starting Prediction Process ################################"+"\n")
        self.test_X = []
        self.test_X.append(preprocess(textinput).split())
        self.predicted = self.etree_w2v_tfidf.predict(self.test_X) 
        self.predicted_prob = self.etree_w2v_tfidf.predict_proba(self.test_X)  
        self.y_predict_dic = dict(zip(self.etree_w2v_tfidf.classes_, self.predicted_prob[0]))
        return self.y_predict_dic

    def prepareTestingData(self):
        logging.info("\n"+"################# Preparing Testing Data ################################"+"\n")
        self.test_X, self.test_y = [], []
        with open(current_app.config['TEST_SET_PATH'], 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
            
        for linestm in train_list:
            #linestm[1] = re.sub('["]', '', linestm[1])    
            logging.debug (linestm[0] + ', ' + linestm[1] + "  =>  " + linestm[2])
        
        self.test_X = [(preprocess(item[0]).strip() + ' ' + preprocess(item[1]).strip()).split() for item in train_list]
        self.test_y = [item[2].strip() for item in train_list]
        self.test_X, self.test_y = np.array(self.test_X, dtype=object), np.array(self.test_y, dtype=object)
        for testx, testy in zip (self.test_X, self.test_y):
            logging.debug (str(testx) + ' >> ' + str(testy))
        logging.info ("Total Testing Examples : %s" % len(self.test_y)) 
        
    def prepareTestingData_ds(self):
        logging.info("\n"+"################# Preparing Testing Data ################################"+"\n")
        self.test_X, self.test_y = [], []
        
        tickets_learn = tickets_learner()
        ticket_data = tickets_learn.getTrainingData()
    
        xX = []
        yY = []
        for linestms in ticket_data:           
            for linestm in linestms:
                logging.debug (linestm['tags'] + " =>  " + linestm['response'])
                xX.append(preprocess(linestm['tags']).strip().split())
                yY.append(linestm['response'].strip()) 
        self.test_X = xX
        self.test_y = yY
       
        self.test_X, self.test_y = np.array(self.test_X, dtype=object), np.array(self.test_y, dtype=object)
        logging.info (dict(zip(self.test_X), (self.test_y)))
        logging.info ("Total Testing Examples : %s" % len(self.test_y))

    def startTestingProcess(self): 
        logging.info("\n"+"################# Starting Testing Process ################################"+"\n")
        '''for intm in self.test_X:
            if (intm.isna()):'''
        self.predicted = self.etree_w2v_tfidf.predict(self.test_X)
        for input_data, output_data in zip(self.test_X, self.predicted) :
            logging.debug (str(input_data) + "  =>  " + str(output_data))
        logging.info ("Total Predicted Testing Examples : %s" % len(self.predicted))
        
    def createConfusionMatrix(self):
        logging.info("\n"+"################# Evaluating Model Performance ################################"+"\n")
        for y_value_a, y_value_p in zip(self.test_y, self.predicted): 
            logging.info ('\'' + y_value_a + '\' >> \'' + y_value_p + '\'' )
        logging.info("Mean: \n" + str(np.mean(self.test_y == self.predicted)))
        
        cm = ConfusionMatrix(self.test_y, self.predicted)
        #logging.info("Confusion Matrix: \n" , cm)
        #cm.plot()
        
        logging.info("f1_score : " + str(f1_score(self.test_y, self.predicted, average="macro", labels=np.unique(self.predicted))))
        logging.info("precision_score : " + str(precision_score(self.test_y, self.predicted, average="macro", labels=np.unique(self.predicted))))
        logging.info("recall_score : " + str(recall_score(self.test_y, self.predicted, average="macro")))

def preprocess(sentence):
    sentence = sentence.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(sentence)
    filtered_words = [w for w in tokens if not w in stopwords.words('english')]
    return " ".join(filtered_words)
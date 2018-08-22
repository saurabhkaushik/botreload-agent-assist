from agentapp.model_select import get_model, getTrainingModel, getResponseModel, getCustomerModel
from agentapp.tickets_learner import tickets_learner
from agentapp.UtilityClass import UtilityClass
from agentapp.UtilityClass_spacy import UtilityClass_spacy
from agentapp.tickets_learner import tickets_learner
from agentapp.TfidfVectorizer import TfidfEmbeddingVectorizer, MeanEmbeddingVectorizer

from gensim.models.word2vec import Word2Vec 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.pipeline import Pipeline
from pandas_ml import ConfusionMatrix 
from sklearn.metrics import  f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

import csv
import re 
import numpy as np
import logging
import pickle
import pandas as pd

class IntentExtractor_resp(object): 
    def __init__(self):
        self.utilclass = UtilityClass()
        self.utilspace = UtilityClass_spacy()

    def prepareTrainingData(self, cust_id):
        logging.info("prepareTrainingData : Started " + str(cust_id))
        self.X, self.y = [], []        
        tickets_learn = tickets_learner()
        ticket_data = tickets_learn.getResponseData(cust_id=cust_id)
        lang = getCustomerModel().getLanguage(cust_id)
        xX = []
        yY = []
        for linestms in ticket_data:           
            for linestm in linestms:
                strx = str(linestm['tags'] + linestm['resp_name'] + linestm['resp_tags'] + linestm['response_text']).strip()
                if (strx != ''):                    
                    strx = self.utilspace.preprocessText(strx, lang=lang, ner=True)
                    strx = str(self.utilclass.cleanData(strx, lang=lang, lowercase=True, remove_stops=True, tag_remove=True))               
                    xX.append(strx.strip().split())
                    yY.append(str(linestm['res_category']).strip())
        self.X = xX
        self.y = yY
                
        self.X, self.y = np.array(self.X, dtype=object), np.array(self.y, dtype=object)

        logging.info ("Total Training Examples : %s" % len(self.y))
        logging.info("prepareTrainingData : Completed " + str(cust_id))
        return
            
    def startTrainingProcess(self, cust_id):
        logging.info("startTrainingProcess : Started " + str(cust_id))
        if len(self.y) < 1: 
            logging.info('Cant process as no Training ')
            return

        #from imblearn.over_sampling import SMOTE, ADASYN
        #self.X, self.y = SMOTE().fit_sample(self.X, self.y)

        dim_size = 100
        self.model = Word2Vec(self.X, size=dim_size, window=5, min_count=1, workers=3)
        self.model.wv.index2word
        
        w2v = {w: vec for w, vec in zip(self.model.wv.index2word, self.model.wv.syn0)}
        #self.etree_w2v_tfidf = Pipeline([("word2vec vectorizer", MeanEmbeddingVectorizer(w2v)), 
        #                ("extra trees", ExtraTreesClassifier(n_estimators=200))])
        #self.etree_w2v_tfidf = Pipeline([("word2vec vectorizer", MeanEmbeddingVectorizer(w2v, dim_size)), 
        #                ("MultinomialNB", MultinomialNB())])
        self.etree_w2v_tfidf = Pipeline([("word2vec vectorizer", MeanEmbeddingVectorizer(w2v, dim_size)), 
                        ("LogisticRegression", LogisticRegression(random_state=0))]) 
        #self.etree_w2v_tfidf = Pipeline([("word2vec vectorizer", MeanEmbeddingVectorizer(w2v, dim_size)), 
        #               ("SVC", SVC(kernel='linear', probability=True))])
        try: 
            self.etree_w2v_tfidf.fit(self.X, self.y)
        except ValueError as err:
            logging.error(err)
        
        logging.info ("Total Training Samples : %s" % len(self.y))
        logging.info("startTrainingProcess : Completed " + str(cust_id))
        return
        
    def getPredictedIntent(self, textinput, cust_id): 
        logging.info("getPredictedIntent : Started " + str(cust_id))
        if len(self.y) < 1: 
            logging.info('Cant process as no Training ')
            return
        self.test_X = []
        lang = getCustomerModel().getLanguage(cust_id)
        strx = self.utilclass.cleanData(textinput, lang=lang, lowercase=True, remove_stops=True, tag_remove=True)
        self.test_X.append(strx.strip().split())
        self.predicted = []
        try:
            self.predicted = self.etree_w2v_tfidf.predict(self.test_X) 
        except ValueError as err: 
            logging.error('getPredictedIntent : ' +  str(err))

        if len(self.predicted) < 1: 
            self.predicted.append('default')
        logging.info("getPredictedIntent : Completed " + str(cust_id))
        return self.predicted

    def getPredictedIntent_list(self, X_in, cust_id): 
        logging.info("getPredictedIntent_list : Started " + str(cust_id))
        
        lang = getCustomerModel().getLanguage(cust_id)
        X_in = X_in.apply(lambda x : self.utilclass.cleanData(x, lang=lang, lowercase=True, remove_stops=True, tag_remove=True).strip().split())
        
        predicted_list= []
        try:
            predicted_list = self.etree_w2v_tfidf.predict(X_in) 
        except ValueError as err: 
            logging.error('getPredictedIntent_list : ' + str(err))   
        except AttributeError as err: 
            logging.error('getPredictedIntent_list : ' + str(err)) 
        predict_df = pd.Series(predicted_list)
        logging.info("getPredictedIntent_list : Completed " + str(cust_id))
        return predict_df

    # Work on Data Frame  
    def startTrainLogPrediction(self, cust_id):
        logging.info("startTrainLogPrediction : Started " + str(cust_id))
        traindata = getTrainingModel()  
        ticketslearn  = tickets_learner()
        ticket_pd = ticketslearn.getTrainingData_DataFrame(cust_id) 
        if (len (ticket_pd) > 0):
            ticket_pd['resp_category'], ticket_pd['predict_prob'] = self.getPredictedIntent_prob(ticket_pd['query'], cust_id)
            traindata.batchUpdate(ticket_pd, cust_id=cust_id)
        
        logging.info("startTrainLogPrediction : Completed " + str(cust_id))
        return 
        
    def getPredictedIntent_prob(self, X_in, cust_id): 
        logging.info("getPredictedIntent_prob : Started " + str(cust_id))
        
        lang = getCustomerModel().getLanguage(cust_id)
        X_in = X_in.apply(lambda x : self.utilclass.cleanData(x, lang=lang, lowercase=True, remove_stops=True, 
                                                              tag_remove=True).strip().split())
        
        try:            
            predicted_list = self.etree_w2v_tfidf.predict(X_in) 
            predicted_prob = self.etree_w2v_tfidf.predict_proba(X_in)           
        except ValueError as err: 
            logging.error('getPredictedIntent_prob : ' + str(err))            
        
        intent_predict_df = pd.DataFrame(predicted_list, columns=['predicted_list'])
        #intent_predict_df ['predicted_prob'] = pd.Series(predicted_prob)
        #print (predicted_prob)
        predict_prob = []
        predict_class = []
        for items in predicted_prob:
            predict_df = pd.DataFrame({'Class': self.etree_w2v_tfidf.classes_, 'Prob' : items})
            predict_prob.append(predict_df.loc[predict_df['Prob'].idxmax(), 'Prob'])
            predict_class.append(predict_df.loc[predict_df['Prob'].idxmax(), 'Class'])
         
        intent_predict_df['predict_class'] = pd.Series(predict_class)
        intent_predict_df['predict_prob'] = pd.Series(predict_prob)
        
        #print (intent_predict_df)        
        
        logging.info("getPredictedIntent_list : Completed " + str(cust_id))
        return intent_predict_df['predict_class'], intent_predict_df['predict_prob']
    
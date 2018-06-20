from agentapp.model_select import get_model, getTrainingModel, getResponseModel, getCustomerModel
from agentapp.StorageOps import StorageOps
from agentapp.UtilityClass import UtilityClass
from agentapp.UtilityClass_spacy import UtilityClass_spacy
from agentapp.IntentExtractor import IntentExtractor
from agentapp.IntentExtractor_resp import IntentExtractor_resp
from agentapp.tickets_learner import tickets_learner
from sklearn.metrics import  f1_score, precision_score, recall_score
from pandas_ml import ConfusionMatrix 
from nltk.stem import PorterStemmer

import pandas as pd 
import logging
import numpy as np

class ModelEvaluate(object):
    
    def __init__(self):
        self.utilclass = UtilityClass()
        self.storage = StorageOps()
        self.utilspace = UtilityClass_spacy()

    def prepareTrainingData(self, cust_id):
        logging.info("prepareTrainingData : Started : " + str(cust_id))
        tickets_learn = tickets_learner()
        ticket_data = tickets_learn.getTrainingData(cust_id=cust_id)
    
        ticket_struct = []
        for linestms in ticket_data:           
            for linestm in linestms:
                if linestm['response'].strip() != '':
                    ticket_struct.append({'id' : linestm['id'], 'query' : linestm['query'], 'response': linestm['response'].strip(), 'tags' : linestm['tags'], 'resp_category' : linestm['resp_category'] })
        self.ticket_pd = pd.DataFrame(ticket_struct)
        #print (self.ticket_pd)
        logging.info ("Total Training Examples : %s" % len(self.ticket_pd))
        logging.info("prepareTrainingData : Completed : " + str(cust_id))
        return 
    
    def startEvaluation(self, cust_id):
        logging.info('startEvaluation : Started : ' + str(cust_id))     
        tickets_learn = tickets_learner()          

        try :
            X_q = self.ticket_pd['query']
        except KeyError as err:
            logging.error("startEvaluation : " + str(err))
            return 

        self.ticket_pd['query_tag'] = self.ticket_pd[['query', 'tags']].apply(lambda x: ' . '.join(x), axis=1) 
        
        intenteng = IntentExtractor()
        #self.ticket_pd['TrainingModel_intent'] = self.ticket_pd['query_tag'].apply(lambda x: ''.join(intenteng.getPredictedIntent(x, cust_id)))
        
        self.ticket_pd['TrainingModel_intent'] = intenteng.getPredictedIntent_list(self.ticket_pd['query'], cust_id)
        
        intenteng_resp = IntentExtractor_resp()
        intenteng_resp.prepareTrainingData(cust_id)
        intenteng_resp.startTrainingProcess(cust_id)
        #self.ticket_pd['ResponseModel_intent'] = self.ticket_pd['query'].apply(lambda x: ''.join(intenteng_resp.getPredictedIntent(x, cust_id)))

        self.ticket_pd['ResponseModel_intent'] = intenteng_resp.getPredictedIntent_list(self.ticket_pd['query'], cust_id)
        self.ticket_pd['intent_tags'] = self.ticket_pd['resp_category'].apply (lambda x: tickets_learn.get_response_mapping_tags(x, cust_id, 'tags').lower().split())
        self.ticket_pd['response_tags'] =  self.ticket_pd['ResponseModel_intent'].apply (lambda x: tickets_learn.get_response_mapping_tags(x, cust_id, 'resp_tags').lower().split())
        
        self.ticket_pd['query_list'] = self.ticket_pd['query_tag'].apply (lambda x:x.lower().split())
        self.ticket_pd['response_list'] = self.ticket_pd['response'].apply (lambda x:x.lower().split())

        self.ticket_pd['query_list'] = self.ticket_pd['query_list'].apply (lambda x: self.applystem(x))
        self.ticket_pd['response_list'] = self.ticket_pd['response_list'].apply (lambda x: self.applystem(x))
                
        self.ticket_pd['match_in_query_list'] = self.ticket_pd.apply (lambda x: self.matchword(x['query_list'], x['intent_tags']), axis=1) 
        self.ticket_pd['match_in_response_list'] = self.ticket_pd.apply (lambda x: self.matchword(x['response_list'], x['response_tags']), axis=1) 
        
        csvfile = self.ticket_pd.to_csv()
        self.storage.put_bucket(csvfile, str("TrainingModel_Evaluate_" + str(cust_id))) 
        logging.info("startEvaluation : Completed : " + str(cust_id))
        return
    
    def matchword(self, X, Y): 
        strx = []
        for items in X: 
            if items in Y: 
                strx.append(items)
        return strx
    
    def applystem(self, X):
        ps = PorterStemmer()
        strx = []
        for items in X: 
            strx.append(ps.stem(items))
        return strx
    
    def createConfusionMatrix(self, cust_id):
        logging.info("createConfusionMatrix : Started " + str(cust_id))
        logging.info("Mean Response Model and Training Model : \n" + str(np.mean(self.ticket_pd['ResponseModel_intent'] == self.ticket_pd['TrainingModel_intent'])))
        logging.info("Mean Processed and Current Model : \n" + str(np.mean(self.ticket_pd['ResponseModel_intent'] == self.ticket_pd['resp_category'])))

        '''
        cm = ConfusionMatrix(self.ticket_pd['ResponseModel_intent'], self.ticket_pd['TrainingModel_intent'])
       
        logging.info("f1_score : " + str(f1_score(self.ticket_pd['ResponseModel_intent'], self.ticket_pd['TrainingModel_intent'], average="macro", labels=np.unique(self.ticket_pd['TrainingModel_intent']))))
        logging.info("precision_score : " + str(precision_score(self.ticket_pd['ResponseModel_intent'], self.ticket_pd['TrainingModel_intent'], average="macro", labels=np.unique(self.ticket_pd['TrainingModel_intent']))))
        logging.info("recall_score : " + str(recall_score(self.ticket_pd['ResponseModel_intent'], self.ticket_pd['TrainingModel_intent'], average="macro")))
        '''
        logging.info("createConfusionMatrix : Completed " + str(cust_id))        
        return 
from agentapp.model_select import get_model, getTrainingModel, getResponseModel, getCustomerModel, getAnalyticsModel
from agentapp.StorageOps import StorageOps
from agentapp.UtilityClass import UtilityClass
from agentapp.UtilityClass_spacy import UtilityClass_spacy
from agentapp.IntentExtractor import IntentExtractor
from agentapp.IntentExtractor_resp import IntentExtractor_resp
from agentapp.tickets_learner import tickets_learner
from sklearn.metrics import  f1_score, precision_score, recall_score
from pandas_ml import ConfusionMatrix 
from nltk.stem import PorterStemmer
from nltk.translate.bleu_score import sentence_bleu

import pandas as pd 
import logging
import numpy as np

class ModelEvaluate(object):
    
    def __init__(self):
        self.utilclass = UtilityClass()
        self.storage = StorageOps()
        self.utilspace = UtilityClass_spacy()
        self.analytics_pd = {}

    def prepareTrainingData(self, cust_id):
        logging.info("prepareTrainingData : Started : " + str(cust_id))
        tickets_learn = tickets_learner()
        ticket_data = tickets_learn.getTrainingData(cust_id=cust_id)
        self.analytics_pd['cust_id'] = cust_id
        ticket_struct = []
        self.analytics_pd['total_tickets'] = 0
        for linestms in ticket_data: 
            self.analytics_pd['total_tickets'] += len(linestms)          
            for linestm in linestms:                
                if linestm['response'].strip() != '':
                    ticket_struct.append({'id' : linestm['id'], 'query' : linestm['query'], 
                                          'response': linestm['response'].strip(), 'tags' : linestm['tags'], 
                                          'resp_category' : linestm['resp_category'], 'feedback_resp' : linestm['feedback_resp'] if 'feedback_resp' in linestm else '',
                                          'feedback_prob' : linestm['feedback_prob'],'predict_prob' : linestm['predict_prob'] if 'predict_prob' in linestm else 0,
                                          'created' : linestm['created']})
        self.ticket_pd = pd.DataFrame(ticket_struct)
        #print (self.ticket_pd)
        if (len(self.ticket_pd) > 0): 
            self.analytics_pd['total_tickets_with_response'] = len(self.ticket_pd)
            self.analytics_pd['last_ticket_timestamp'] = max(self.ticket_pd['created'])
            self.analytics_pd['Mean_feedback_prob'] = self.ticket_pd['feedback_prob'].mean()
            self.analytics_pd['Mean_predict_prob'] = self.ticket_pd['predict_prob'].mean()
        
        logging.info ("Total Training Examples : %s" % len(self.ticket_pd))
        logging.info("prepareTrainingData : Completed : " + str(cust_id))
        return 
    
    def startEvaluation(self, cust_id):
        logging.info('startEvaluation : Started : ' + str(cust_id))     
        tickets_learn = tickets_learner()          

        if (len(self.ticket_pd) > 0):             
            intenteng = IntentExtractor()           
            intenteng_resp = IntentExtractor_resp()
            intenteng_resp.prepareTrainingData(cust_id)
            intenteng_resp.startTrainingProcess(cust_id)
            
            self.ticket_pd['TrainingModel_intent'] = intenteng.getPredictedIntent_list(self.ticket_pd['query'], cust_id)
            self.ticket_pd['ResponseModel_intent'] = intenteng_resp.getPredictedIntent_list(self.ticket_pd['query'], cust_id)
            
            respmap = tickets_learn.get_response_map(cust_id, 'tags')
            resptagmap = tickets_learn.get_response_map(cust_id, 'resp_tags')
            
            self.ticket_pd['intent_tags'] = self.ticket_pd['TrainingModel_intent'].apply (lambda x: self.getMatch(respmap, x).lower().split())
            self.ticket_pd['response_tags'] =  self.ticket_pd['TrainingModel_intent'].apply (lambda x: self.getMatch(resptagmap, x).lower().split())
            
            self.ticket_pd['query_list'] = self.ticket_pd['query'].apply (lambda x:x.lower().split())
            self.ticket_pd['response_list'] = self.ticket_pd['response'].apply (lambda x:x.lower().split())
    
            self.ticket_pd['query_list'] = self.ticket_pd['query_list'].apply (lambda x: self.applystem(x))
            self.ticket_pd['response_list'] = self.ticket_pd['response_list'].apply (lambda x: self.applystem(x))
                    
            self.ticket_pd['intent_tags_in_query_list'] = self.ticket_pd.apply (lambda x: self.matchword(x['query_list'], x['intent_tags']), axis=1) 
            self.ticket_pd['resp_tags_in_response_list'] = self.ticket_pd.apply (lambda x: self.matchword(x['response_list'], x['response_tags']), axis=1) 
    
            self.ticket_pd['percentage_match_in_query_list'] = self.ticket_pd.apply (lambda x: self.percentmatchword(x['query_list'], x['intent_tags']), axis=1) 
            self.ticket_pd['percentage_match_in_response_list'] = self.ticket_pd.apply (lambda x: self.percentmatchword(x['response_list'], x['response_tags']), axis=1) 
            
            resp_text_map = tickets_learn.get_response_map(cust_id, 'response_text')
            self.ticket_pd['intent_response_text'] = self.ticket_pd['TrainingModel_intent'].apply (lambda x: self.getMatch(resp_text_map, x))
            self.ticket_pd['response_response_text'] = self.ticket_pd['ResponseModel_intent'].apply (lambda x: self.getMatch(resp_text_map, x))
            self.ticket_pd['bleu_score_intent'] = self.ticket_pd.apply(lambda x: self.getBleuScore(x['response'], x['intent_response_text']), axis=1)
            self.ticket_pd['bleu_score_response'] = self.ticket_pd.apply(lambda x: self.getBleuScore(x['response'], x['response_response_text']), axis=1)
            
            csvfile = self.ticket_pd.to_csv()
            self.storage.put_bucket(csvfile, str("TrainingModel_Evaluate_" + str(cust_id))) 
        logging.info("startEvaluation : Completed : " + str(cust_id))
        return
    
    def getBleuScore(self, refdata, candata):
        reference = [refdata.lower().split()]
        candidate = candata.lower().split()
        score = sentence_bleu(reference, candidate, weights=(0, 1, 0, 0))
        return score
    
    def getMatch (self, xmap, val): 
        tags = ''
        try: 
            tags = xmap[val]
        except KeyError as err: 
            logging.error('getMatch :' + str(err))
        return tags 
        
    def matchword(self, X, Y): 
        strx = []
        for items in X: 
            if items in Y: 
                strx.append(items)
        return strx
    
    def percentmatchword(self, X, Y): 
        strx = []
        tot_words = len(X) + len(Y)
        mat_words = 0
        if tot_words < 1: 
            return 0
        for items in X: 
            if items in Y: 
                mat_words += 1 
        centmatch = int((mat_words * 100)/tot_words)
        return centmatch
    
    def applystem(self, X):
        ps = PorterStemmer()
        strx = []
        for items in X: 
            strx.append(ps.stem(items))
        return strx
    
    def createConfusionMatrix(self, cust_id):
        logging.info("createConfusionMatrix : Started " + str(cust_id))
        if (len(self.ticket_pd) > 0): 
            
            self.analytics_pd['Mean_Accuracy_Intent_vs_Response'] = np.mean(self.ticket_pd['TrainingModel_intent'] == self.ticket_pd['ResponseModel_intent'])
            self.analytics_pd['Mean_Accuracy_Intent_vs_Saved'] = np.mean(self.ticket_pd['TrainingModel_intent'] == self.ticket_pd['resp_category'])
            self.analytics_pd['Percentage_Match_Tags_vs_Query'] = self.ticket_pd['percentage_match_in_query_list'].mean()
            self.analytics_pd['Percentage_Match_Tags_vs_Query'] = self.ticket_pd['percentage_match_in_response_list'].mean()
            self.analytics_pd['Bleu_Score_Intent'] = self.ticket_pd['bleu_score_intent'].mean()
            self.analytics_pd['Bleu_Score_Response'] = self.ticket_pd['bleu_score_response'].mean()
            self.analytics_pd['Feedback_tickets_count'] = np.mean(len(str(self.ticket_pd['feedback_resp'])) > 0)
            
            logging.info("\nMean Intent Model vs Response Model     : \n" + str(self.analytics_pd['Mean_Accuracy_Intent_vs_Response']))
            logging.info("Mean Intent Model vs Saved Model        : \n" + str(self.analytics_pd['Mean_Accuracy_Intent_vs_Saved']))
    
            logging.info("Average Percentage Match in query : \n" + str(self.analytics_pd['Percentage_Match_Tags_vs_Query']))
            logging.info("Average Percentage Match in query : \n" + str(self.analytics_pd['Percentage_Match_Tags_vs_Query']))

            logging.info("Bleu Score - Intent               : \n" + str(self.analytics_pd['Bleu_Score_Intent']))
            logging.info("Bleu Score - Response             : \n" + str(self.analytics_pd['Bleu_Score_Response']))
            
            getAnalyticsModel().create(self.analytics_pd)
            
        logging.info("createConfusionMatrix : Completed " + str(cust_id))        
        return 
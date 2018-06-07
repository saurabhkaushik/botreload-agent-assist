from agentapp.model_select import get_model, getTrainingModel, getResponseModel, getCustomerModel
from agentapp.StorageOps import StorageOps
from agentapp.UtilityClass import UtilityClass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics import pairwise_distances_argmin_min
from agentapp.tickets_learner import tickets_learner
from nltk.tokenize import RegexpTokenizer
import numpy as np
from nltk.corpus import stopwords
import pandas as pd 
import logging
import re
import math 
from gensim.summarization import summarize

class SmartRepliesSelector(object):
    
    def __init__(self):
        self.utilclass = UtilityClass()
        self.storage = StorageOps()

    def prepareTrainingData(self, cust_id):
        logging.info("prepareTrainingData : Started : " + str(cust_id))
        ticket_data = self.getTrainingData(cust_id=cust_id)
    
        ticket_struct = []
        for linestms in ticket_data:           
            for linestm in linestms:
                if linestm['response'].strip() != '':
                    ticket_struct.append({'id' : linestm['id'], 'query' : linestm['query'], 'response': linestm['response'].lower().strip(), 'tags' : linestm['tags']})
        self.ticket_pd = pd.DataFrame(ticket_struct)
        #print (self.ticket_pd)
        logging.info ("Total Training Examples : %s" % len(self.ticket_pd))
        logging.info("prepareTrainingData : Completed : " + str(cust_id))
        return 
    
    def generateNewResponse(self, cust_id):
        logging.info('generateNewResponse : Started : ' + str(cust_id))
        self.ticket_pd['response_cluster'] = -1
        self.ticket_pd['select_response'] = np.nan
        X_q = []
        try :
            X_q = self.ticket_pd['query']
        except KeyError as err:
            logging.error("generateNewResponse : " + str(err))
            return 
        X_q = self.ticket_pd['query'].apply(lambda x: self.utilclass.cleanData(x, lowercase=True, remove_stops=True))
        query_clstr_itr = int (math.sqrt(len(X_q) / 2)) #int (len(X_q) / 10) 
        print ('Query Cluster Size : ', query_clstr_itr)
        if (query_clstr_itr <= 1): 
            return
        if (query_clstr_itr > 15): 
            query_clstr_itr = 15
        self.ticket_pd['query_cluster'], _, self.ticket_pd['select_tags'] = self.getKMeanClusters(cust_id, X_q, query_clstr_itr)
        
        for x in range (0, query_clstr_itr): 
            query_sub = self.ticket_pd[self.ticket_pd.query_cluster == x]            
            resp_clst_itr = int (math.sqrt(len(query_sub) / 2)) #int(len(query_sub) / 5)
            print ('Response Cluster Size : ',resp_clst_itr)                 
            if resp_clst_itr <= 1:
                continue
            if resp_clst_itr > 5:
                resp_clst_itr = 5
            qx = query_sub['response'].apply(lambda x: self.utilclass.cleanData(x, lowercase=True, remove_stops=True))
            query_sub['response_cluster'], query_sub['select_response'], ___, query_sub['response_summary'] = self.getKMeanClusters_resp(cust_id, qx, query_sub['response'], resp_clst_itr) 
            for index, items in query_sub.iterrows(): 
                self.ticket_pd.loc[(self.ticket_pd['id'] == items['id']), 'response_cluster'] = int (items['response_cluster'])
                self.ticket_pd.loc[(self.ticket_pd['id'] == items['id']), 'select_response'] = items['select_response']
                self.ticket_pd.loc[(self.ticket_pd['id'] == items['id']), 'response_summary'] = items['response_summary']
        print (self.ticket_pd)
        logging.info('generateNewResponse : Completed : ' + str(cust_id))
        return 
    
    def populateResponseData(self, cust_id): 
        logging.info ('populateResponseData : Started ' + str(cust_id))
        try: 
            tx = self.ticket_pd['response_cluster']
        except KeyError as err:
            logging.error("populateResponseData : " + str(err))
            return 
        
        resp_model = getResponseModel()
        storageOps = StorageOps()
        next_page_token = 0
        token = None
        last_id = 9999
        while next_page_token != None:             
            resp_logs, next_page_token = resp_model.list(cursor=token, modifiedflag=False, defaultflag=False, cust_id=cust_id, done=True)
            token = next_page_token
            for resp_log in resp_logs:
                resp_model.delete(resp_log['id'], cust_id)
                last_id = resp_log['id']

        rep_index = int(last_id) + 1
        for index, item in self.ticket_pd.iterrows(): 
            if item['select_response'] == 'true' and item['select_tags'].strip() != '': 
                resp_model.create((cust_id + '_Response_' + str(rep_index)), (cust_id + '_Response_' + str(rep_index)), item['response_summary'], item['select_tags'], done=True, id=rep_index, cust_id=cust_id)
                rep_index += 1 
            
        csvfile = self.ticket_pd.to_csv()        
        storageOps.put_bucket(csvfile, str("SR_CSV_" + str(cust_id))) 
        logging.info ('populateResponseData : Completed ' + str(cust_id))
        return
    
    def getKMeanClusters(self, cust_id, X_in, true_k):
        #logging.info("getKMeanClusters : " + str(cust_id))
        selected_resp = []
        selected_tags = []
        prediction = []
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            X = vectorizer.fit_transform(X_in)
        except ValueError as err: 
            logging.error("getKMeanClusters : " , err)
            return prediction, selected_resp, selected_tags
        model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
        model.fit(X)  
        prediction = model.predict(X)
         
        closest, _ = pairwise_distances_argmin_min(model.cluster_centers_, X)
        
        order_centroids = model.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
        tags_clurt = []
        for i in range(true_k):
            tags_temp = []
            for ind in order_centroids[i, :20]:
                tags_temp.append(terms[ind].lower().strip())
            tags_clurt.append(tags_temp)
        
        closest = closest.tolist()
        input_x = X_in.tolist()
        for i in range(len(prediction)):  
            qtags = '' 
            for resp_tags in tags_clurt[prediction[i]]:
                if resp_tags in input_x[i]:
                    qtags += resp_tags + ' '
            selected_tags.append(qtags.strip())
            if i in closest:  
                selected_resp.append('true')
            else :
                selected_resp.append('false')
           
        return prediction, selected_resp, selected_tags 
    
    def getKMeanClusters_resp(self, cust_id, X_in, X2_in, true_k):
        #logging.info("getKMeanClusters : " + str(cust_id))
        selected_resp = []
        selected_tags = []
        prediction = []
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            X = vectorizer.fit_transform(X_in)
        except ValueError as err: 
            logging.error("getKMeanClusters : " , err)
            return prediction, selected_resp, selected_tags
        model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
        model.fit(X)  
        prediction = model.predict(X)
         
        closest, _ = pairwise_distances_argmin_min(model.cluster_centers_, X)
        
        order_centroids = model.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
        tags_clurt = []
        for i in range(true_k):
            tags_temp = []
            for ind in order_centroids[i, :20]:
                tags_temp.append(terms[ind].lower().strip())
            tags_clurt.append(tags_temp)
        
        closest = closest.tolist()
        input_x = X_in.tolist()
        for i in range(len(prediction)):  
            qtags = '' 
            for resp_tags in tags_clurt[prediction[i]]:
                if resp_tags in input_x[i]:
                    qtags += resp_tags + ' '
            selected_tags.append(qtags.strip())
            if i in closest:  
                selected_resp.append('true')
            else :
                selected_resp.append('false')
                
        input_x2 = X2_in.tolist()
        txtforsum = []
        sumresponse = []
        for i in range(true_k):
            for j in range(len(prediction)):
                if i == prediction[j]: 
                    txtforsum.append(input_x2[j]) 
            sumresponse.append(self.summarizationtext(txtforsum))
        outsumresp = []
        for i in range(len(prediction)):
            outsumresp.append(sumresponse[prediction[i]])
        return prediction, selected_resp, selected_tags, outsumresp 
    
    def getTrainingData(self, cust_id):   
        #logging.info ('getTrainingData : ' + str(cust_id))
        ticket_data = []
        next_page_token = 0
        token = None
        while next_page_token != None:             
            ticket_logs, next_page_token = getTrainingModel().list(cursor=token, feedback_flag=None, cust_id=cust_id, done=True)
            token = next_page_token
            ticket_data.append(ticket_logs)
        return ticket_data 

    def summarizationtext(self, textlist):       
        ratio_c = 1 / len(textlist)
        intext = " ".join(textlist) 
        sumtext = ''
        if len (intext) > 10:
            try: 
                sumtext = summarize(intext, word_count=50) #ratio=ratio_c)
            except ValueError as err: 
                logging.error(err)
        return sumtext  
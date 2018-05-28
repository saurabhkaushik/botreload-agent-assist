from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import logging
from agentapp.tickets_learner import tickets_learner
from nltk.tokenize import RegexpTokenizer
import numpy as np
from nltk.corpus import stopwords
import pandas as pd 
from agentapp.model_select import get_model, getTrainingModel, getResponseModel, getCustomerModel

class SmartRepliesSelector(object):
    
    def createProcessor(self, cust_id):
        self.prepareTrainingData(cust_id)
        self.ticket_pd['query_cluster'] = self.getKMeanClusters(cust_id, self.X_q, true_k = 10)
        #self.ticket_pd['response_cluster'] = None 
        for x in range (0, 10): 
            query_sub = self.ticket_pd[self.ticket_pd.query_cluster == x]            
               query_sub['response_cluster'] = self.getKMeanClusters(cust_id, query_sub['response'], true_k = 2) 
               query_sub.drop(columns=['query', 'tags', 'response', 'query_cluster'])
               print (query_sub)
               self.ticket_pd.merge(query_sub, on='id', how='left')
            #print (self.ticket_pd)
        #print (self.ticket_pd) 
        
    def prepareTrainingData(self, cust_id):
        logging.info("prepareTrainingData : " + str(cust_id))
        self.X_q, self.X_r = [], []
        #tickets_learn = tickets_learner() 
        ticket_data = self.getTrainingData(cust_id=cust_id)
    
        ticket_struct = []
        for linestms in ticket_data:           
            for linestm in linestms:
                logging.debug (linestm['tags'] + " =>  " + linestm['resp_category'])
                ticket_struct.append({'id' : linestm['id'], 'query' : linestm['query'], 'response': linestm['response'], 'tags' : linestm['tags']})
        self.ticket_pd = pd.DataFrame(ticket_struct)
        self.X_q = self.ticket_pd['query']
        self.X_r = self.ticket_pd['response']

        logging.info ("Total Training Examples : %s" % len(self.ticket_pd))
    
    def getKMeanClusters(self, cust_id, X_in, true_k = 10):
        logging.info("getKMeanClusters : " + str(cust_id))
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            X = vectorizer.fit_transform(X_in)
        except ValueError as err: 
            logging.error(err)
            return
            
        
        model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
        model.fit(X)
        
        '''
        print("Top terms per cluster:")
        order_centroids = model.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
        for i in range(true_k):
            print("Cluster %d:" % i),
            for ind in order_centroids[i, :10]:
                print(' %s' % terms[ind]),
            print   
        print("\n")
        print ("labels_ : ", model.labels_)
        
        print ("cluster_centers_ : ", model.cluster_centers_)        
        '''
        prediction = model.predict(X)
        return prediction 
    
    def getTrainingData(self, cust_id):   
        logging.info ('getTrainingData : ')
        ticket_data = []
        next_page_token = 0
        token = None
        while next_page_token != None:             
            ticket_logs, next_page_token = getTrainingModel().list_all(cursor=token, cust_id=cust_id, done=False)
            token = next_page_token
            ticket_data.append(ticket_logs)
        return ticket_data 
        
def preprocess(sentence):
    sentence = sentence.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(sentence)
    filtered_words = [w for w in tokens if not w in stopwords.words('english')]
    return " ".join(filtered_words)

import datetime
from agentapp.model_select import get_model, getTrainingModel, getResponseModel, getCustomerModel
import json
import logging 
import csv
from flask import current_app
import pandas as pd

# [START build_service]
from google.cloud import datastore
from google.cloud import storage
import google

class tickets_learner(object):

    def __init__(self):
        self.client = datastore.Client()
        self.storage_client = storage.Client()
    # [END build_service]
    
    def extractTrainingData_old(self, cust_id):   
        logging.info ('extractTrainingData : ')
        next_page_token = 0
        token = None        
        from agentapp.IntentExtractor import IntentExtractor
        intenteng = IntentExtractor()
        while next_page_token != None:             
            ticket_logs, next_page_token = get_model().list('tickets', cursor=token, cust_id='default', done=True)
            token = next_page_token
            for ticket_log in ticket_logs: 
                tickets_data = ticket_log["json_data"] 
                tickets_data_json = json.loads(tickets_data)
                for ticket_data in tickets_data_json['tickets']: 
                    description = ticket_data['description']
                    subject = ticket_data['subject']
                    tags = ', '.join(ticket_data['tags']) 
                    #print (str(subject + ' . ' + description + ' . ' + tags))
                    predicted = intenteng.getPredictedIntent(str(subject + ' . ' + description + ' . ' + tags) , cust_id)  
                    if len(predicted) < 1: 
                        predicted = ['Default']
                    getTrainingModel().create(tags, str(subject + ' . ' + description), '', '', done=True, resp_category=predicted[0], cust_id=cust_id)

    def extractTrainingData(self, cust_id):   
        logging.info ('extractTrainingData : ')
        next_page_token = 0
        token = None        
        from agentapp.IntentExtractor import IntentExtractor
        intenteng = IntentExtractor()
        while next_page_token != None:             
            ticket_logs, next_page_token = get_model().list('tickets', cursor=token, cust_id=cust_id, done=True)
            token = next_page_token
            for ticket_log in ticket_logs: 
                tickets_data = ticket_log["json_data"] 
                tickets_data_json = json.loads(tickets_data)
                #print (tickets_data_json)
                itr = 0
                for ticket_data in tickets_data_json['upload_ticket_data']: 
                    #print(ticket_data)
                    comments = ''
                    for comment_data in tickets_data_json['upload_comment_data']:
                        if (comment_data['id'] == ticket_data['id']):
                            try:
                                comments = comment_data['comments'][1]['plain_body']
                            except IndexError as err: 
                                logging.debug('')
                    
                    description = ticket_data['description']
                    subject = ticket_data['subject']                    
                    tags = ', '.join(ticket_data['tags']) 
                    predicted = intenteng.getPredictedIntent(str(subject + ' . ' + description + ' . ' + tags) , cust_id)
                    if len(predicted) < 1: 
                        predicted = ['Default']
                    getTrainingModel().create(tags, str(subject + ' . ' + description), comments, '',  done=True, resp_category=predicted[0], cust_id=cust_id)
                    itr += 1

    def getTrainingData(self, cust_id):   
        logging.info ('getTrainingData : ')
        ticket_data = []
        next_page_token = 0
        token = None
        while next_page_token != None:             
            ticket_logs, next_page_token = getTrainingModel().list_all(cursor=token, cust_id=cust_id, done=True)
            token = next_page_token
            ticket_data.append(ticket_logs)
        return ticket_data 
    
    def import_customerdata(self): 
        logging.info ('import_customerdata : Started ')
        with open(current_app.config['CUST_SET_PATH'], 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
        rid = 100
        for linestm in train_list:
            getCustomerModel().create(linestm[0].strip().lower(), language=linestm[1].strip().lower(), done=True, id=rid)
            rid += 1
        logging.info ('import_customerdata : Completed')

    def import_trainingdata(self, cust_id, lang_type): 
        logging.info ('import_trainingdata : Started')
        with open(current_app.config['TRAIN_SET_PATH'] + '-' +lang_type + '.csv', 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
        rid = 100
        while rid < 200: 
            for linestm in train_list:
                getTrainingModel().create(linestm[0].strip(), linestm[1].strip(), '', resp_category=linestm[2].strip(), done=True, id=rid, cust_id=cust_id)
                rid += 1
        logging.info ('import_trainingdata : Completed')
    
    def import_responsedata(self, cust_id, lang_type): 
        logging.info ('import_responsedata : Started')
        with open(current_app.config['CANNED_RESP_PATH'] + '-' +lang_type + '.csv', 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
        rid = 100
        for linestm in train_list:
            getResponseModel().create(linestm[0].strip(), linestm[0].strip(), linestm[1].strip(), linestm[2].strip(), done=True, id=rid, cust_id=cust_id)
            rid += 1
        logging.info ('import_responsedata : Completed')
            
    def get_response_mapping(self, response, cust_id):
        logging.info ('get_response_mapping : ')
        ds_response = getResponseModel().list(cust_id=cust_id, done=True)
        print ( 'ds_response : '+str(ds_response)) 
        
        for resp in ds_response: 
            if (resp != None) and (len(resp) > 0) :
                return resp[0]
        return None
    
    def formatOutput(self, predicted_intent, cust_id): 
        logging.info ('formatOutput : ')
        tickets_learn = tickets_learner()
        comments_struct = []  
        df_intent = pd.DataFrame(list(predicted_intent.items()), columns=['Resp_Class', 'Resp_Prob'])
        df_intent = df_intent.sort_values(['Resp_Prob'], ascending=[False])
        df_intent['Comment'] = 'NA'
        ds_response = getResponseModel().list(cust_id=cust_id, done=True) 
        i = 0
        for index, row in df_intent.iterrows():
            for resp_list in ds_response: 
                if (resp_list != None) and (len(resp_list) > 0) :
                    for resp_item in resp_list:
                        if resp_item['resp_name'] == row['Resp_Class']: 
                            comments_struct.append({'id': resp_item['id'], 'name' : resp_item['resp_name'], 'comment': resp_item['response_text'], 'prob': int(row['Resp_Prob']*100)}) 
            if (i >= 4):
                break
            i+=1        
        return comments_struct  

    def get_bucket(self, cust_id):
        print('get_bucket:')         
        try:
            bucket = self.storage_client.get_bucket(current_app.config['STORAGE_BUCKET']) 
            m_blob = bucket.get_blob(cust_id + '_model.pkl')
            file = m_blob.download_as_string()
            return file
        except google.cloud.exceptions.NotFound:
            print('Sorry, that bucket does not exist!')        
        return None
        
    def put_bucket(self, file, cust_id):
        print('put_bucket:')
        try:
            bucket = self.storage_client.get_bucket(current_app.config['STORAGE_BUCKET'])
            filename = cust_id + '_model.pkl'
            m_blob = bucket.blob(filename)            
            m_blob.upload_from_string(file)
        except google.cloud.exceptions.NotFound:
            print('Sorry, that bucket does not exist!')        
        #print('Blob created.')
        return file
        
    def create_bucket(self):
        print('create_bucket:')
        try:
            bucket = self.storage_client.lookup_bucket(current_app.config['STORAGE_BUCKET'])
            if bucket == None: 
                bucket = self.storage_client.create_bucket(current_app.config['STORAGE_BUCKET'])
        except google.cloud.exceptions.Conflict:
            print('Sorry, that bucket was not created!')        
        logging.info('Bucket created.')
    
    # Copy of Web Service Call 
    def processNewCustomer(self):
        logging.info('processNewCustomer : ')
        cust_model = getCustomerModel()
        cust_list = cust_model.list(newflag=True, done=True)
        from agentapp.IntentExtractor import IntentExtractor
        intenteng = IntentExtractor()
        for cust_x in cust_list[0]:             
            self.import_trainingdata(cust_x['cust_name'], cust_x['language']) 
            intenteng.prepareTrainingData(cust_x['cust_name']) 
            intenteng.startTrainingProcess(cust_x['cust_name'])
            cust_model.update(cust_x['cust_name'], language=cust_x['language'], intent_threshold=cust_x['intent_threshold'], organization=cust_x['organization'], email_id=cust_x['email_id'], password =cust_x['password'], newflag=False, done=True, id=cust_x['id'])
            logging.info('Processed new Customer : ' + cust_x['cust_name'])
            
        logging.info('Processed all new Customers.')
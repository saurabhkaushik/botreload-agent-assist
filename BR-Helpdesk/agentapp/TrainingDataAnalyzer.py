import datetime
from agentapp.model_select import get_model, getTrainingModel, getResponseModel, getCustomerModel
import json
import logging 
import csv
from flask import current_app
import pandas as pd
from google.cloud import datastore
from google.cloud import storage
import google
from nltk.tokenize import RegexpTokenizer
import numpy as np
from nltk.corpus import stopwords
import re 
class TrainingDataAnalyzer(object):
    
    def __init__(self):
        self.client = datastore.Client()
        self.storage_client = storage.Client()
    
    def copyOldTrainingLog(self):
        logging.info ('copyOldTrainingLog : Starting')        
        trainlog = get_model()
        next_page_token = 0
        token = None
        while next_page_token != None:
            ticket_logs, next_page_token = trainlog.list('tickets', cursor=token, cust_id='', done=True)
            token = next_page_token
            for ticket_log in ticket_logs:
                trainlog.create(ticket_log['type'], ticket_log['json_data'], created=ticket_log['created'], done=True, cust_id='default')
                trainlog.delete(id=ticket_log['id'], cust_id='')
                print ('Copying Ticket data: ' , ticket_log['id'])
        print ('copyOldTrainingLog: Completed ')

    def extractTicketData_default(self, src_cust_id='default'):   
        logging.info ('extractTicketData_default : Started :' + str(src_cust_id))
        trainlog = get_model()
        traindata = getTrainingModel() 

        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        while next_page_token != None:             
            ticket_logs, next_page_token = trainlog.list('tickets', cursor=token, cust_id=src_cust_id, done=True)
            token = next_page_token
            for ticket_log in ticket_logs: 
                tickets_data = ticket_log["json_data"] 
                tickets_data_json = json.loads(tickets_data)
                for ticket_data in tickets_data_json['tickets']: 
                    description = ticket_data['description']
                    subject = ticket_data['subject']
                    tags = ', '.join(ticket_data['tags']) 
                    url = ticket_data['url']  
                    id = ticket_data['id']           
                    for cust_id_x in cust_list:
                        if cust_id_x['cust_name'] in url:
                            traindata.create(tags, str(subject + ' . ' + description), '', done=False, id=id, cust_id=cust_id_x['cust_name'])                            
                            trainlog.delete(ticket_log['id'], cust_id=src_cust_id)
                            print('Creating for Ticket Id : ' , ticket_data['id'], cust_id_x['cust_name'])                            
        logging.info ('extractTicketData_default : Completed : ' + str(src_cust_id))
    
    def extractTicketData_cust(self, cust_id):   
        logging.info ('extractTicketData_cust : Started : ' + str(cust_id))
        trainlog = get_model()
        traindata = getTrainingModel() 

        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        while next_page_token != None:             
            ticket_logs, next_page_token = trainlog.list('tickets', cursor=token, cust_id=cust_id, done=True)
            token = next_page_token
            for ticket_log in ticket_logs: 
                tickets_data = ticket_log["json_data"] 
                tickets_data_json = json.loads(tickets_data)
                for ticket_data in tickets_data_json['tickets']: 
                    description = ticket_data['description']
                    subject = ticket_data['subject']
                    tags = ', '.join(ticket_data['tags']) 
                    url = ticket_data['url']  
                    id = ticket_data['id']     
                    traindata.create(tags, str(subject + ' . ' + description), '', id=id, done=False, cust_id=cust_id)
                    trainlog.delete(ticket_log['id'], cust_id=cust_id)
                    print('Creating for Ticket Id : ' , ticket_data['id'], cust_id)
        logging.info ('extractTicketData_cust : Completed : ' + str(cust_id))
        
    def extractIntentData_default(self, src_cust_id='default'):   
        logging.info ('extractIntentData_default : Started : ' + str(src_cust_id))
        trainlog = get_model()
        traindata = getTrainingModel() 

        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        while next_page_token != None:             
            intent_logs, next_page_token = trainlog.list('intent', cursor=token, cust_id=src_cust_id, done=True)
            token = next_page_token
            for intent_log in intent_logs: 
                intents_data = intent_log["json_data"] 
                intents_data_json = json.loads(intents_data)
                description = intents_data_json['description']
                subject = intents_data_json['subject']
                tags = ', '.join(intents_data_json['requester']['tags']) 
                cust_id = intents_data_json['currentAccount']['subdomain'] 
                id = intents_data_json['id']
                response = ''
                if len(intents_data_json['comments']) > 0:
                    response = intents_data_json['comments'][0]['value']
                    response = cleanhtml (response)
                for cust_id_x in cust_list:
                    if cust_id_x['cust_name'] == cust_id:
                        traindata.create(tags, str(subject + ' . ' + description), response, id=id, done=False, cust_id=cust_id)
                        trainlog.delete(intent_log['id'], cust_id=src_cust_id)
                        print('Creating for Intent : ' , intents_data_json['id'], cust_id)
        logging.info ('extractIntentData_default : Completed : ' + str(src_cust_id))
    
    def extractIntentData_cust(self, cust_id):   
        logging.info ('extractIntentData_cust : Started : ' + str(cust_id))
        trainlog = get_model()
        traindata = getTrainingModel() 

        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        while next_page_token != None:             
            intent_logs, next_page_token = trainlog.list('intent', cursor=token, cust_id=cust_id, done=True)
            token = next_page_token
            for intent_log in intent_logs: 
                intents_data = intent_log["json_data"] 
                intents_data_json = json.loads(intents_data)
                description = intents_data_json['description']
                subject = intents_data_json['subject']
                tags = ', '.join(intents_data_json['requester']['tags']) 
                response = ''
                id = intents_data_json['id']
                if len(intents_data_json['comments']) > 0:
                    response = intents_data_json['comments'][0]['value']
                    response = cleanhtml (response)
                traindata.create(tags, str(subject + ' . ' + description), response, id = id, done=False, cust_id=cust_id)
                trainlog.delete(intent_log['id'], cust_id=cust_id)
                print('Creating for Intent : ' , intents_data_json['id'], cust_id)
        logging.info ('extractIntentData_cust : Completed : ' + str(cust_id))  
    
    def extractFeedbackData_default(self, src_cust_id='default'):   
        logging.info ('extractFeedbackData_default : Started : ' + str(src_cust_id))
        trainlog = get_model()
        traindata = getTrainingModel() 

        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        while next_page_token != None:             
            intent_logs, next_page_token = trainlog.list('feedback', cursor=token, cust_id=src_cust_id, done=True)
            token = next_page_token
            for intent_log in intent_logs: 
                intents_data = intent_log["json_data"]                 
                intents_data_json = json.loads(intents_data)
                selected_response_id = intents_data_json["selected_response_id"]
                cust_id = intents_data_json["ticket_data"]['currentAccount']['subdomain'] 
                id = intents_data_json["ticket_data"]['id']                
                for cust_id_x in cust_list:
                    if cust_id_x['cust_name'] == cust_id:
                        train_data = traindata.read(id, cust_id=cust_id)
                        response_data = getResponseModel().read(selected_response_id, cust_id=cust_id)
                        if train_data != None and response_data != None: 
                            traindata.update(train_data["tags"], train_data["query"], train_data["response"], query_category=train_data['query_category'], resp_category=response_data['res_category'], feedback_flag=True, done=True, id=train_data['id'], cust_id=cust_id)
                            trainlog.delete(intent_log['id'], cust_id=src_cust_id)
                            print('Updating Feedback : ' , id, cust_id)
        logging.info ('extractFeedbackData_default : Completed : ' + str(src_cust_id))
    
    def extractFeedbackData_cust(self, cust_id):   
        logging.info ('extractFeedbackData_cust : Started : ' + str(cust_id))
        trainlog = get_model()
        traindata = getTrainingModel() 

        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        while next_page_token != None:             
            intent_logs, next_page_token = trainlog.list('feedback', cursor=token, cust_id=cust_id, done=True)
            token = next_page_token
            for intent_log in intent_logs: 
                intents_data = intent_log["json_data"] 
                intents_data_json = json.loads(intents_data)
                selected_response_id = intents_data_json["selected_response_id"]
                cust_id = intents_data_json["ticket_data"]['currentAccount']['subdomain'] 
                id = intents_data_json["ticket_data"]['id']                
                train_data = traindata.read(id, cust_id=cust_id)
                response_data = getResponseModel().read(selected_response_id, cust_id=cust_id)
                if train_data != None and response_data != None: 
                    traindata.update(train_data["tags"], train_data["query"], train_data["response"], query_category=train_data['query_category'], resp_category=response_data['res_category'], feedback_flag=True, done=True, id=train_data['id'], cust_id=cust_id)
                    trainlog.delete(intent_log['id'], cust_id=cust_id)
                    print('Updating Feedback : ' , id, cust_id)
        logging.info ('extractFeedbackData_cust : Completed : ' + str(cust_id))  
    
    def extractTicketData_new(self, cust_id):   
        logging.info ('extractTrainingData : Started : ' + str(cust_id))
        trainlog = get_model()
        traindata = getTrainingModel() 

        next_page_token = 0
        token = None        
        while next_page_token != None:             
            ticket_logs, next_page_token = trainlog.list('tickets', cursor=token, cust_id=cust_id, done=True)
            token = next_page_token
            for ticket_log in ticket_logs: 
                tickets_data = ticket_log["json_data"] 
                tickets_data_json = json.loads(tickets_data)
                for ticket_data in tickets_data_json['upload_ticket_data']: 
                    comments = ''
                    for comment_data in tickets_data_json['upload_comment_data']:
                        if (comment_data['id'] == ticket_data['id']):
                            try:
                                comments = comment_data['comments'][1]['plain_body']
                            except IndexError as err: 
                                logging.debug('')
                    comments = cleanhtml (comments)
                    description = ticket_data['description']
                    subject = ticket_data['subject'] 
                    id =  ticket_data['id']                  
                    tags = ', '.join(ticket_data['tags']) 
                    traindata.create(tags, str(str(subject) + ' . ' + str(description)), comments, done=False, id=id, cust_id=cust_id)
                    trainlog.delete(ticket_log['id'], cust_id=cust_id)
                    print('Creating for Tickets : ' , id, cust_id)
        logging.info ('extractTrainingData : Completed :' + cust_id)
        
    def applyPrediction_trainingdata(self, cust_id):
        logging.info ('applyPrediction : Started : ' + str(cust_id))
        trainlog = get_model()
        traindata = getTrainingModel() 

        next_page_token = 0
        token = None 
        from agentapp.IntentExtractor import IntentExtractor
        intenteng = IntentExtractor()
        while next_page_token != None:             
            training_logs, next_page_token = getTrainingModel().list(cursor=token, cust_id=cust_id, feedback_flag=False, done=False)
            token = next_page_token
            for training_log in training_logs: 
                predicted = intenteng.getPredictedIntent(str(training_log['query'] + ' . ' + training_log['tags']) , cust_id)  
                if len(predicted) < 1: 
                    predicted = ['Default']
                traindata.update(training_log['tags'], training_log['query'], training_log['response'], query_category=training_log['query_category'], 
                    done=True, id = training_log['id'], resp_category=predicted[0], cust_id=cust_id)
                print ('processing training data :', training_log['id'])
        logging.info ('applyPrediction : Completed : ' + cust_id)

    def applyPrediction_responsedata(self, cust_id):
        logging.info ('applyPrediction_response : Started : ' + str(cust_id))
        trainlog = get_model()
        traindata = getTrainingModel() 

        next_page_token = 0
        token = None 
        from agentapp.IntentExtractor_resp import IntentExtractor_resp
        intenteng = IntentExtractor_resp()
        intenteng.prepareTrainingData(cust_id)
        intenteng.startTrainingProcess(cust_id)
   
        while next_page_token != None:             
            training_logs, next_page_token = traindata.list(cursor=token, feedback_flag=False, cust_id=cust_id)
            token = next_page_token
            for training_log in training_logs: 
                predicted = intenteng.getPredictedIntent(str(training_log['query'] + ' . ' + training_log['tags']) , cust_id)  
                if len(predicted) < 1: 
                    predicted = ['Default']
                traindata.update(training_log['tags'], training_log['query'], training_log['response'], query_category=training_log['query_category'], 
                    done=True, id = training_log['id'], resp_category=predicted[0], cust_id=cust_id)
                print ('processing training data :', training_log['id'])
        logging.info ('applyPrediction_response : Completed : ' + str(cust_id))

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext
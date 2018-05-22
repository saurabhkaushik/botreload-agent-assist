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

class TrainingDataAnalyzer(object):

    def __init__(self):
        self.client = datastore.Client()
        self.storage_client = storage.Client()
    # [END build_service]
    
    def copyOldTrainingLog(self):
        logging.info ('copyOldTrainingLog : ')
        traindb = get_model()
        next_page_token = 0
        token = None
        while next_page_token != None:
            ticket_logs, next_page_token = traindb.list('tickets', cursor=token, cust_id='')
            token = next_page_token
            for ticket_log in ticket_logs:
                traindb.create(ticket_log['type'], ticket_log['json_data'], created=ticket_log['created'], done=True, cust_id='default')
                print ('Copying : ' , ticket_log['id'])

    def extractTicketData_default(self, src_cust_id='default'):   
        logging.info ('extractTicketData_default : ')
        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        from agentapp.IntentExtractor import IntentExtractor
        intenteng = IntentExtractor()
        traindata = get_model()
        #print(cust_list, next_page_token)
        while next_page_token != None:             
            ticket_logs, next_page_token = traindata.list('tickets', cursor=token, cust_id=src_cust_id, done=True)
            token = next_page_token
            #print (ticket_logs) 
            for ticket_log in ticket_logs: 
                tickets_data = ticket_log["json_data"] 
                tickets_data_json = json.loads(tickets_data)
                #print(tickets_data_json)
                for ticket_data in tickets_data_json['tickets']: 
                    description = ticket_data['description']
                    subject = ticket_data['subject']
                    tags = ', '.join(ticket_data['tags']) 
                    url = ticket_data['url']             
                    #print (url)
                    for cust_id_x in cust_list:
                        if cust_id_x['cust_name'] in url:
                            #print (url + ' has ' + cust_id_x['cust_name'])
                            getTrainingModel().create(tags, str(subject + ' . ' + description), '', done=False, cust_id=cust_id_x['cust_name'])
                            print('Creating for Ticket Id : ' , ticket_data['id'])
        # Deleting processed Ticket data from default
        ticket_logs, next_page_token = traindata.list('tickets', cust_id=src_cust_id, done=True)
        for ticket_log in ticket_logs: 
            traindata.delete(ticket_log['id'], cust_id=src_cust_id)
    
    def extractTicketData_cust(self, cust_id):   
        logging.info ('extractTicketData_cust : ')
        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        from agentapp.IntentExtractor import IntentExtractor
        intenteng = IntentExtractor()
        traindata = get_model()
        #print(cust_list, next_page_token)
        while next_page_token != None:             
            ticket_logs, next_page_token = traindata.list('tickets', cursor=token, cust_id=cust_id, done=True)
            token = next_page_token
            #print (ticket_logs) 
            for ticket_log in ticket_logs: 
                tickets_data = ticket_log["json_data"] 
                tickets_data_json = json.loads(tickets_data)
                #print(tickets_data_json)
                for ticket_data in tickets_data_json['tickets']: 
                    description = ticket_data['description']
                    subject = ticket_data['subject']
                    tags = ', '.join(ticket_data['tags']) 
                    url = ticket_data['url']             
                    getTrainingModel().create(tags, str(subject + ' . ' + description), '', done=False, cust_id=cust_id)
                    print('Creating for Ticket Id : ' , ticket_data['id'])
        # Deleting processed Ticket data from default
        ticket_logs, next_page_token = traindata.list('tickets', cust_id=cust_id, done=True)
        for ticket_log in ticket_logs: 
            traindata.delete(ticket_log['id'], cust_id=cust_id)

    def extractIntentData_default(self, src_cust_id='default'):   
        logging.info ('extractIntentData_default : ')
        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        from agentapp.IntentExtractor import IntentExtractor
        intenteng = IntentExtractor()
        traindata = get_model()
        #print(cust_list, next_page_token)
        while next_page_token != None:             
            intent_logs, next_page_token = traindata.list('intent', cursor=token, cust_id=src_cust_id, done=True)
            token = next_page_token
            #print (ticket_logs) 
            for intent_log in intent_logs: 
                intents_data = intent_log["json_data"] 
                intents_data_json = json.loads(intents_data)
                #print(intents_data_json)
                description = intents_data_json['description']
                subject = intents_data_json['subject']
                tags = ', '.join(intents_data_json['requester']['tags']) 
                cust_id = intents_data_json['currentAccount']['subdomain'] 
                response = intents_data_json['comments'][0]['value']
                getTrainingModel().create(tags, str(subject + ' . ' + description), response, done=False, cust_id=cust_id)
                print('Creating for Ticket Id : ' , intents_data_json['id'])
        # Deleting processed Ticket data from default
        ticket_logs, next_page_token = traindata.list('intent', cust_id=src_cust_id, done=True)
        for ticket_log in ticket_logs: 
            traindata.delete(ticket_log['id'], cust_id=src_cust_id)
    
    def extractIntentData_cust(self, cust_id):   
        logging.info ('extractIntentData_cust : ')
        next_page_token = 0
        token = None        
        cust_list, next_page_token2 = getCustomerModel().list(done=True)
        from agentapp.IntentExtractor import IntentExtractor
        intenteng = IntentExtractor()
        traindata = get_model()
        #print(cust_list, next_page_token)
        while next_page_token != None:             
            intent_logs, next_page_token = traindata.list('intent', cursor=token, cust_id=cust_id, done=True)
            token = next_page_token
            #print (ticket_logs) 
            for intent_log in intent_logs: 
                intents_data = intent_log["json_data"] 
                intents_data_json = json.loads(intents_data)
                description = intents_data_json['description']
                subject = intents_data_json['subject']
                tags = ', '.join(intents_data_json['requester']['tags']) 
                response = intents_data_json['currentAccount']['subdomain']              
                getTrainingModel().create(tags, str(subject + ' . ' + description), response, done=False, cust_id=cust_id)
                print('Creating for Ticket Id : ' , intents_data_json['id'])
        # Deleting processed Ticket data from default
        ticket_logs, next_page_token = traindata.list('tickets', cust_id=cust_id, done=True)
        for ticket_log in ticket_logs: 
            traindata.delete(ticket_log['id'], cust_id=cust_id)    
    
    def extractTicketData_new(self, cust_id):   
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
                    getTrainingModel().create(tags, str(subject + ' . ' + description), comments, done=False, resp_category=predicted[0], cust_id=cust_id)
        ticket_logs, next_page_token = get_model().list('tickets', cust_id=cust_id, done=True)
        for ticket_log in ticket_logs: 
            get_model().delete(ticket_log['id'], cust_id=cust_id) 

    def applyPrediction(self, cust_id):
        next_page_token = 0
        token = None 
        from agentapp.IntentExtractor import IntentExtractor
        intenteng = IntentExtractor()
        while next_page_token != None:             
            training_logs, next_page_token = getTrainingModel().list_all(cursor=token, cust_id=cust_id, done=False)
            token = next_page_token
            for training_log in training_logs: 
                predicted = intenteng.getPredictedIntent(str(training_log['query'] + ' . ' + training_log['tags']) , cust_id)  
                if len(predicted) < 1: 
                    predicted = ['Default']
                getTrainingModel().update(training_log['tags'], training_log['query'], training_log['response'], query_category=training_log['query_category'], 
                    done=True, id = training_log['id'], resp_category=predicted[0], cust_id=cust_id)
                print ('processing training data :', training_log['id'])

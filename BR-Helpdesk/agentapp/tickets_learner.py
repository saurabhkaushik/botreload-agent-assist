import datetime
from agentapp.model_select import get_model, getTrainingModel, getResponseModel
import json
import logging 
import csv

TRAIN_SET_PATH = 'input/hd_training_data.csv'
CANNED_RESP_PATH = 'input/hd_canned_resp.csv'

# [START build_service]
from google.cloud import datastore

class tickets_learner(object):

    def __init__(self):
        self.client = datastore.Client()
    # [END build_service]
    
    def extract_save_data(self):   
        next_page_token = 0
        token = None
        while next_page_token != None:             
            ticket_logs, next_page_token = get_model().list('tickets', cursor=token)
            token = next_page_token
            for ticket_log in ticket_logs: 
                tickets_data = ticket_log["json_data"] 
                tickets_data_json = json.loads(tickets_data)
                for ticket_data in tickets_data_json['tickets']: 
                    description = ticket_data['description']
                    subject = ticket_data['subject']
                    tags = ticket_data['tags']
                    getTrainingModel().create(tags, description, subject, '', 'false', '')
    
    def getTrainingData(self):   
        ticket_data = []
        next_page_token = 0
        token = None
        while next_page_token != None:             
            ticket_logs, next_page_token = getTrainingModel().list_all(cursor=token)
            token = next_page_token
            ticket_data.append(ticket_logs)
        return ticket_data 
    
    def import_trainingdata(self): 
        with open(TRAIN_SET_PATH, 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
            
        for linestm in train_list:
            getTrainingModel().create(linestm[0], linestm[1], '', linestm[2], 'true')
            
    def import_responsedata(self): 
        with open(CANNED_RESP_PATH, 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
        rid = 100
        for linestm in train_list:
            getResponseModel().create(linestm[0], linestm[0], linestm[1], id=rid)
            rid += 1
            
    def get_response_mapping(self, response):
        ds_response = getResponseModel().list(response.strip())
        for resp in ds_response: 
            if (resp != None) and (len(resp) > 0) :
                return resp[0]
        return None
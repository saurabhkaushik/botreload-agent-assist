import datetime
from agentapp.model_select import get_model, getTrainingModel, getResponseModel
import json
import logging 
import csv
from flask import current_app
import pandas as pd

# [START build_service]
from google.cloud import datastore

class tickets_learner(object):

    def __init__(self):
        self.client = datastore.Client()
    # [END build_service]
    
    def extract_save_data(self):   
        logging.info ('extract_save_data : ')
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
        logging.info ('getTrainingData : ')
        ticket_data = []
        next_page_token = 0
        token = None
        while next_page_token != None:             
            ticket_logs, next_page_token = getTrainingModel().list_all(cursor=token)
            token = next_page_token
            ticket_data.append(ticket_logs)
        return ticket_data 
    
    def import_trainingdata(self): 
        logging.info ('import_trainingdata : ')
        with open(current_app.config['TRAIN_SET_PATH'], 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
        rid = 100
        while rid < 1000: 
            for linestm in train_list:
                getTrainingModel().create(linestm[0].strip(), linestm[1].strip(), '', linestm[2].strip(), 'true', id=rid)
                rid += 1
            
    def import_responsedata(self): 
        logging.info ('import_responsedata : ')
        with open(current_app.config['CANNED_RESP_PATH'], 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
        rid = 100
        for linestm in train_list:
            getResponseModel().create(linestm[0].strip(), linestm[0].strip(), linestm[1].strip(), id=rid)
            rid += 1
            
    def get_response_mapping(self, response):
        logging.info ('get_response_mapping : ')
        ds_response = getResponseModel().list()
        print ( 'ds_response : '+str(ds_response)) 
        
        for resp in ds_response: 
            if (resp != None) and (len(resp) > 0) :
                return resp[0]
        return None
    
    def format_output(self, predicted_intent): 
        logging.info ('format_output : ')
        comments_struct = []    
        with open(current_app.config['CANNED_RESP_PATH'], 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            resp_list = list(reader)
        resp_dict = {rows[0].strip() : rows[1] for rows in resp_list}
        y_predict_dic = sorted(predicted_intent.items(), key=lambda x: x[1], reverse=True)
        i = 0
        for ss in y_predict_dic:
            comments_struct.append({'id': list(resp_dict.keys()).index(ss[0].strip()), 'name' : ss[0], 'comment': resp_dict.get(ss[0].strip(), ''), 'prob': int(ss[1]*100)})
            if (i >= 4):
                break
            i+=1
        return comments_struct
    
    def format_output_ds(self, predicted_intent): 
        logging.info ('format_output_ds : ')
        tickets_learn = tickets_learner()
        comments_struct = []  
        df_intent = pd.DataFrame(list(predicted_intent.items()), columns=['Resp_Class', 'Resp_Prob'])
        df_intent = df_intent.sort_values(['Resp_Prob'], ascending=[False])
        df_intent['Comment'] = 'NA'
        ds_response = getResponseModel().list() 
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
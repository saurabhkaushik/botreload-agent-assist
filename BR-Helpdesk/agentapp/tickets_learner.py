from agentapp.model_select import get_model, getTrainingModel, getResponseModel, getCustomerModel
import json
import logging 
import csv
import datetime
from flask import current_app
import pandas as pd

class tickets_learner(object):
    
    def getTrainingData(self, cust_id, done=True):   
        logging.info ('getTrainingData : '  + str(cust_id))
        ticket_data = []
        next_page_token = 0
        token = None
        while next_page_token != None:             
            ticket_logs, next_page_token = getTrainingModel().list(cursor=token, cust_id=cust_id, done=done)
            token = next_page_token
            ticket_data.append(ticket_logs)
        return ticket_data 
    
    def getResponseData(self, cust_id, modifiedflag=None, defaultflag=None):   
        logging.info ('getResponseData : ' + str(cust_id))
        resp_data = []
        next_page_token = 0
        token = None
        while next_page_token != None:             
            resp_logs, next_page_token = getResponseModel().list(cursor=token, modifiedflag=modifiedflag, defaultflag=defaultflag, cust_id=cust_id, done=True)
            token = next_page_token
            resp_data.append(resp_logs)
        return resp_data 

    def getTrainingLog(self, cust_id, log_type, done=True):   
        logging.info ('getTrainingLog : '  + str(cust_id))
        trainlog = get_model()
        ticket_data = []
        next_page_token = 0
        token = None
        while next_page_token != None:             
            ticket_logs, next_page_token = trainlog.list(cursor=token, log_type=log_type, cust_id=cust_id, done=True)
            token = next_page_token
            ticket_data.append(ticket_logs)
        return ticket_data 
    
    def getTrainingData_DataFrame(self, cust_id):
        logging.info("prepareTrainingData : Started : " + str(cust_id))
        tickets_learn = tickets_learner()
        ticket_data = tickets_learn.getTrainingData(cust_id=cust_id, done=None)
    
        ticket_struct = []
        for linestms in ticket_data:           
            for linestm in linestms:                
                ticket_struct.append({'id' : linestm['id'], 'query' : linestm['query'], 'query_category' : linestm['query_category'], 
                'feedback_flag' : linestm['feedback_flag'], 'feedback_prob' : linestm['feedback_prob'], 'done' : True,
                'response': linestm['response'].strip(), 'tags' : linestm['tags']})
        ticket_pd = pd.DataFrame(ticket_struct)

        logging.info ("Total Training Examples : %s" % len(ticket_pd))
        logging.info("prepareTrainingData : Completed : " + str(cust_id))
        return ticket_pd
    
    def import_customerdata(self): 
        logging.info ('import_customerdata : Started ')
        with open(current_app.config['CUST_SET_PATH'], 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
        rid = 100
        for linestm in train_list:
            getCustomerModel().create(linestm[0].strip().lower(), language=linestm[1].strip().lower(), done=True, id=rid)
            rid += 1
        logging.info ('import_customerdata : Completed' )

    def import_trainingdata(self, cust_id, lang_type): 
        logging.info ('import_trainingdata : Started ' + str(cust_id))
        with open(current_app.config['TRAIN_SET_PATH'] + '-' +lang_type + '.csv', 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
        rid = 100
        #while rid < 200: 
        traindata_struct = []
        for linestm in train_list:
            traindata_struct.append({'id' : rid, 'query' : linestm[0].strip(), 'query_category' : '', 
                    'feedback_flag' : False, 'feedback_prob' : 100, 'done' : True, 'response': linestm[1].strip(), 
                    'resp_category': linestm[2].strip(), 'tags' : ''})
            #getTrainingModel().create(linestm[0].strip(), linestm[1].strip(), '', resp_category=linestm[2].strip(), done=True, id=rid, cust_id=cust_id)
            rid += 1
        traindata_pd = pd.DataFrame(traindata_struct)
        getTrainingModel().batchUpdate(traindata_pd, cust_id)
        logging.info ('import_trainingdata : Completed '  + str(cust_id))
    
    def import_responsedata(self, cust_id, lang_type): 
        logging.info ('import_responsedata : Started ' + str(cust_id))
        with open(current_app.config['CANNED_RESP_PATH'] + '-' +lang_type + '.csv', 'r', encoding='windows-1252') as f:
            reader = csv.reader(f)
            train_list = list(reader)
        rid = 100
        respdata_struct = []
        for linestm in train_list:
            respdata_struct.append({'id' : rid, 'resp_name': linestm[0].strip(),
                    'res_category': linestm[0].strip(),
                    'response_text' : linestm[1].strip(),
                    'tags' : linestm[2].strip(),
                    'modifiedflag': False,
                    'defaultflag' : True,
                    'resp_tags' : linestm[2].strip(),
                    'created': datetime.datetime.utcnow(),
                    'done': True})            
            #getResponseModel().create(linestm[0].strip(), linestm[0].strip(), linestm[1].strip(), linestm[2].strip(), linestm[2].strip(), defaultflag=True, done=True, id=rid, cust_id=cust_id)
            rid += 1
        respdata_pd = pd.DataFrame(respdata_struct)
        getResponseModel().batchUpdate(respdata_pd, cust_id)
        logging.info ('import_responsedata : Completed ' + str(cust_id))
            
    def get_response_mapping(self, response, cust_id):
        logging.info ('get_response_mapping : ' + str(cust_id) + ' : ' + response)
        ds_response = getResponseModel().list(res_category=response, cust_id=cust_id, done=True)
        for resp in ds_response: 
            if (resp != None) and (len(resp) > 0) :
                return resp[0]
        return None
    
    def get_response_mapping_tags(self, response, cust_id, tags):
        logging.info ('get_response_mapping_tags : ' + str(cust_id))
        ds_response = getResponseModel().list(res_category=response, cust_id=cust_id, done=True)
        for resp in ds_response: 
            if (resp != None) and (len(resp) > 0) :
                return resp[0][tags]
        return ''

    def get_response_map(self, cust_id, tags):
        logging.info ('get_response_map : ' + str(cust_id))
        ds_response = getResponseModel().list(cust_id=cust_id, done=True)
        resp_map = {}
        for resp_list in ds_response: 
            if (resp_list != None) and (len(resp_list) > 0) :
                for resp in resp_list:
                    resp_map[resp['res_category']] = resp[tags]              
        return resp_map
    
    def formatOutput(self, predicted_intent, cust_id): 
        logging.info ('formatOutput : ' + str(cust_id))
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
                        if resp_item['res_category'] == row['Resp_Class']: 
                            comments_struct.append({'id': resp_item['id'], 'name' : resp_item['resp_name'], 'comment': resp_item['response_text'], 'prob': int(row['Resp_Prob']*100)}) 
            if (i >= 4):
                break
            i+=1        
        return comments_struct  


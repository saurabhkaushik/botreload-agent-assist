from src.EntityExtractor import EntityExtractor
from src.IntentExtractor import IntentExtractor
from src.dsConnector import dsConnector
    
from flask import Flask, jsonify
from flask import request
from flask import make_response
from flask import abort
from flask import url_for
import csv
import json
import time
import os
import logging 

app = Flask(__name__) 

entityeng = EntityExtractor()
intenteng = IntentExtractor()
dsConnect = dsConnector()

intenteng.prepareTrainingData()
intenteng.startTrainingProcess()

CANNED_RESP_PATH = 'input/hd_canned_resp.csv'

def format_output(predicted_intent): 
    comments_struct = []    
    with open(CANNED_RESP_PATH, 'r', encoding='windows-1252') as f:
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

@app.route('/intent', methods=['POST'])
def intent():
    logging.info('intent : ')
    dsConnect.add_logs('intent', str(request.json))
 
    received_data = request.json
    intent_input = received_data['description'] + '. ' + received_data['comment'] + '. ' + received_data['subject']
    predicted_intent = intenteng.getIntentForText(intent_input)
    formatted_resp =  format_output(predicted_intent)
    json_resp = json.dumps(formatted_resp)
    
    logging.info('response : ' )
    dsConnect.add_logs('response', str(json_resp))
    return json_resp

@app.route('/entity', methods=['POST'])
def entity():
    Received = request.json
    Email_Content = ""
    if 'query' in Received:
        Email_Content = Received['query']
    #email_input = 'Subject: Customer Payment. Customer Payment 76543 for Horus Financials to be applied.'
    predicted_entity = entityeng.POS_Tagging(Email_Content)
    
    resp = {}
    resp["Entity_values"] = predicted_entity
    json_resp = json.dumps(resp)
    return json_resp

@app.route('/uploadtickets', methods=['POST'])
def uploadtickets():
    logging.info('tickets : ')
    dsConnect.add_logs('tickets', str(request.json))
    return '200' 

@app.route('/feedbkloop', methods=['POST'])
def uploadfeedback():
    logging.info('feedback : ')
    dsConnect.add_logs('feedback', str(request.json))
    return '200'  

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    #app.run(threaded=True)
    #app.run('0.0.0.0', port=80, threaded=True)
        

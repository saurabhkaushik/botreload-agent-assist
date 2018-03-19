from src.EntityExtractor import EntityExtractor
from src.IntentExtractor import IntentExtractor
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

logger = logging.getLogger('br-srv-app')
hdlr = logging.FileHandler('log/br-app-day.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO) 

loggertrain = logging.getLogger('br-srv-train')
hdlr = logging.FileHandler('log/br-app-train.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
loggertrain.addHandler(hdlr) 
loggertrain.setLevel(logging.INFO) 

entityeng = EntityExtractor() 
intenteng = IntentExtractor()

intenteng.prepareTrainingData()
intenteng.startTrainingProcess()

CANNED_RESP_PATH = 'input/hd_canned_resp.csv'
#TICKET_FILE = 'log/ticket_'
#FEEDBACK_FILE = 'log/feedback.csv'

def format_output(predicted_intent): 
    comments_struct = []    
    with open(CANNED_RESP_PATH, 'r', encoding='windows-1252') as f:
        reader = csv.reader(f)
        resp_list = list(reader)
    resp_dict = {rows[0].strip() : rows[1] for rows in resp_list}
    y_predict_dic = sorted(predicted_intent.items(), key=lambda x: x[1], reverse=True)
    i = 0
    for ss in y_predict_dic:
        comments_struct.append({'id': i, 'name' : ss[0], 'comment': resp_dict.get(ss[0].strip(), ''), 'prob': int(ss[1]*100)})
        if (i >= 4):
            break
        i+=1
    loggertrain.info('format_output : ' + str(comments_struct))
    return comments_struct

@app.route('/intent', methods=['POST'])
def intent():
    loggertrain.info('intent : ' + str(request.json))
    received_data = request.json
    intent_input = received_data['description'] + '. ' + received_data['comment'] + '. ' + received_data['subject']
    predicted_intent = intenteng.getIntentForText(intent_input)
    formatted_resp =  format_output(predicted_intent)
    logger.info ('Output :' + str(formatted_resp))
    json_resp = json.dumps(formatted_resp)
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
    loggertrain.info('uploadtickets : ' + str(request.json))
    '''received_data = request.json
    with open(TICKET_FILE + str(time.time()) + '.csv', 'w') as outfile:
        json.dump(received_data, outfile)
    json_resp = json.dumps(received_data)'''
    return '200' 

@app.route('/feedbkloop', methods=['POST'])
def uploadfeedback():
    loggertrain.info('uploadfeedback : ' + str(request.json))
    '''received_data = request.json
    if os.path.exists(FEEDBACK_FILE):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    with open(FEEDBACK_FILE, append_write) as outfile:
        json.dump(received_data, outfile)'''
    #json_resp = json.dumps(received_data)
    return '200'  

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    #app.run(threaded=True)
    #app.run('0.0.0.0', port=80, threaded=True)
        

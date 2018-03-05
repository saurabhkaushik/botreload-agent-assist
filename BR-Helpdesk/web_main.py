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

app = Flask(__name__)  

entityeng = EntityExtractor() 
intenteng = IntentExtractor()

intenteng.prepareTrainingData()
intenteng.startTrainingProcess()

CANNED_RESP_PATH = 'input/hd_canned_resp.csv'
TICKET_FILE = 'log/ticket_'
TAG_FILE = 'log/tag_'

def format_output(predicted_intent): 
    comments_struct = []    
    with open(CANNED_RESP_PATH, 'r') as f:
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
    return comments_struct

@app.route('/intent', methods=['POST'])
def intent():
    print('Request : ', request.json)
    received_data = request.json
    predicted_intent = intenteng.getIntentForText(received_data)
    formatted_resp =  format_output(predicted_intent)
    print ('Output :', formatted_resp)
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
    print('Request : ', request.json)
    received_data = request.json
    with open(TICKET_FILE + str(time.time()) + '.csv', 'w') as outfile:
        json.dump(received_data, outfile)
    #json_resp = json.dumps(received_data)
    return None 

@app.route('/uploadtags', methods=['POST'])
def uploadtags():
    print('Request : ', request.json)
    received_data = request.json
    with open(TAG_FILE  + str(time.time()) + '.csv', 'w') as outfile:
        json.dump(received_data, outfile)
    #json_resp = json.dumps(received_data)
    return None 

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    #app.run(threaded=True)
    app.run('0.0.0.0', port=80, threaded=True)
        

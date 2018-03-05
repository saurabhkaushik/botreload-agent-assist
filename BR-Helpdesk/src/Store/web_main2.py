from src.EntityExtractor import EntityExtractor
from src.IntentExtractor import IntentExtractor
from flask import Flask, jsonify
from flask import request
from flask import make_response
from flask import abort
from flask import url_for
import csv
import json

app = Flask(__name__)  

entityeng = EntityExtractor() 
intenteng = IntentExtractor()

intenteng.prepareTrainingData()
intenteng.startTrainingProcess()

CANNED_RESP_PATH = 'input/hd_canned_resp.csv'

def format_output(predicted_intent): 
    y_predict_dic = sorted(predicted_intent.items(), key=lambda x: x[1], reverse=True)
    comments_struct = []
    i = 0
    for s in y_predict_dic:
        comments_struct.append({'id': i, 'comment': s[0], 'prob': s[1]})
        i+=1
    return comments_struct

def map_response(predicted_intent):
    with open(CANNED_RESP_PATH, 'r') as f:
        reader = csv.reader(f)
        resp_list = list(reader)
    resp_dict = {rows[0].strip() : rows[1] for rows in resp_list}
    new_pred_dict = dict((resp_dict.get(key.strip(), ''), value) for key, value in predicted_intent.items())
    print ('Old Dict: ', predicted_intent)
    print ('New Dict: ', new_pred_dict)
    return new_pred_dict

@app.route('/intent', methods=['POST'])
def intent():
    print('Request : ', request.json)
    received_data = request.json
    print("received_data : ", received_data)
    '''query_data = received_data['query_data']
    if 'query_data' in received_data:
        query_data = received_data['query_data']'''
    predicted_intent = intenteng.getIntentForText(received_data)
    predicted_intent = map_response(predicted_intent)
    formatted_resp =  format_output(predicted_intent)
    #resp_out = format_output(formatted_resp)
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

    json_resp = json.dumps(received_data)
    return json_resp

@app.route('/uploadtags', methods=['POST'])
def uploadtags():
    print('Request : ', request.json)
    received_data = request.json

    json_resp = json.dumps(received_data)
    return json_resp

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    #app.run(threaded=True)
    app.run('0.0.0.0', port=80, threaded=True)
        

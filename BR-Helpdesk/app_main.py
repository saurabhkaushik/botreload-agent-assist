from src.EntityExtractor import EntityExtractor
from src.IntentExtractor import IntentExtractor
from flask import Flask, jsonify
from flask import request
from flask import make_response
from flask import abort
from flask import url_for
import csv

import json 

import logging 

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

CANNED_RESP_PATH = 'input/hd_canned_resp.csv'

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

intenteng = IntentExtractor()

intenteng.prepareTrainingData()
intenteng.startTrainingProcess()
predicted_intent = intenteng.getIntentForText("Thanks for getting in touch for more info on our product. ")
formatted_resp =  format_output(predicted_intent)
print ("format_output : ", formatted_resp)

#intenteng.prepareTestingData()
#intenteng.startTestingProcess()
#intenteng.createConfusionMatrix()
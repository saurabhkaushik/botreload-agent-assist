from agentapp.EntityExtractor import EntityExtractor
from agentapp.IntentExtractor import IntentExtractor
from agentapp.tickets_learner import tickets_learner
from agentapp.model_select import get_model, getTrainingModel

from flask import current_app, redirect
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

CANNED_RESP_PATH = 'input/hd_canned_resp.csv'
entityeng = EntityExtractor()
intenteng = IntentExtractor()

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logging.basicConfig(level=logging.INFO)

    # Setup the data model.
    with app.app_context():
        model = get_model()
        model.init_app(app)
        ticketLearner = tickets_learner()
        ticketLearner.import_trainingdata()
        ticketLearner.import_responsedata()
        intenteng.prepareTrainingData_ds()
        intenteng.startTrainingProcess()

    # Register the Bookshelf CRUD blueprint.
    from .crud import crud
    app.register_blueprint(crud, url_prefix='/books')
    
    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('crud.list'))
    
    @app.route('/intent', methods=['POST'])
    def intent():
        logging.info('intent : ')
        get_model().create('intent', json.dumps(request.json))
        
        received_data = request.json
        intent_input = received_data['description'] + '. ' + received_data['comment'] + '. ' + received_data['subject']
        predicted_intent = intenteng.getIntentForText(intent_input)
        formatted_resp =  format_output_ds(predicted_intent)
        print ('formatted_resp: ', formatted_resp)
        json_resp = json.dumps(formatted_resp)
        get_model().create('response', json_resp)
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
        get_model().create('tickets', json.dumps(request.json))
        return '200' 
    
    @app.route('/feedbkloop', methods=['POST'])
    def uploadfeedback():
        logging.info('feedback : ')
        get_model().create('feedback', json.dumps(request.json))
        return '200'  
    
    @app.route('/importdata', methods=['GET'])
    def startDataImport():
        logging.info('startDataImport : ')
        ticketLearner = tickets_learner() 
        ticketLearner.import_trainingdata()  
        ticketLearner.import_responsedata() 
        return '200'  
    
    @app.route('/preparedata', methods=['GET'])
    def prepareTrainingData():
        logging.info('prepareTrainingData : ')
        ticketLearner = tickets_learner() 
        ticketLearner.extract_save_data() 
        return '200'  
    
    @app.route('/training', methods=['GET'])
    def doFunctionTesting():
        logging.info('doFunctionTesting : ')
        intenteng2 = IntentExtractor()
        intenteng2.prepareTrainingData_ds()
        intenteng2.startTrainingProcess()
        predictedint = intenteng2.getIntentForText('I have received this defective product. It has been malfunctioning from day one. Kindly replace it asap.')
        print(predictedint)
        #ticketLearner = tickets_learner()
        #ticketLearner.get_response_mapping('Software_Sales_Billing')
        return '200'
    
    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    @app.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    return app

def startModel():
    print ('--- Initializing Models and Training Process ----- ')
    ticketLearner = tickets_learner() 
    ticketLearner.import_trainingdata()  
    ticketLearner.import_responsedata()
    intenteng.prepareTrainingData_ds()
    intenteng.startTrainingProcess()

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

def format_output_ds(predicted_intent): 
    tickets_learn = tickets_learner()
    comments_struct = []    
    y_predict_dic = sorted(predicted_intent.items(), key=lambda x: x[1], reverse=True)
    i = 0
    for ss in y_predict_dic:
        response_data = tickets_learn.get_response_mapping(ss[0].strip())
        if response_data != None: 
            comments_struct.append({'id': response_data['id'], 'name' : response_data['resp_name'], 'comment': response_data['response_text'], 'prob': int(ss[1]*100)})
        if (i >= 4):
            break
        i+=1
    return comments_struct
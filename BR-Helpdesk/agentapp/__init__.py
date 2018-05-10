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

import re
import csv
import json
import time
import os
import logging 

#entityeng = EntityExtractor()
intenteng = IntentExtractor()
ticketLearner = tickets_learner()
cust_id = ''
cust_list = []

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
        #ticketLearner.import_trainingdata(cust_id)
        #ticketLearner.import_responsedata(cust_id)
        #intenteng.prepareTrainingData_ds(cust_id) 
        #intenteng.startTrainingProcess(cust_id)
        #intenteng.prepareTestingData(cust_id)
        #intenteng.startTestingProcess(cust_id)
        #intenteng.createConfusionMatrix(cust_id)
        cust_list = current_app.config['CUSTOMER_LIST']
        ticketLearner.create_bucket()
        
    logging.info('Current Customers : '+ str(cust_list))

    # Register the Bookshelf CRUD blueprint.
    from .crud import crud
    app.register_blueprint(crud, url_prefix='/smartreply')
    
    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('crud.login'))
    
    @app.route('/intent', methods=['POST'])
    def intent():
        logging.info('intent : ') 
        intent_input = ''
        
        received_data = request.json
        t_cust_id = ''
        try: 
            t_cust_id = received_data['currentAccount']['subdomain']
        except KeyError as err:
            logging.error(err)
        cust_id = get_validcust(t_cust_id) 
        logging.info('Customer Id : ' + str(cust_id))
        
        get_model().create('intent', json.dumps(request.json), done=True, cust_id=cust_id)
        if (received_data['requester']['email'] == received_data['comments'][0]['author']['email']):
            intent_input = cleanhtml(received_data['comments'][0]['value'])
        else:
            intent_input = cleanhtml(received_data['description'] + '. ' + received_data['subject'])
            
        #intent_input = received_data['description'] + '. ' + received_data['comments'] + '. ' + received_data['subject']
        predicted_intent = intenteng.getIntentForText(intent_input, cust_id) 
        formatted_resp = ticketLearner.formatOutput(predicted_intent, cust_id) 
        logging.info('\'' + str(intent_input) + '\' >> ' + str(formatted_resp))
        json_resp = json.dumps(formatted_resp)
        get_model().create('response', json_resp, done=True, cust_id=cust_id)
        return json_resp

    @app.route('/entity', methods=['POST'])
    def entity():
        Received = request.json
        Email_Content = ""
        if 'query' in Received:
            Email_Content = Received['query']
        predicted_entity = entityeng.POS_Tagging(Email_Content)
        
        resp = {}
        resp["Entity_values"] = predicted_entity
        json_resp = json.dumps(resp)
        return json_resp

    @app.route('/uploadtickets', methods=['POST'])
    def uploadtickets():
        logging.info('tickets : ')
        
        received_data = request.json
        t_cust_id = '' 
        try: 
            t_cust_id = received_data['currentAccount']['subdomain']
        except KeyError as err:
            logging.error(err)
        cust_id = get_validcust(t_cust_id) 
        logging.info('Customer Id : ' + str(cust_id))
        
        get_model().create('tickets', json.dumps(request.json), done=True, cust_id=get_validcust(cust_id))
        return '200' 
    
    @app.route('/uploadfeedback', methods=['POST'])
    def uploadfeedback():
        logging.info('feedback : ')
        
        received_data = request.json
        t_cust_id = ''
        try: 
            t_cust_id = received_data['ticket_data']['currentAccount']['subdomain']
        except KeyError as err:
            logging.info(err)
        cust_id = get_validcust(t_cust_id) 
        logging.info('Customer Id : ' + str(cust_id))
        
        get_model().create('feedback', json.dumps(request.json), done=True, cust_id=get_validcust(cust_id))
        return '200'  
    
    @app.route('/importdata', methods=['GET'])
    def startDataImport():
        logging.info('startDataImport : ')
        for cust_id_x in cust_list:
            ticketLearner.import_trainingdata(cust_id_x)  
            ticketLearner.import_responsedata(cust_id_x) 
        return '200'  
    
    @app.route('/starttraining', methods=['GET'])
    def startTrainingModels():
        logging.info('startTrainingModels : ')
        for cust_id_x in cust_list:
            intenteng.prepareTrainingData(cust_id_x) 
            intenteng.startTrainingProcess(cust_id_x)
        return '200'  
    
    @app.route('/preparedata', methods=['GET'])
    def prepareTrainingData():
        logging.info('prepareTrainingData : ')
        for cust_id_x in cust_list:
            ticketLearner.extractTrainingData(cust_id_x)
        ticket_logs, next_page_token = get_model().list('tickets', cust_id='', done=True)
        #token = next_page_token        
        for ticket_log in ticket_logs: 
            get_model().delete(ticket_log['id'], cust_id=cust_id) 
        return '200'  
    
    @app.route('/testingservice', methods=['GET'])
    def startTestingModels():
        for cust_id_x in cust_list:
            intenteng.prepareTestingData(cust_id_x)
            intenteng.startTestingProcess(cust_id_x)
            intenteng.createConfusionMatrix(cust_id_x)
        logging.info('doFunctionTesting : ')
        return '200'

    @app.route('/addcustomer', methods=['GET'])
    def addcustomer():
        logging.info('addcustomer : ')
        cust_id = request.args.get('cust_id')
        
        if cust_id == None or cust_id == '': 
            logging.info('Could not create customer' + cust_id)
            return '200'
        ticketLearner.import_trainingdata(cust_id)  
        ticketLearner.import_responsedata(cust_id) 
        intenteng.prepareTrainingData(cust_id) 
        intenteng.startTrainingProcess(cust_id)
        logging.info('Created new Customer : ' + cust_id)
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

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def authenticate_cust(cust_id_x): 
    t_cust_id = None
    cust_list = current_app.config['CUSTOMER_LIST']
    cust_id_x = cust_id_x.strip()
    if cust_id_x != None and cust_id_x != '':
        for x in cust_list:
            if x.lower() == cust_id_x.lower():
                t_cust_id = x                 
    return t_cust_id

def get_validcust(cust_id_x): 
    t_cust_id = ''
    cust_list = current_app.config['CUSTOMER_LIST']
    cust_id_x = cust_id_x.strip()
    if cust_id_x != None:
        for x in cust_list:
            if x.lower() == cust_id_x.lower():
                t_cust_id = x                 
    return t_cust_id
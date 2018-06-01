from agentapp.EntityExtractor import EntityExtractor
from agentapp.IntentExtractor import IntentExtractor
from agentapp.tickets_learner import tickets_learner
from agentapp.SmartRepliesSelector import SmartRepliesSelector
from agentapp.model_select import get_model, getTrainingModel, getCustomerModel
from agentapp.TrainingDataAnalyzer import TrainingDataAnalyzer

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
data_analyzer = TrainingDataAnalyzer()

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
        ticketLearner.create_bucket()
        
    #logging.info('Current Customers : '+ str(cust_list))

    # Register the Bookshelf CRUD blueprint.
    from .crud import crud
    app.register_blueprint(crud, url_prefix='/smartreply')
    
    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('crud.login'))
    
    @app.route('/intent', methods=['POST'])
    def predictIntent():
        logging.info('predictIntent : ') 
        intent_input = ''
        cust_id = ''
        
        received_data = request.json        
        try: 
            cust_id = received_data['currentAccount']['subdomain']
        except KeyError as err:
            logging.error(err)
            cust_id = 'default'
        
        cust = getCustomerModel().authenticate(cust_id.strip().lower(), newflag=False)
        
        if cust == None:
            cust_id = 'default'
        else: 
            cust_id = cust['cust_name']

        logging.info('Customer Id : ' + str(cust_id))
        
        get_model().create('intent', json.dumps(request.json), done=True, cust_id=cust_id)
        len_comment = len(received_data['comments']) 
        if ((len_comment > 0) and (received_data['requester']['email'] == received_data['comments'][0]['author']['email'])):
            intent_input = cleanhtml(received_data['comments'][0]['value'])
        else:
            intent_input = cleanhtml(received_data['description'] + '. ' + received_data['subject'])
            
        predicted_intent = intenteng.getIntentForText(intent_input, cust_id) 
        formatted_resp = ticketLearner.formatOutput(predicted_intent, cust_id) 
        logging.info('\'' + str(intent_input) + '\' >> ' + str(formatted_resp))
        json_resp = json.dumps(formatted_resp)
        #get_model().create('response', json_resp, done=True, cust_id=cust_id)
        return json_resp

    @app.route('/entity', methods=['POST'])
    def extractEntity():
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
    def uploadTickets():
        logging.info('uploadTickets : ')
        cust_id = ''
        received_data = request.json
        #print (received_data)
        try: 
            cust_id = received_data['ticket_data']['currentAccount']['subdomain']
        except KeyError as err:
            logging.error(err)
            cust_id = 'default'
        
        cust = getCustomerModel().authenticate(cust_id.strip().lower(), newflag=False)
        if cust == None:
            cust_id = 'default'
        else: 
            cust_id = cust['cust_name']

        logging.info('Customer Id : ' + str(cust_id))
        
        get_model().create('tickets', json.dumps(request.json), done=True, cust_id=cust_id)
        return '200' 
    
    @app.route('/uploadfeedback', methods=['POST'])
    def uploadFeedback():
        logging.info('uploadFeedback : ')
        
        received_data = request.json
        cust_id = ''
        try: 
            cust_id = received_data['ticket_data']['currentAccount']['subdomain']                        
        except KeyError as err:
            logging.info(err)
            cust_id = 'default'
        
        cust = getCustomerModel().authenticate(cust_id.strip().lower(), newflag=False)
        if cust == None:
            cust_id = 'default'
        else: 
            cust_id = cust['cust_name']

        logging.info('Customer Id : ' + str(cust_id))
        
        get_model().create('feedback', json.dumps(request.json), done=True, cust_id=cust_id)
        return '200'  
    
    @app.route('/importdata', methods=['GET'])
    def startDataImport():
        logging.info('startDataImport : ')
        ticketLearner.import_customerdata()
        cust_list, next_page_token = getCustomerModel().list(done=True)
        #print (cust_list) 
        for cust_id_x in cust_list:
            ticketLearner.import_trainingdata(cust_id_x['cust_name'], cust_id_x['language'])  
            ticketLearner.import_responsedata(cust_id_x['cust_name'], cust_id_x['language'])         
        return '200'  
    
    @app.route('/starttraining', methods=['GET'])
    def startTrainingModels():
        logging.info('startTrainingModels : ')
        cust_list, next_page_token = getCustomerModel().list(done=True)
        for cust_id_x in cust_list:
            intenteng.prepareTrainingData(cust_id_x['cust_name']) 
            intenteng.startTrainingProcess(cust_id_x['cust_name'])
        return '200'  
    
    @app.route('/buildsmartreplies', methods=['GET'])
    def buildSmartReplies():
        logging.info('buildSmartReplies : ') 
        cust_list, next_page_token = getCustomerModel().list(done=True)
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                replyeng = SmartRepliesSelector()
                replyeng.prepareTrainingData(cust_id_x['cust_name'])
                replyeng.generateNewResponse(cust_id_x['cust_name'])
                replyeng.populateResponseData(cust_id_x['cust_name'])
        return '200'
            
    @app.route('/startretraining', methods=['GET'])
    def startRetraining():
        logging.info('startRetraining : ')        
        # Apply Predicitons to all False Done 
        cust_list, next_page_token = getCustomerModel().list(done=True)
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                data_analyzer.applyPrediction_responsedata(cust_id_x['cust_name'])
                intenteng.prepareTrainingData(cust_id_x['cust_name']) 
                intenteng.startTrainingProcess(cust_id_x['cust_name'])
        return '200'

    @app.route('/processnewcustomer', methods=['GET'])
    def processNewCustomer():
        logging.info('processnewcustomer : ')
        ticketLearner.processNewCustomer()
        return '200'
    
    @app.route('/preparedata', methods=['GET'])
    def prepareTrainingData():
        logging.info('prepareTrainingData : ')        
        # Copy TrainingLog to defaultTrainingLog
        data_analyzer.copyOldTrainingLog()
        
        # Extract TrainingData from Ticket defaultTrainingLog to Cust_TrainingData 
        data_analyzer.extractTicketData_default()
        
        # Extract Trainingdata from Ticket custTrainingLog to Cust_TrainingData         
        cust_list, next_page_token = getCustomerModel().list(done=True)
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                data_analyzer.extractTicketData_cust(cust_id_x['cust_name'])
        
        # Extract TrainingData from Intent defaultTrainingLog to Cust_TrainingData 
        data_analyzer.extractIntentData_default()
        
        # Extract TrainingData from Intent CustTrainingLog to Cust_TrainingData         
        cust_list, next_page_token = getCustomerModel().list(done=True)
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                data_analyzer.extractIntentData_cust(cust_id_x['cust_name'])

        # Extract TrainingData from Intent defaultTrainingLog to Cust_TrainingData 
        data_analyzer.extractFeedbackData_default()
        
        # Extract TrainingData from Intent CustTrainingLog to Cust_TrainingData         
        cust_list, next_page_token = getCustomerModel().list(done=True)
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                data_analyzer.extractFeedbackData_cust(cust_id_x['cust_name'])
        
        # Extract TrainingData from Ticket/Comment in Cust_TrainingData
        cust_list, next_page_token = getCustomerModel().list(done=True)
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                data_analyzer.extractTicketData_new(cust_id_x['cust_name'])        
        return '200'
        
    @app.route('/testingservice', methods=['GET'])
    def startTestingModels():
        logging.info('startTestingModels : ')
        cust_list, next_page_token = getCustomerModel().list(done=True)
        for cust_id_x in cust_list:
            intenteng.prepareTestingData(cust_id_x['cust_name'])
            intenteng.startTestingProcess(cust_id_x['cust_name'])
            intenteng.createConfusionMatrix(cust_id_x['cust_name'])
        return '200'
    
    ''' 
    @app.route('/addcustomer', methods=['GET'])
    def addCustomer():
        logging.info('addcustomer : ')
        cust_id = request.args.get('cust_id')
        lang_type = request.args.get('lang_type')
        if cust_id == None or cust_id == '' or lang_type==None or lang_type=='': 
            logging.info('Could not create new customer' + cust_id)
            return '200'
        getCustomerModel().create(cust_id.strip().lower(), done=True, id=rid)
        cust_id_x = getCustomerModel().authenticate(cust_id.strip().lower())
        if cust_id_x:
            ticketLearner.import_trainingdata(cust_id_x['cust_name'], cust_id_x['language'])  
            ticketLearner.import_responsedata(cust_id_x['cust_name'], cust_id_x['language']) 
            intenteng.prepareTrainingData(cust_id_x['cust_name']) 
            intenteng.startTrainingProcess(cust_id_x['cust_name'])
            logging.info('Created new Customer : ' + cust_id_x['cust_name'])
        else: 
            logging.info('Could not create new customer' + cust_id)
            return '200'
        logging.info('Created new customer' + cust_id)
        return '200'  
    '''
    
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

from agentapp.EntityExtractor import EntityExtractor
from agentapp.IntentExtractor import IntentExtractor
from agentapp.IntentExtractor_resp import IntentExtractor_resp
from agentapp.tickets_learner import tickets_learner
from agentapp.StorageOps import StorageOps
from agentapp.SmartRepliesSelector import SmartRepliesSelector
from agentapp.model_select import get_model, getTrainingModel, getCustomerModel
from agentapp.TrainingDataAnalyzer import TrainingDataAnalyzer
from agentapp.UtilityClass import UtilityClass

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
storageOps = StorageOps()
utilclass = UtilityClass()
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
        storageOps.create_bucket()
        
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
        intenteng = IntentExtractor() 
        ticketLearner = tickets_learner()
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
            intent_input = utilclass.cleanhtml(received_data['comments'][0]['value'])
        else:
            intent_input = utilclass.cleanhtml(received_data['description'] + '. ' + received_data['subject'])
            
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
        cust_id = request.args.get('cust_id')
        cust_list =[]
        if cust_id == None:             
            cust_list, __ = getCustomerModel().list(done=True)
        else: 
            cust_list = [{'cust_name' : cust_id}]
        logging.info('Processing startDataImport For : ' + str(cust_list))

        ticketLearner = tickets_learner()
        ticketLearner.import_customerdata()
        for cust_id_x in cust_list:
            ticketLearner.import_trainingdata(cust_id_x['cust_name'], cust_id_x['language'])  
            ticketLearner.import_responsedata(cust_id_x['cust_name'], cust_id_x['language'])         
        return '200'  
    
    @app.route('/starttraining', methods=['GET'])
    def startTrainingModels():
        logging.info('startTrainingModels : ')
        cust_id = request.args.get('cust_id')
        cust_list =[]
        if cust_id == None:             
            cust_list, __ = getCustomerModel().list(done=True)
        else: 
            cust_list = [{'cust_name' : cust_id}]
        logging.info('Processing startTrainingModels For : ' + str(cust_list))

        intenteng = IntentExtractor() 
        for cust_id_x in cust_list:
            intenteng.prepareTrainingData(cust_id_x['cust_name']) 
            intenteng.startTrainingProcess(cust_id_x['cust_name'])
        return '200'  
    
    @app.route('/buildsmartreplies', methods=['GET'])
    def buildSmartReplies():
        logging.info('buildSmartReplies : ') 
        cust_id = request.args.get('cust_id')
        cust_list =[]
        if cust_id == None:             
            cust_list, __ = getCustomerModel().list(done=True)
        else: 
            cust_list = [{'cust_name' : cust_id}]
        logging.info('Processing buildSmartReplies For : ' + str(cust_list))

        replyeng = SmartRepliesSelector()
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default':                 
                replyeng.prepareTrainingData(cust_id_x['cust_name'])
                replyeng.generateNewResponse(cust_id_x['cust_name'])
                replyeng.populateResponseData(cust_id_x['cust_name'])
        return '200'
            
    @app.route('/startretraining', methods=['GET'])
    def startRetraining():
        logging.info('startRetraining : ')        
        cust_id = request.args.get('cust_id')
        cust_list =[]
        if cust_id == None:             
            cust_list, __ = getCustomerModel().list(done=True)
        else: 
            cust_list = [{'cust_name' : cust_id}]
        logging.info('Processing startRetraining For : ' + str(cust_list))
       
        intenteng = IntentExtractor() 
        intenteng_resp = IntentExtractor_resp()
        cust_model = getCustomerModel()
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default':
                intenteng_resp.prepareTrainingData(cust_id_x['cust_name'])
                intenteng_resp.startTrainingProcess(cust_id_x['cust_name'])
                intenteng_resp.startTrainLogPrediction(cust_id_x['cust_name'])        
                intenteng.prepareTrainingData(cust_id_x['cust_name']) 
                intenteng.startTrainingProcess(cust_id_x['cust_name'])
        return '200'

    @app.route('/processnewcustomer', methods=['GET'])
    def processNewCustomer():
        logging.info('processnewcustomer : ')        
        cust_id = request.args.get('cust_id')
        cust_list =[]
        if cust_id == None:             
            cust_list, __ = getCustomerModel().list(done=True)
        else: 
            cust_list = [{'cust_name' : cust_id}]
        logging.info('Processing processNewCustomer For : ' + str(cust_list))

        cust_model = getCustomerModel()
        ticketLearner = tickets_learner()
        intenteng = IntentExtractor()
        for cust_x in cust_list:             
            ticketLearner.import_trainingdata(cust_x['cust_name'], cust_x['language']) 
            intenteng.prepareTrainingData(cust_x['cust_name']) 
            intenteng.startTrainingProcess(cust_x['cust_name'])
            cust_model.update(cust_x['cust_name'], language=cust_x['language'], intent_threshold=cust_x['intent_threshold'], organization=cust_x['organization'], email_id=cust_x['email_id'], password =cust_x['password'], newflag=False, done=True, id=cust_x['id'])
            logging.info('Processed new Customer : ' + cust_x['cust_name'])
        return '200'
    
    @app.route('/copyoldtrainingdata', methods=['GET'])
    def copyOldTrainingData():
        logging.info('copyOldTrainingData : ')        
        data_analyzer = TrainingDataAnalyzer()
        data_analyzer.copyOldTrainingLog()
        return '200'

    @app.route('/copydefaulttrainingdata', methods=['GET'])
    def copyDefaultTrainingData():
        logging.info('copyDefaultTrainingData : ')        
        data_analyzer = TrainingDataAnalyzer()
        data_analyzer.copyDefaultTrainingLog()
        return '200'
    
    @app.route('/processtrainingdata', methods=['GET'])
    def processTrainingData():
        logging.info('processTrainingData : ')        
        cust_id = request.args.get('cust_id')
        cust_list =[]
        if cust_id == None:             
            cust_list, __ = getCustomerModel().list(done=True)
        else: 
            cust_list = [{'cust_name' : cust_id}]
        logging.info('Processing processTrainingData For : ' + str(cust_list))

        data_analyzer = TrainingDataAnalyzer()
        # Extraction of Intent data          
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                data_analyzer.extractIntentData_cust(cust_id_x['cust_name']) 
        '''
        # Extraction of Old Ticket data          
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                data_analyzer.extractTicketData_cust(cust_id_x['cust_name'])
        # Extraction of Feedback data          
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                data_analyzer.extractFeedbackData_cust(cust_id_x['cust_name'])
        # Extraction of New Ticket data 
        for cust_id_x in cust_list:
            if cust_id_x['cust_name'] != 'default': 
                data_analyzer.extractNewTicketData_cust(cust_id_x['cust_name'])   
        '''     
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


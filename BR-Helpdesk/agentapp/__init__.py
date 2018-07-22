from agentapp.EntityExtractor import EntityExtractor
from agentapp.IntentExtractor import IntentExtractor
from agentapp.tickets_learner import tickets_learner
from agentapp.StorageOps import StorageOps
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

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)
    storage = StorageOps()
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
        storage.create_bucket()
        
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
        utilclass = UtilityClass()
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

    @app.route('/getticketflag', methods=['POST'])
    def getTicketFlag():
        logging.info('getTicketFlag : ')
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

        if cust_id == 'default':
            status_flag = False
        else: 
            status_flag = getCustomerModel().getTicketFlag(cust_id)
        
        resp = {}
        resp["Ticket_Flag"] = status_flag
        
        json_resp = json.dumps(resp)
        return json_resp
    
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
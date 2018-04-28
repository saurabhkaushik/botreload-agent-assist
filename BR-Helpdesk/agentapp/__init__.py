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

entityeng = EntityExtractor()
intenteng = IntentExtractor()
ticketLearner = tickets_learner()

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
        #ticketLearner.import_trainingdata()
        ticketLearner.import_responsedata()
        intenteng.prepareTrainingData_ds() 
        intenteng.startTrainingProcess()
        #intenteng.prepareTestingData()
        #intenteng.startTestingProcess()
        #intenteng.createConfusionMatrix()

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
        intent_input = ''
        if (received_data['requester']['email'] == received_data['comments'][0]['author']['email']):
            intent_input = cleanhtml(received_data['comments'][0]['value'])
        else:
            intent_input = cleanhtml(received_data['description'] + '. ' + received_data['subject'])
            
        #intent_input = received_data['description'] + '. ' + received_data['comments'] + '. ' + received_data['subject']
        predicted_intent = intenteng.getIntentForText(intent_input)
        formatted_resp = ticketLearner.format_output_ds(predicted_intent) 
        logging.info('\'' + str(intent_input) + '\' >> ' + str(formatted_resp))
        json_resp = json.dumps(formatted_resp)
        get_model().create('response', json_resp)
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
        get_model().create('tickets', json.dumps(request.json))
        return '200' 
    
    @app.route('/uploadfeedback', methods=['POST'])
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
    
    @app.route('/testingservice', methods=['GET'])
    def doFunctionTesting():
        logging.info('doFunctionTesting : ')
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

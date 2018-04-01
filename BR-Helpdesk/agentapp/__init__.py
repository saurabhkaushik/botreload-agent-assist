from agentapp.EntityExtractor import EntityExtractor
from agentapp.IntentExtractor import IntentExtractor

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

    # Register the Bookshelf CRUD blueprint.
    from .crud import crud
    app.register_blueprint(crud, url_prefix='/books')

    entityeng = EntityExtractor()
    intenteng = IntentExtractor()
    
    intenteng.prepareTrainingData()
    intenteng.startTrainingProcess()
    
    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('crud.list'))
    
    @app.route('/intent', methods=['POST'])
    def intent():
        logging.info('intent : ')
        get_model().create('intent', str(request.json))
        
        received_data = request.json
        intent_input = received_data['description'] + '. ' + received_data['comment'] + '. ' + received_data['subject']
        predicted_intent = intenteng.getIntentForText(intent_input)
        formatted_resp =  format_output(predicted_intent)
        json_resp = json.dumps(formatted_resp)
        
        logging.info('response : ' )
        get_model().create('response', str(request.json))
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
        get_model().create('tickets', str(request.json))
        return '200' 
    
    @app.route('/feedbkloop', methods=['POST'])
    def uploadfeedback():
        logging.info('feedback : ')
        get_model().create('feedback', str(request.json))
        return '200'  
    
    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    # Add an error handler. This is useful for debugging the live application,
    # however, you should disable the output of the exception for production
    # applications.
    @app.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    return app


def get_model():
    model_backend = current_app.config['DATA_BACKEND']
    if model_backend == 'cloudsql':
        from . import model_cloudsql
        model = model_cloudsql
    elif model_backend == 'datastore':
        from . import model_datastore
        model = model_datastore
    elif model_backend == 'mongodb':
        from . import model_mongodb
        model = model_mongodb
    else:
        raise ValueError(
            "No appropriate databackend configured. "
            "Please specify datastore, cloudsql, or mongodb")

    return model

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
import datetime
 
# [START build_service]
from google.cloud import datastore

class ticket_learner(object):

    def __init__(self):
        self.client = datastore.Client()
    # [END build_service]
    
    def extract_save_data(self):        
        while next_page_token != None: 
            tickets, next_page_token = get_model().list(cursor=token)
            for ticket in tickets: 
                json_ticket = json.load(ticket['json_data'])
                tags = json_ticket['tags']
                query = json_ticket['description']
                response = json_ticket['comment']
                getTrainingModel().create(tags, query, response)
        
    #def process_train_data(self):
    #def train_data(self):
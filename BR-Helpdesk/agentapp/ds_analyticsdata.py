from flask import current_app
from google.cloud import datastore
import datetime

builtin_list = list

def init_app(app):
    pass

def get_client():
    return datastore.Client(current_app.config['PROJECT_ID'])

# [START from_datastore]
def from_datastore(entity):
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()

    entity['id'] = entity.key.id
    return entity
# [END from_datastore]

# [START list]
def list(limit=999, cust_id=None, cursor=None, done=None) : 
    ds = get_client()

    query = ds.query(kind= 'AnalyticsData')
    if done != None: 
        query.add_filter('done', '=', done)
    if cust_id != None: 
        query.add_filter('cust_id', '=', cust_id)
    query_iterator = query.fetch(limit=limit, start_cursor=cursor)
    page = next(query_iterator.pages)

    entities = builtin_list(map(from_datastore, page))
    next_cursor = (
        query_iterator.next_page_token.decode('utf-8')
        if query_iterator.next_page_token else None)

    return entities, next_cursor
# [END list]

def read(id):
    ds = get_client()
    key = ds.key('AnalyticsData', int(id))
    results = ds.get(key)
    return from_datastore(results)

# [START update]
def update(analytics_data, id=None):
    ds = get_client()
    
    if id:
        key = ds.key('AnalyticsData', int(id))
    else:
        key = ds.key('AnalyticsData')
        
    entity = datastore.Entity(key=key)
    
    entity.update({
            'cust_id': analytics_data['cust_id'],
            'ticket_total_count': analytics_data['ticket_total_count'],
            'response_total_count': analytics_data['response_total_count'],
            'response_modified_count': analytics_data['response_modified_count'],
            'response_default_count': analytics_data['response_default_count'],
            'total_ticket_with_response': analytics_data['total_tickets_with_response'],
            'Mean_Accuracy_Intent_vs_Response': analytics_data['Mean_Accuracy_Intent_vs_Response'],
            'Mean_Accuracy_Intent_vs_Saved': analytics_data['Mean_Accuracy_Intent_vs_Saved'],
            'Percentage_Match_Tags_vs_Query': analytics_data['Percentage_Match_Tags_vs_Query'],
            'Percentage_Match_Tags_vs_Query': analytics_data['Percentage_Match_Tags_vs_Query'],
            'Bleu_Score_Intent': analytics_data['Bleu_Score_Intent'],
            'Bleu_Score_Response': analytics_data['Bleu_Score_Response'],
            'ticket_last_timestamp': analytics_data['ticket_last_timestamp'],
            'Feedback_tickets_count' : analytics_data['Feedback_tickets_count'],
            'Mean_feedback_prob' : analytics_data['Mean_feedback_prob'],
            'Mean_predict_prob' : analytics_data['Mean_predict_prob'],
            'created': datetime.datetime.utcnow(),
            'done': True
        })
    
    #entity.update(data)
    ds.put(entity)
    return from_datastore(entity)

create = update
# [END update]

def delete(id):
    ds = get_client()
    key = ds.key('AnalyticsData', int(id))
    #data = read(id)
    #if data != None:
        #update(data['type'], data['json_data'], id=data['id'], done=False, cust_id=cust_id)
    ds.delete(key)

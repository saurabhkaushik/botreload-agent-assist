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
def list(limit=999, cursor=None, cust_id='', feedback_flag=None, done=None):
    ds = get_client() 

    query = ds.query(kind= cust_id +'TrainingData')#, order=['id'])
    if done != None: 
        query.add_filter('done', '=', done)
    if feedback_flag != None: 
        query.add_filter('feedback_flag', '=', feedback_flag)

    query_iterator = query.fetch(limit=limit, start_cursor=cursor)
    page = next(query_iterator.pages)

    entities = builtin_list(map(from_datastore, page))
    next_cursor = (
        query_iterator.next_page_token.decode('utf-8')
        if query_iterator.next_page_token else None)

    return entities, next_cursor

# [START list]
def list_by_respcategory(resp_category, limit=999, cursor=None, cust_id='', done=None):
    ds = get_client() 

    query = ds.query(kind= cust_id +'TrainingData') #, order=['type'])
    query.add_filter('resp_category', '=', resp_category)
    if done != None: 
        query.add_filter('done', '=', done)
    query_iterator = query.fetch(limit=limit, start_cursor=cursor)
    page = next(query_iterator.pages)

    entities = builtin_list(map(from_datastore, page))
    next_cursor = (
        query_iterator.next_page_token.decode('utf-8')
        if query_iterator.next_page_token else None)

    return entities, next_cursor

def read(id, cust_id=''):
    ds = get_client()
    key = ds.key(cust_id +'TrainingData', int(id))
    results = ds.get(key)
    return from_datastore(results)

# [START update]
def update(tags, query, response, query_category='', resp_category='', done=False, id=None, 
           feedback_resp = '', feedback_flag=False, feedback_prob=0, predict_prob=0, cust_id=''):
    ds = get_client()
    
    if id:
        key = ds.key(cust_id +'TrainingData', int(id))
    else:
        key = ds.key(cust_id +'TrainingData')

    entity = datastore.Entity(
        key=key,
        exclude_from_indexes=['query', 'response'])
    
    entity.update({
            'tags': tags,
            'query' : query,
            'query_category' : query_category, 
            'response' : response,
            'resp_category': resp_category,  
            'feedback_resp' : feedback_resp,
            'feedback_flag': feedback_flag,
            'feedback_prob' : feedback_prob, 
            'predict_prob' : predict_prob, 
            'created': datetime.datetime.utcnow(),
            'done': done
        })
    
    #entity.update(data)
    ds.put(entity)
    return from_datastore(entity)


create = update
# [END update]


# [START update]
def batchUpdate(traindata, cust_id=''):
    ds = get_client() 
    
    iter = int(len(traindata) / 400) + 1
    for i in range(iter):        
        i1 = (i) * 400
        i2 = ((i+1) * 400) - 1
        batch_data = traindata.iloc[i1:i2]
        batch = ds.batch()  
        batch.begin()  
        for index, items in batch_data.iterrows():
            if items['id'] != None:
                key = ds.key(cust_id +'TrainingData', int(items['id']))
            else:
                key = ds.key(cust_id +'TrainingData')
            entity = datastore.Entity(key=key, exclude_from_indexes=['query', 'response'])
            entity.update({
                    'tags': items['tags'],
                    'query' : items['query'],
                    'query_category' : items['query_category'], 
                    'response' : items['response'],
                    'resp_category': items['resp_category'],  
                    'feedback_resp' : items['feedback_resp'] if 'feedback_resp' in items else '',
                    'feedback_flag': items['feedback_flag'] if 'feedback_flag' in items else False,
                    'feedback_prob' : items['feedback_prob'] if 'feedback_prob' in items else 0, 
                    'predict_prob' : items['predict_prob'] if 'predict_prob' in items else 0, 
                    'created': datetime.datetime.utcnow(),
                    'done': items['done']
                })
            batch.put(entity)            
        batch.commit()
    return 

def delete(id, cust_id=''):
    ds = get_client()
    key = ds.key(cust_id +'TrainingData', int(id))
    data = read(id, cust_id=cust_id)
    if data != None:
        update(data['tags'], data['query'], data['response'], query_category=data['query_category'], resp_category=data['resp_category'], id=data['id'], done=False, cust_id=cust_id)
    #ds.delete(key)
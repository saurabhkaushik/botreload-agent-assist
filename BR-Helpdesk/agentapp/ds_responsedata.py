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
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()

    entity['id'] = entity.key.id
    return entity
# [END from_datastore]

# [START list]
def list(res_category=None, limit=999, cursor=None, modifiedflag=None, defaultflag=None, cust_id=None, done=None):
    ds = get_client()

    query = ds.query(kind=cust_id + 'ResponseData')#, order=['id']) 
    if res_category != None and res_category != '': 
        query.add_filter('res_category', '=', res_category)
    if done != None: 
        query.add_filter('done', '=', done)
    if modifiedflag != None: 
        query.add_filter('modifiedflag', '=', modifiedflag)
    if defaultflag != None: 
        query.add_filter('defaultflag', '=', defaultflag)

    query_iterator = query.fetch(limit=limit, start_cursor=cursor)
    page = next(query_iterator.pages)

    entities = builtin_list(map(from_datastore, page))
    next_cursor = (
        query_iterator.next_page_token.decode('utf-8')
        if query_iterator.next_page_token else None)

    return entities, next_cursor
# [END list]

def read(id, cust_id=''):
    ds = get_client()
    key = ds.key(cust_id + 'ResponseData', int(id))
    results = ds.get(key)
    return from_datastore(results)

# [START update]
def update(cat_name, res_category, response_text, tags, resp_tags, modifiedflag=False, defaultflag=False, done=False, id=None, cust_id=''):
    ds = get_client()
    
    if id:
        key = ds.key(cust_id + 'ResponseData', int(id))
    else:
        key = ds.key(cust_id + 'ResponseData')

    entity = datastore.Entity(
        key=key,
        exclude_from_indexes=['response_text'])
    
    entity.update({
            'resp_name': cat_name,
            'res_category': res_category,
            'response_text' : response_text,
            'tags' : tags,
            'modifiedflag': modifiedflag,
            'defaultflag' : defaultflag,
            'resp_tags' : resp_tags,
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
                key = ds.key(cust_id +'ResponseData', int(items['id']))
            else:
                key = ds.key(cust_id +'ResponseData')
            entity = datastore.Entity(key=key, exclude_from_indexes=['query', 'response'])
            entity.update({
                'resp_name': items['resp_name'],
                'res_category': items['res_category'],
                'response_text': items['response_text'],
                'tags' : items['tags'],
                'modifiedflag' : items['modifiedflag'],
                'defaultflag' : items['defaultflag'],
                'resp_tags': items['resp_tags'],
                'created': datetime.datetime.utcnow(),
                'done': items['done']
                })
            batch.put(entity)
        batch.commit()
    return 

def delete(id, cust_id=''):
    ds = get_client()
    key = ds.key(cust_id + 'ResponseData', int(id))
    data = read(id, cust_id=cust_id)
    if data != None:
        update(data['resp_name'], data['res_category'], data['response_text'], data['tags'], data['resp_tags'], id=data['id'], done=False, cust_id=cust_id) 
    #ds.delete(key)

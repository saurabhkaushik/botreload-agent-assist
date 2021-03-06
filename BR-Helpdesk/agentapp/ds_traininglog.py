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
def list(log_type=None, limit=999, cursor=None, cust_id='', done=None) : 
    ds = get_client()

    query = ds.query(kind= cust_id +'TrainingLog')
    if log_type != None and log_type != '': 
        query.add_filter('type', '=', log_type)
    if done != None: 
        query.add_filter('done', '=', done)
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
    key = ds.key(cust_id +'TrainingLog', int(id))
    results = ds.get(key)
    return from_datastore(results)


# [START update]
def update(req_type, data, done=False, id=None, created=None, cust_id=''):
    ds = get_client()
    
    if id:
        key = ds.key(cust_id +'TrainingLog', int(id))
    else:
        key = ds.key(cust_id +'TrainingLog')
        
    if created == None:
        created = datetime.datetime.utcnow()
    
    entity = datastore.Entity(
        key=key,
        exclude_from_indexes=['json_data'])
    
    entity.update({
            'type': req_type,
            'created': datetime.datetime.utcnow(),
            'json_data': data,
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
    
    iter = int(len(traindata) / 100) + 1
    for i in range(iter):        
        i1 = (i) * 100
        i2 = ((i+1) * 100) - 1
        batch_data = traindata.iloc[i1:i2]
        batch = ds.batch()  
        batch.begin()  
        for index, items in batch_data.iterrows():
            if items['id'] != None:
                key = ds.key(cust_id +'TrainingLog', int(items['id']))
            else:
                key = ds.key(cust_id +'TrainingLog')
            entity = datastore.Entity(key=key, exclude_from_indexes=['json_data'])
            entity.update({
                    'type': items['type'],
                    'created': datetime.datetime.utcnow(),
                    'json_data': items['json_data'],
                    'done': items['done']
                })
            batch.put(entity)
        batch.commit()
    return 

def delete(id, cust_id=''):
    ds = get_client()
    key = ds.key(cust_id +'TrainingLog', int(id))
    data = read(id, cust_id=cust_id)
    if data != None:
        update(data['type'], data['json_data'], id=data['id'], done=False, cust_id=cust_id)
    #ds.delete(key)

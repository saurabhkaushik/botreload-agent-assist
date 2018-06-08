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
def list(cust_name='', newflag=False, limit=999, cursor=None, done=False):
    ds = get_client()

    query = ds.query(kind='CustomerData')     
    if done != None: 
        query.add_filter('done', '=', done)
    if newflag != None: 
        query.add_filter('newflag', '=', newflag)
    if cust_name != None and cust_name != '': 
        query.add_filter('cust_name', '=', cust_name)
    query_iterator = query.fetch(limit=limit, start_cursor=cursor)
    page = next(query_iterator.pages)

    entities = builtin_list(map(from_datastore, page))
    next_cursor = (
        query_iterator.next_page_token.decode('utf-8')
        if query_iterator.next_page_token else None)

    return entities, next_cursor

def read(id):
    ds = get_client()
    key = ds.key('CustomerData', int(id))
    results = ds.get(key)
    return from_datastore(results)

def authenticate(cust_id_x, newflag=None): 
    cust_list = list(cust_name=cust_id_x.strip().lower(), newflag=newflag, done=True)    
    if len(cust_list[0]) > 0 : 
        return cust_list[0][0]
    return None 

# [START update]
def update(cust_name, language='en', intent_threshold=100, organization='', 
    email_id='', password ='', newflag=False, done=False, id=None):
    ds = get_client()
    
    if id:
        key = ds.key('CustomerData', int(id))
    else:
        key = ds.key('CustomerData')

    entity = datastore.Entity(
        key=key)
    
    entity.update({
            'cust_name': cust_name,
            'language': language,
            'intent_threshold': intent_threshold,
            'organization' : organization,
            'email_id' : email_id,
            'password' : password,
            'newflag' : newflag,
            'created': datetime.datetime.utcnow(),
            'done': done
        })
    
    #entity.update(data)
    ds.put(entity)
    return from_datastore(entity)


create = update
# [END update]


def delete(id):
    ds = get_client()
    key = ds.key('CustomerData', int(id))
    data = read(id)
    if data != None:
        update(data['cust_name'], intent_threshold = data['intent_threshold'], organization = data['organization'], email_id = data['email_id'], id=data['id'], done=False) 
    #ds.delete(key)

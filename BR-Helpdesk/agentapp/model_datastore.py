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
def list(limit=10, cursor=None):
    ds = get_client()

    query = ds.query(kind='TrainingLog', order=['type'])
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
    key = ds.key('TrainingLog', int(id))
    results = ds.get(key)
    return from_datastore(results)


# [START update]
def update(req_type, data, id=None):
    ds = get_client()
    
    if id:
        key = ds.key('TrainingLog', int(id))
    else:
        key = ds.key('TrainingLog')

    entity = datastore.Entity(
        key=key,
        exclude_from_indexes=['json_data'])
    
    entity.update({
            'type': req_type,
            'created': datetime.datetime.utcnow(),
            'json_data': data,
            'done': False
        })
    
    #entity.update(data)
    ds.put(entity)
    return from_datastore(entity)


create = update
# [END update]


def delete(id):
    ds = get_client()
    key = ds.key('TrainingLog', int(id))
    ds.delete(key)

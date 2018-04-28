def delete_all(): 
    ds = get_client()
    entries = ds.key('TrainingData', keys_only=True) 
    ds.delete(entries)
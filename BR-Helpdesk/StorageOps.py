import datetime
import json
import logging 
import csv
from flask import current_app
import pandas as pd

from google.cloud import datastore
from google.cloud import storage
import google

class StorageOps(object):

    def __init__(self):
        self.client = datastore.Client()
        self.storage_client = storage.Client()

    def get_bucket(self, cust_id):
        print('get_bucket:' + str(cust_id))         
        try:
            bucket = self.storage_client.get_bucket(current_app.config['STORAGE_BUCKET']) 
            m_blob = bucket.get_blob(cust_id + '_model.pkl')
            if m_blob == None:
                m_blob = bucket.get_blob('default' + '_model.pkl')
                logging.error('Could find Pickle file for Organization, Serving Default : '+ str(cust_id))
            file = m_blob.download_as_string()
            return file
        except google.cloud.exceptions.NotFound:
            print('Sorry, that bucket does not exist!')        
        return None
        
    def put_bucket(self, file, cust_id):
        print('put_bucket:' + str(cust_id))
        try:
            bucket = self.storage_client.get_bucket(current_app.config['STORAGE_BUCKET'])
            filename = cust_id + '_model.pkl'
            m_blob = bucket.blob(filename)            
            m_blob.upload_from_string(file)
        except google.cloud.exceptions.NotFound:
            print('Sorry, that bucket does not exist!')        
        #print('Blob created.')
        return file
        
    def create_bucket(self):
        print('create_bucket:' )
        try:
            bucket = self.storage_client.lookup_bucket(current_app.config['STORAGE_BUCKET'])
            if bucket == None: 
                bucket = self.storage_client.create_bucket(current_app.config['STORAGE_BUCKET'])
        except google.cloud.exceptions.Conflict:
            print('Sorry, that bucket was not created!')        
        logging.info('Bucket created.')
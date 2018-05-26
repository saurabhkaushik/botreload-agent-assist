import configparser

config = configparser.ConfigParser()
config.read('config.py')

print (config['DATA_BACKEND'])

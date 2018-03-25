from src.EntityExtractor import EntityExtractor
from src.IntentExtractor import IntentExtractor
  
from flask import Flask, jsonify
from flask import request
from flask import make_response
from flask import abort
from flask import url_for
import csv

import json 

intenteng = IntentExtractor()

intenteng.prepareTrainingData()
intenteng.startTrainingProcess()
predicted_intent = intenteng.getIntentForText("Thanks for getting in touch for more info on our product. ")
print ("format_output : ", predicted_intent)

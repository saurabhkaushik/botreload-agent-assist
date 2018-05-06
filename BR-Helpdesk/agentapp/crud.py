from agentapp.model_select import getResponseModel, getTrainingModel
from agentapp import authenticate_cust
from flask import Blueprint, redirect, render_template, request, url_for
import logging 
crud = Blueprint('crud', __name__)

from agentapp.IntentExtractor import IntentExtractor
intenteng = IntentExtractor()

# [START list]
@crud.route("/")
def login():    
    return render_template("login.html") 
# [END list]

# [START auth]
@crud.route("/auth")
def auth():    
    t_cust_id = request.args.get('cust_id', None)
    cust_id = authenticate_cust(t_cust_id)
    if cust_id == None: 
        logging.error('\'' + t_cust_id + '\' is invalid customer Organization. ')
        return render_template("login.html")
    return redirect(url_for('.list', cust_id=cust_id))
# [END auth]

# [START list]
@crud.route("/list")
def list():    
    token = request.args.get('page_token', None)
    cust_id = request.args.get('cust_id', None)
    if cust_id == None: 
        cust_id = ''
    
    if token:
        token = token.encode('utf-8')

    books, next_page_token = getResponseModel().list(cursor=token, cust_id=cust_id, done=True)

    return render_template(
        "list.html", cust_id=cust_id,
        books=books,
        next_page_token=next_page_token)
# [END list]


@crud.route('/<id>')
def view(id):
    cust_id = request.args.get('cust_id', None).strip()
    if cust_id == None: 
        cust_id = ''
    book = getResponseModel().read(id, cust_id)
    return render_template("view.html", cust_id=cust_id, book=book)


# [START add]
@crud.route('/add', methods=['GET', 'POST'])
def add():
    cust_id = request.args.get('cust_id', None).strip()
    if cust_id == None: 
        cust_id = ''
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        book = getResponseModel().create(data['resp_name'], data['resp_name'], data['response_text'], data['tags'], done=True, id=None, cust_id=cust_id)
        traindata = getTrainingModel().create(data['tags'], data['response_text'], '', query_category='', resp_category=data['resp_name'], done=True, id=None, cust_id=cust_id)
        return redirect(url_for('.view', cust_id=cust_id, id=book['id']))

    return render_template("form.html", cust_id=cust_id, action="Add", book={})
# [END add]


@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    cust_id = request.args.get('cust_id', None).strip()
    if cust_id == None: 
        cust_id = ''
    book = getResponseModel().read(id, cust_id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        orgdata = getResponseModel().read(id, cust_id=cust_id)
        book = getResponseModel().update(data['resp_name'], data['resp_name'], data['response_text'], data['tags'], done=True, id=id, cust_id=cust_id)
        print (orgdata['resp_name'])
        trainlist = getTrainingModel().list_by_respcategory(orgdata['resp_name'], cust_id=cust_id)
        for resp in trainlist: 
            if (resp != None) and (len(resp) > 0) :
                for resp_item in resp: 
                    getTrainingModel().update(data['tags'], resp_item['query'], resp_item['response'], resp_item['query_category'], resp_category=data['resp_name'], done=True, id=resp_item['id'], cust_id=cust_id)
        return redirect(url_for('.view', cust_id=cust_id, id=book['id']))

    return render_template("form.html", cust_id=cust_id, action="Edit", book=book)


@crud.route('/<id>/delete')
def delete(id):
    cust_id = request.args.get('cust_id', None).strip()
    if cust_id == None: 
        cust_id = ''
    
    dataitm = getResponseModel().read(id, cust_id)
    
    trainlist = getTrainingModel().list_by_respcategory(dataitm['resp_name'], cust_id=cust_id, done=True)
    for resp in trainlist: 
        if (resp != None) and (len(resp) > 0) :
            for resp_item in resp: 
                getTrainingModel().delete(resp_item['id'], cust_id=cust_id)
                    
    getResponseModel().delete(id, cust_id)
    return redirect(url_for('.list', cust_id=cust_id))

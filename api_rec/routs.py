from flask import request, jsonify, abort, render_template
from api_rec.models import User, Data
from api_rec import app, db, bcrypt, jwt
from api_rec.forms import RegistrationForm, LoginForm
import joblib
import traceback
import pandas as pd
import numpy as np
from flask import Flask
from collections import defaultdict
import json
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
import io
import pickle 
import requests
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)
import datetime

#df_movies_tf_idf_described = joblib.load("df_movies_tf_idf_described.pkl")


#data = pd.read_json("data.json")
#max_id = max(data['movieId'])
print('Model loaded')
def factorization(data):
    tfidf = TfidfVectorizer()
    #name = str(name)+".pkl"
    tfidfmat = tfidf.fit_transform(data.movie_tags)
    #return pickle.dump(tfidfmat,open(name,"wb"))
    return tfidfmat


def get_closest_movies(name, num_rec, data_name):

    quer = Data.query.filter_by(data_name=data_name).first() #get data query 
    nbrs = quer.model_mat
    data = quer.data_mat
    data_real = quer.data
    #data = quer[['movieId',s'movie_tags']]
    #tfidf = TfidfVectorizer()
    #tfidfmat = tfidf.fit_transform(data.movie_tags)
    distances, indices = nbrs.kneighbors(data.getrow(name),n_neighbors = num_rec)
    '''pred the data indices'''
    #names_similar = pd.Series(indices.flatten()).map(data_real.reset_index()['movieId'])
    #result = pd.DataFrame({'distance': distances.flatten(), 'movieId': names_similar})
    #df_result = pd.merge(data_real, result, how='right', on='movieId')
    '''put the data indices in list for iteration'''
    #data = []
   # for v  in np.nditer(indices):
    #    data.append(v)
    result = pd.DataFrame(data=indices.flatten(), columns=['id']).drop([0])
    #create Datafram object 
    #indices['id'] = pd.Series("id",index=indices.index)
    
    return result.to_json(orient="records")
    #return data

'''@app.route('/', methods=['POST'])
def predict():
    #old function that i don't use 
    try:
        json_ = request.json
        mid = int(json_["movieId"])
        num_rec = int(json_["num_rec"])
        data_id = int(json_["id"])
        closest_movies = get_closest_movies(mid, num_rec, data_id)
        closest_movies_json = closest_movies.to_json(orient="records")

        return closest_movies_json

    except:
        return ("Error")'''

@app.route('/pred',methods=['GET'])
#@jwt_required
def pred():
    '''the predction function
       frist get parameter from url header 
       scound feed it to the pre defined predction function
       third form the npArray as json and return it '''
    try :
        try:
            dico = request.args.to_dict() #frist 
            mid = int(dico['movie_id'])
            num_rec = int(dico['num_rec'])
            data_name = str(dico['data_name'])      
            try:
                 #scound
                #closest_movies_json = closest_movies.to_json(orient="records") #third 
                return get_closest_movies(mid, num_rec, data_name) 
                

                #return jsonify(d)
            except :
                #return jsonify({"Error": "out of index", "status": 1}) 
                return jsonify({'trace': traceback.format_exc()})     
        except :
            return jsonify({"Error": "invalid data type ", "status": 2})
    except:
        return jsonify({'trace': traceback.format_exc()})     

@app.route('/get_data_from_project_user', methods=['POST'])
@jwt_required
def get_data():
    '''get new data and save it and factorize it '''
    try:
        json_ = request.json
        url = str(json_["url"])  
        user_id = int(json_['user_id'])  
        data_name = str(json_['data_name'])
        s=requests.get(url).content
        c=pd.read_json(s) #Tfidf factorization
        data = factorization(c)
        data_ = Data(data=c, data_mat=data, user_id=user_id, data_name = data_name, data_link=url)
        db.session.add(data_)
        db.session.commit()
        return jsonify({"success":"all clear"})
    except:
        return jsonify({"Error": "bad request","Status": 3})
        #return jsonify({'trace': traceback.format_exc()})
@app.route('/send_data',methods=['GET'])
def send_data():
    '''form local data as api'''
    data = pd.read_json('./data.json')
    data = data
    data_ = data.to_json(orient='records')
    return data_


@app.route('/show',methods=['POST'])
@jwt_required
def show():
    '''show data from the api '''
    json_ = request.json
    url = str(json_["url"])  
    user_id = int(json_['user_id'])  
    return requests.get(url).content

@app.route('/show_content',methods=['GET'])
@jwt_required
def show_content():
    '''showing the data from database '''
    quer = Data.query.get(1).data
    #data = pd.DataFrame(quer)[['movieId','movie_tags']]
    #data = data.to_json(orient="records")
    return jsonify({"num_rec": len(quer)})

@app.route('/update_data', methods=['POST'])
@jwt_required
def update_data():    
    '''get the new data of the user delete the old one 
       factorize the new one and save it  '''
    try:
        json_ = request.json #get the parametars from url 
        url = str(json_["url"])  
        user_id = int(json_['user_id'])  
        data_id = int(json_['data_id']) 
        data_name = str(json_['data_name'])
        s=requests.get(url).content #get the content from url
        c=pd.read_json(s) #read data from json to pd.Dataframe
        data = factorization(c) #tfidf factorization
        dele = Data.query.get(data_id)
        db.session.delete(dele)
        db.session.commit()
        data_ = Data(data=c, data_mat=data, user_id=user_id, data_name = data_name, data_link=url)
        db.session.add(data_)
        db.session.commit()
        return jsonify({"success":"all clear","len":len(c)})
    except:
        return jsonify({"Error":"Bad request","status": 3})

@app.route('/sing_in',methods=['POST','GET'])
def sing_in():
    json_ = request.json #get the parametars from url 
    username = str(json_["username"])  
    password = str(json_['password']) 
    
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        #token = jwt.encode({'email': auth.email, 'exp': datetime.datetime.utcnow()+ datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token': access_token})
    #except:
        #return jsonify({'error': 'invalid'})
    #return jsonify({'user': auth.username})  

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    data = Data.query.filter_by(user_id=current_user).all()
    data_name = []
    for i in data :
        data_name.append(i.data_name)
    data_name = tuple(data_name)
    return jsonify(data_name)

@app.route('/update_data_admin', methods=['get'])
@jwt_required
def update_data_admin():    
    '''get the new data of the user delete the old one 
       factorize the new one and save it  '''
    try:
        for url in db.session.query(Data).all():
 #get the content from url
            name = url.data_name
            url_ = url.data_link
            user_id = url.user_id
            c=pd.read_json(url_) #read data from json to pd.Dataframe
            data = factorization(c) #tfidf factorization
            db.session.delete(url)
            db.session.commit()
            data_ = Data(data=c, data_mat=data, user_id=user_id, data_name = name, data_link=url_)
            db.session.add(data_)
            db.session.commit()
            return jsonify({"success":"all clear","len":len(c)})
    except:

        return jsonify({'trace': traceback.format_exc()})    

'''
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')


#regist the the user 
@app.route('/register', methods=['GET','POST'])
def registeration():
    form = RegistrationForm()

    return render_template('register.html', title='Register', form=form)

#log in function
@app.route('/login',methods=['GET','POST'])
def log_in():
    form = LoginForm()

    return render_template('login.html', title='Login', form=form)


#log out function
@app.route('/logout', methods=['GET','POST'])
def log_out(): 
    return jsonify({'success':'access is conformatife'})
'''
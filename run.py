from api_rec import app

if __name__ == '__main__':
    app.run(debug=True, port = 8000)
'''from sklearn.externals import joblib
import traceback
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, abort
from collections import defaultdict
import json
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from flask_sqlalchemy import SQLAlchemy



def get_closest_movies(name, num_rec= 10):
    distances, indices = nbrs.kneighbors(df_movies_tf_idf_described.getrow(name),n_neighbors = num_rec)
    names_similar = pd.Series(indices.flatten()).map(data.reset_index()['movieId'])
    result = pd.DataFrame({'distance': distances.flatten(), 'movieId': names_similar})
    df_result = pd.merge(data, result, how='right', on='movieId')
    return (df_result)
'''
'''app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.PickleType, nullable=False)

    def __repr__(self):
        return f"User('{self.data}')"'''

'''@app.route('/', methods=['POST'])
def predict():
    try:
        json_ = request.json
        mid = int(json_["movieId"])
        num_rec = int(json_["num_rec"])
        closest_movies = get_closest_movies(mid, num_rec)
        closest_movies_json = closest_movies.to_json(orient="records")

        return closest_movies_json

    except:
        return ("Error")

@app.route('/pred',methods=['GET'])
def pred():
    try :
        try:
            dico = request.args.to_dict()
            mid = int(dico['movie_id'])
            num_rec = int(dico['num_rec'])
            try :
                closest_movies = get_closest_movies(mid, num_rec)
                closest_movies_json = closest_movies.to_json(orient="records")
                return closest_movies_json
                
            except :
                return jsonify({"Error": "out of index","status": 1})
        except :
            return jsonify({"Error": "invalid data type ", "status": 2})
    except:
        return jsonify({'trace': traceback.format_exc()})  '''   



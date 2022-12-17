from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from numpy import random
import requests
import json
df = pd.read_csv('final_movies.csv')
app = Flask(__name__)
CORS(app)
def get_similarity(index):
    vectorizer = TfidfVectorizer()
    feature_vectors = vectorizer.fit_transform(df['comb'])
    similarity = cosine_similarity(feature_vectors)
    return similarity[index]
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/movielist")
def get_movie_list():
    df = pd.read_csv('final_movies.csv')
    d = list(set(list(df['original_title'].values)))
    if(len(d) == 0):
        return jsonify(None)
    return jsonify(d)
@app.route("/getids/<string:moviename>")
def get_ids(moviename):
    imdb_id = (df.loc[df['original_title']==moviename,['imdb_title_id']]).values[0][0]
    response = requests.get('https://api.themoviedb.org/3/find/'+imdb_id+
                                '?api_key=bc9494ce80d96b4eefaffdeea5679261&language=en-US&external_source=imdb_id')
    tmdbid = -1
    res = response.json()
    if(len(res['movie_results'])):
            tmdbid = str(res['movie_results'][0]['id'])
    result = {'imdb_id':imdb_id,'tmdb_id':tmdbid}
    return jsonify(result)


@app.route("/similarity/<string:imdb_id>")
def get_movie_similarity(imdb_id):
    imdb = imdb_id
    movie = df.loc[df['imdb_title_id'] == imdb]
    if len(movie) == 0:
        imdb = random.choice(list(df['imdb_title_id']))
    name = (df.loc[df['imdb_title_id'] == imdb]).original_title.values[0]
    closest_index = df[df['original_title'] == name].index.values[0]
    try:
        len(similarity)
    except:
        similarity = get_similarity(closest_index)
    similarity_score = list(enumerate(similarity))
    # print(similarity_score)
    sorted_score = sorted(similarity_score, key=lambda x: x[1], reverse=True)
    # print(sorted_score)
    result = []

    for i in range(1, 11):
        idx = sorted_score[i][0]
        # print(idx)de
        response = requests.get('https://api.themoviedb.org/3/find/'+df['imdb_title_id'][idx] +
                                '?api_key=bc9494ce80d96b4eefaffdeea5679261&language=en-US&external_source=imdb_id')
        res = response.json()
        tmdbid = 0
        if(len(res['movie_results'])):
            tmdbid = str(res['movie_results'][0]['id'])
            response2 = requests.get('https://api.themoviedb.org/3/movie/' +
                                     tmdbid+'?api_key=bc9494ce80d96b4eefaffdeea5679261&language=en-US')
            res2 = response2.json()
        else:
            tmdbid = -1
            res2 = {}
        if(tmdbid != -1):
            result.append({'title': df['original_title'][idx], 'index': idx,
                           'imdb_id': df['imdb_title_id'][idx], 'tmdb_id': tmdbid, 'movie_details': res2})
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)

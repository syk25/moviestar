from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys


app = Flask(__name__)

client = MongoClient('mongodb://jungle:jungle@localhost:27017/dbjungle')

db = client.dbjungle



class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)



app.json = CustomJSONProvider(app)


# API #1: HTML 틀(template) 전달

@app.route('/')
def home():
    return render_template('index.html')


# API #2: 휴지통에 버려지지 않은 영화 목록을 반환합니다.
@app.route('/api/list', methods=['GET'])
def show_movies():

    sortMode = request.args.get('sortMode', 'likes')


    if sortMode == 'likes' or sortMode == 'viewers' or sortMode == 'date' :
        movies = list(db.movies.find({'trashed': False}, {}))
    else:
        return jsonify({'result': 'failure'})


    return jsonify({'result': 'success', 'movies_list': movies})

@app.route('/api/list/trash', methods=['GET'])
def show_trashed_movies():

    sortMode = request.args.get('sortMode', 'likes')



    if sortMode == 'likes' or sortMode == 'viewers' or sortMode == 'date' :
        movies = list(db.movies.find({'trashed': True}, {}))
    else:
        return jsonify({'result': 'failure'})


    return jsonify({'result': 'success', 'movies_list': movies})

# API #3: 영화에 좋아요 숫자를 하나 올립니다.
@app.route('/api/like', methods=['POST'])
def like_movie():

    title_receive = request.form['post_title']
    movie = db.movies.find_one({'title':title_receive})


    new_likes = movie['likes'] + 1


    result = db.movies.update_one({'title':title_receive}, {'$set': {'likes': new_likes}})

    # 4. 하나의 영화만 영향을 받아야 하므로 result.updated_count 가 1이면  result = success 를 보냄
    if result.modified_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

# API #5. 영화카드를 휴지통으로 보냅니다.
@app.route('/api/update/trash', methods=['POST'])
def trash_movie():
    title_receive = request.form['post_title']
    movie = db.movies.find_one({'title':title_receive})
    result = db.movies.update_one({'title':title_receive},{'$set':{'trashed':True}})
    if movie != None:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

# API #6 휴지통에 있는 영화카드를 다시 복구합니다.
@app.route('/api/update/restore',methods=['POST'])
def restore_movie():
    title_receive = request.form['post_title']
    movie = db.movies.find_one({'title':title_receive})
    result = db.movies.update_one({'title':title_receive},{'$set':{'trashed':False}})
    if movie != None:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

# API #7 휴지통에 있는 영화카드를 영구 삭제합니다.
@app.route('/api/update/delete', methods=['POST'])
def delete_movie():
    title_receive = request.form['post_title']
    movie = db.movies.find_one({'title':title_receive})
    db.movies.delete_one({'title': title_receive})
    if movie != None:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})


if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)

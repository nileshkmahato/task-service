from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.todo
tasks_collection = db.tasks

@app.route('/tasks', methods=['POST'])
def create_task():
    task = request.json
    tasks_collection.insert_one(task)
    return jsonify(task), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = list(tasks_collection.find({}, {'_id': 0}))
    return jsonify(tasks), 200

@app.route('/tasks/<title>', methods=['PUT'])
def update_task(title):
    task = request.json
    tasks_collection.update_one({'title': title}, {'$set': task})
    return jsonify(task), 200

@app.route('/tasks/<title>', methods=['DELETE'])
def delete_task(title):
    tasks_collection.delete_one({'title': title})
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
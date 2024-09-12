from flask import Flask, request, jsonify, render_template, send_from_directory
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Determine if we're running locally or in Kubernetes
if os.environ.get('KUBERNETES_SERVICE_HOST'):
    # We're in Kubernetes, use the service name
    mongo_uri = 'mongodb://mongo:27017/todo'
else:
    # We're running locally, use localhost
    mongo_uri = 'mongodb://localhost:27017/todo'

client = MongoClient(mongo_uri)
db = client.todo
tasks_collection = db.tasks

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['POST'])
def create_task():
    task = request.json
    result = tasks_collection.insert_one(task)
    task['_id'] = str(result.inserted_id)  # Convert ObjectId to string
    return jsonify(task), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = list(tasks_collection.find())
    for task in tasks:
        task['_id'] = str(task['_id'])  # Convert ObjectId to string
    return jsonify(tasks), 200

@app.route('/tasks/<title>', methods=['PUT'])
def update_task(title):
    task = request.json
    result = tasks_collection.update_one({'title': title}, {'$set': task})
    if result.modified_count:
        return jsonify(task), 200
    return jsonify({"error": "Task not found"}), 404

@app.route('/tasks/<title>', methods=['DELETE'])
def delete_task(title):
    result = tasks_collection.delete_one({'title': title})
    if result.deleted_count:
        return '', 204
    return jsonify({"error": "Task not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
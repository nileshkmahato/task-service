from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson import ObjectId
import os
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')
sender_mail = 'donlorose6@gmail.com'

# MongoDB connection URI (Kubernetes or Localhost)
mongo_uri = 'mongodb://mongo:27017/todo' if os.environ.get('KUBERNETES_SERVICE_HOST') else 'mongodb://localhost:27017/todo'
client = MongoClient(mongo_uri)
db = client.todo
tasks_collection = db.tasks

# Notification service URL (dynamically adjust based on environment)
if os.environ.get('KUBERNETES_SERVICE_HOST'):
    # We're in Kubernetes, use the service name in the cluster
    notification_service_url = 'http://notification-service:5001/notify'
else:
    # We're running locally, use localhost
    notification_service_url = 'http://localhost:5001/notify'

def send_notification(action, task_title, email):
    notification_payload = {
        'action': action,
        'task': task_title,
        'email': sender_mail 
    }
    try:
        response = requests.post(notification_service_url, json=notification_payload)
        if response.status_code == 200:
            print(f"Notification sent for {action} task: {task_title}")
        else:
            print(f"Failed to send notification: {response.content}")
    except Exception as e:
        print(f"Error connecting to notification service: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['POST'])
def create_task():
    task = request.json
    result = tasks_collection.insert_one(task)
    task['_id'] = str(result.inserted_id)  # Convert ObjectId to string

    # Send notification when task is created
    send_notification('created', task['title'], task.get('email', sender_mail))  # Default email

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
        # Send notification when task is updated
        send_notification('updated', title, task.get('email', sender_mail))
        return jsonify(task), 200
    return jsonify({"error": "Task not found"}), 404

@app.route('/tasks/<title>', methods=['DELETE'])
def delete_task(title):
    result = tasks_collection.delete_one({'title': title})
    if result.deleted_count:
        # Send notification when task is deleted
        send_notification('deleted', title, sender_mail)
        return '', 204
    return jsonify({"error": "Task not found"}), 404

@app.route('/tasks/<title>/complete', methods=['PUT'])
def complete_task(title):
    task = tasks_collection.find_one({'title': title})
    if task:
        tasks_collection.update_one({'title': title}, {'$set': {'completed': True}})
        # Send notification when task is completed
        send_notification('completed', title, sender_mail)
        return jsonify({'message': 'Task marked as complete'}), 200
    return jsonify({"error": "Task not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

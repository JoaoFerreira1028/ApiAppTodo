from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb+srv://joaompferreira00:OjgPlWVoHvkzjIdl@cluster0.6rxdm.mongodb.net/sample_mflix?retryWrites=true&w=majority&appName=Cluster0")
db = client["sample_mflix"]
users_collection = db["UsersTodo"]
todo_collection = db["TodoApp"]

# Function to convert ObjectId to string for Users
def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "fullname": user["fullname"],
        "email": user["email"],
        "password": user["password"]
    }

# Function to convert ObjectId to string for Todo
def serialize_todo(todo):
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "completed": todo["completed"],
        "user": str(todo["user"])  # Reference to the user
    }

# GET route - List all users
@app.route('/users', methods=['GET'])
def list_users():
    users = list(users_collection.find())
    return jsonify([serialize_user(u) for u in users])

# GET route - Fetch user by username
@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = users_collection.find_one({"username": username})
    if user:
        return jsonify(serialize_user(user))
    return jsonify({"error": "User not found"}), 404

# POST route - Create new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or not all(k in data for k in ("username", "fullname", "email", "password")):
        return jsonify({"error": "Incomplete data"}), 400

    if users_collection.find_one({"username": data["username"]}):
        return jsonify({"error": "Username already exists"}), 400

    result = users_collection.insert_one(data)
    return jsonify({"id": str(result.inserted_id), "message": "User created"}), 201

# PUT route - Update user by username
@app.route('/users/<username>', methods=['PUT'])
def update_user(username):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if new username already exists
    new_username = data.get("username")
    if new_username and new_username != username:
        if users_collection.find_one({"username": new_username}):
            return jsonify({"error": "Username already exists"}), 400

    updated_data = {}
    for field in ["username", "fullname", "email", "password"]:
        if field in data:
            updated_data[field] = data[field]

    if updated_data:
        if "username" in updated_data:
            # Update the username in MongoDB
            users_collection.update_one({"username": username}, {"$set": updated_data})
            # Update the username in the URL
            return jsonify({"message": f"User {username} updated to {updated_data['username']}"}), 200
        else:
            users_collection.update_one({"username": username}, {"$set": updated_data})
            return jsonify({"message": "User updated"}), 200
    else:
        return jsonify({"error": "No valid fields to update"}), 400

# DELETE route - Delete user by username
@app.route('/users/<username>', methods=['DELETE'])
def delete_user(username):
    result = users_collection.delete_one({"username": username})
    if result.deleted_count == 1:
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"error": "User not found"}), 404

# GET route - List all tasks for a specific user
@app.route('/todos', methods=['GET'])
def list_todos():
    user_id = request.args.get('user')  # Get the user ID from query parameters
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    todos = list(todo_collection.find({"user": user_id}))
    return jsonify([serialize_todo(t) for t in todos])

# GET route - Fetch task by ID
@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = todo_collection.find_one({"_id": ObjectId(todo_id)})
    if todo:
        return jsonify(serialize_todo(todo))
    return jsonify({"error": "Task not found"}), 404

# POST route - Create new task
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.json
    if not data or "title" not in data or "user" not in data:
        return jsonify({"error": "Incomplete data"}), 400
    
    data["completed"] = False
    
    # Check if user exists
    user = users_collection.find_one({"_id": ObjectId(data["user"])})
    if not user:
        return jsonify({"error": "User not found"}), 400
    
    result = todo_collection.insert_one(data)
    return jsonify({"id": str(result.inserted_id), "message": "Task created"}), 201

# PUT route - Update task by ID
@app.route('/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    todo = todo_collection.find_one({"_id": ObjectId(todo_id)})
    if not todo:
        return jsonify({"error": "Task not found"}), 404

    updated_data = {}
    for field in ["title", "completed"]:
        if field in data:
            updated_data[field] = data[field]

    if updated_data:
        todo_collection.update_one({"_id": ObjectId(todo_id)}, {"$set": updated_data})
        return jsonify({"message": "Task updated"}), 200
    else:
        return jsonify({"error": "No valid fields to update"}), 400

# DELETE route - Delete task by ID
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    result = todo_collection.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Task deleted"}), 200
    return jsonify({"error": "Task not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

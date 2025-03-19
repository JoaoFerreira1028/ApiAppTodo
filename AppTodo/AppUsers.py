from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "OjgPlWVoHvkzjIdl" 
jwt = JWTManager(app)

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

# POST route - Create new user with hashed password
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or not all(k in data for k in ("username", "fullname", "email", "password")):
        return jsonify({"error": "Incomplete data"}), 400

    if users_collection.find_one({"username": data["username"]}):
        return jsonify({"error": "Username already exists"}), 400

    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already exists"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())

    user_data = {
        "username": data["username"],
        "fullname": data["fullname"],
        "email": data["email"],
        "password": hashed_password.decode('utf-8')
    }

    result = users_collection.insert_one(user_data)
    return jsonify({"id": str(result.inserted_id), "message": "User created"}), 201

@app.route('/users/<username>', methods=['PUT'])
@jwt_required()
def update_user(username):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    updated_data = {}

    # Atualiza todos os campos diretamente (inclui hash para password)
    for field in ["username", "fullname", "email", "password"]:
        if field in data:
            if field == "password":
                hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())
                updated_data["password"] = hashed_password.decode('utf-8')
            else:
                updated_data[field] = data[field]

    users_collection.update_one({"username": username}, {"$set": updated_data})
    return jsonify({"message": "User updated"}), 200

@app.route('/users/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):
    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Delete user
    users_collection.delete_one({"_id": user["_id"]})

    # Delete all tasks associated with user
    todo_collection.delete_many({"user": str(user["_id"])})

    return jsonify({"message": "User and associated tasks deleted"}), 200

# GET route - List all tasks for a specific user
@app.route('/todos', methods=['GET'])
@jwt_required()
def list_todos():
    current_user_id = get_jwt_identity()
    todos = list(todo_collection.find({"user": current_user_id}))
    return jsonify([serialize_todo(t) for t in todos])

# GET route - Fetch task by ID
@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = todo_collection.find_one({"_id": ObjectId(todo_id)})
    if todo:
        return jsonify(serialize_todo(todo))
    return jsonify({"error": "Task not found"}), 404

# POST route - Create new task (JWT protected)
@app.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
    current_user_id = get_jwt_identity()
    data = request.json
    if not data or "title" not in data:
        return jsonify({"error": "Incomplete data"}), 400

    data["completed"] = False
    data["user"] = current_user_id  # Associar task ao user autenticado

    result = todo_collection.insert_one(data)
    return jsonify({"id": str(result.inserted_id), "message": "Task created"}), 201

@app.route('/todos/<todo_id>', methods=['PUT'])
@jwt_required()
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

@app.route('/todos/<todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    result = todo_collection.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Task deleted"}), 200
    return jsonify({"error": "Task not found"}), 404

# POST route - User login with JWT using Flask-JWT-Extended
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not all(k in data for k in ("username", "password")):
        return jsonify({"error": "Username and password are required"}), 400

    user = users_collection.find_one({"username": data["username"]})
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    if bcrypt.checkpw(data["password"].encode('utf-8'), user["password"].encode('utf-8')):
        access_token = create_access_token(identity=str(user["_id"]))

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user_id": str(user["_id"]),
            "fullname": user["fullname"],
            "username": user["username"],
            "email": user["email"]
        }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')

from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Configura conexão com MongoDB local
client = MongoClient("mongodb+srv://joaompferreira00:<db_password>@cluster0.6rxdm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["sample_mflix"]
collection = db["UsersTodo"]

# Função para converter ObjectId em string
def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "fullname": user["fullname"],
        "email": user["email"],
        "password": user["password"]
    }

# Rota GET - Listar todos os usuários
@app.route('/users', methods=['GET'])
def list_users():
    users = list(collection.find())
    return jsonify([serialize_user(u) for u in users])

# Rota GET - Buscar usuário por username
@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = collection.find_one({"username": username})
    if user:
        return jsonify(serialize_user(user))
    return jsonify({"error": "Usuário não encontrado"}), 404

# Rota POST - Criar novo usuário
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or not all(k in data for k in ("username", "fullname", "email", "password")):
        return jsonify({"error": "Dados incompletos"}), 400

    if collection.find_one({"username": data["username"]}):
        return jsonify({"error": "Username já existe"}), 400

    result = collection.insert_one(data)
    return jsonify({"id": str(result.inserted_id), "message": "Usuário criado"}), 201

if __name__ == '__main__':
    app.run(debug=True)


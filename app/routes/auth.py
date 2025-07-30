from flask import Blueprint, request, jsonify
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta


auth_bp = Blueprint('auth', __name__)

import re

def generate_username(name):
    base_username = re.sub(r'\s+', '.', name.strip().lower())
    base_username = re.sub(r'[^a-z0-9\.]', '', base_username)  # remove caracteres especiais
    username = base_username
    counter = 1

    while User.query.filter_by(username=username).first():
        counter += 1
        username = f"{base_username}{counter}"

    return username


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get("name")
    role = data.get("role")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Usuário já existe com este e-mail"}), 400

    username = generate_username(name)

    hashed = generate_password_hash(password)
    user = User(username=username, password=hashed, name=name, email=email, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "msg": "Usuário criado com sucesso",
        "username": username
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Credenciais inválidas"}), 401

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=30))
    return jsonify(access_token=access_token), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "role": user.role.value
    }), 200

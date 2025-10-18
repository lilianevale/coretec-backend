import re
from flask import Blueprint, request, jsonify, render_template_string
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from app import mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


auth_bp = Blueprint('auth', __name__)


def generate_username(name):
    base_username = re.sub(r'\s+', '.', name.strip().lower())
    # remove caracteres especiais
    base_username = re.sub(r'[^a-z0-9\.]', '', base_username)
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
    user = User(username=username, password=hashed,
                name=name, email=email, role=role)
    db.session.add(user)
    db.session.commit()

    html_body = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f6f6f6;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="background-color: #003366; padding: 20px; color: white;">
                <h2>Bem-vindo ao Coretec!</h2>
            </div>
            <div style="padding: 20px; color: #333;">
                <p>Olá <strong>{name}</strong>,</p>
                <p>Seu cadastro foi realizado com sucesso no sistema <strong>Coretec</strong>! 🎉</p>
                <p>Aqui estão os seus dados de acesso:</p>
                <ul>
                    <li><strong>Usuário:</strong> {username}</li>
                    <li><strong>Email:</strong> {email}</li>
                </ul>
                <p>Estamos felizes em ter você conosco.</p>
                <p style="margin-top: 30px;">Atenciosamente,<br><strong>Equipe Coretec</strong></p>
            </div>
            <div style="background-color: #f0f0f0; padding: 10px; text-align: center; font-size: 12px; color: #777;">
                Este é um e-mail automático. Por favor, não responda.
            </div>
        </div>
    </div>
    """

    try:
        msg = Message(
            subject="🎉 Cadastro realizado com sucesso - Coretec",
            recipients=[email],
            html=html_body
        )
        mail.send(msg)
    except Exception as e:
        print("Erro ao enviar e-mail:", e)

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

    access_token = create_access_token(identity=str(
        user.id), expires_delta=timedelta(days=30))
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

serializer = URLSafeTimedSerializer("chave-secreta-reset-senha")


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "E-mail não encontrado"}), 404

    # Gera token válido por 1 hora
    token = serializer.dumps(email, salt="reset-password-salt")

    # altere para seu front real
    reset_link = f"http://localhost:3000/reset-password/{token}"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f6f6f6;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="background-color: #003366; padding: 20px; color: white;">
                <h2>Redefinição de senha - Coretec</h2>
            </div>
            <div style="padding: 20px; color: #333;">
                <p>Olá <strong>{user.name}</strong>,</p>
                <p>Recebemos um pedido para redefinir sua senha.</p>
                <p>Clique no botão abaixo para criar uma nova senha. Este link é válido por 1 hora.</p>
                <a href="{reset_link}" style="display:inline-block; background-color:#003366; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; margin-top:20px;">Redefinir senha</a>
                <p style="margin-top:20px;">Se você não solicitou, ignore este e-mail.</p>
            </div>
        </div>
    </div>
    """

    try:
        msg = Message(
            subject="🔑 Redefinição de senha - Coretec",
            recipients=[email],
            html=html_body
        )
        mail.send(msg)
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return jsonify({"msg": "Erro ao enviar e-mail"}), 500

    return jsonify({"msg": "E-mail de recuperação enviado com sucesso"}), 200


@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    try:
        email = serializer.loads(
            token, salt="reset-password-salt", max_age=3600)
    except SignatureExpired:
        return jsonify({"msg": "Token expirado"}), 400
    except BadSignature:
        return jsonify({"msg": "Token inválido"}), 400

    data = request.get_json()
    new_password = data.get("password")

    if not new_password or len(new_password) < 6:
        return jsonify({"msg": "Senha deve ter ao menos 6 caracteres"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"msg": "Senha redefinida com sucesso"}), 200

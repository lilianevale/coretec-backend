from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .models import db

def create_app():
    app = Flask(__name__)
    CORS(app)
    
     # Configuração do MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://u758915510_liliane:Liliane2025@193.203.175.84/u758915510_liliane'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuração do JWT
    app.config["JWT_SECRET_KEY"] = "Term228687535@"
    jwt = JWTManager(app)

    # Inicializa DB
    db.init_app(app)
    
    from .routes.magnel import magnel_bp
    from .routes.pretracao import pretracao_bp
    from .routes.ancoragem import ancoragem_bp
    from .routes.concreto import concreto_bp
    from .routes.tensao import tensao_bp
    from .routes.armadura import armadura_bp
    from .routes.fluencia import fluencia_bp
    from .routes.auth import auth_bp

    app.register_blueprint(magnel_bp)
    app.register_blueprint(pretracao_bp)
    app.register_blueprint(ancoragem_bp)
    app.register_blueprint(concreto_bp)
    app.register_blueprint(tensao_bp)
    app.register_blueprint(armadura_bp)
    app.register_blueprint(fluencia_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app

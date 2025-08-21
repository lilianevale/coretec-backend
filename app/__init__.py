from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from .models import db

mail = Mail()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
     # Configuração do MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://u758915510_liliane:Liliane2025@193.203.175.84/u758915510_liliane'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuração do JWT
    app.config["JWT_SECRET_KEY"] = "Term228687535@"
    jwt = JWTManager(app)
    
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Configuração do e-mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # ou outro servidor
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'coretectools.ufcat@gmail.com'  # coloque seu e-mail aqui
    app.config['MAIL_PASSWORD'] = 'legvkwgyjkducauk'     # app password ou senha real
    app.config['MAIL_DEFAULT_SENDER'] = 'ezequiel.pires082000@gmail.com'

    # Inicializa DB
    db.init_app(app)
    mail.init_app(app)
    
    from .routes.magnel import magnel_bp
    from .routes.pretracao import pretracao_bp
    from .routes.ancoragem import ancoragem_bp
    from .routes.concreto import concreto_bp
    from .routes.tensao import tensao_bp
    from .routes.fsarmadura import fsarmadura_bp
    from .routes.estadio1 import estadio1_bp
    from .routes.estadio2 import estadio2_bp
    from .routes.armadura import armadura_bp
    from .routes.fluencia import fluencia_bp
    from .routes.gerador_questoes import gerador_questoes_bp
    from .routes.auth import auth_bp

    app.register_blueprint(fsarmadura_bp)
    app.register_blueprint(estadio1_bp)
    app.register_blueprint(estadio2_bp)
    app.register_blueprint(magnel_bp)
    app.register_blueprint(pretracao_bp)
    app.register_blueprint(ancoragem_bp)
    app.register_blueprint(concreto_bp)
    app.register_blueprint(tensao_bp)
    app.register_blueprint(armadura_bp)
    app.register_blueprint(fluencia_bp)
    app.register_blueprint(gerador_questoes_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app

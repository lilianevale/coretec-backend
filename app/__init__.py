from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    from .routes.magnel import magnel_bp
    from .routes.pretracao import pretracao_bp
    from .routes.ancoragem import ancoragem_bp
    from .routes.concreto import concreto_bp
    from .routes.tensao import tensao_bp
    from .routes.armadura import armadura_bp
    from .routes.fluencia import fluencia_bp

    app.register_blueprint(magnel_bp)
    app.register_blueprint(pretracao_bp)
    app.register_blueprint(ancoragem_bp)
    app.register_blueprint(concreto_bp)
    app.register_blueprint(tensao_bp)
    app.register_blueprint(armadura_bp)
    app.register_blueprint(fluencia_bp)

    return app

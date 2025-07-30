from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class RoleEnum(enum.Enum):
    aluno = "aluno"
    professor = "professor"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.aluno)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
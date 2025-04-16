from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import timedelta

app = Flask(__name__)
app.secret_key = '12081978560097542'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Egor2002@localhost:5432/my_database'
app.config['JWT_SECRET_KEY'] = '560097542'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=10)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(minutes=60)

jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)


from app.web import route
from app.database import model
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a5bb2099e164a5c9dcc613a4ddc015d3'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_mang = LoginManager(app)
login_mang.login_view = 'login'
login_mang.login_message_category = 'ingo'

from Application import routes
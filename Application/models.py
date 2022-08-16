from Application import db, login_mang, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as ser

@login_mang.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    img = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='autor', lazy=True)

    def get_reset_token(self,expires_sec=1800):
        s = ser(app.config['SECRET_KEY'], expires_sec)
        return s.dump({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = ser(app.config['SECRET_KEY'])
        try:
            user_id = s.load(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.img}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    up_votes = db.Column(db.Integer, default=0)
    down_votes = db.Column(db.Integer, default=0)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comms = db.relationship('Post')



    def __repr__(self):
        return f"Pot('{self.title}', '{self.date}')"

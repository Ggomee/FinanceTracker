from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app #pulling this from __init__ file
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True) #relationship not a column

    def get_reset_token(self, expires_sec=1800):    #method review object oriented series Youtube?
        s= Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod  #telling python not to expect "self" argument
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    start_year=db.Column(db.Integer, nullable=False)
    start_month = db.Column(db.Integer, nullable=False)  #is this better if db.Date? SQL Alchemy mentioned issue with sqlite
    inflation=db.Column(db.Integer, nullable=False)
    withdrawal_rate = db.Column(db.Integer, nullable=False)
    start_age = db.Column(db.Integer)
    retirement_age=db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #this is a db column

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
###RECEVIED WARNING FOR DECIMAL TYPE CHECK LATER!
class Details(db.Model):
    details_id = db.Column(db.Integer, primary_key=True)
    category=db.Column(db.String(100), nullable=False)
    date_entry_year=db.Column(db.Integer, nullable=False)
    date_entry_month=db.Column(db.Integer, nullable=False)
    entry_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    perc_change=db.Column(db.Integer)
    contrib = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False) #this is a db column
#    Do i need a back reference?
#    How does the post id connect? just foreignkey enough?
    def __repr__(self):
        return f"Post('{self.category}', {self.entry_name}', {self.value}','{self.post_id}')"

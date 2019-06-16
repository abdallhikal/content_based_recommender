#import necessary libs  
from api_rec import db, login_manager
from flask_login import UserMixin

#a loader function that get the user form the database 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Data(db.Model):
    '''get data of user save it in (data) 
    and save the vectorizor in (data_mat)'''
    id = db.Column(db.Integer, primary_key=True) #integer field
    data = db.Column(db.PickleType, nullable=False) #pickleType field 
    data_mat = db.Column(db.PickleType, nullable=False)
    model_mat = db.Column(db.PickleType)
    data_name = db.Column(db.String(150), nullable=False, unique=True)
    data_link = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)

    def __repr__(self):
        return f"Data('{self.data}')"

class User(db.Model, UserMixin):
    '''save the user name in(user_name) and make one to many on (data)'''
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(30), unique=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(13), unique=True)
    email = db.Column(db.String(),unique=True)
    roll = db.Column(db.Integer)
    #image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    Data = db.relationship('Data', backref='user', lazy='dynamic')
    def __repr__(self):
        return f"User('{self.username}')"



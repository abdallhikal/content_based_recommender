#import packages 
from flask import request, jsonify, abort, render_template, url_for, flash, redirect, request, abort
from api_rec.models import User, Data
from api_rec import app, db, bcrypt
from api_rec.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, UpdataPostForm
from flask_login import login_user, current_user, logout_user, login_required
import uuid
import jwt
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd 
from sqlalchemy import exc

#define the home page for each user 
@app.route("/")
@app.route("/home")
@login_required
def home():
    data = Data.query.filter_by(user_id = current_user.get_id())
    return render_template('home.html', posts=data)

#a function for an about page 
@app.route("/about")
def about():
    return render_template('about.html', title='About')

#regester functions for registeration
@app.route("/register",methods=['POST','GET'])
def register():
    if current_user.is_authenticated: #if user is logged in redirect him to the home page 
        return redirect(url_for('home'))
    form = RegistrationForm() #define the registration 
    if form.validate_on_submit(): #if the form inputs are valid create  a new user 
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, public_id=str(uuid.uuid4()), phone=form.phone.data)
        try:
            #ave the new user in the database 
            db.session.add(user)
            db.session.flush()
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            db.session.flush('Exception will be raised')
            flash('Something happend please sign up again or contact us ', 'danger')
            return redirect( url_for('register'))

        db.session.commit()
        #flash a message that the user has been created 
        flash(f'Account create for { form.username.data }!', 'success')
        return redirect(url_for('login'))
    #else return the registeration template  
    return render_template('register.html', title='Register', form=form)
#define a log in function 
@app.route("/login",methods=['POST','GET'])
def login():
    #if that user is logged in then return him back to the home page 
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #getting the form of the log in page 
    form = LoginForm()
    if form.validate_on_submit():
        #if the inputs are valid the process the request 
        user = User.query.filter_by(email=form.email.data).first()
        if user :
            #if the user and hashed password are correct then log him
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else: 
                #if not the flash him a message that the password is not correct 
                flash('Worng password','danger')
        else:
            #if the user does not exist then flash him "Worng Email"
            flash('Worng Email','danger')
        #flash(f'Account create for { form.username.data }!', 'success')
    else:


        return render_template('login.html', title='Login', form=form)
#simple log out function 
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
#update user account informations 
@app.route("/account", methods=['POST','GET'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    #image_file = url_for('static', filename='profile_image/' + current_user.image_file)
    return render_template('account.html', title='account', form=form)

#helper tf-idf function 
def factorization(data):
    tfidf = TfidfVectorizer()
    #name = str(name)+".pkl"
    tfidfmat = tfidf.fit_transform(data.movie_tags)
    #return pickle.dump(tfidfmat,open(name,"wb"))
    return tfidfmat

#getting new training data from logged in users 
@app.route("/data/new", methods=['POST','GET'])
@login_required
def new_data():
    form = PostForm()
    if form.validate_on_submit():
        try:
            #get data from url 
            data_url =form.data_url.data
            try :
                #read the data as pandas dataframe 
                data_pd = pd.read_json(data_url)
                try:
                    #vectorize the input data 
                    data_mat = factorization(data_pd)
                    #save the data in the data base 
                    data = Data(data_name=form.name.data, data_mat=data_mat, data=data_pd, user_id = int(current_user.get_id()),data_link=data_url)
            #data_ = Data(data=c, data_mat=data, user_id=user_id, data_name = data_name, data_link=url)
                    db.session.add(data)
                    db.session.commit()
                    flash('Your data has been created!','success')
                    return redirect(url_for('home'))
                except:
                    #if the data not in the shape that the model expect the flash him this message 
                    flash('Please send data in shape','danger')
            except:
                #if the data not js then flash this message 
                flash('Please send json data ','danger')

        except:
            flash('Not valid url','danger')
            
    return render_template('create_data.html', title='new_data',
     form=form, legend='New Project')

@app.route("/test")
@login_required
def test():
    
    current_user.Data
#function to get a spicefic data 
@app.route("/post/<int:post_id>", methods=['POST','GET'])
@login_required
def post(post_id):
   
    post = Data.query.get_or_404(post_id)
    return render_template('post.html', title=post.data_name, post=post)
#update a specific data  
@app.route("/post/<int:post_id>/update", methods=['POST','GET'])
@login_required
def post_update(post_id):
    
    post = Data.query.get_or_404(post_id)
    if post.user_id != int(current_user.get_id()):
        abort (403)
    form = UpdataPostForm()
    if form.validate_on_submit():
        try:
            post.data_name = form.name.data
            post.data_link = form.data_url.data
            data_url =form.data_url.data
            
            data_pd = pd.read_json(data_url)
            if data_pd.shape == (0,0):
                flash("There is no data send")
                return render_template('create_data.html', title='Update Title', post=post,
    form=form, legend='Update Project')
            else :
                try:
                    data_mat = factorization(data_pd)
                    post.data = data_pd
                    post.data_mat=data_mat
                    try:# post = Data(data_name=form.name.data, data_mat=data_mat, data=data_pd, user_id = int(current_user.get_id()),data_link=data_url)
                        db.session.commit()
                        flash('Your data have been update','success')
                        return redirect( url_for('post',post_id=post.id))
                    except:
                        flash('this name is taken', 'danger')
                        return render_template('create_data.html', title='Update Title', post=post,
        form=form, legend='Update Project')
                except:
                    flash('Data not in shape', 'danger')
                    return render_template('create_data.html', title='Update Title', post=post,
        form=form, legend='Update Project')
        except: 
            flash('Not valid url', 'danger')
            return render_template('create_data.html', title='Update Title', post=post,
        form=form, legend='Update Project')

    elif request.method == 'GET':
        form.name.data = post.data_name
        form.data_url.data = post.data_link
    
    return render_template('create_data.html', title='Update Title', post=post,
    form=form, legend='Update Project')

#simple delete function 
@app.route("/post/<int:post_id>/delet", methods=['POST'])
@login_required
def post_delete(post_id):
        
    post = Data.query.get_or_404(post_id)
    if post.user_id != int(current_user.get_id()):
        abort (403)
    db.session.delete(post)
    db.session.commit()
    flash('Your data have been Deleted','success')
    return redirect(url_for('home'))



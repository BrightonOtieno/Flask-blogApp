from flaskblog.forms import UserRegistrationForm,UserLoginForm,UserAccountForm
from flaskblog.models import User,Post
from flask import url_for,render_template,flash,redirect,request
from flaskblog import app,bcrypt,db
from flask_login import login_user ,current_user, logout_user,login_required
from PIL import Image
import secrets
import os

@app.route('/')
@app.route('/home')
def home_page():
    
    return render_template('index.html')


@app.route('/about')
def about_page():
    
    return render_template('about.html')


@app.route('/registration',methods=['GET','POST'])
def user_registration_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
        email=form.email.data,
        password = hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data}  Your Account has been created successfully you can now login','success')
        return redirect(url_for('user_login_page'))
    return render_template('register.html',form=form)


@app.route('/login',methods=['GET','POST'])
def user_login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

    form = UserLoginForm()
    #print(form.username.data)
    #print(form.password.data)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login was successful ','success')
            return redirect(next_page) if next_page else redirect(url_for('home_page'))
        
        else:
            flash('Login was unsuccessful please check your Email and Password','danger')
        
    return render_template('login.html',form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('user_login_page'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pic',picture_file_name)

    output_size = (140,140)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    #i.save(picture_path)
    
    i.save(picture_path)

    return picture_file_name


@app.route('/account',methods=['GET','POST'])
@login_required
def account():
    image_file = url_for('static', filename='profile_pic/'+ current_user.image_file)
    form = UserAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Profile has been Updated successfully','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', image_file=image_file,form=form)




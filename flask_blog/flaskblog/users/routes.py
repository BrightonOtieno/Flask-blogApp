from flask_login import login_user ,current_user, logout_user,login_required
from flaskblog.models import Post,User
from flask import url_for,render_template,flash,redirect,request,abort,Blueprint
from flaskblog import db,bcrypt
from flaskblog.users.forms import  UserRegistrationForm, UserLoginForm,UserAccountForm,RequestResetForm,ResetPasswordForm
from flaskblog.users.utils import send_reset_email,save_picture

users = Blueprint('users',__name__)


@users.route('/registration',methods=['GET','POST'])
def user_registration_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
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
        return redirect(url_for('users.user_login_page'))
    return render_template('register.html',form=form)


@users.route('/login',methods=['GET','POST'])
def user_login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))

    form = UserLoginForm()
    #print(form.username.data)
    #print(form.password.data)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login was successful ','success')
            return redirect(next_page) if next_page else redirect(url_for('main.home_page'))
        
        else:
            flash('Login was unsuccessful please check your Email and Password','danger')
        
    return render_template('login.html',form=form)

@users.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('users.user_login_page'))




@users.route('/account',methods=['GET','POST'])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', image_file=image_file,form=form)





    
@users.route('/user/<string:username>')
def user_post(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
    return render_template('user_posts.html',posts=posts,user=user)





@users.route('/reset-password-request',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        flash('Must be logged out in order to request for password reset','secondary')
        return redirect(url_for('main.home_page'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Instructions on how to reset your password has been sent to your email','info')
        return redirect(url_for('users.user_login_page'))
    return render_template('reset_request.html',title='Password Reset Request',form = form)

@users.route('/reset-password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        flash('Must be logged out in order to request for password reset','secondary')
        return redirect(url_for('main.home_page'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an Invalid Or Expired Token','warning')
        return redirect(url_for('users.reset_request'))
    else:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = form.password.data
            db.session.commit()
            flash(f'{form.username.data}  Your Password was updated successfully you can now login','success')
            return redirect(url_for('users.user_login_page'))

    return render_template('reset_password.html',title='Password Reset ',form = form)
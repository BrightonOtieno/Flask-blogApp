from flaskblog.forms import UserRegistrationForm,UserLoginForm,UserAccountForm,PostCreateForm,RequestResetForm,ResetPasswordForm
from flaskblog.models import User,Post
from flask import url_for,render_template,flash,redirect,request,abort
from flaskblog import app,bcrypt,db,mail
from flask_login import login_user ,current_user, logout_user,login_required
from PIL import Image
import secrets
import os
from flask_mail import Message

@app.route('/')
@app.route('/home')
@login_required
def home_page():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
    return render_template('index.html',posts=posts)




@app.route('/user/<string:username>')
def user_post(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
    return render_template('user_posts.html',posts=posts,user=user)


@app.route('/post/new',methods = ['POST','GET'])
@login_required
def new_post():
    form = PostCreateForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully','success')
        return redirect(url_for('home_page'))
    return render_template('create_post.html',form=form,legend='Create Post')



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


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template('post.html',post=post,title=post.title)


@app.route("/post/<int:post_id>/update",methods =['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    # if the current user is not the author
    if post.author != current_user:
        abort(403)
    else: # if current user is the author 
        form = PostCreateForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                post.title = form.title.data
                post.content = form.content.data
                db.session.commit()
                flash('Your Post was updated successfully','success')
                return redirect(url_for('post',post_id = post.id))
        else:
            form.title.data = post.title 
            form.content.data = post.content

    return render_template('create_post.html',form=form,title="post-update",legend='Update Post')


@app.route("/post/<int:post_id>/delete",methods =['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # if the current user is not the author
    if post.author != current_user:
        abort(403)
    else: # if current user is the author 
        db.session.delete(post)
        db.session.commit()
        flash('Your Post was successfully deleted','success')
        return redirect(url_for('home_page'))


def send_reset_email(user):
    token = User.get_reset_token(user)
    msg = Message('Password Reset Request',sender='brightonhoods@gmail.com',recipients=[user.email])

    msg.body = f'''To reset your Password,visit the following link:
{url_for('reset_token',token=token,_external=True)}
If you did not make the request please IGNORE the email and no changes will be made
    '''
    mail.send(msg)



@app.route('/reset-password-request',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        flash('Must be logged out in order to request for password reset','secondary')
        return redirect(url_for('home_page'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Instructions on how to reset your password has been sent to your email','info')
        return redirect(url_for('user_login_page'))
    return render_template('reset_request.html',title='Password Reset Request',form = form)

@app.route('/reset-password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        flash('Must be logged out in order to request for password reset','secondary')
        return redirect(url_for('home_page'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an Invalid Or Expired Token','warning')
        return redirect(url_for('reset_request'))
    else:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = form.password.data
            db.session.commit()
            flash(f'{form.username.data}  Your Password was updated successfully you can now login','success')
            return redirect(url_for('user_login_page'))

    return render_template('reset_password.html',title='Password Reset ',form = form)
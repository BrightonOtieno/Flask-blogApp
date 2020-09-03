from flask_login import login_user ,current_user, logout_user,login_required
from flaskblog.models import Post
from flask import url_for,render_template,flash,redirect,request,abort,Blueprint
from flaskblog import db
from flaskblog.posts.forms import  PostCreateForm


posts = Blueprint('posts',__name__)



@posts.route('/post/new',methods = ['POST','GET'])
@login_required
def new_post():
    form = PostCreateForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully','success')
        return redirect(url_for('main.home_page'))
    return render_template('create_post.html',form=form,legend='Create Post')




@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template('post.html',post=post,title=post.title)


@posts.route("/post/<int:post_id>/update",methods =['GET','POST'])
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
                return redirect(url_for('posts.post',post_id = post.id))
        else:
            form.title.data = post.title 
            form.content.data = post.content

    return render_template('create_post.html',form=form,title="post-update",legend='Update Post')


@posts.route("/post/<int:post_id>/delete",methods =['POST'])
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
        return redirect(url_for('main.home_page'))


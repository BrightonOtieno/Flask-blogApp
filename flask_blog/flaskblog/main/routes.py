from flask import Blueprint,render_template,request
from flaskblog.models import Post
from flask_login import login_required
main = Blueprint('main',__name__)




@main.route('/')
@main.route('/home')
@login_required
def home_page():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
    return render_template('index.html',posts=posts)
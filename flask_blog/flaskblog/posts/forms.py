from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField
from wtforms.validators import DataRequired

class PostCreateForm(FlaskForm):
    title = StringField('title',validators=[DataRequired()])
    content =TextAreaField('content',validators=[DataRequired()]) 
    submit = SubmitField('post')

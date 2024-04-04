from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
class SearchForm(FlaskForm):
    classroom = StringField('Classroom')
    submit = SubmitField('Search')
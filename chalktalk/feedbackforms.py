from flask_wtf import FlaskForm
from wtforms import TextAreaField, RadioField, SubmitField


class Feedbackform(FlaskForm):
    rating = RadioField('Hvor mye forstod du av ', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    comment = TextAreaField("Eventuelle kommentarer om temaet:")
    submit = SubmitField("Lagre")
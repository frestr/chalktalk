from flask_wtf import Form
from wtforms import TextAreaField, RadioField, SubmitField


class Feedbackform(Form):
    rating = RadioField('Hvor mye forstod du av tema', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    comment = TextAreaField("Message")
    submit = SubmitField("Lagre")
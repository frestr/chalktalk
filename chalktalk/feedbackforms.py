from flask_wtf import FlaskForm
from wtforms import TextAreaField, RadioField, SubmitField


class Feedbackform(FlaskForm):
    rating = RadioField('Forståelse', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    comment = TextAreaField("Kommentar")
    submit = SubmitField("Lagre")
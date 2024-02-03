from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, RadioField, TextAreaField
from wtforms.validators import InputRequired, EqualTo, Length


class RegistrationForm(FlaskForm):
    user = StringField("User Name: ", validators=[
                       InputRequired(), Length(min=2, max=30)])
    password = PasswordField("Password: ", validators=[
                             InputRequired(), Length(min=6)])
    password2 = PasswordField("Confirm Password: ",
                              validators=[InputRequired(), EqualTo("password")])
    email = StringField("Email: ", validators=[InputRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    user = StringField("User Name: ")
    password = PasswordField("Password: ")
    submit = SubmitField("Login")


class ChoiceForm(FlaskForm):
    language = SelectField("Language choice: ",
                           choices=["English", "French", "Germany"],
                           validators=[InputRequired()])
    section = RadioField("Section choice: ",
                         choices=["Rear Mezzanine",
                                  "Front Mezzanine", "Orchestra"],
                         default="Rear Mezzanine")
    seat = SelectField("Seat choice: ",
                       choices=["A", "B", "C", "D", "E"],
                       validators=[InputRequired()])


class SearchForm(FlaskForm):
    name = StringField("Name:")
    date = StringField("Date:")
    submit = SubmitField("Find Tickets")


class ReviewForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Content", validators=[InputRequired()])
    submit = SubmitField("Post")


class FilterForm(FlaskForm):
    filter = RadioField("Sorted by: ",
                        choices=["Price(low to high)",
                                 "Price(high to low)", "Show Date"],
                        default="Price(low to high)")
    submit = SubmitField("Apply Filter")


class PayForm(FlaskForm):
    pay = SelectField("Payment choice: ",
                      choices=["PayPal", "Google Pay", "Credit Card"],
                      default="PayPal")


class ContactForm(FlaskForm):
    user = StringField("User Name", validators=[
        InputRequired(), Length(min=2, max=30)])
    email = StringField("Email", validators=[InputRequired()])

    topic = SelectField("Topic",
                        choices=["I have a question about the show",
                                 "I have a question about tickets", "I have a question about my order", "I need help with something else"],
                        default="I have a question about the show")
    message = TextAreaField("Message", validators=[InputRequired()])

    submit = SubmitField("Submit")

class CustomerForm(FlaskForm):
    filter_customer = SelectField("Select Topic", choices=["I have a question about the show","I have a question about tickets", "I have a question about my order", "I need help with something else"], default="I have a question about the show")
    submit = SubmitField("Apply Filter")

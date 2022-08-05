from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, PasswordField, TextAreaField, SelectField, RadioField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Length
from datetime import datetime, timedelta
from wtforms.fields.html5 import EmailField, TimeField, DateField, DateTimeField

class RegistrationForm(FlaskForm):
    user_id = StringField("User Id:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm Password:",  validators=[InputRequired(),
                        EqualTo("password")])
    fname = StringField('First Name:', validators=[InputRequired()])
    lname = StringField('Last Name:', validators=[InputRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    user_id = StringField("User Id:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class RequestForm(FlaskForm):
    food = StringField("Enter request: ", validators=[InputRequired(), Length(min=5)])
    submit = SubmitField("Submit")

class ReviewForm(FlaskForm):
    food = SelectField("Food: ", validators=[InputRequired()])
    review = TextAreaField("Leave a review below.", validators=[InputRequired()])
    submit = SubmitField("Submit")

class OrderForm(FlaskForm):
    defo = datetime.now() + timedelta(days=7)
    date = DateField("Date of Delivery:* ", validators=[InputRequired()], default=defo)
    time = TimeField("Time of Delivery:*", validators=[InputRequired()], format='%H:%M', default=(datetime.now().replace(hour=13, minute=00)))
    info = TextAreaField('Additional Info: ')
    first_line = StringField("Address Line 1*:", validators=[InputRequired()], render_kw={"placeholder": "House number, Address Line"})
    sec_line = StringField("Adress Line 2: ")
    town = StringField("Town: ", render_kw={"placeholder": "Town"})
    county = StringField("County:*", validators=[InputRequired()], render_kw={"placeholder": "County"})
    eircode = StringField('Eircode:* ', validators=[InputRequired()], render_kw={"placeholder": "ex: A65 F4E2"})
    submit = SubmitField("Pay")

class AddForm(FlaskForm):
    name = StringField("Name:* ", validators=[InputRequired()])
    price = IntegerField("Price:* ", validators=[InputRequired()])
    description = TextAreaField("Description: ")
    allergens = StringField("Allergens: ")
    var = StringField('Varieties: ')
    submit = SubmitField("Add")

class RemoveForm(FlaskForm):
    Id = SelectField("Order Id", validators=[InputRequired()])
    submit = SubmitField('Remove')

class EditForm(FlaskForm):
    Id = SelectField("Review Id", validators=[InputRequired()])
    review = TextAreaField("Review", validators=[InputRequired()])
    submit = SubmitField("Edit")

class EditFForm(FlaskForm):
    name = SelectField("Food Name", validators=[InputRequired()])
    price = IntegerField("Price")
    description = TextAreaField("Description")
    submit = SubmitField("Update")

class UpdateForm(FlaskForm):
    Id = SelectField('Order Id', validators=[InputRequired()])
    status = SelectField('Order Id', choices = [('', ''), ('RECEIVED','Received'), 
                        ('ON THE WAY', 'On the way'), ('PROCESSING', 'Processing'), ('DONE', 'Done')])
    submit = SubmitField('Update')

class UpdateRForm(FlaskForm):
    Id = SelectField('Request Id', validators=[InputRequired()])
    submit = SubmitField('Update')

class AgreeForm(FlaskForm):
    agree = BooleanField("There are no", validators=[InputRequired()]) 
    submit = SubmitField("Submit")

class CancelForm(FlaskForm):
    cancel = BooleanField("Cancel Order")
    submit = SubmitField("Cancel")

class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")

class PassForm(FlaskForm):
    old_password = PasswordField("Old Password:", validators=[InputRequired()])
    npassword = PasswordField("New Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm New Password:",  validators=[InputRequired(),
                        EqualTo("npassword")])
    submit = SubmitField("Submit")

class UserForm(FlaskForm):
    user_id = StringField("New User Id:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class NameForm(FlaskForm):
    password = PasswordField("Password:", validators=[InputRequired()])
    fname = StringField('First Name:', validators=[InputRequired()])
    lname = StringField('Last Name:', validators=[InputRequired()])
    submit = SubmitField("Submit")

class ProceedForm(FlaskForm):
    yesno = BooleanField('''Orders are no cancellation. 
                Payments can be made in advance. In failure to pay at delivery time
                will result to angry mama. Click to proceed.''')
    submit = SubmitField('Proceed')
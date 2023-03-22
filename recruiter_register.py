from mailbox import Message

from flask import Flask, render_template, request, flash, url_for, Blueprint, current_app
from wtforms import Form, StringField, validators, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from database import get_db

recruiter_blueprint = Blueprint('recruiter_blueprint', __name__)

sent_otp = 652013
login_email = []
user_details = []


def email_validators(form, field):
    domains_not_allowed = ['yahoo.com', 'gmail.com']
    newdata = field.data.split('@')[-1]
    print(newdata)
    if newdata in domains_not_allowed:
        print("Error Generated")
        field.errors.append("Please Enter your professional mail")
        return False
    return True


class CreateData(FlaskForm):
    name = StringField("name", validators=[InputRequired()])
    mail = EmailField("Email", validators=[InputRequired(), email_validators])
    password = PasswordField("password", validators=[InputRequired()])
    conformpassword = PasswordField("Password", validators=[InputRequired()])
    company = StringField("Company", validators=[InputRequired()])
    submit = SubmitField("Submit")


class Submit_otp(Form):
    otp = StringField("OTP", validators=[InputRequired()])
    submit = SubmitField("submit")


@recruiter_blueprint.route("/recruiter_register", methods=["POST", "GET"])
def recruiter_register():
    form = CreateData()  # request.form is required
    domain_not_allowed = ['yahoo.com', 'gmail.com']
    if form.validate_on_submit():
        print(form.mail.data)
        db = get_db()
        if_exist = db.execute("SELECT EXISTS (SELECT 1 FROM user WHERE mail = ?)", (form.mail.data,))
        row = if_exist.fetchone()
        exists = row[0] if row is not None else 0
        print(type(exists))
        print(exists)
        if exists == 1:
            exist_msg = "User Already Exsits!"
            return render_template('recruiter_register.html', form=form, exist_msg=exist_msg)
        password = form.password.data
        conform = form.conformpassword.data
        if password != conform:
            pass_error = "Passwords Doesn't Match"
            return render_template('recruiter_register.html', form=form, pass_error=pass_error)
        login_email.append(form.mail.data)
        user_details.append(form.name.data)
        user_details.append(form.mail.data)
        user_details.append(form.password.data)
        user_details.append(form.company.data)
        dmail = login_email[0]
        msg = Message("OTP To Authenticate", sender="thrinadh.manubothu@gmail.com", recipients=[dmail])
        msg.body = f"Your OTP to Authenticate: {sent_otp}"
        with current_app.app_context():
            current_app.extensions['mail'].send(msg)

        return render_template('recruiter_authentication.html')
    return render_template('recruiter_register.html', form=form)


@recruiter_blueprint.route('/recruiter_validate-email/', methods=["POST", "GET"])
def validate():
    dmail = login_email[0]
    login_email.pop()
    #msg = Message("OTP To Authenticate", sender="thrinadh.manubothu@gmail.com", recipients=[dmail])
    #msg.body = f"Your OTP to Authenticate: {sent_otp}"
    #with current_app.app_context():
    #    current_app.extensions['mail'].send(msg)
    received_otp = request.args.get("otp")
    if received_otp == str(sent_otp):
        print("OTP Successful")
        with current_app.app_context():
            db = get_db()
            name = user_details[0]
            print(name)
            mail = user_details[1]
            password = user_details[2]
            company = user_details[3]
            db.execute("insert into user (name,mail,password,type,company) values (?,?,?,?,?)",
                       [name, mail, password, 1, company])
            db.commit()
            user_details.clear()
            print(user_details)
            success = True
        return render_template('auth_successful.html',success=success)
    else:
        auth_not = "Not Successful"
        return render_template('auth_successful.html',auth_not=auth_not)
    # return render_template('authentication.html')

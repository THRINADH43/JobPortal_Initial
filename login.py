from flask import Flask, render_template, request, flash, url_for, Blueprint, current_app, session, redirect, request
from wtforms import Form, StringField, validators, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from database import get_db
from flask_session import Session
from jobseeker_home import jobseeker_home
from recruiter_home import recruiter_home

login_blueprint = Blueprint('login_blueprint', __name__)
login_blueprint.register_blueprint(jobseeker_home, url_prefix='/login')
login_blueprint.register_blueprint(recruiter_home, url_prefix='/login')

sent_otp = 652013


class CreateData(FlaskForm):
    mail = EmailField("Email", validators=[InputRequired()])
    password = StringField("Password", validators=[InputRequired()])
    submit = SubmitField("Submit")


@login_blueprint.route('/login', methods=["GET", "POST"])
def login():
    form = CreateData()
    mail = request.form.get('mail')
    if form.validate_on_submit():
        # mail = form.mail.data
        password = form.password.data
        with current_app.app_context():
            db = get_db()
            cur = db.execute('select id,password,type from user where  mail = ?', [mail])
            user_result = cur.fetchone()
            print(user_result)
            print(type(user_result))
            if user_result is not None:
                if user_result['password'] == password:
                    print("Password Validated")
                    # session['logged_in'] = True
                    session['id'] = user_result['id']
                    session['type'] = user_result['type']
                    user_id = session['id']
                    print(user_id)
                    if user_result['type'] == 1:
                        return redirect(url_for('login_blueprint.recruiter_home.recruiter_home_page'))
                    else:
                        return redirect(url_for('login_blueprint.jobseeker_home.jobseeker_home_page'))
                else:
                    msg = "Wrong Password/User Not Found"
                    return render_template('login.html',form=form,msg=msg)
            print(session.get('id'))
    return render_template('login.html', form=form)


@login_blueprint.route('/forgotpassword', methods=["POST", "GET"])
def forgotpassword():
    change = True
    if request.method == "POST":
        dmail = request.form.get('email')
        print(request.form.get('email'))
        db = get_db()
        email_found = db.execute('select * from user where mail = ?', [request.form.get('email')]).fetchone()
        print(type(email_found))
        if email_found is None:
            print("No Such User Found")
            msg = "No Such User Found"
            return render_template('change_password.html', msg=msg, change=change)
        else:
            found = True
            session['mail'] = dmail
            msg = Message("OTP To Authenticate", sender="thrinadh.manubothu@gmail.com", recipients=[dmail])
            msg.body = f"Your OTP to Authenticate: {sent_otp}"
            with current_app.app_context():
                current_app.extensions['mail'].send(msg)
            return render_template('change_password.html', found=True)
    return render_template('change_password.html', change=change)


@login_blueprint.route('/forgotpasswordotp', methods=["POST", "GET"])
def forgotpasswordotp():
    if request.method == "POST":
        print(request.form.get('otp'))
        received = request.form.get('otp')
        print(received)
        print(type(received))
        if int(received) != sent_otp:
            msg = "OTP Doesn't Match"
            return render_template('change_password.html', msg=msg)
        else:
            return render_template('change_password_data.html')
    msg = "Please check with the details submitted."
    return render_template('change_password.html', msg=msg)


@login_blueprint.route('/updatepassword', methods=["POST", "GET"])
def updatepassword():
    if request.method == "POST":
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if password1 != password2:
            msg = "Passwords Doesn't Match"
            return render_template('change_password_data.html', msg=msg)
        else:
            db = get_db()
            db.execute("update user set password = ? where mail = ?", [password1, session['mail']])
            db.commit()
            session.pop('mail')
            message = "Your password Has been Updated"
            return render_template('change_password_data.html', message=message)
    return render_template('change_password_data.html')

from mailbox import Message
from flask import Flask, render_template, request, flash, url_for, Blueprint, current_app,session
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, validators, PasswordField, SubmitField, EmailField, FileField, SelectField, \
    RadioField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from database import get_db
import os

upload_path = './resumes'

if not os.path.exists(upload_path):
    os.mkdir(upload_path)

jobseeker_blueprint = Blueprint('jobseeker_blueprint', __name__)

sent_otp = 652013
login_email = []
user_details = []
userid = []

allowed_extensions = {'pdf'}


class CreateData(FlaskForm):
    name = StringField("name", [validators.InputRequired()])
    mail = EmailField("Email", [validators.InputRequired()])
    password = PasswordField("password", [validators.InputRequired()])
    conformpassword = PasswordField("Conform",[validators.InputRequired()])
    submit = SubmitField("Submit")


class Submit_otp(Form):
    otp = StringField("OTP", [validators.InputRequired()])
    submit = SubmitField("submit")


class Userdetails(FlaskForm):
    jobtype = RadioField("Type", choices=[('Full Time', 'Full Time'), ('Part Time', 'Part Time'), ('Intern', 'Intern')]
                         , default='Full Time')
    bio = StringField("description", [validators.InputRequired()])
    skill1 = SelectField('skill 1',
                         choices=[('None', 'select from the below'), ('python', 'python'), ('java', 'java'),
                                  ('c++', 'c++'), ])
    skill2 = SelectField('skill 2',
                         choices=[('None', 'select from the below'), ('mysql', 'mysql'), ('mongodb', 'mondogb')])
    location1 = SelectField('Location 1',
                            choices=[('None', 'Select from below'), ('Hyderabad', 'Hyderabad'),
                                     ('Banglore', 'Banglore'), ('Chennai', 'Chennai'), ('Mumbai', 'Mumbai')])
    location2 = SelectField('Location 2',
                            choices=[('None', 'Select from below'), ('Hyderabad', 'Hyderabad'), ('Chennai', 'Chennai'),
                                     ('Banglore', 'Banglore'), ('Mumbai', 'Mumbai')])
    remote = RadioField("Remote", choices=[('yes', 'yes'), ('no', 'no')], default='no')
    occupation = SelectField("I am a", choices=[("None", "Select from below"), ("Student", "Student"),
                                                ("Professional", "Professional")])
    graduation_year = SelectField("Graduation Year",
                                  choices=[("None", "None"), ("2024", "2024"), ("2025", "2025"), ("2026", "2026")])
    experience = SelectField("Years of Experience",
                             choices=[('None', 'Select from below'), ('0-2', '0-2'), ('2-5', '2-5'),
                                      ('5-8', '5-8'), ('8+', '8+')])
    previous_experience = StringField("PreviousExperience", [validators.Length(min=10, max=100)])
    file = FileField("Upload a PDF file")
    githublink = StringField("GitHub Link", [validators.length(min=10, max=2500)])
    linkedinlink = StringField("Linkedin Link", [validators.Length(min=10, max=2500)])
    college = StringField("College", [validators.Length(min=10, max=50)])
    submit = SubmitField('submit')


@jobseeker_blueprint.route("/jobseeker_register", methods=["POST", "GET"])
def jobseeker_register():
    form = CreateData()  # request.form is required
    print("Route Entered Here")
    #if request.method == "POST":
    if form.validate_on_submit():
        print("Getting Reply from request")
        print(form.mail.data)
        mail = form.mail.data
        db = get_db()
        if_exist = db.execute("SELECT EXISTS (SELECT 1 FROM user WHERE mail = ?)", (form.mail.data,))
        row = if_exist.fetchone()
        exists = row[0] if row is not None else 0
        print(type(exists))
        print(exists)
        if exists == 1:
            exist_msg = "User Already Exsits!"
            return render_template('jobseeker_register.html',form=form,exist_msg=exist_msg)
        password = form.password.data
        conform = form.conformpassword.data
        if password != conform:
            pass_error = "Passwords Doesn't Match"
            return render_template('jobseeker_register.html',form=form,pass_error=pass_error)
        login_email.append(form.mail.data)
        user_details.append(form.name.data)
        user_details.append(form.mail.data)
        user_details.append(form.password.data)
        dmail = login_email[0]
        msg = Message("OTP To Authenticate", sender="connectcareer78@gmail.com", recipients=[dmail])
        msg.body = f"Your OTP to Authenticate: {sent_otp}"
        with current_app.app_context():
            current_app.extensions['mail'].send(msg)
        return render_template('jobseeker_authentication.html')
    return render_template('jobseeker_register.html', form=form)


@jobseeker_blueprint.route('/jobseeker_validate-email/', methods=["POST", "GET"])
def validate():
    dmail = login_email[0]
    login_email.pop()
    #msg = Message("OTP To Authenticate", sender="connectcareer78@gmail.com", recipients=[dmail])
    #msg.body = f"Your OTP to Authenticate: {sent_otp}"
    #with current_app.app_context():
    #    current_app.extensions['mail'].send(msg)
    #    print("Mail Sent")
    received_otp = request.args.get("otp")
    if received_otp == str(sent_otp):
        with current_app.app_context():
            db = get_db()
            name = user_details[0]
            mail = user_details[1]
            password = user_details[2]
            db.execute("insert into user (name,mail,password,type) values (?,?,?,?)",
                       [name, mail, password, 0])
            db.commit()

            user_id = db.execute('select user.id as id from user where name = ? and password = ?', [user_details[0],
                                                                                                    user_details[2]])
            user_result = user_id.fetchone()
            print(user_id)
            user_details.clear()
            print(f"userid: {user_result['id']}")
            session['id'] = user_result['id']
            print(f"userid from session: {session['id']}")
        return render_template('jobseeker_authentication_successful.html')
    else:
        return render_template('auth_not.html')
    # return render_template('authentication.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@jobseeker_blueprint.route('/registerdetails', methods=["POST", "GET"])
def registerdetails():
    userdata = Userdetails()
    if request.method == "POST":
        file = userdata.file.data
        filename = secure_filename(file.filename)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_path, filename))
        user = session['id']
        bio = userdata.bio.data
        jobtype = userdata.jobtype.data
        skill1 = userdata.skill1.data
        skill2 = userdata.skill2.data
        location1 = userdata.location1.data
        location2 = userdata.location2.data
        remote = userdata.remote.data
        occupation = userdata.occupation.data
        graduation = userdata.graduation_year.data
        if graduation:
            experience = "0-2"
        else:
            experience = userdata.experience.data
        previousexperience = userdata.previous_experience.data
        resume = filename
        githublink = userdata.githublink.data
        linkedinlink = userdata.linkedinlink.data
        college = userdata.college.data
        db = get_db()
        db.execute(
            'insert into jobseeker (id, bio, jobtype, skill1, skill2, location1, location2, remote, occupation, '
            'graduation, experience, previousexperience, resume, githublink, linkedinlink, college) values (?,?,?,?,'
            '?,?,?,?,?,?,?,?,?,?,?,?)',
            [user, bio, jobtype, skill1, skill2, location1, location2, remote, occupation, graduation, experience,
             previousexperience, resume, githublink, linkedinlink, college])
        db.commit()
        session.clear()
        return render_template('jobseeker_user_register.html')
    return render_template('jobseeker_user_details.html', form=userdata)

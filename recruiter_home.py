from flask import Blueprint, session, render_template, redirect, url_for, request, current_app, send_file
from flask_wtf import FlaskForm
from wtforms import validators, SelectField, StringField, SubmitField, RadioField, Form, PasswordField
from wtforms.validators import InputRequired, DataRequired
from database import get_db
from mailbox import Message
from flask_mail import Message

recruiter_home = Blueprint('recruiter_home', __name__)


class Create_Job(FlaskForm):
    # title = StringField("title", [validators.InputRequired(), validators.Length(min=8, max=1800)])
    title = SelectField("title", choices=[("Softwaredeveloper", "SoftwareDeveloper"), ("MLEnginner", "MLEnginner"),
                                          ("NetworkEnginner", "NetworkEnginner"), ("Sr.Software", "Sr.software"),
                                          ("Systemadmin", "Systemadmin")], default="Softwaredeveloper")
    description = StringField("description", [validators.InputRequired(), validators.Length(min=10, max=4500)])
    jobtype = RadioField("Type", choices=[('Full Time', 'Full Time'), ('Part Time', 'Part Time'), ('Intern', 'Intern')]
                         , default='Full Time', validators=[DataRequired()])
    skill1 = SelectField('skill 1',
                         choices=[('None', 'select from the below'), ('python', 'python'), ('java', 'java'),
                                  ('c++', 'c++')], validators=[DataRequired()])
    skill2 = SelectField('skill 2',
                         choices=[('None', 'select from the below'), ('mysql', 'mysql'), ('mongodb', 'mondogb')])
    location1 = SelectField('Location 1',
                            choices=[('None', 'Select from below'), ('Hyderabad', 'Hyderabad'),
                                     ('Banglore', 'Banglore'), ('Chennai', 'Chennai'), ('Mumbai', 'Mumbai')]
                            , validators=[DataRequired()])
    location2 = SelectField('Location 2',
                            choices=[('None', 'Select from below'), ('Hyderabad', 'Hyderabad'), ('Chennai', 'Chennai'),
                                     ('Banglore', 'Banglore'), ('Mumbai', 'Mumbai')])
    experience = SelectField('experience',
                             choices=[('None', 'Select from below'), ('0-2', '0-2'), ('2-5', '2-5'), ('5-8', '5-8'),
                                      ('8+', '8+')])
    remote = RadioField("Remote", choices=[('yes', 'yes'), ('no', 'no')], default='no', validators=[DataRequired()])
    link = StringField("Link", [validators.InputRequired(), validators.length(min=10, max=2500)])
    submit = SubmitField('submit')


class PasswordUpdate(Form):
    old_password = PasswordField("Enter Old Password", [validators.InputRequired()])
    new_password = PasswordField("Enter New Password", [validators.InputRequired()])
    conform_new = PasswordField("Enter New Password Again", [validators.InputRequired()])
    submit = SubmitField("Submit")


@recruiter_home.route('/recruiter_home_page', methods=["POST", "GET"])
def recruiter_home_page():
    if 'id' not in session or session['type'] != 1:  # To Protect Routes
        print(session['id'])
        session.clear()
        return redirect('/login')
    db = get_db()
    username = db.execute('select user.name as name from user where id = ?', [session['id']])
    name = username.fetchone()
    session['name'] = name['name']
    return render_template('recruiter_home_page.html', name=name['name'])


@recruiter_home.route('/post_job', methods=["POST", "GET"])
def post_job():
    form = Create_Job()
    if 'id' not in session or session['type'] != 1:  # To Protect Routes
        if 'id' in session:
            print(session['id'])
        session.clear()
        return redirect('/login')
    if form.validate_on_submit():
        session['data'] = form.data
        return redirect(url_for('login_blueprint.recruiter_home.confirm'))
    return render_template('job_posting.html', form=form)


@recruiter_home.route('/post_job/confirm', methods=["GET", "POST"])
def confirm():
    if 'id' not in session or session['type'] != 1:  # To Protect Routes
        print(session['id'])
        session.clear()
        return redirect('/login')
    if 'data' not in session:
        return redirect(url_for('post_job'))
    data = session['data']
    if request.method == "POST":
        db = get_db()
        try:
            db.execute('insert into jobposting (title, type, description, experience, skill1, skill2, location1, '
                       'location2, remote, createdby, link) values (?,?,?,?,?,?,?,?,?,?,?)',
                       [data['title'], data['jobtype'], data['description'], data['experience'], data['skill1'],
                        data['skill2'], data['location1'], data['location2'], data['remote'], session['id'],
                        data['link']])
            db.commit()
            session.pop('data')
        except Exception as e:
            session.pop('data')
            error = str(e)
            if error is not None:
                if 'UNIQUE constraint' in error:
                    error = "Error: Duplicate Entry"
                elif 'NOT NULL constraint' in error:
                    error = "Error: Missing Required Field"
                else:
                    error = "Error: {}".format(error)
            return render_template('job_posting_error.html', error=error)
        msg = "Job Posted. Check in Created by me"
        if 'data' not in session:
            print("Session data cleared")
        return render_template('job_posting_conformed.html', msg=msg)
    return render_template('job_posting_confirm.html', data=data)


@recruiter_home.route('/recruiter_logout', methods=["POST", "GET"])
def recruiter_logout():
    if 'id' not in session or session['type'] != 1:  # To Protect Routes
        print(session['id'])
        session.clear()
        return redirect('/login')
    print(f"Logged in User Id: {session.get('id')}")
    session.clear()
    return redirect('/')


@recruiter_home.route('/createdbyme', methods=["POST", "GET"])
def createdbyme():
    if 'id' not in session or session['type'] != 1:  # To Protect Routes
        print(session['id'])
        session.clear()
        return redirect('/login')
    db = get_db()
    user_result = db.execute(
        'select jobposting.jobid as jobid, jobposting.title as title from jobposting where createdby = ?',
        [session['id']])
    result = user_result.fetchall()
    # print(result)
    # print(result[0][0])
    # print(result[0]['title'])
    # print(len(result))
    # for i in range(len(result)):
    #    print(result[i][0])
    # if result is not None:
    return render_template('recruiter_created.html', result=result)
    # return render_template('recruiter_created.html')


@recruiter_home.route('/createbyme/<jobid>', methods=["POST", "GET"])
def createdbymeid(jobid):
    job_id = jobid
    if 'id' not in session or session['type'] != 1:  # To Protect Routes
        print(session['id'])
        session.clear()
        return redirect('/login')
    db = get_db()
    user_result = db.execute('select  jobposting.title as title, jobposting.type as type, jobposting.description as '
                             'description,jobposting.experience as experience,jobposting.skill1 as skill1,'
                             '' 'jobposting.skill2 as skill2, jobposting.location1 as location1,jobposting.location2 '
                             'as location2, jobposting.remote as remote,jobposting.createdby as createdby,'
                             'jobposting.link as link from jobposting where jobid = ?', [job_id])
    result = user_result.fetchone()
    # print(type(result))
    # print(result[0])
    # print(result)
    # print(result['title'])
    if result is None:
        msg = "No such Job"
        return render_template('recruiter_job_created.html', msg=msg)
    session['jobid'] = jobid
    return render_template('recruiter_job_created.html', result=result, job_id=job_id)


@recruiter_home.route('/eligible', methods=["GET", "POST"])
def eligible():
    db = get_db()
    user_result = db.execute('select  jobposting.title as title, jobposting.type as type, jobposting.description as '
                             'description,jobposting.experience as experience,jobposting.skill1 as skill1,'
                             '' 'jobposting.skill2 as skill2, jobposting.location1 as location1,jobposting.location2 '
                             'as location2, jobposting.remote as remote,jobposting.createdby as createdby,'
                             'jobposting.link as link from jobposting where jobid = ?', [session['jobid']])
    result = user_result.fetchone()
    search_result = db.execute('select DISTINCT jobseeker.id as id,u.name as name,jobseeker.skill1 as skill1,jobseeker.skill2 as skill2,'
                               'jobseeker.experience as experience,jobseeker.bio as bio from jobseeker, user JOIN user u on jobseeker.id = u.id  where skill1 = '
                               '? and skill2 = ? and '
                               'location1 = ? and location2 = ? and jobtype = ?  and remote = ?', [result['skill1'],
                                                                                                   result['skill2'],
                                                                                                   result['location1'],
                                                                                                   result['location2'],
                                                                                                   result['type'],
                                                                                                   result['remote']])
    jobresult = search_result.fetchall()
    print(jobresult)
    if len(jobresult) == 0:
        no_result = "No Suitable Candidates Found. We are sorry for that. Please try after few days."
        return render_template('recruiter_job_created.html', no_result=no_result)
    return render_template('recruiter_job_created.html', jobresult=jobresult)


@recruiter_home.route('/notify/<id>', methods=["POST", "GET"])
def notify(id):
    db = get_db()
    jobseeker_details = db.execute('select user.name as name,user.mail as mail from user where id = ?', [id])
    jobseeker = jobseeker_details.fetchone()
    jobdetails = db.execute('select  jobposting.title as title, jobposting.type as type, jobposting.description as '
                            'description,jobposting.experience as experience,jobposting.skill1 as skill1,'
                            '' 'jobposting.skill2 as skill2, jobposting.location1 as location1,jobposting.location2 '
                            'as location2, jobposting.remote as remote,jobposting.createdby as createdby,'
                            'jobposting.link as link from jobposting where jobid = ?', [session['jobid']])
    job = jobdetails.fetchone()
    msg = Message("Congratulations, You have been notified by recruiters.", sender="thrinadh.manubothu@gmail.com",
                  recipients=[jobseeker['mail']])
    msg.body = f"Hello {jobseeker['name']}.You have been noticied for the following job. Jobid: {session['jobid']}\n" \
               f"Title:{job['title']}\nDescription:{job['description']}\nLink:{job['link']}\n" \
               f"Please Look with the Given Job id and Apply for it.\n" \
               f"All the Best!"
    with current_app.app_context():
        current_app.extensions['mail'].send(msg)
    message = "Mail Sent"
    # TODO: Send Alert to the recruiter after the mail has been successfully posted.
    return redirect(url_for('login_blueprint.recruiter_home.eligible'))


@recruiter_home.route('/eligible/<id>', methods=["POST", "GET"])
def eligibleid(id):
    db = get_db()
    userdata = db.execute('select  jobseeker.bio as bio, jobseeker.college as college,'
                          'jobseeker.githublink as githublink, jobseeker.linkedinlink as linkedin, jobseeker.resume as resume '
                          'from jobseeker where id = ?', [id])
    user = userdata.fetchone()
    return render_template('recruiter_job_created.html', user=user)


@recruiter_home.route('/appliedby', methods=["POST", "GET"])
def appliedby():
    db = get_db()
    apply_list = db.execute(
        'select a.applicantid as applicantid, u.name as name,j.bio as bio, j.jobtype as jobtype, j.linkedinlink as linkedin,'
        'j.githublink as github, j.college as college, j.skill1 as skill1,'
        ' j.skill2 as skill2,j.experience as experience, j.resume as resume'
        ' from applied a join jobseeker j on j.id = a.applicantid join user u on u.id = j.id where a.jobid = ?', [session['jobid']])
    apply = apply_list.fetchall()
    if len(apply) == 0:
        applymessage = "Sorry, No one applied to this Job"
        return render_template('recruiter_job_created.html', applymessage=applymessage)
    return render_template('recruiter_job_created.html', apply=apply)


@recruiter_home.route('/download/<filename>', methods=["GET", "POST"])
def download(filename):
    try:
        return send_file(f"./resumes/{filename}", as_attachment=True)
    except Exception as e:
        return str(e)


@recruiter_home.route('/recruiter/updatepassword', methods=["POST", "GET"])
def updatepassword():
    name = session['name']
    passwordupdate = PasswordUpdate()
    db = get_db()
    if request.method == "POST":
        old = request.form.get("old_password")
        new = request.form.get("new_password")
        conform_new = request.form.get("conform_new")
        oldpassword = db.execute("select user.password as password from user where id = ?", [session['id']]).fetchone()
        if oldpassword['password'] != old:
            passmsg = "Old Password Doesn't Match"
            return render_template('recruiter_home_page.html', passmsg=passmsg, name=name)
        if new != conform_new:
            passmsg = "New Passwords Doesn't Match"
            return render_template('recruiter_home_page.html', passmsg=passmsg, name=name)
        try:
            db.execute("update user set password = ? where id = ?", [new, session['id']])
            db.commit()
            passmsg = "Password Updated!"
            return render_template('recruiter_home_page.html', passmsg=passmsg, name=name)
        except Exception as e:
            raise e
    return render_template('recruiter_home_page.html', passwordupdate=passwordupdate, name=name)


@recruiter_home.route('/deletejob/<jobid>', methods=["POST", "GET"])  # Working Perfectly.
def deletejob(jobid):
    db = get_db()
    try:
        db.execute("delete from jobposting where jobid = ?", [jobid])
        db.commit()
        db.execute("delete from applied where jobid = ?", [jobid])
        delete_msg = "Job Deleted Successfully."
        return render_template('recruiter_job_created.html', delete_msg=delete_msg)
    except Exception as e:
        raise (e)
    return render_template('recruiter_job_created.html')

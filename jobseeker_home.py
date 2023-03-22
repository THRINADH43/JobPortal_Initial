from flask import Blueprint, session, redirect, render_template, request, send_file
from werkzeug.utils import secure_filename

from database import get_db
from wtforms import Form, StringField, validators, PasswordField, SubmitField, EmailField, FileField, SelectField, \
    RadioField, Form
from flask_wtf import FlaskForm
import os

from jobseeker_register import allowed_extensions

jobseeker_home = Blueprint('jobseeker_home', __name__)

upload_path = './resumes'

if not os.path.exists(upload_path):
    os.mkdir(upload_path)


class Data(Form):
    job = StringField("Enter Job: ")
    submit = SubmitField("Submit")


class SearchJob(FlaskForm):
    title = SelectField("title", choices=[("Softwaredeveloper", "SoftwareDeveloper"), ("MLEnginner", "MLEnginner"),
                                          ("NetworkEnginner", "NetworkEnginner"), ("Sr.Software", "Sr.software"),
                                          ("Systemadmin", "Systemadmin")], default="Softwaredeveloper")
    submmit = SubmitField("Submit")


class PasswordUpdate(Form):
    old_password = PasswordField("Enter Old Password", [validators.InputRequired()])
    new_password = PasswordField("Enter New Password", [validators.InputRequired()])
    conform_new = PasswordField("Enter New Password Again", [validators.InputRequired()])
    submit = SubmitField("Submit")


class Userdetails(FlaskForm):
    jobtype = RadioField("Type", choices=[('Full Time', 'Full Time'), ('Part Time', 'Part Time'), ('Intern', 'Intern')]
                         , default='Full Time')
    bio = StringField("description")
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


@jobseeker_home.route('/jobseeker_home_page')
def jobseeker_home_page():
    search = True
    if 'id' not in session or session['type'] != 0:
        session.clear()
        return redirect('/login')
    db = get_db()
    user = db.execute('select user.name as name from user where id = ?', [session['id']])
    userresult = user.fetchone()
    session['name'] = userresult['name']
    return render_template('jobseeker_home_page.html', search=search)


@jobseeker_home.route('/jobseeker_logout', methods=["POST", "GET"])
def jobseeker_logout():
    if 'id' not in session:
        session.clear()
        return redirect('/login')
    print(f"logging out: {session['id']} and username: {session['name']}")
    session.clear()
    return redirect('/')


@jobseeker_home.route('/jobseeker_search_jobid', methods=["POST", "GET"])
def jobseeker_search_jobid():
    search = True
    if request.method == "POST":
        jobid = request.form.get('jobid')
        db = get_db()
        jobresult = db.execute('select jobposting.description as description,'
                               ' jobposting.experience as experience, jobposting.title as title, jobposting.link as link,'
                               'jobposting.type as type, jobposting.createdby as createdby, jobposting.location1 as location1,'
                               'jobposting.location2 as location2, jobposting.skill1 as skill1, jobposting.skill2 as skill2,'
                               'jobposting.remote as remote from jobposting where jobid = ?', [jobid])
        jobsearch = jobresult.fetchone()
        if jobsearch is None:
            msg = "The Job ID is not Found"
            return render_template('jobseeker_home_page.html', msg=msg, search=search)
        createdid = jobsearch['createdby']
        created = db.execute('select user.name as name from user where id = ?', [createdid])
        createdname = created.fetchone()
        createdidname = createdname['name']
        print(type(jobsearch))
        session['jobid'] = jobid
        return render_template('jobseeker_home_page.html', createdidname=createdidname, jobsearch=jobsearch,
                               jobid=jobid, search=search)


@jobseeker_home.route('/jobseeker_apply', methods=["POST", "GET"])
def jobseeker_apply():
    # print(session['job'])
    db = get_db()
    check_applied = db.execute('select * from applied where applicantid = ?  and jobid = ?',
                               [session['id'], session['jobid']])
    check = check_applied.fetchone()
    if check is not None:
        msg = "You already Applied to this Job."
        return render_template('jobseeker_home_page.html', msg=msg)
    applied = db.execute('insert into applied (applicantid,jobid) values (?,?)', [session['id'], session['jobid']])
    apply = db.commit()
    print(session['jobid'])
    session.pop('jobid')
    msg = "Applied to job"
    # TODO: Check that the jobseeker applies only once.If They Tries to attemt second time. Alert them not to do it.
    return render_template('jobseeker_home_page.html', msg=msg)


@jobseeker_home.route('/applied_list', methods=["POST", "GET"])
def applied_list():
    db = get_db()
    apply_list = db.execute('select a.jobid as jobid,j.skill1 as skill1,'
                            'j.title as title, j.type as type, j.experience as experience, u.name as name '
                            'from applied a JOIN jobposting j on j.jobid = a.jobid'
                            ' JOIN user u on u.id = j.createdby where a.applicantid = ?', [session['id']])
    apply = apply_list.fetchall()
    if len(apply) == 0:
        msg = "You didn't apply to any job.\nplease check for suitable jobs and apply."
        return render_template('jobseeker_home_page.html', msg=msg)
    return render_template('jobseeker_home_page.html', apply=apply)


@jobseeker_home.route('/google_api', methods=["GET", "POST"])
def google_api():
    d = Data()
    if request.method == "POST":
        return request.data
    return render_template('jobseeker_google_api.html', d=d)


@jobseeker_home.route('/myprofile', methods=["GET", "POST"])
def myprofile():
    my = True
    db = get_db()
    profile = db.execute('select j.jobtype as jobtype,'
                         'j.bio as bio,j.skill1 as skill1, j.skill2 as skill2,'
                         'j.location1 as location1,j.location2 as location2,j.remote as remote,'
                         'j.githublink as github,j.linkedinlink as linkedin,j.experience as experience'
                         ' from jobseeker j where j.id = ?', [session['id']])
    myprofile = profile.fetchone()
    return render_template('jobseeker_home_page.html', myprofile=myprofile, my=my)


@jobseeker_home.route('/download', methods=["GET", "POST"])
def download():
    db = get_db()
    file = db.execute('select jobseeker.resume as resume from jobseeker where id = ?', [session['id']])
    fileresult = file.fetchone()
    filename = fileresult['resume']
    try:
        return send_file(f"./resumes/{filename}", as_attachment=True)
    except Exception as e:
        return str(e)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@jobseeker_home.route('/update', methods=["GET", "POST"])
def update():
    to_update = True
    userdata = Userdetails()
    db = get_db()
    original_data = db.execute("select j.jobtype as jobtype,j.experience as experience,j.linkedinlink as linkedin,"
                               "j.githublink as github,j.skill1 as skill1,j.skill2 as skill2, "
                               "j.location1 as location1,j.location2 as location2,j.bio as bio,j.occupation as occupation,"
                               "j.graduation as graduation,j.remote as remote,j.resume as resume,"
                               "j.college as college from jobseeker j where id = ?", [session['id']])
    original = dict(original_data.fetchone())
    if request.method == "POST":
        file = userdata.file.data
        filename = secure_filename(file.filename)
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
        if original['bio'] != bio:
            if bio:
                print("Query Entered here")
                original['bio'] = bio
        if original['resume'] != resume:
            if resume:
                original['resume'] = resume
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(upload_path, filename))
        if original['jobtype'] != jobtype:
            if jobtype != "None":
                original['jobtype'] = jobtype
        if original['skill1'] != skill1:
            if skill1 != "None":
                original['skill1'] = skill1
        if original['skill2'] != skill2:
            if skill2 != "None":
                original['skill2'] = skill2
        if original['location1'] != location1:
            if location1 != "None":
                original['location1'] = location1
        if original['location2'] != location2:
            if location2 != "None":
                original['location2'] = location2
        if original['remote'] != remote:
            original['remote'] = remote
        if original['occupation'] != occupation:
            if occupation != "None":
                original['occupation'] = occupation
        if original['graduation'] != graduation:
            if graduation != "None":
                original['graduation'] = graduation
        if original['linkedin'] != linkedinlink:
            if linkedinlink:
                original['linkedin'] = linkedinlink
        if original['github'] != githublink:
            if githublink:
                original['github'] = githublink
        if original['college'] != college:
            if college:
                original['college'] = college
        if original['experience'] != experience:
            original['experience'] = experience
        try:
            db.execute(
                'update jobseeker set bio = ?, jobtype = ?, skill1 = ?, skill2 = ?, location1 = ?,'
                ' location2 = ?, remote = ?, occupation = ?,'
                'graduation = ?, experience = ?, resume = ?, githublink = ?, linkedinlink = ?, college = ? where id = ?',
                [original['bio'], original['jobtype'], original['skill1'], original['skill2'], original['location1'],
                 original['location2'], original['remote'], original['occupation'], original['graduation'],
                 original['experience'],
                 original['resume'], original['github'], original['linkedin'], original['college'], session['id']])
            db.commit()
            msg = "Data Updated Successfull!"
            return render_template('jobseeker_update.html', msg=msg)
        except Exception as e:
            raise e
    return render_template('jobseeker_update.html', form=userdata, to_update=to_update)


@jobseeker_home.route('/updatepassword', methods=["POST", "GET"])
def updatepassword():
    passwordupdate = PasswordUpdate()
    db = get_db()
    if request.method == "POST":
        old = request.form.get("old_password")
        new = request.form.get("new_password")
        conform_new = request.form.get("conform_new")
        oldpassword = db.execute("select user.password as password from user where id = ?", [session['id']]).fetchone()
        if oldpassword['password'] != old:
            passmsg = "Old Password Doesn't Match"
            return render_template('jobseeker_home_page.html', passmsg=passmsg)
        if new != conform_new:
            passmsg = "New Passwords Doesn't Match"
            return render_template('jobseeker_home_page.html', passmsg=passmsg)
        try:
            db.execute("update user set password = ? where id = ?", [new, session['id']])
            db.commit()
            passmsg = "Password Updated!"
            return render_template('jobseeker_home_page.html', passmsg=passmsg)
        except Exception as e:
            raise e
    return render_template('jobseeker_home_page.html', passwordupdate=passwordupdate)


@jobseeker_home.route('/searchjob', methods=["GET", "POST"])
def searchjob():
    searchname = SearchJob()
    if request.method == "POST":
        print("Request in POST method")
        title = request.form.get("title")
        print(f"Title: {title}")
        db = get_db()
        user_result = db.execute('select j.skill1 as skill1, j.skill2 as skill2, j.experience as experience,'
                                 'j.location1 as location1,j.remote as remote,'
                                 'j.jobtype as jobtype from jobseeker j where id = ?', [session['id']]).fetchone()
        job_result = db.execute(
            'select j.jobid as jobid,'
            'j.location2 as location2,j.description as description,j.link as link, u.name as name '
            'from jobposting j JOIN user u on u.id = j.createdby '
            ' where title = ? and skill1 = ? and skill2 = ? and location1 = ? and j.type = ? and '
            'experience = ?',
            [title, user_result['skill1'], user_result['skill2'], user_result['location1'],
             user_result['jobtype'], user_result['experience']]).fetchall()
        print(user_result)
        print(job_result)
        print(type(job_result))
        if len(job_result) == 0:
            msg = "No Jobs Found According to your Preferences. Skills, Location, Experience are taken into " \
                  "consideration "
            return render_template('jobseeker_search_name.html', msg=msg)
        else:
            return render_template('jobseeker_search_name.html', job_result=job_result, user_result=user_result,
                                   title=title)
    return render_template('jobseeker_search_name.html', searchname=searchname, session=session)


@jobseeker_home.route('/apply_job/<jobid>', methods=["POST", "GET"])
def apply_job(jobid):
    jobid = jobid
    db = get_db()
    check_applied = db.execute('select * from applied where applicantid = ?  and jobid = ?',
                               [session['id'], jobid])
    check = check_applied.fetchone()
    if check is not None:
        msg = "You already Applied to this Job."
        return render_template('jobseeker_home_page.html', msg=msg)
    applied = db.execute('insert into applied (applicantid,jobid) values (?,?)', [session['id'], jobid])
    apply = db.commit()
    msg = "Applied to job"
    # TODO: Check that the jobseeker applies only once.If They Tries to attemt second time. Alert them not to do it.
    return render_template('jobseeker_search_name.html', msg=msg)

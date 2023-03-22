from flask import Flask, render_template
from flask_mail import Mail
from login import login_blueprint
from recruiter_register import recruiter_blueprint
from jobseeker_register import jobseeker_blueprint

app = Flask(__name__)


app.config["MAIL_USERNAME"] = "" # Use your Mail
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "" #Use you mail Server
app.config["MAIL_PASSWORD"] = "" # Use Your Password
app.config['EMAIL_USE_TLS'] = True
app.secret_key = "Thrinadh"
mail = Mail(app)

app.register_blueprint(recruiter_blueprint)
app.register_blueprint(jobseeker_blueprint)
app.register_blueprint(login_blueprint)


@app.route('/', methods=["POST", "GET"])
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)

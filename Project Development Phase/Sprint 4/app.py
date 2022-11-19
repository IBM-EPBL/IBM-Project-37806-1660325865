from flask import Flask, render_template, request, redirect,session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment
from apscheduler.schedulers.background import BackgroundScheduler
from flask_session import Session
import ibm_db
import bcrypt
import os
import smtplib
import requests
import json


load_dotenv()

db = os.getenv("DATABASE")
host = os.getenv("HOSTNAME")
port = os.getenv("PORT")
sslcert = os.getenv("SSLServerCertificate")
userId = os.getenv("UID")
password = os.getenv("PWD")
sendgrid = os.getenv('SENDGRID_API_KEY')
email = os.getenv('EMAIL')
mail_pwd = os.getenv('EMAIL_PASSWORD')
rapid_api_key = os.getenv('RAPID_API_KEY')

conn = ibm_db.connect(
    f'DATABASE={db};HOSTNAME={host};PORT={port};SECURITY=SSL;SSLServerCertificate={sslcert};UID={userId};PWD={password}', '', '')


def message(subject="Python Notification",
            text="", img=None, attachment=None):

    # build message contents
    msg = MIMEMultipart()

    f = open("./templates/notificationsmail.html", "r", errors="ignore")
    html_content = f.read()

    html_contentt = Environment().from_string(
        html_content).render(msg=text)

    # Add Subject
    msg['Subject'] = subject

    # Add text contents
    msg.attach(MIMEText(html_contentt, 'html'))
    return msg


def mail():

    # initialize connection to our email server,
    # we will use gmail here
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()

    # Login with your email and password
    smtp.login(email, mail_pwd)

    url = "https://newscatcher.p.rapidapi.com/v1/search_enterprise"

    querystring = {"q": "news", "lang": "en",
                   "sort_by": "relevancy", "topic": "news", "page": "1", "media": "True"}

    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": "newscatcher.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    json_object = json.loads(response.text)

    data = json_object["articles"]

    # Call the message function
    msg = message("Exciting news today!", data[:10])

    sql = "SELECT email FROM users"
    stmt = ibm_db.prepare(conn, sql)
    # ibm_db.bind_param(stmt, 1, "shirleychristabel.23it@licet.ac.in")
    ibm_db.execute(stmt)
    users = []
    # List of emails
    while ibm_db.fetch_row(stmt) != False:
        users.append(ibm_db.result(stmt, 0))

    smtp.sendmail(from_addr="veronishwetha.23it@licet.ac.in",
                            to_addrs=users, msg=msg.as_string())

    smtp.quit()


sched = BackgroundScheduler(daemon=True)
sched.add_job(mail, 'interval', minutes=60)
sched.start()


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    if not session.get("email"):
        return render_template('signin.html')
    else:
        return redirect("/dashboard",code=302)


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':

        email = request.form['username']
        pwd = request.form['password']
        password = ""

        sql = "SELECT password FROM users WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        auth_token = ibm_db.fetch_assoc(stmt)

        if auth_token:
            # encoding user password
            userBytes = pwd.encode('utf-8')
            byte_pwd = bytes(auth_token['PASSWORD'], 'utf-8')

            # checking password
            result = bcrypt.checkpw(userBytes, byte_pwd)
            print(result)

            if result:
                session["email"] = email
                return redirect("/dashboard", code=302)
            else:
                return render_template('signin.html', msg="Invalid Credentials")
        else:
            return render_template('signin.html', msg="User doesn't exist")


@app.route('/signup')
def signup_form():
    return render_template('signup.html')

@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/create_user', methods=['POST', 'GET'])
def create_user():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        firstName = request.form['first_name']
        lastName = request.form['last_name']
        interests = request.form['interests']
        # converting password to array of bytes
        bytes = password.encode('utf-8')

        # generating the salt
        salt = bcrypt.gensalt()

        # Hashing the password
        hashed_password = bcrypt.hashpw(bytes, salt)

        try:

            insert_sql = "INSERT INTO users VALUES (?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, firstName)
            ibm_db.bind_param(prep_stmt, 2, lastName)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, hashed_password)
            ibm_db.bind_param(prep_stmt, 5, interests)
            ibm_db.execute(prep_stmt)

            f = open("./templates/mail.html", "r")
            html_content = f.read()

            message = Mail(
                from_email='raksha.23it@licet.ac.in',
                to_emails=email,
                subject='Registeration Confirmation',
                html_content=html_content)
            try:
                sg = SendGridAPIClient(sendgrid)
                response = sg.send(message)
                print(response.status_code)
            except Exception as e:
                print("ERROR: PC LOAD LETTER")
            print(type(email))
            session["email"] = email

            return redirect("/dashboard", code=302)
        except e:
            return redirect("/signup", code=302)


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if request.method == 'GET':
        if not session.get("email"):
            return redirect("/")
        else:
            email = session.get("email")
            sql = "SELECT interests FROM users WHERE email=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.execute(stmt)
            interest = ibm_db.fetch_assoc(stmt)
            interest_value = interest['INTERESTS']
            url = "https://newscatcher.p.rapidapi.com/v1/search_enterprise"

            querystring = {"q": interest_value, "lang": "en",
                        "sort_by": "date", "topic":interest_value, "page": "1", "media": "True"}

            headers = {
                "X-RapidAPI-Key": rapid_api_key,
                "X-RapidAPI-Host": "newscatcher.p.rapidapi.com"
            }

            response = requests.request(
                "GET", url, headers=headers, params=querystring)
            json_object = json.loads(response.text)
            # f = open("data.json","r")
            # data = f.read()
            # json_object = json.loads(data)
            return render_template('dashboard.html', students=json_object)
    # search endpoint
    elif request.method == 'POST':
        if not session.get("email"):
            return redirect("/")
        else:
            search = request.form['search']
            email = session.get("email")
            sql = "SELECT interests FROM users WHERE email=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.execute(stmt)
            interest = ibm_db.fetch_assoc(stmt)
            interest_value = interest['INTERESTS']
            url = "https://newscatcher.p.rapidapi.com/v1/search_enterprise"

            querystring = {"q": search, "lang": "en",
                        "sort_by": "date", "topic": interest_value, "page": "1", "media": "True"}

            headers = {
                "X-RapidAPI-Key": rapid_api_key,
                "X-RapidAPI-Host": "newscatcher.p.rapidapi.com"
            }

            response = requests.request(
                "GET", url, headers=headers, params=querystring)
            json_object = json.loads(response.text)
            return render_template('dashboard.html', students=json_object)


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == 'POST':
        if not session.get("email"):
            return redirect("/")
        else:
            try:
                email = session.get("email")
                password = request.form['password']
                interests = request.form['interests']
                # converting password to array of bytes
                bytes = password.encode('utf-8')

                # generating the salt
                salt = bcrypt.gensalt()

                # Hashing the password
                hashed_password = bcrypt.hashpw(bytes, salt)

                sql = "SELECT first_name, last_name, email FROM users WHERE email =?"
                stmt = ibm_db.prepare(conn, sql)
                ibm_db.bind_param(stmt, 1, email)
                ibm_db.execute(stmt)

                update_sql = "UPDATE USERS SET PASSWORD = ?, INTERESTS = ? WHERE email = ?"
                prep_stmt = ibm_db.prepare(conn, update_sql)
                ibm_db.bind_param(prep_stmt, 1, hashed_password)
                ibm_db.bind_param(prep_stmt, 2, interests)
                ibm_db.bind_param(prep_stmt, 3, email)
                ibm_db.execute(prep_stmt)
                return redirect("/dashboard", code=302)
            except e:
                return redirect("/dashboard", code=302)
    elif request.method == 'GET':
        if not session.get("email"):
            return redirect("/")
        else:
            email = session.get("email")
            sql = "SELECT first_name, email FROM users WHERE email =?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.execute(stmt)
            data = ibm_db.fetch_assoc(stmt)
            return render_template('profile.html', msg=data)


@app.route("/logout")
def logout():
    session["email"] = None
    return redirect("/", code=302)

# mail()


if __name__ == "__main__":
    app.run()

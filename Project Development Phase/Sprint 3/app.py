from flask import Flask, render_template, request, redirect
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment
from apscheduler.schedulers.background import BackgroundScheduler
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

    f = open("./templates/mail.html", "r")
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

    querystring = {"q": "Elon Musk", "lang": "en",
                   "sort_by": "relevancy", "page": "1", "media": "True"}

    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": "newscatcher.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    json_object = json.loads(response.text)

    data = json_object["articles"][0]["title"]
    print(data)

    # Call the message function
    msg = message("Exciting news today!", data)

    # Make a list of emails, where you wanna send mail
    to = ["veronishwetha@gmail.com"]

    # Provide some data to the sendmail function!
    smtp.sendmail(from_addr="veronishwetha.23it@licet.ac.in",
                            to_addrs=to, msg=msg.as_string())

    # Finally, don't forget to close the connection
    smtp.quit()


sched = BackgroundScheduler(daemon=True)
sched.add_job(mail, 'interval', minutes=60)
sched.start()


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('signin.html')


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

            if result:
                return redirect("/dashboard", code=302)
            else:
                return render_template('signin.html', msg="Invalid Credentials")
        else:
            return render_template('signin.html', msg="User doesn't exist")


@app.route('/signup')
def signup_form():
    return render_template('signup.html')


@app.route('/create_user', methods=['POST', 'GET'])
def create_user():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        firstName = request.form['first_name']
        lastName = request.form['last_name']
        # intersts = request.form['interests']
        # converting password to array of bytes
        bytes = password.encode('utf-8')

        # generating the salt
        salt = bcrypt.gensalt()

        # Hashing the password
        hashed_password = bcrypt.hashpw(bytes, salt)

        insert_sql = "INSERT INTO users VALUES (?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, firstName)
        ibm_db.bind_param(prep_stmt, 2, lastName)
        ibm_db.bind_param(prep_stmt, 3, email)
        ibm_db.bind_param(prep_stmt, 4, hashed_password)
        # ibm_db.bind_param(prep_stmt, 5, intersts)
        ibm_db.execute(prep_stmt)

        message = Mail(
            from_email='veronishwetha.23it@licet.ac.in',
            to_emails=email,
            subject='Sending with Twilio SendGrid is Fun',
            html_content='<strong>and easy to do anywhere, even with Python</strong>')
        try:
            sg = SendGridAPIClient(
                sendgrid)
            response = sg.send(message)
        except Exception as e:
            print("ERROR: PC LOAD LETTER")

        return redirect("/dashboard", code=302)


@app.route('/dashboard')
def dashboard():
    # url = "https://newscatcher.p.rapidapi.com/v1/search_enterprise"

    # querystring = {"q": "Elon Musk", "lang": "en",
    #                "sort_by": "relevancy", "page": "1", "media": "True"}

    # headers = {
    #     "X-RapidAPI-Key": "05db4efea2msha6e24b9b04d0fa1p1d2e10jsn70ec1b71e643",
    #     "X-RapidAPI-Host": "newscatcher.p.rapidapi.com"
    # }

    # response = requests.request(
    #     "GET", url, headers=headers, params=querystring)
    # json_object = json.loads(response.text)

    file1 = open("data.json", "r")
    json_object = json.load(file1)

    # file1.writelines(response.text)

    return render_template('dashboard.html', students=json_object)


@app.route('/notifications')
def notifications():
    return render_template('notifications.html')


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == 'POST':
        email = request.form['email']
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
        print(ibm_db.execute(stmt))

        insert_sql = "INSERT INTO users VALUES (?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, hashed_password)
        ibm_db.bind_param(prep_stmt, 2, interests)
        ibm_db.execute(prep_stmt)

        message = Mail(
            from_email='veronishwetha.23it@licet.ac.in',
            to_emails=email,
            subject='Sending with Twilio SendGrid is Fun',
            html_content='<strong>and easy to do anywhere, even with Python</strong>')
        try:
            sg = SendGridAPIClient(
                sendgrid)
            response = sg.send(message)
        except Exception as e:
            print("ERROR: PC LOAD LETTER")

        return render_template('dashboard.html', msg="Details uploaded successfuly..")
    elif request.method == 'GET':
        email = 'elizabethsubhikshavictoria.23it@licet.ac.in'
        sql = "SELECT first_name, email FROM users WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        data = ibm_db.fetch_assoc(stmt)
        print(type(data))
    return render_template('profile.html', msg=data)


# mail()
# schedule.every(5).seconds.do(mail)
if __name__ == "__main__":
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    app.run(debug=True)

from flask import Flask, render_template, request, redirect
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import ibm_db
import bcrypt
import os

load_dotenv()

db = os.getenv("DATABASE")
host = os.getenv("HOSTNAME")
port = os.getenv("PORT")
sslcert = os.getenv("SSLServerCertificate")
userId = os.getenv("UID")
password = os.getenv("PWD")
sendgrid = os.getenv('SENDGRID_API_KEY')
conn = ibm_db.connect(
    f'DATABASE={db};HOSTNAME={host};PORT={port};SECURITY=SSL;SSLServerCertificate={sslcert};UID={userId};PWD={password}', '', '')

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
    return render_template('dashboard.html')


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


if __name__ == "__main__":
    app.run(debug=True)

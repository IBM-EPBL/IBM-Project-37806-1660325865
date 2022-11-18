from flask import Flask, render_template, request, redirect,session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from flask_session import Session
import ibm_db
import bcrypt
import os
import smtplib
import json


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

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template('signin.html')

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
        interests = request.form['interests']
        # converting password to array of bytes
        bytes = password.encode('utf-8')

        # generating the salt
        salt = bcrypt.gensalt()

        # Hashing the password
        hashed_password = bcrypt.hashpw(bytes, salt)

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


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    return render_template('dashboard.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route("/logout")
def logout():
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    if not session.get("email"):
        return render_template('signin.html')
    else:
        return redirect("/dashboard",code=302)

@app.route('/signin', methods=['POST'])
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

@app.route('/signup')
def signup_form():
    return render_template('signup.html')

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

if __name__ == "__main__":
    app.run(debug=True)

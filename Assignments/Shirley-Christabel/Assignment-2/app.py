from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/sign-in')
def signin_form():
    return render_template('signin.html')


@app.route('/signup')
def signup_form():
    return render_template('signup.html')


@app.route('/insertUser', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            name = request.form['email']
            password = request.form['password']

            with sql.connect("student_database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO users (email,password) VALUES (?,?)", (email, password))
                con.commit()
                msg = "Record successfully added!"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("home.html")
            con.close()


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=True)

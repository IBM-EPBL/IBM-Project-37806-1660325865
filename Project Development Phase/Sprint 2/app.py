from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/notifications')
def notifications():
    return render_template('notifications.html')


@app.route('/profile')
def about():
    return render_template('profile.html')


@app.route('/sign-in')
def signin_form():
    return render_template('sign-in.html')


@app.route('/sign-up')
def signup_form():
    return render_template('sign-up.html')


# @app.route('/tables')
# def signup_form():
#     return render_template('tables.html')


# if __name__ == "__main__":
#     app.run()

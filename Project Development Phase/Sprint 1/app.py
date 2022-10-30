from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def signin_form():
    return render_template('signin.html')

if __name__ == "__main__":
    app.run(debug=True)

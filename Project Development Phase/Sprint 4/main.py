import ibm_db
from dotenv import load_dotenv
import json
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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

# conn = ibm_db.connect(
#     f'DATABASE={db};HOSTNAME={host};PORT={port};SECURITY=SSL;SSLServerCertificate={sslcert};UID={userId};PWD={password}', '', '')


message = Mail(
    from_email='raksha.23it@licet.ac.in',
    to_emails='raksha.23it@licet.ac.in',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(sendgrid)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)

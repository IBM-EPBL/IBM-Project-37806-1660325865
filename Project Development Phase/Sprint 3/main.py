from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request
import smtplib
import os
import schedule
import time


def message(subject="Python Notification",
            text="", img=None, attachment=None):

    # build message contents
    msg = MIMEMultipart()
    data = "hello"

    # f = open("mail.html", "r")
    # html_content = f.read()

    html_content = render_template("mail.html", msg="hello")

    html = html_content

    # Add Subject
    msg['Subject'] = subject

    # Add text contents
    msg.attach(MIMEText(text))
    msg.attach(MIMEText(html, 'html'))
    return msg


def mail():

    # initialize connection to our email server,
    # we will use gmail here
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()

    # Login with your email and password
    smtp.login('veronishwetha.23it@licet.ac.in', 'joanof@20')

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
    # # Open function to open the file "MyFile1.txt"
    # # (same directory) in read mode and
    # file1 = open("data.json", "w")

    # file1.writelines(response.text)

    # print(type(json_object))

    # Call the message function
    msg = message("Good!", "Hi there!")

    # Make a list of emails, where you wanna send mail
    to = ["veronishwetha@gmail.com"]

    # Provide some data to the sendmail function!
    smtp.sendmail(from_addr="veronishwetha.23it@licet.ac.in",
                            to_addrs=to, msg=msg.as_string())

    # Finally, don't forget to close the connection
    smtp.quit()


# mail()
# schedule.every(2).seconds.do(mail)
# # schedule.every(10).minutes.do(mail)
# # schedule.every().hour.do(mail)
# # schedule.every().day.at("10:30").do(mail)
# # schedule.every(5).to(10).minutes.do(mail)
# # schedule.every().monday.do(mail)
# # schedule.every().wednesday.at("13:15").do(mail)
# # schedule.every().minute.at(":17").do(mail)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

import os
import configparser
import smtplib
from email.message import EmailMessage

#  TODO: sending mail after completing checking
#  Sending files (excel and pickle file to verification

"""Checking if config.ini exist"""
if not os.path.isfile('config.ini'):
    print("Config file not found")
    exit(1)
config = configparser.ConfigParser()
config.read('config.ini')


main_link = config['source']['main_link']

"""Receiver = list of receivers,
Subject = subject of a message
body = message in HTML
Attachment = direct PATH to the attachment in csv"""


def done_all_mail(done_time):
    subject = f"Successful scraping: {done_time}"
    receiver = config['mail']['Receiver1']
    body = f"Done successfully, no problems here."
    send_email(receiver, subject, body)


def send_email(receiver, subject, body):
    email_address = config['mail']['sender_mail']
    email_password = config['mail']['mail_password']

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = email_address
    message["To"] = receiver
    message.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(message)


    """Attachment if needed"""
"""    with open(attachment, "rb") as f:
        attachment = f.read()
        file_type = f.name
        file_name = "attachment.csv"
    msg.add_attachment(attachment, maintype='csv', subtype=file_type, filename=file_name)"""

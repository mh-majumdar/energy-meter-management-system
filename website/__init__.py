from flask import Flask
from flask_login import LoginManager
from .extensions import db
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, validators
from wtforms.validators import DataRequired, Email, Length
from flask import Blueprint, render_template
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .scheduler import start_scheduler
from flask_mail import Message
from flask import current_app
from flask_mail import Mail, Message
from flask_mail import Mail, Message

from flask import Flask
from flask_mail import Mail, Message
import requests
import urllib.parse

app = Flask(__name__)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''     
app.config['MAIL_PASSWORD'] = ''        
app.config['MAIL_DEFAULT_SENDER'] = '' 

mail = Mail(app)

API_KEY = ''
SENDER_ID = '8809617623722'

def send_sms_backend(phone_number, message):
    """Send SMS using BulkSMSBD API"""
    try:
        encoded_message = urllib.parse.quote(message)
        url = f"http://bulksmsbd.net/api/smsapi?api_key={API_KEY}&type=text&number={phone_number}&senderid={SENDER_ID}&message={encoded_message}"
        response = requests.get(url)
        if response.status_code == 200 and 'SMS Submitted Successfully' in response.text:
            print(f"✅ SMS sent to {phone_number}")
            return True
        else:
            print(f"❌ SMS failed to {phone_number}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending SMS: {str(e)}")
        return False

def send_balance_low_email(balance):
    """Send balance low alert email."""
    try:
        subject = "Meter Balance Low Alert"
        recipient = ["hasanmehedi1115@student.nstu.edu.bd"]
        body = f"Your current meter balance is BDT {balance:.2f}. Please recharge soon to avoid disconnection."
        msg = Message(subject=subject, recipients=recipient, body=body)
        mail.send(msg)
        print("✅ Balance low alert email sent.")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

@app.route("/")
def index():
    # Dummy meter accounts for demonstration
    meter_accounts = [
        
    ]
    alerts_sent = 0
    for account in meter_accounts:
        balance = account["balance"]
        phone_number = account["phone"]
        if balance < 50:
            message = f"Your current balance is BDT {balance:.2f}. Please recharge soon to avoid disconnection."
            if send_sms_backend(phone_number, message):
                alerts_sent += 1
            send_balance_low_email(balance)
    return f"📤 Total SMS alerts sent: {alerts_sent}"

if __name__ == "__main__":
    app.run(debug=True, port=5000)

DB_NAME = "database.db"



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

   
    # Import models here
   

    # Start the scheduler
    with app.app_context():
        start_scheduler(app, db)
    # Import models after initializing db
    from .models import User

    # Register blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
   


    # Create database
    with app.app_context():
        db.create_all()
        print("Database created!")

    # Configure login manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
   

    return app
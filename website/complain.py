# website/complain.py
import os
import smtplib
from datetime import datetime
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# === Constants ===
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'EMAIL_ADDRESS': '',
    'EMAIL_PASSWORD': '',
    'RECIPIENT_EMAIL': ''
}

# === Form ===
class ComplaintForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20, max=2000)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Length(max=20)])
    image = FileField('Image', validators=[FileAllowed(ALLOWED_EXTENSIONS)])

# === Utilities ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_complaint_email(form_data, image_path=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['EMAIL_ADDRESS']
        msg['To'] = EMAIL_CONFIG['RECIPIENT_EMAIL']
        msg['Subject'] = f"New Complaint: {form_data['title']}"

        body = f"""
        New Complaint Received
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Title: {form_data['title']}
        Description: {form_data['description']}
        Email: {form_data['email']}
        Phone: {form_data.get('phone', 'Not provided')}
        """

        msg.attach(MIMEText(body, 'plain'))

        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(image_path)}'
                )
                msg.attach(part)

        server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
        server.starttls()
        server.login(EMAIL_CONFIG['EMAIL_ADDRESS'], EMAIL_CONFIG['EMAIL_PASSWORD'])
        server.sendmail(EMAIL_CONFIG['EMAIL_ADDRESS'], EMAIL_CONFIG['RECIPIENT_EMAIL'], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_confirmation_email(user_email, complaint_title):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['EMAIL_ADDRESS']
        msg['To'] = user_email
        msg['Subject'] = "Complaint Received - Digital Meter Service"

        body = f"""
        Dear Customer,

        Thank you for contacting us. We have received your complaint.
        Title: {complaint_title}
        Date Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
        server.starttls()
        server.login(EMAIL_CONFIG['EMAIL_ADDRESS'], EMAIL_CONFIG['EMAIL_PASSWORD'])
        server.sendmail(EMAIL_CONFIG['EMAIL_ADDRESS'], user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {str(e)}")
        return False

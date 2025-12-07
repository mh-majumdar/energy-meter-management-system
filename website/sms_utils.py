import requests
import urllib.parse
from .models import MeterAccount
from .extensions import db  # Assuming db is initialized in extensions.py

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

def check_all_accounts_balance():
    """Check all meter accounts and send SMS for low balances (<50 BDT)"""
    try:
        meter_accounts = MeterAccount.query.all()
        alerts_sent = 0

        for account in meter_accounts:
            balance = account.balance or 0.0
            if balance < 50:
                # Access phone number from related user → profile
                user = account.user
                profile = user.profile if user else None

                phone_number = "8801521558116"

                message = f"Your current balance is BDT {balance:.2f}. Please recharge soon to avoid disconnection."
                if send_sms_backend(phone_number, message):
                    alerts_sent += 1

        print(f"📤 Total SMS alerts sent: {alerts_sent}")
        return alerts_sent

    except Exception as e:
        print(f"❌ Error in balance check: {str(e)}")
        return 0

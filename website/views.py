from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from .models import User, Profile
from .models import MeterAccount, Transaction
from .import db
from datetime import datetime
import urllib.parse
from flask import Flask, render_template, request, flash
import requests
import os
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from .complain import ComplaintForm, allowed_file, send_complaint_email, send_confirmation_email
# Add these imports to the top of your views.py file
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request
import requests
import PyPDF2
import io
import re
from datetime import datetime, timedelta
import json




views = Blueprint('views', __name__)
 # Register blueprints
# Create blueprint


#api for sms flash  
API_KEY = ''
SENDER_ID = ''  # Use your approved sender ID

views = Blueprint("views", __name__)


class PDFDataExtractor:
    def __init__(self):
        self.base_url = "https://misc.bpdb.gov.bd/storage/daily_entry/"
    
    def get_pdf_url(self, date_str=None):
        """Generate PDF URL for given date or today"""
        if date_str:
            return f"{self.base_url}{date_str}.pdf"
        else:
            today = datetime.now().strftime("%Y-%m-%d")
            return f"{self.base_url}{today}.pdf"
    
    def extract_pdf_text(self, pdf_url):
        """Extract text from PDF URL without downloading"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(pdf_url, headers=headers, timeout=30, verify=False)

            response.raise_for_status()
            
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return None
    
    def parse_power_station_data(self, text):
        """Parse power station data from extracted text"""
        stations = []
        
        try:
            # Look for Comilla zone section (case insensitive)
            comilla_patterns = [
                r'Comilla.*?Zone.*?(?=\n\n|\Z)',
                r'COMILLA.*?ZONE.*?(?=\n\n|\Z)',
                r'Comilla.*?(?=Zone|ZONE|zone).*?(?=\n\n|\Z)',
                r'(?i)comilla.*?(?=\n\n|\Z)'
            ]
            
            comilla_text = ""
            for pattern in comilla_patterns:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    comilla_text = match.group()
                    break
            
            if not comilla_text:
                # Try to find any table-like structure
                table_pattern = r'(\w+(?:\s+\w+)*)\s+(\d+)\s*[xX×]\s*(\d+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)'
                matches = re.findall(table_pattern, text)
            else:
                # More flexible pattern for power station data
                station_patterns = [
                    r'(\w+(?:\s+\w+)*)\s+(\d+)\s*[xX×]\s*(\d+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)',
                    r'(\w+(?:\s+\w+)*)\s+(\d+)\s+(\d+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)',
                    r'([A-Za-z\s]+)\s+(\d+)\s*[xX×]\s*(\d+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)'
                ]
                
                matches = []
                for pattern in station_patterns:
                    matches = re.findall(pattern, comilla_text)
                    if matches:
                        break
            
            for match in matches:
                if len(match) >= 8:
                    station_data = {
                        'name': match[0].strip(),
                        'units': match[1],
                        'unit_capacity': match[2],
                        'installed_capacity': match[3],
                        'derated_capacity': match[4],
                        'yesterday_gen': match[5],
                        'today_gen': match[6],
                        'yesterday_peak': match[7],
                        'limitation': self._extract_limitation(text, match[0]),
                        'shutdown_machines': self._extract_shutdown_info(text, match[0]),
                        'maintenance_status': self._extract_maintenance_status(text, match[0]),
                        'actual_peak': self._extract_actual_peak(text, match[0]),
                        'probable_peak': self._extract_probable_peak(text, match[0]),
                        'shortfall': self._extract_shortfall(text, match[0]),
                        'remarks': self._extract_remarks(text, match[0]),
                        'startup_date': self._extract_startup_date(text, match[0])
                    }
                    stations.append(station_data)
            
            # If no stations found, create sample data for testing
            if not stations:
                stations = self._create_sample_data()
                
        except Exception as e:
            print(f"Error parsing power station data: {e}")
            stations = self._create_sample_data()
        
        return stations
    
    def _extract_limitation(self, text, station_name):
        """Extract limitation information for a specific station"""
        try:
            pattern = rf'{re.escape(station_name)}.*?(?:Gas|Coal|Oil|Water).*?Limitation.*?([^\n]+)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else 'None'
        except:
            return 'None'
    
    def _extract_shutdown_info(self, text, station_name):
        """Extract shutdown machine information"""
        try:
            pattern = rf'{re.escape(station_name)}.*?shut.*?down.*?([^\n]+)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else 'None'
        except:
            return 'None'
    
    def _extract_maintenance_status(self, text, station_name):
        """Extract maintenance status"""
        try:
            pattern = rf'{re.escape(station_name)}.*?(?:Maintenance|maintenance).*?([^\n]+)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else 'Operational'
        except:
            return 'Operational'
    
    def _extract_actual_peak(self, text, station_name):
        """Extract actual peak generation"""
        try:
            pattern = rf'{re.escape(station_name)}.*?Actual.*?Peak.*?(\d+\.?\d*)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(1) if match else '0'
        except:
            return '0'
    
    def _extract_probable_peak(self, text, station_name):
        """Extract probable peak generation"""
        try:
            pattern = rf'{re.escape(station_name)}.*?Probable.*?Peak.*?(\d+\.?\d*)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(1) if match else '0'
        except:
            return '0'
    
    def _extract_shortfall(self, text, station_name):
        """Extract generation shortfall"""
        try:
            pattern = rf'{re.escape(station_name)}.*?shortfall.*?(\d+\.?\d*)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(1) if match else '0'
        except:
            return '0'
    
    def _extract_remarks(self, text, station_name):
        """Extract remarks/description"""
        try:
            pattern = rf'{re.escape(station_name)}.*?(?:Description|Remarks).*?([^\n]+)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else 'No remarks'
        except:
            return 'No remarks'
    
    def _extract_startup_date(self, text, station_name):
        """Extract probable startup date"""
        try:
            pattern = rf'{re.escape(station_name)}.*?start.*?up.*?date.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(1) if match else 'TBD'
        except:
            return 'TBD'
    
    def _create_sample_data(self):
        """Create sample data when PDF parsing fails"""
        return [
            {
                'name': 'Comilla Combined Cycle',
                'units': '2',
                'unit_capacity': '200',
                'installed_capacity': '400',
                'derated_capacity': '380',
                'yesterday_gen': '350',
                'today_gen': '365',
                'yesterday_peak': '375',
                'limitation': 'Gas supply limited',
                'shutdown_machines': 'None',
                'maintenance_status': 'Operational',
                'actual_peak': '365',
                'probable_peak': '380',
                'shortfall': '15',
                'remarks': 'Operating normally',
                'startup_date': 'N/A'
            },
            {
                'name': 'Comilla Steam',
                'units': '1',
                'unit_capacity': '150',
                'installed_capacity': '150',
                'derated_capacity': '140',
                'yesterday_gen': '120',
                'today_gen': '135',
                'yesterday_peak': '130',
                'limitation': 'Coal quality issue',
                'shutdown_machines': 'None',
                'maintenance_status': 'Operational',
                'actual_peak': '135',
                'probable_peak': '140',
                'shortfall': '5',
                'remarks': 'Coal supply improved',
                'startup_date': 'N/A'
            }
        ]
    
    def extract_national_demand(self, text):
        """Extract national demand information"""
        try:
            # Multiple patterns to catch different formats
            demand_patterns = [
                r'National.*?Demand.*?(\d+\.?\d*)',
                r'NATIONAL.*?DEMAND.*?(\d+\.?\d*)',
                r'Total.*?Demand.*?(\d+\.?\d*)',
                r'System.*?Demand.*?(\d+\.?\d*)',
                r'Demand.*?(\d+\.?\d*)\s*MW'
            ]
            
            demand_value = None
            for pattern in demand_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    demand_value = match.group(1)
                    break
            
            if demand_value:
                return {
                    'national_demand': demand_value,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                # Return sample data if not found
                return {
                    'national_demand': '12500',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            print(f"Error extracting national demand: {e}")
            return {
                'national_demand': '12500',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

# Initialize extractor
extractor = PDFDataExtractor()




@views.route("/")
@views.route("/home")
@login_required
def home():
    return render_template("index.html", user=current_user)

@views.route("/user_info", methods=["GET", "POST"])
@login_required
def user_info():
    # Get or create profile for current user
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
    
    if request.method == "POST":
        # Personal Information
        profile.fathers_name = request.form.get("fathers_name")
        profile.mothers_name = request.form.get("mothers_name")
        profile.date_of_birth = request.form.get("date_of_birth")
        profile.phone = request.form.get("phone")
        profile.guardians_name = request.form.get("guardians_name")
        profile.guardians_phone = request.form.get("guardians_phone")
        profile.hall_for_residence = request.form.get("hall_for_residence")
        profile.hall_for_roll = request.form.get("hall_for_roll")
        profile.blood_group = request.form.get("blood_group")
        profile.religion = request.form.get("religion")
        profile.nationality = request.form.get("nationality")
        profile.nid_number = request.form.get("nid_number")
        profile.gender = request.form.get("gender")
        profile.marital_status = request.form.get("marital_status")
        
        # Present Address
        profile.present_division = request.form.get("present_division")
        profile.present_district = request.form.get("present_district")
        profile.present_upazilla = request.form.get("present_upazilla")
        profile.present_post_office = request.form.get("present_post_office")
        profile.present_village = request.form.get("present_village")
        profile.present_house_name = request.form.get("present_house_name")
        profile.present_house_no = request.form.get("present_house_no")
        profile.present_road_no = request.form.get("present_road_no")
        
        # Permanent Address
        profile.permanent_division = request.form.get("permanent_division")
        profile.permanent_district = request.form.get("permanent_district")
        profile.permanent_upazilla = request.form.get("permanent_upazilla")
        profile.permanent_post_office = request.form.get("permanent_post_office")
        profile.permanent_village = request.form.get("permanent_village")
        profile.permanent_house_name = request.form.get("permanent_house_name")
        profile.permanent_house_no = request.form.get("permanent_house_no")
        profile.permanent_road_no = request.form.get("permanent_road_no")
        
        # Academic Information
        profile.academic_level = request.form.get("academic_level")
        profile.faculty = request.form.get("faculty")
        profile.department = request.form.get("department")
        profile.session = request.form.get("session")
        profile.year_term = request.form.get("year_term")
        profile.student_id = request.form.get("student_id")

         # Energy Meter Information
        profile.meter_id = request.form.get("meter_id")
        profile.connection_type = request.form.get("connection_type")
        profile.phone_no = request.form.get("phone_no")
        profile.installation_date = request.form.get("installation_date")
        profile.supply_voltage = request.form.get("supply_voltage")
        
        db.session.commit()
        flash("Profile information updated successfully!", "success")
        return render_template("profile_info.html", user=current_user, profile=profile)
    
    return render_template("profile_form.html", user=current_user, profile=profile)

@views.route("/edit_profile")
@login_required
def edit_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    return render_template("profile_form.html", user=current_user, profile=profile)

@views.route("/view_profile")
@login_required
def view_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
        flash("Please complete your profile information.", "info")
        return redirect(url_for("views.edit_profile"))
    
    return render_template("profile_info.html", user=current_user, profile=profile)


@views.route('/balance')
@login_required
def balance():
    # Get the current user's meter account
    db.session.expire_all()
    meter_account = MeterAccount.query.filter_by(user_id=current_user.id).first()
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    # If the user doesn't have a meter account yet, create one
    if not meter_account:
        meter_id = f"BD-{datetime.now().year}-{str(current_user.id).zfill(4)}"
        meter_account = MeterAccount(meter_id=meter_id, user_id=current_user.id)
        db.session.add(meter_account)
        db.session.commit()
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(meter_account_id=meter_account.id).order_by(Transaction.created_at.desc()).limit(5).all()
    
    return render_template('check_balance.html', meter_account=meter_account, transactions=recent_transactions, profile=profile)

@views.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')



@views.route('/payment')
@login_required
def payment():
    return render_template('payment.html')

@views.route('/pay', methods=['POST'])
def pay():
    meter_id = request.form['meter_id']
    amount = request.form['amount']

    # Validate meter_id exists in either MeterAccount or Profile
    meter_account = MeterAccount.query.filter_by(meter_id=meter_id).first()
    profile = None
    
    if not meter_account:
        # Check if meter_id exists in Profile table
        profile = Profile.query.filter_by(meter_id=meter_id).first()
        if not profile:
            return f"Meter ID {meter_id} not found", 404
        
        # Check if user already has a MeterAccount
        meter_account = MeterAccount.query.filter_by(user_id=profile.user_id).first()
        if not meter_account:
            # Create MeterAccount for this user
            meter_account = MeterAccount(
                meter_id=meter_id,
                user_id=profile.user_id,
                balance=90.0  # Default balance
            )
            db.session.add(meter_account)
            db.session.commit()

    store_id = ''
    store_passwd = ''

    post_body = {
        'store_id': store_id,
        'store_passwd': store_passwd,
        'total_amount': amount,
        'currency': 'BDT',
        'tran_id': f"TXN_{meter_id}_{amount}",
        'success_url': 'http://127.0.0.1:5000/success',
        'fail_url': 'http://127.0.0.1:5000/fail',
        'cancel_url': 'http://127.0.0.1:5000/cancel',
        'cus_name': 'Meter User',
        'cus_email': 'user@example.com',
        'cus_add1': 'Noakhali',
        'cus_phone': '01711111111',
        'shipping_method': 'NO',
        'product_name': f"Meter Recharge for {meter_id}",
        'product_category': 'Recharge',
        'product_profile': 'general',
    }

    response = requests.post('', data=post_body)
    response_data = response.json()

    if response_data.get('status') == 'SUCCESS':
        return redirect(response_data['GatewayPageURL'])
    else:
        return "Payment initiation failed", 400
    
@views.route('/success', methods=['GET', 'POST'])
def success():
    # Try to get val_id from both GET and POST parameters
    val_id = request.args.get('val_id') or request.form.get('val_id')
    
    # Debug: Print all parameters received
    print("GET parameters:", dict(request.args))
    print("POST parameters:", dict(request.form))
    
    if not val_id:
        return "Missing val_id parameter", 400

    validation_url = ""
    params = {
        'val_id': val_id,
        'store_id': '',
        'store_passwd': '',
        'format': 'json'
    }

    response = requests.get(validation_url, params=params)
    try:
        result = response.json()
    except Exception:
        return f"Invalid response from payment gateway: {response.text}", 500

    print("Payment validation result:", result)  # Debug print

    status = result.get('status')
    if status != 'VALID':
        return f"Payment validation failed: {result}", 400

    amount = float(result.get('amount', 0))
    tran_id = result.get('tran_id')  # Expected format: TXN_<meter_id>_<amount>
    if not tran_id:
        return "Transaction ID missing", 400

    parts = tran_id.split('_')
    if len(parts) < 3:
        return "Invalid transaction ID format", 400

    meter_id = parts[1]
    print(f"Extracted meter_id from transaction: {meter_id}")

    # First try to find in MeterAccount table
    meter_account = MeterAccount.query.filter_by(meter_id=meter_id).first()
    
    # If not found in MeterAccount, try to find by Profile's meter_id
    if not meter_account:
        print(f"Meter not found in MeterAccount, searching in Profile...")
        profile = Profile.query.filter_by(meter_id=meter_id).first()
        if profile:
            # Find or create MeterAccount for this user
            meter_account = MeterAccount.query.filter_by(user_id=profile.user_id).first()
            if not meter_account:
                # Create new MeterAccount if it doesn't exist
                meter_account = MeterAccount(
                    meter_id=meter_id,
                    user_id=profile.user_id,
                    balance=0.0
                )
                db.session.add(meter_account)
                db.session.commit()
                print(f"Created new MeterAccount for meter_id: {meter_id}")
    
    if not meter_account:
        return f"Meter ID {meter_id} not found in system", 404

    print(f"Found meter account: {meter_account.meter_id}, current balance: {meter_account.balance}")

    # Update balance
    old_balance = meter_account.balance
    meter_account.balance += amount
    db.session.commit()

    print(f"Balance updated: {old_balance} + {amount} = {meter_account.balance}")

    # Log the transaction
    transaction = Transaction(
        meter_account_id=meter_account.id,
        amount=amount,
        transaction_type='credit',
        description='Recharge via SSLCommerz',
        reference_id=tran_id
    )
    db.session.add(transaction)
    db.session.commit()

    # Prepare data for rendering balance page
    recent_transactions = Transaction.query.filter_by(meter_account_id=meter_account.id)\
                                           .order_by(Transaction.created_at.desc()).limit(5).all()

    # Get profile
    profile = Profile.query.filter_by(user_id=meter_account.user_id).first()

    return render_template('check_balance.html',
                           meter_account=meter_account,
                           transactions=recent_transactions,
                           profile=profile,
                           message=f"Recharge successful! ৳{amount} added. New balance: ৳{meter_account.balance}")


@views.route('/fail')
def fail():
    return "Payment Failed"

@views.route('/cancel')
def cancel():
    return "Payment Canceled"



@views.route('/sendfunds', methods=['GET', 'POST'])
@login_required
def sendfunds():
    if request.method == 'GET':
        return render_template('sendfunds.html')

    print(f"[DEBUG] POST request received")
    print(f"[DEBUG] Form data: {request.form}")
    
    # POST method logic
    receiver_meter_id = request.form.get('meter_id')
    amount_str = request.form.get('amount')

    print(f"[DEBUG] Receiver meter ID: {receiver_meter_id}")
    print(f"[DEBUG] Amount string: {amount_str}")

    # Validate input
    if not receiver_meter_id or not amount_str:
        print(f"[DEBUG] Missing required fields")
        flash('Meter ID and Amount are required.', 'error')
        return redirect(url_for('views.sendfunds'))

    try:
        amount = float(amount_str)
        print(f"[DEBUG] Parsed amount: {amount}")
        if amount <= 0:
            raise ValueError("Amount must be positive.")
    except ValueError as e:
        print(f"[DEBUG] Amount validation error: {e}")
        flash('Invalid amount entered.', 'error')
        return redirect(url_for('views.sendfunds'))

    print(f"[DEBUG] Current user ID: {current_user.id}")

    try:
        print(f"[DEBUG] Starting transaction...")
        
        # Use the same logic as /success route to find sender's meter account
        # First try to find sender in MeterAccount table
        sender_account = MeterAccount.query.filter_by(user_id=current_user.id).first()
        sender_meter_id = None
        
        # If not found in MeterAccount, try to find by Profile's meter_id
        if not sender_account:
            print(f"[DEBUG] Sender not found in MeterAccount, searching in Profile...")
            sender_profile = Profile.query.filter_by(user_id=current_user.id).first()
            if sender_profile and sender_profile.meter_id:
                sender_meter_id = sender_profile.meter_id
                # Create new MeterAccount if it doesn't exist
                sender_account = MeterAccount(
                    meter_id=sender_meter_id,
                    user_id=current_user.id,
                    balance=90.0
                )
                db.session.add(sender_account)
                db.session.commit()
                print(f"[DEBUG] Created new sender MeterAccount for meter_id: {sender_meter_id}")
            else:
                print(f"[DEBUG] Sender profile or meter ID missing")
                flash('Your meter ID not found. Please update your profile.', 'error')
                return redirect(url_for('views.sendfunds'))
        else:
            sender_meter_id = sender_account.meter_id
            print(f"[DEBUG] Sender account found with meter_id: {sender_meter_id}")

        print(f"[DEBUG] Sender account ID: {sender_account.id}, Balance: {sender_account.balance}")

        # Prevent self-transfer
        if sender_meter_id == receiver_meter_id:
            print(f"[DEBUG] Self-transfer attempt")
            flash('You cannot send funds to yourself.', 'error')
            return redirect(url_for('views.sendfunds'))

        # Check if sender has sufficient balance  
        if sender_account.balance < amount:
            print(f"[DEBUG] Insufficient balance: {sender_account.balance} < {amount}")
            flash(f'Insufficient balance. Your current balance is ৳{sender_account.balance}', 'error')
            return redirect(url_for('views.sendfunds'))

        # Use the same logic as /success route to find receiver
        # First try to find in MeterAccount table
        receiver_account = MeterAccount.query.filter_by(meter_id=receiver_meter_id).first()
        
        # If not found in MeterAccount, try to find by Profile's meter_id
        if not receiver_account:
            print(f"[DEBUG] Receiver not found in MeterAccount, searching in Profile...")
            receiver_profile = Profile.query.filter_by(meter_id=receiver_meter_id).first()
            if receiver_profile:
                # Find or create MeterAccount for this user
                receiver_account = MeterAccount.query.filter_by(user_id=receiver_profile.user_id).first()
                if not receiver_account:
                    # Create new MeterAccount if it doesn't exist
                    receiver_account = MeterAccount(
                        meter_id=receiver_meter_id,
                        user_id=receiver_profile.user_id,
                        balance=90.0
                    )
                    db.session.add(receiver_account)
                    db.session.commit()
                    print(f"[DEBUG] Created new receiver MeterAccount for meter_id: {receiver_meter_id}")
            else:
                print(f"[DEBUG] Receiver not found")
                flash(f'Receiver meter ID {receiver_meter_id} not found.', 'error')
                return redirect(url_for('views.sendfunds'))
        
        print(f"[DEBUG] Receiver account ID: {receiver_account.id}, Balance: {receiver_account.balance}")

        print(f"[DEBUG] Before transfer:")
        print(f"[DEBUG] - Sender balance: ৳{sender_account.balance}")
        print(f"[DEBUG] - Receiver balance: ৳{receiver_account.balance}")
        print(f"[DEBUG] - Transfer amount: ৳{amount}")

        # Update balances
        old_sender_balance = sender_account.balance
        old_receiver_balance = receiver_account.balance
        
        sender_account.balance -= amount
        receiver_account.balance += amount

        print(f"[DEBUG] After balance update (before commit):")
        print(f"[DEBUG] - Sender balance: ৳{sender_account.balance}")
        print(f"[DEBUG] - Receiver balance: ৳{receiver_account.balance}")

        # Create transaction records
        sender_transaction = Transaction(
            meter_account_id=sender_account.id,
            amount=amount,
            transaction_type='send',
            description=f'Sent to {receiver_meter_id}',
            sender_id=sender_account.id,
            receiver_id=receiver_account.id
        )

        receiver_transaction = Transaction(
            meter_account_id=receiver_account.id,
            amount=amount,
            transaction_type='receive',
            description=f'Received from {sender_meter_id}',
            sender_id=sender_account.id,
            receiver_id=receiver_account.id
        )

        db.session.add(sender_transaction)
        db.session.add(receiver_transaction)
        
        print(f"[DEBUG] Committing transaction...")
        db.session.commit()
        
        print(f"[DEBUG] Transaction committed successfully!")
        print(f"[DEBUG] Final balances:")
        print(f"[DEBUG] - Sender: {old_sender_balance} -> {sender_account.balance}")
        print(f"[DEBUG] - Receiver: {old_receiver_balance} -> {receiver_account.balance}")

        # Verify the balances were actually saved
        db.session.refresh(sender_account)
        db.session.refresh(receiver_account)
        print(f"[DEBUG] Verified balances after refresh:")
        print(f"[DEBUG] - Sender: {sender_account.balance}")
        print(f"[DEBUG] - Receiver: {receiver_account.balance}")

        flash(f'Successfully sent ৳{amount} to {receiver_meter_id}. Your new balance: ৳{sender_account.balance}', 'success')
        return redirect(url_for('views.balance'))

    except Exception as e:
        print(f"[DEBUG] ERROR during transfer: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        flash(f'Transfer failed: {str(e)}', 'error')
        return redirect(url_for('views.sendfunds'))




@views.route('/requestfunds')
@login_required
def requestfunds():
    return render_template('requestfunds.html')


@views.route('/sms', methods=['GET', 'POST'])
def send_sms():
    if request.method == 'POST':
        number = request.form['number']
        message = request.form['message']

        # URL encode the message
        encoded_message = urllib.parse.quote(message)
        url = f"http://bulksmsbd.net/api/smsapi?api_key={API_KEY}&type=text&number={number}&senderid={SENDER_ID}&message={encoded_message}"

        # Send GET request to API
        response = requests.get(url)

        if response.status_code == 200 and 'SMS Submitted Successfully' in response.text:
            flash("✅ SMS sent successfully!", "success")
        else:
            flash(f"❌ Failed to send SMS. Response: {response.text}", "danger")

    return render_template("sms.html")



@views.route('/complain', methods=['GET', 'POST'])
def complain():
    form = ComplaintForm()
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{file.filename}"
                secure_name = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(secure_name)
                image_path = secure_name

        complaint_data = {
            'title': form.title.data,
            'description': form.description.data,
            'email': form.email.data,
            'phone': form.phone.data or 'Not provided'
        }

        if send_complaint_email(complaint_data, image_path):
            send_confirmation_email(form.email.data, form.title.data)
            flash("Complaint submitted successfully!", 'success')
            return redirect(url_for('views.complain'))
        else:
            flash("Something went wrong. Please try again.", 'error')

    return render_template('complain.html', form=form)

@views.app_errorhandler(413)
def too_large(e):
    flash("File too large. Please upload a file under 5MB.", 'error')
    return redirect(url_for('views.complain'))

@views.route('/power_grid')
@login_required
def power_grid():
    return render_template('power_grid.html')

@views.route('/bill_summary')
@login_required
def bill_summary():
    return render_template('bill_summary.html', user=current_user)

@views.route('/payment_history')
@login_required
def payment_history():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get filter parameters
    transaction_type = request.args.get('type', 'all')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    print(f"[DEBUG] Payment history request - User: {current_user.id}, Page: {page}")
    
    try:
        # Find user's meter account using the same logic as other routes
        user_meter_account = MeterAccount.query.filter_by(user_id=current_user.id).first()
        
        if not user_meter_account:
            # Try to find by Profile's meter_id
            user_profile = Profile.query.filter_by(user_id=current_user.id).first()
            if user_profile and user_profile.meter_id:
                # Create new MeterAccount if it doesn't exist
                user_meter_account = MeterAccount(
                    meter_id=user_profile.meter_id,
                    user_id=current_user.id,
                    balance=90.0
                )
                db.session.add(user_meter_account)
                db.session.commit()
                print(f"[DEBUG] Created new MeterAccount for user: {current_user.id}")
            else:
                flash('Your meter account not found. Please update your profile.', 'error')
                return redirect(url_for('views.profile'))
        
        print(f"[DEBUG] Found meter account: {user_meter_account.meter_id}")
        
        # Build query to get all transactions related to this user
        # This includes: transactions on their account, transactions they sent, transactions they received
        base_query = db.session.query(Transaction).filter(
            db.or_(
                Transaction.meter_account_id == user_meter_account.id,
                Transaction.sender_id == user_meter_account.id,
                Transaction.receiver_id == user_meter_account.id
            )
        )
        
        # Apply transaction type filter
        if transaction_type != 'all':
            if transaction_type == 'credit':
                # Show credit transactions (recharges) and received funds
                base_query = base_query.filter(
                    db.or_(
                        Transaction.transaction_type == 'credit',
                        db.and_(
                            Transaction.transaction_type == 'receive',
                            Transaction.receiver_id == user_meter_account.id
                        )
                    )
                )
            elif transaction_type == 'debit':
                # Show sent transactions
                base_query = base_query.filter(
                    db.and_(
                        Transaction.transaction_type == 'send',
                        Transaction.sender_id == user_meter_account.id
                    )
                )
            else:
                base_query = base_query.filter(Transaction.transaction_type == transaction_type)
        
        # Apply date filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                base_query = base_query.filter(Transaction.created_at >= from_date)
            except ValueError:
                flash('Invalid from date format. Use YYYY-MM-DD.', 'error')
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                # Add 1 day to include the entire day
                to_date = to_date + timedelta(days=1)
                base_query = base_query.filter(Transaction.created_at < to_date)
            except ValueError:
                flash('Invalid to date format. Use YYYY-MM-DD.', 'error')
        
        # Order by most recent first
        base_query = base_query.order_by(Transaction.created_at.desc())
        
        # Paginate the results
        transactions = base_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        print(f"[DEBUG] Found {transactions.total} transactions")
        
        # Calculate totals for summary
        total_credits = db.session.query(db.func.sum(Transaction.amount)).filter(
            db.or_(
                db.and_(Transaction.transaction_type == 'credit', Transaction.meter_account_id == user_meter_account.id),
                db.and_(Transaction.transaction_type == 'receive', Transaction.receiver_id == user_meter_account.id)
            )
        ).scalar() or 0.0
        
        total_debits = db.session.query(db.func.sum(Transaction.amount)).filter(
            db.and_(Transaction.transaction_type == 'send', Transaction.sender_id == user_meter_account.id)
        ).scalar() or 0.0
        
        # Get user profile for display
        user_profile = Profile.query.filter_by(user_id=current_user.id).first()
        
        return render_template('payment_history.html',
                             transactions=transactions,
                             meter_account=user_meter_account,
                             profile=user_profile,
                             total_credits=total_credits,
                             total_debits=total_debits,
                             current_type=transaction_type,
                             current_date_from=date_from,
                             current_date_to=date_to)
    
    except Exception as e:
        print(f"[DEBUG] ERROR in payment_history: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error loading payment history.', 'error')
        return redirect(url_for('views.balance'))


@views.route('/export_transactions')
@login_required
def export_transactions():
    """Export transactions to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    try:
        # Find user's meter account
        user_meter_account = MeterAccount.query.filter_by(user_id=current_user.id).first()
        
        if not user_meter_account:
            user_profile = Profile.query.filter_by(user_id=current_user.id).first()
            if not user_profile or not user_profile.meter_id:
                flash('Your meter account not found.', 'error')
                return redirect(url_for('views.payment_history'))
            
            user_meter_account = MeterAccount(
                meter_id=user_profile.meter_id,
                user_id=current_user.id,
                balance=90.0
            )
            db.session.add(user_meter_account)
            db.session.commit()
        
        # Get all transactions
        transactions = db.session.query(Transaction).filter(
            db.or_(
                Transaction.meter_account_id == user_meter_account.id,
                Transaction.sender_id == user_meter_account.id,
                Transaction.receiver_id == user_meter_account.id
            )
        ).order_by(Transaction.created_at.desc()).all()
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date', 'Type', 'Amount (৳)', 'Description', 'Reference ID', 'Balance Impact'
        ])
        
        # Write data
        for transaction in transactions:
            # Determine balance impact for this user
            if transaction.transaction_type == 'credit':
                balance_impact = f'+{transaction.amount}'
            elif transaction.transaction_type == 'send' and transaction.sender_id == user_meter_account.id:
                balance_impact = f'-{transaction.amount}'
            elif transaction.transaction_type == 'receive' and transaction.receiver_id == user_meter_account.id:
                balance_impact = f'+{transaction.amount}'
            else:
                balance_impact = '0'
            
            writer.writerow([
                transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                transaction.transaction_type.title(),
                transaction.amount,
                transaction.description or '',
                transaction.reference_id or '',
                balance_impact
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=transactions_{user_meter_account.meter_id}_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response
        
    except Exception as e:
        print(f"[DEBUG] ERROR in export_transactions: {str(e)}")
        flash('Error exporting transactions.', 'error')
        return redirect(url_for('views.payment_history'))


@views.route('/energy_uses')
@login_required
def energy_uses():
    return render_template('energy_uses.html')


@views.route('/componets')
@login_required
def components():
    return render_template('components.html')


@views.route('/api/extract-data', methods=['GET'])
def extract_data():
    """API endpoint to extract PDF data for today"""
    try:
        # Get today's PDF
        pdf_url = extractor.get_pdf_url()
        
        # Extract text from PDF
        text = extractor.extract_pdf_text(pdf_url)
        
        if not text:
            return jsonify({
                'error': 'Failed to extract PDF data. PDF might not be available or accessible.',
                'success': False
            }), 500
        
        # Parse data
        stations = extractor.parse_power_station_data(text)
        national_demand = extractor.extract_national_demand(text)
        
        return jsonify({
            'success': True,
            'pdf_url': pdf_url,
            'national_demand': national_demand,
            'comilla_stations': stations,
            'extraction_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_stations': len(stations)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}',
            'success': False
        }), 500

@views.route('/api/extract-data/<date>', methods=['GET'])
def extract_data_by_date(date):
    """API endpoint to extract PDF data for specific date"""
    try:
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD format.',
                'success': False
            }), 400
        
        # Get PDF for specific date
        pdf_url = extractor.get_pdf_url(date)
        
        # Extract text from PDF
        text = extractor.extract_pdf_text(pdf_url)
        
        if not text:
            return jsonify({
                'error': f'Failed to extract PDF data for {date}. PDF might not be available.',
                'success': False
            }), 500
        
        # Parse data
        stations = extractor.parse_power_station_data(text)
        national_demand = extractor.extract_national_demand(text)
        
        return jsonify({
            'success': True,
            'pdf_url': pdf_url,
            'date': date,
            'national_demand': national_demand,
            'comilla_stations': stations,
            'extraction_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_stations': len(stations)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}',
            'success': False
        }), 500

@views.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'service': 'BPDB PDF Extractor'
    })

@views.route('/api/test-pdf/<date>', methods=['GET'])
def test_pdf_access(date):
    """Test if PDF is accessible for a given date"""
    try:
        pdf_url = extractor.get_pdf_url(date)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(pdf_url, headers=headers, timeout=10)
        
        return jsonify({
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'pdf_url': pdf_url,
            'accessible': response.status_code == 200,
            'content_type': response.headers.get('content-type', 'unknown'),
            'content_length': response.headers.get('content-length', 'unknown')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'pdf_url': pdf_url if 'pdf_url' in locals() else 'unknown'
        })

@views.route('/api/raw-text/<date>', methods=['GET'])
def get_raw_text(date):
    """Get raw extracted text for debugging purposes"""
    try:
        pdf_url = extractor.get_pdf_url(date)
        text = extractor.extract_pdf_text(pdf_url)
        
        if not text:
            return jsonify({
                'error': 'Failed to extract text from PDF',
                'success': False
            }), 500
        
        return jsonify({
            'success': True,
            'pdf_url': pdf_url,
            'raw_text': text[:2000] + '...' if len(text) > 2000 else text,  # Limit text length
            'text_length': len(text),
            'extraction_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}',
            'success': False
        }), 500

# Error handlers
@views.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'success': False
    }), 404

@views.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'success': False
    }), 500

@views.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')
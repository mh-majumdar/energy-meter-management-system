from .extensions import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    
    # One-to-one relationship with Profile
    profile = db.relationship('Profile', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Personal Information
    fathers_name = db.Column(db.String(150))
    mothers_name = db.Column(db.String(150))
    date_of_birth = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    guardians_name = db.Column(db.String(150))
    guardians_phone = db.Column(db.String(20))
    hall_for_residence = db.Column(db.String(150))
    hall_for_roll = db.Column(db.String(150))
    blood_group = db.Column(db.String(10))
    religion = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    nid_number = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    marital_status = db.Column(db.String(20))
   
    
    # Present Address
    present_division = db.Column(db.String(100))
    present_district = db.Column(db.String(100))
    present_upazilla = db.Column(db.String(100))
    present_post_office = db.Column(db.String(100))
    present_village = db.Column(db.String(100))
    present_house_name = db.Column(db.String(100))
    present_house_no = db.Column(db.String(30))
    present_road_no = db.Column(db.String(30))
    
    # Permanent Address
    permanent_division = db.Column(db.String(100))
    permanent_district = db.Column(db.String(100))
    permanent_upazilla = db.Column(db.String(100))
    permanent_post_office = db.Column(db.String(100))
    permanent_village = db.Column(db.String(100))
    permanent_house_name = db.Column(db.String(100))
    permanent_house_no = db.Column(db.String(30))
    permanent_road_no = db.Column(db.String(30))
    
    # Academic Information
    academic_level = db.Column(db.String(50))
    faculty = db.Column(db.String(150))
    department = db.Column(db.String(150))
    session = db.Column(db.String(20))
    year_term = db.Column(db.String(30))
    student_id = db.Column(db.String(20))

    meter_id = db.Column(db.String(100))
    connection_type = db.Column(db.String(50))
    phone_no = db.Column(db.String(100))
    installation_date = db.Column(db.String(20))  # Can use db.Date if you process it
    supply_voltage = db.Column(db.String(50))
 
    # Timestamp
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

class MeterAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.String(20), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Float, default=90.0)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Define the relationship with User
    user = db.relationship('User', backref=db.backref('meter_account', uselist=False))
    
    # Define relationship with Transaction - specify foreign_keys explicitly
    transactions = db.relationship('Transaction', 
                                  foreign_keys='Transaction.meter_account_id',
                                  backref='account', 
                                  lazy=True)
    
    # Sent transactions
    sent_transactions = db.relationship('Transaction',
                                      foreign_keys='Transaction.sender_id',
                                      backref='sender',
                                      lazy=True)
    
    # Received transactions
    received_transactions = db.relationship('Transaction',
                                         foreign_keys='Transaction.receiver_id',
                                         backref='receiver',
                                         lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meter_account_id = db.Column(db.Integer, db.ForeignKey('meter_account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'add', 'send', 'receive'
    description = db.Column(db.String(255))
    reference_id = db.Column(db.String(100), nullable=True)  # Add this field
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    
    # For send/receive transactions
    sender_id = db.Column(db.Integer, db.ForeignKey('meter_account.id'), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('meter_account.id'), nullable=True)
# Digital Meter Service

A comprehensive digital meter management system built with Flask, designed to help users monitor electricity consumption, manage bills, process payments, and submit complaints through an intuitive web interface.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **User Authentication**: Secure user registration and login with password hashing
- **User Profiles**: Comprehensive user profile management including personal, contact, and address information
- **Meter Management**: Track and manage meter accounts
- **Bill Tracking**: View and manage electricity bills and consumption
- **Payment Processing**: Process and track electricity payments
- **Transaction History**: Detailed transaction and payment history
- **Complaint System**: Submit and track electricity-related complaints with PDF support
- **SMS Notifications**: Send SMS alerts via BulkSMSBD API
- **Email Notifications**: Email-based communication for complaints and confirmations
- **Admin Dashboard**: Administrative interface for managing users and complaints
- **Responsive UI**: Modern, mobile-friendly interface with CSS styling

## 🛠️ Tech Stack

### Backend

- **Python 3.x**
- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM for database management
- **Flask-Login** - User session management
- **Flask-Mail** - Email sending
- **Flask-WTF** - Form handling and CSRF protection
- **WTForms** - Form validation

### Frontend

- **HTML5**
- **CSS3**
- **JavaScript**
- **Jinja2** - Templating engine

### Additional Libraries

- **PyPDF2** - PDF file handling
- **Requests** - HTTP requests library
- **BulkSMSBD API** - SMS service integration

### Database

- **SQLite** (default) or configurable SQL database via SQLAlchemy

## 📁 Project Structure

Digital Meter Service/
├── app.py # Application entry point
├── website/ # Main Flask package
│ ├── **init**.py # Flask app initialization, mail config
│ ├── auth.py # Authentication routes (login/signup)
│ ├── views.py # Main application views and routes
│ ├── models.py # Database models (User, Profile, etc.)
│ ├── extensions.py # Flask extensions initialization
│ ├── complain.py # Complaint handling and forms
│ ├── scheduler.py # Background task scheduling
│ ├── sms_utils.py # SMS utility functions
│ ├── static/ # Static files
│ │ ├── \*.css # Stylesheets
│ │ └── Images/ # Image assets
│ └── Templates/ # HTML templates
│ ├── base.html # Base template
│ ├── index.html # Homepage
│ ├── login.html # Login page
│ ├── signup.html # Registration page
│ ├── dashboard.html
│ ├── bill_summary.html
│ ├── check_balance.html
│ ├── payment.html
│ ├── complain.html
│ ├── admin_dashboard.html
│ └── [other templates]
├── instance/ # Instance-specific configuration
├── README.md # This file
└── pycache/ # Python cache files

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/digital-meter-service.git
   cd digital-meter-service

   ```

2. **Create a virtual environment**
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate

3. **Install dependencies**
   pip install flask flask-sqlalchemy flask-login flask-mail flask-wtf wtforms requests pypdf2

4. **Initialize the database**
   python

   > > > from website import create_app, db
   > > > app = create_app()
   > > > with app.app_context():
   > > > ... db.create_all()
   > > > exit()

5. **Run the application**
   python app.py

Usage
User Registration & Login
Navigate to /signup to create a new account
Use /login to log in with credentials
Dashboard
View electricity consumption and bill information
Check account balance
Access payment history
Meter Management
View all associated meter accounts
Track consumption data
Bill Payments
Process electricity bill payments
View transaction history
Complaints
Submit new complaints about electricity service
Attach supporting documents (PDF)
Track complaint status
Admin Panel
Access /admin_dashboard for administrative functions
Manage users and complaints
📝 File Descriptions
File Purpose
app.py Application entry point, starts Flask development server
**init**.py Flask app factory, database initialization, mail & SMS config
auth.py User authentication (signup, login, logout)
views.py Main application routes and view functions
models.py SQLAlchemy database models
extensions.py Flask extensions (db, login manager)
complain.py Complaint form handling and email notifications
scheduler.py Background task scheduling
sms_utils.py SMS sending utilities
🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👥 Author
[Your Name]

🙏 Acknowledgments
Flask documentation and community
BulkSMSBD for SMS service
All contributors and supporters
📧 Contact
For questions or suggestions, please contact [your-email@example.com]

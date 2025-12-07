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
3. ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
5. ```bash
   pip install flask flask-sqlalchemy flask-login flask-mail flask-wtf wtforms requests pypdf2
   ```

6. **Initialize the database**
   ```bash
   > > > from website import create_app, db
   > > > app = create_app()
   > > > with app.app_context():
   > > > ... db.create_all()
   > > > exit()
   ```

7. **Run the application**
8. ```bash
   python app.py
   ```




🙏 Acknowledgments
Flask documentation and community
BulkSMSBD for SMS service
All contributors and supporters
📧 Contact
For questions or suggestions, please contact [your-email@example.com]

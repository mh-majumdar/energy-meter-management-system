from apscheduler.schedulers.background import BackgroundScheduler
from .sms_utils import check_all_accounts_balance

def start_scheduler(app, db):
    scheduler = BackgroundScheduler()

    def job():
        with app.app_context():
            # Use db inside your check function if needed
            check_all_accounts_balance()

    scheduler.add_job(func=job, trigger="interval", minutes=1000)
    scheduler.start()
    print("✅ Scheduler started")

import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from sqlalchemy import inspect

def init_production_database():
    """
    Safe production database initialization script.
    Creates required tables if they do not exist.
    NEVER drops tables, NEVER deletes user data, and NEVER injects demo accounts.
    """
    print("=" * 60)
    print("SAFE PRODUCTION DATABASE INITIALIZATION")
    print("=" * 60)

    app = create_app()
    with app.app_context():
        engine = db.engine
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Mask credentials in output
        masked_uri = db_uri
        if '@' in masked_uri:
            proto, rest = masked_uri.split('://', 1)
            creds, host_part = rest.split('@', 1)
            if ':' in creds:
                user, _ = creds.split(':', 1)
                masked_uri = f"{proto}://{user}:****@{host_part}"
        
        print(f"Target Database   : {masked_uri}")
        print(f"Dialect / Driver  : {engine.dialect.name} / {engine.dialect.driver}")
        
        # Create tables safely (if not already existing)
        print("Checking and creating required tables...")
        db.create_all()

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"Current Tables in DB: {', '.join(existing_tables)}")

        required_tables = {'users', 'worker_profiles', 'employer_profiles', 'jobs', 'applications'}
        missing = required_tables - set(existing_tables)
        if missing:
            print(f"ERROR: Missing expected tables: {missing}")
            sys.exit(1)
        else:
            print("SUCCESS: All required tables verified successfully!")
            print("Production database is ready for live traffic.")

if __name__ == '__main__':
    init_production_database()

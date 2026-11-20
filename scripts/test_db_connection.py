import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from sqlalchemy import text

def test_connection():
    print("=" * 60)
    print("DATABASE CONNECTIVITY DIAGNOSTIC TOOL")
    print("=" * 60)

    app = create_app()
    with app.app_context():
        engine = db.engine
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        # Mask password in URI for safe display
        masked_uri = db_uri
        if '@' in masked_uri:
            proto, rest = masked_uri.split('://', 1)
            creds, host_part = rest.split('@', 1)
            if ':' in creds:
                user, _ = creds.split(':', 1)
                masked_uri = f"{proto}://{user}:****@{host_part}"

        print(f"Target Database URI : {masked_uri}")
        print(f"Database Dialect    : {engine.dialect.name}")
        print(f"Database Driver     : {engine.dialect.driver}")

        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                print(f"Connection Status   : SUCCESS (Ping result: {result})")
                
                # Check tables
                tables = engine.dialect.get_table_names(conn)
                print(f"Detected Tables     : {', '.join(tables) if tables else 'None'}")
                print("All database checks passed successfully!")
                return True
        except Exception as e:
            print(f"Connection Status   : FAILED")
            print(f"Error Details       : {str(e)}")
            print("-" * 60)
            print("Troubleshooting for External Managed Cloud MySQL:")
            print("1. Set DATABASE_URL in your .env or hosting environment variables:")
            print("   Format: mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>?ssl_ca=<ca_path>")
            print("2. Ensure your cloud MySQL database allows inbound connections from anywhere (0.0.0.0/0).")
            print("3. Check that username, password, host, and port are correct.")
            print("-" * 60)
            return False

if __name__ == '__main__':
    test_connection()

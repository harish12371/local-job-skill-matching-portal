import os
import ssl
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Environment detection
    IS_VERCEL = bool(os.environ.get('VERCEL') == '1')
    ENV = os.environ.get('FLASK_ENV', 'production' if IS_VERCEL else 'development')
    IS_PRODUCTION = (ENV == 'production') or IS_VERCEL

    # Secret key handling
    dev_default_secret = 'local-job-skill-portal-dev-secret-key-9928374'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if IS_PRODUCTION:
            # Generate a secure fallback warning in production if not explicitly configured
            SECRET_KEY = os.environ.get('SECRET_KEY', dev_default_secret)
        else:
            SECRET_KEY = dev_default_secret
    
    # Database URL handling
    # Convert 'mysql://' to 'mysql+pymysql://' for SQLAlchemy compatibility
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url:
        if raw_db_url.startswith('mysql://'):
            raw_db_url = raw_db_url.replace('mysql://', 'mysql+pymysql://', 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        # Fallback for local development if DATABASE_URL is not set
        base_dir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(base_dir, 'instance', 'local_portal.db')}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Engine options & Serverless connection pooling
    connect_args = {}
    if 'mysql' in SQLALCHEMY_DATABASE_URI:
        # Handle Managed Cloud MySQL SSL requirement (TiDB, Aiven, AWS RDS, PlanetScale)
        ssl_ca = os.environ.get('MYSQL_SSL_CA')
        if ssl_ca and os.path.exists(ssl_ca):
            connect_args['ssl'] = {'ca': ssl_ca}
        elif os.environ.get('MYSQL_SSL_REQUIRE', '').lower() in ('true', '1', 'required'):
            ssl_ctx = ssl.create_default_context()
            connect_args['ssl'] = ssl_ctx
        elif 'ssl_ca=' in SQLALCHEMY_DATABASE_URI or 'ssl=' in SQLALCHEMY_DATABASE_URI:
            pass  # Already passed via query parameter

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'connect_args': connect_args
    }
    
    # Session & Cookie security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Use Secure cookies in production (HTTPS on Vercel)
    SESSION_COOKIE_SECURE = IS_PRODUCTION or (os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ('true', '1'))
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

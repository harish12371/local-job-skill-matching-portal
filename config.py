
import os
import ssl
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv


# ============================================================
# 1. BASE DIRECTORY AND ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

# Load local .env file.
# Vercel environment variables take precedence.
load_dotenv(dotenv_path=ENV_FILE, override=False)


# ============================================================
# 2. ENVIRONMENT HELPERS
# ============================================================

def env_bool(name, default=False):
    """Convert environment variable into a boolean."""

    value = os.environ.get(name)

    if value is None:
        return default

    return value.strip().lower() in (
        "true",
        "1",
        "yes",
        "on"
    )


IS_VERCEL = os.environ.get("VERCEL") == "1"

ENV = os.environ.get(
    "FLASK_ENV",
    "production" if IS_VERCEL else "development"
)

IS_PRODUCTION = (
    ENV.lower() == "production"
    or IS_VERCEL
)


# ============================================================
# 3. FLASK CONFIGURATION
# ============================================================

class Config:

    DEBUG = not IS_PRODUCTION

    # --------------------------------------------------------
    # SECRET KEY
    # --------------------------------------------------------

    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY:

        if IS_PRODUCTION:
            raise RuntimeError(
                "SECRET_KEY must be configured in production."
            )

        SECRET_KEY = (
            "local-job-skill-portal-dev-secret-key-9928374"
        )

    # --------------------------------------------------------
    # DATABASE URL
    # --------------------------------------------------------

    raw_db_url = os.environ.get("DATABASE_URL")

    if raw_db_url:

        # Convert mysql:// into mysql+pymysql://
        if raw_db_url.startswith("mysql://"):

            raw_db_url = raw_db_url.replace(
                "mysql://",
                "mysql+pymysql://",
                1
            )

        SQLALCHEMY_DATABASE_URI = raw_db_url

    else:

        # Never use SQLite fallback in production.
        if IS_PRODUCTION:
            raise RuntimeError(
                "DATABASE_URL must be configured in production."
            )

        # Local SQLite fallback.
        instance_dir = BASE_DIR / "instance"
        instance_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        SQLALCHEMY_DATABASE_URI = (
            f"sqlite:///{instance_dir / 'local_portal.db'}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = env_bool(
        "SQLALCHEMY_ECHO",
        False
    )

    # --------------------------------------------------------
    # MYSQL / TIDB SSL CONFIGURATION
    # --------------------------------------------------------

    connect_args = {}

    is_mysql = SQLALCHEMY_DATABASE_URI.startswith(
        (
            "mysql://",
            "mysql+pymysql://"
        )
    )

    if is_mysql:

        ssl_required = env_bool(
            "MYSQL_SSL_REQUIRE",
            IS_PRODUCTION
        )

        ssl_ca = os.environ.get("MYSQL_SSL_CA")

        if ssl_ca:

            # Resolve relative certificate paths.
            ca_path = Path(ssl_ca)

            if not ca_path.is_absolute():

                ca_path = (
                    BASE_DIR / ca_path
                )

            if not ca_path.is_file():

                raise RuntimeError(
                    f"MySQL CA certificate not found: {ca_path}"
                )

            # Create verified TLS context.
            ssl_context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cafile=str(ca_path)
            )

            connect_args["ssl"] = ssl_context

        elif ssl_required:

            # Use system trusted CA certificates.
            ssl_context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH
            )

            connect_args["ssl"] = ssl_context

    # --------------------------------------------------------
    # SQLALCHEMY CONNECTION POOLING
    # --------------------------------------------------------

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "connect_args": connect_args
    }

    # --------------------------------------------------------
    # SESSION AND COOKIE SECURITY
    # --------------------------------------------------------

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = (
        IS_PRODUCTION
        or env_bool(
            "SESSION_COOKIE_SECURE",
            False
        )
    )

    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=86400
    )

    # --------------------------------------------------------
    # CSRF PROTECTION
    # --------------------------------------------------------

    WTF_CSRF_ENABLED = True

    WTF_CSRF_TIME_LIMIT = 3600

    # --------------------------------------------------------
    # REQUEST SIZE LIMIT
    # --------------------------------------------------------

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

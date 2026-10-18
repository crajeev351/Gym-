import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'vigor-gym-secret-key-super-secure-change-in-production-2026')
    
    # Database config: default to SQLite in instance/ directory if DATABASE_URL not set
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
        db_path = os.path.join(basedir, 'instance', 'gym.db').replace('\\', '/')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    else:
        # Fix legacy postgres:// prefix for SQLAlchemy compatibility
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = db_url
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))

    # Security & Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

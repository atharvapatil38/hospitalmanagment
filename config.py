import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Safely attempt to create instance directory if filesystem is writable
try:
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
except (OSError, PermissionError):
    pass

def get_database_uri(default_sqlite_filename):
    """
    Resolve SQLALCHEMY_DATABASE_URI with support for:
    - DATABASE_URL / POSTGRES_URL (Vercel Postgres, Neon, Supabase)
    - Automatic fix for postgres:// to postgresql:// (SQLAlchemy requirement)
    - Vercel serverless /tmp fallback when using SQLite
    """
    raw_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL') or os.environ.get('POSTGRES_PRISMA_URL')
    if raw_url:
        if raw_url.startswith('postgres://'):
            return raw_url.replace('postgres://', 'postgresql://', 1)
        return raw_url
    
    # If deployed on Vercel and no external DB is configured, use /tmp for SQLite
    if os.environ.get('VERCEL'):
        return 'sqlite:////tmp/careplus.db'
    
    return 'sqlite:///' + os.path.join(basedir, 'instance', default_sqlite_filename).replace('\\', '/')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'careplus-hms-super-secret-key-2026-prod'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ITEMS_PER_PAGE = 15
    HOSPITAL_NAME = 'CarePlus Multispeciality Hospital'
    HOSPITAL_EMAIL = 'contact@careplus.com'
    HOSPITAL_PHONE = '+1 (800) 555-CARE'
    HOSPITAL_ADDRESS = '742 Evergreen Healthcare Blvd, Medical District'
    HOSPITAL_CURRENCY = '₹'
    DEFAULT_TAX_RATE = 5.0  # 5%

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_database_uri('careplus_dev.db')

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = get_database_uri('careplus_prod.db')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

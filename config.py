import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost/skillbridge'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL')
    MAIL_PASSWORD = os.environ.get('APPPASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('EMAIL')
    
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Admin settings
    SUPERPASSWORD = os.environ.get('SUPERPASSWORD', 'SKILLBRIDGE')
    
    # M-Pesa settings
    MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
    MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')

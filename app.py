import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://localhost/skillbridge")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('EMAIL')
    app.config['MAIL_PASSWORD'] = os.environ.get('APPPASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL')
    
    # File upload configuration
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Add context processor for current year
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.now().year}
    
    # Register blueprints
    from blueprints.public import public_bp
    from blueprints.auth import auth_bp
    from blueprints.profiles import profiles_bp
    from blueprints.messaging import messaging_bp
    from blueprints.reviews import reviews_bp
    from blueprints.admin import admin_bp
    from blueprints.billing import billing_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profiles_bp, url_prefix='/profiles')
    app.register_blueprint(messaging_bp, url_prefix='/messages')
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(billing_bp, url_prefix='/billing')
    
    # Create database tables
    with app.app_context():
        import models
        db.create_all()
        
        # Create default admin settings
        from models import AdminSettings, MPesaEnvironment
        if not AdminSettings.query.first():
            admin_settings = AdminSettings()
            admin_settings.media_photos_enabled = True
            admin_settings.media_videos_enabled = False
            admin_settings.global_override_enabled = True  # Start with free access
            admin_settings.mpesa_env = MPesaEnvironment.SANDBOX
            admin_settings.mpesa_company_name = 'SkillBridge Africa'
            db.session.add(admin_settings)
            db.session.commit()
            
        # Create dummy profiles if none exist
        from models import User, Profile
        if Profile.query.count() == 0:
            create_dummy_profiles()
    
    return app

def create_dummy_profiles():
    """Create 10 dummy placeholder profiles for demonstration"""
    from models import User, Profile, UserRole, ProfileType, AvailabilityStatus, RateType, UrgencyLevel
    import random
    
    # Sample data for dummy profiles
    professional_data = [
        {
            "email": "demo.plumber@example.com",
            "title": "Expert Plumber - Example Profile",
            "category": "Plumbing",
            "bio": "This is a demonstration profile. Professional plumbing services with 10+ years experience.",
            "location_country": "Kenya",
            "location_county": "Nairobi",
            "location_town": "Westlands",
            "tags": "plumbing,repairs,installation,emergency",
            "years_experience": 10,
            "rate_type": "hourly",
            "rate_value": 1500
        },
        {
            "email": "demo.electrician@example.com", 
            "title": "Licensed Electrician - Example Profile",
            "category": "Electrical",
            "bio": "This is a demonstration profile. Certified electrical contractor for residential and commercial projects.",
            "location_country": "Kenya",
            "location_county": "Mombasa",
            "location_town": "Nyali",
            "tags": "electrical,wiring,installation,repair",
            "years_experience": 8,
            "rate_type": "daily",
            "rate_value": 5000
        },
        {
            "email": "demo.mason@example.com",
            "title": "Master Mason - Example Profile", 
            "category": "Masonry",
            "bio": "This is a demonstration profile. Skilled in stonework, brickwork, and concrete construction.",
            "location_country": "Kenya",
            "location_county": "Kiambu",
            "location_town": "Thika",
            "tags": "masonry,construction,stonework,concrete",
            "years_experience": 15,
            "rate_type": "fixed",
            "rate_value": 50000
        },
        {
            "email": "demo.tutor@example.com",
            "title": "Mathematics Tutor - Example Profile",
            "category": "Education",
            "bio": "This is a demonstration profile. Experienced mathematics teacher offering private tutoring.",
            "location_country": "Kenya", 
            "location_county": "Nakuru",
            "location_town": "Nakuru Town",
            "tags": "mathematics,tutoring,education,algebra",
            "years_experience": 5,
            "rate_type": "hourly",
            "rate_value": 800
        },
        {
            "email": "demo.photographer@example.com",
            "title": "Event Photographer - Example Profile",
            "category": "Photography",
            "bio": "This is a demonstration profile. Professional event and portrait photographer.",
            "location_country": "Kenya",
            "location_county": "Nairobi",
            "location_town": "Karen",
            "tags": "photography,events,portraits,weddings",
            "years_experience": 6,
            "rate_type": "fixed",
            "rate_value": 15000
        }
    ]
    
    client_data = [
        {
            "email": "demo.client1@example.com",
            "title": "Home Renovation Project - Example Profile",
            "bio": "This is a demonstration profile. Looking for skilled professionals for home renovation.",
            "location_country": "Kenya",
            "location_county": "Nairobi", 
            "location_town": "Kilimani",
            "what_looking_for": "Need plumber and electrician for bathroom renovation",
            "urgency": "This month"
        },
        {
            "email": "demo.client2@example.com",
            "title": "Wedding Planning - Example Profile", 
            "bio": "This is a demonstration profile. Planning a wedding and need various service providers.",
            "location_country": "Kenya",
            "location_county": "Kajiado",
            "location_town": "Ngong",
            "what_looking_for": "Photographer, caterer, and event coordinator needed",
            "urgency": "Flexible"
        },
        {
            "email": "demo.client3@example.com",
            "title": "Student Tutoring - Example Profile",
            "bio": "This is a demonstration profile. Parent seeking math tutor for high school student.",
            "location_country": "Kenya",
            "location_county": "Kiambu", 
            "location_town": "Ruiru",
            "what_looking_for": "Mathematics tutor for Form 3 student",
            "urgency": "This week"
        },
        {
            "email": "demo.client4@example.com",
            "title": "Construction Project - Example Profile",
            "bio": "This is a demonstration profile. Commercial construction project needs skilled workers.",
            "location_country": "Kenya",
            "location_county": "Machakos",
            "location_town": "Machakos Town", 
            "what_looking_for": "Masons and general construction workers",
            "urgency": "Today"
        },
        {
            "email": "demo.client5@example.com",
            "title": "Corporate Event - Example Profile",
            "bio": "This is a demonstration profile. Planning corporate event and need service providers.",
            "location_country": "Kenya",
            "location_county": "Nairobi",
            "location_town": "Upper Hill",
            "what_looking_for": "Event photographer and catering services",
            "urgency": "This month"
        }
    ]
    
    # Create dummy users and profiles
    for i, prof_data in enumerate(professional_data):
        user = User()
        user.email = prof_data["email"]
        user.password_hash = generate_password_hash("demo123")
        user.role = UserRole.USER
        user.is_active = True
        user.email_verified = True
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        profile = Profile()
        profile.user_id = user.id
        profile.type = ProfileType.PROFESSIONAL
        profile.title = prof_data["title"]
        profile.bio = prof_data["bio"]
        profile.location_country = prof_data["location_country"]
        profile.location_county = prof_data["location_county"]
        profile.location_town = prof_data["location_town"]
        profile.tags = prof_data["tags"]
        profile.category = prof_data["category"]
        profile.years_experience = prof_data["years_experience"]
        profile.rate_type = RateType(prof_data["rate_type"])
        profile.rate_value = prof_data["rate_value"]
        profile.availability = AvailabilityStatus.AVAILABLE
        profile.is_listed = True
        profile.is_new_user_flag = True
        db.session.add(profile)
    
    for i, client_data_item in enumerate(client_data):
        user = User()
        user.email = client_data_item["email"]
        user.password_hash = generate_password_hash("demo123")
        user.role = UserRole.USER
        user.is_active = True
        user.email_verified = True
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        profile = Profile()
        profile.user_id = user.id
        profile.type = ProfileType.CLIENT
        profile.title = client_data_item["title"]
        profile.bio = client_data_item["bio"]
        profile.location_country = client_data_item["location_country"]
        profile.location_county = client_data_item["location_county"]
        profile.location_town = client_data_item["location_town"]
        profile.what_looking_for = client_data_item["what_looking_for"]
        profile.urgency = UrgencyLevel(client_data_item["urgency"])
        profile.availability = AvailabilityStatus.AVAILABLE
        profile.is_listed = True
        profile.is_new_user_flag = True
        db.session.add(profile)
    
    db.session.commit()
    logging.info("Created 10 dummy placeholder profiles")

# Create the app instance
app = create_app()

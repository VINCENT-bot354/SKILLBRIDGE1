from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db
import enum

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class ProfileType(enum.Enum):
    CLIENT = "CLIENT"
    PROFESSIONAL = "PROFESSIONAL"

class AvailabilityStatus(enum.Enum):
    AVAILABLE = "Available"
    BUSY = "Busy"
    ON_VACATION = "On Vacation"

class UrgencyLevel(enum.Enum):
    TODAY = "Today"
    THIS_WEEK = "This week"
    THIS_MONTH = "This month"
    FLEXIBLE = "Flexible"

class RateType(enum.Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    FIXED = "fixed"
    NEGOTIABLE = "negotiable"

class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    PENDING = "PENDING"

class PlanAudience(enum.Enum):
    CLIENT = "CLIENT"
    PROFESSIONAL = "PROFESSIONAL"

class MPesaEnvironment(enum.Enum):
    SANDBOX = "SANDBOX"
    LIVE = "LIVE"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profiles = db.relationship('Profile', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_user_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_user_id', backref='recipient', lazy='dynamic')
    written_reviews = db.relationship('Review', foreign_keys='Review.reviewer_user_id', backref='reviewer', lazy='dynamic')
    received_reviews = db.relationship('Review', foreign_keys='Review.reviewed_user_id', backref='reviewed_user', lazy='dynamic')
    
    @property
    def is_active(self):
        return self.active
    
    @is_active.setter
    def is_active(self, value):
        self.active = value

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.Enum(ProfileType), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    location_country = db.Column(db.String(100), nullable=False, index=True)
    location_county = db.Column(db.String(100), nullable=False, index=True)
    location_sub_county = db.Column(db.String(100), nullable=True)
    location_town = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text, nullable=True)  # Comma-separated
    availability = db.Column(db.Enum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE)
    
    # Professional-specific fields
    category = db.Column(db.String(100), nullable=True, index=True)
    rate_type = db.Column(db.Enum(RateType), nullable=True)
    rate_value = db.Column(db.Numeric(10, 2), nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    team_name = db.Column(db.String(200), nullable=True)
    years_experience = db.Column(db.Integer, nullable=True)
    is_group = db.Column(db.Boolean, default=False)
    
    # Client-specific fields
    what_looking_for = db.Column(db.Text, nullable=True)
    urgency = db.Column(db.Enum(UrgencyLevel), nullable=True)
    
    # Visibility and status
    is_listed = db.Column(db.Boolean, default=True, nullable=False)
    is_new_user_flag = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_boosted = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewed_profile_id', backref='reviewed_profile', lazy='dynamic')
    views = db.relationship('ProfileView', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def total_views(self):
        return self.views.count()
    
    __table_args__ = (
        db.Index('idx_profile_type_category_location', 'type', 'category', 'location_country', 'location_county'),
    )

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    recipient_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    profile_context_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    is_admin_message = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        db.Index('idx_message_recipient_created', 'recipient_user_id', 'created_at'),
    )

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    reviewer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Star ratings (1-5)
    professionalism_rating = db.Column(db.Integer, nullable=False)
    skill_rating = db.Column(db.Integer, nullable=False)
    ease_of_work_rating = db.Column(db.Integer, nullable=False)
    overall_rating = db.Column(db.Float, nullable=False)  # Calculated average
    
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class UpdatePost(db.Model):
    __tablename__ = 'update_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    banner_image_url = db.Column(db.String(500), nullable=True)
    is_pinned = db.Column(db.Boolean, default=False)
    audience = db.Column(db.String(50), default='PUBLIC')  # PUBLIC, LOGGED_IN, PRO_ONLY, CLIENT_ONLY
    start_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Banner(db.Model):
    __tablename__ = 'banners'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    cta_text = db.Column(db.String(100), nullable=True)
    cta_href = db.Column(db.String(500), nullable=True)
    target_rule_json = db.Column(db.Text, nullable=True)  # JSON targeting rules
    start_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Plan(db.Model):
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    audience = db.Column(db.Enum(PlanAudience), nullable=False)
    price_kes = db.Column(db.Numeric(10, 2), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    features_json = db.Column(db.Text, nullable=False)  # JSON features and limits
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.PENDING)
    start_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_at = db.Column(db.DateTime, nullable=False)
    metadata_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='subscriptions')
    profile = db.relationship('Profile', backref='subscriptions')
    plan = db.relationship('Plan', backref='subscriptions')
    
    __table_args__ = (
        db.Index('idx_subscription_user_profile_status', 'user_id', 'profile_id', 'status'),
    )

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    mpesa_phone = db.Column(db.String(15), nullable=False)
    amount_kes = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    provider_ref = db.Column(db.String(200), nullable=True)
    account_reference = db.Column(db.String(200), nullable=False, unique=True)
    raw_callback_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', backref='payments')
    profile = db.relationship('Profile', backref='payments')
    plan = db.relationship('Plan', backref='payments')
    
    __table_args__ = (
        db.Index('idx_payment_status_created', 'status', 'created_at'),
    )

class AdminSettings(db.Model):
    __tablename__ = 'admin_settings'
    
    id = db.Column(db.Integer, primary_key=True, default=1)
    media_photos_enabled = db.Column(db.Boolean, default=True)
    media_videos_enabled = db.Column(db.Boolean, default=False)
    global_override_enabled = db.Column(db.Boolean, default=True)
    
    # M-Pesa settings
    mpesa_shortcode = db.Column(db.String(20), nullable=True)
    mpesa_passkey = db.Column(db.String(500), nullable=True)
    mpesa_company_name = db.Column(db.String(200), default='SkillBridge Africa')
    mpesa_env = db.Column(db.Enum(MPesaEnvironment), default=MPesaEnvironment.SANDBOX)
    callback_base_url = db.Column(db.String(500), nullable=True)
    
    # Admin password
    admin_password_hash = db.Column(db.String(256), nullable=True)
    
    # Email settings (fallback when env vars not available)
    email_server = db.Column(db.String(200), default='smtp.gmail.com')
    email_port = db.Column(db.Integer, default=587)
    email_username = db.Column(db.String(200), nullable=True)
    email_password = db.Column(db.String(200), nullable=True)
    
    # Logo settings
    logo_url = db.Column(db.String(500), nullable=True)
    
    # Customer support settings
    support_whatsapp = db.Column(db.String(20), nullable=True)
    support_phone = db.Column(db.String(20), nullable=True)
    support_email = db.Column(db.String(200), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MediaAsset(db.Model):
    __tablename__ = 'media_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # IMAGE, VIDEO
    url = db.Column(db.String(500), nullable=False)
    storage_provider = db.Column(db.String(50), default='LOCAL')  # LOCAL, S3, CLOUDINARY
    filename = db.Column(db.String(300), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    is_homepage_photo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class FeatureFlag(db.Model):
    __tablename__ = 'feature_flags'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value_json = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class HomepagePhoto(db.Model):
    __tablename__ = 'homepage_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(100), nullable=True)  # plumbing, electrical, etc.
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class ProfileView(db.Model):
    __tablename__ = 'profile_views'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    viewer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for anonymous views
    viewer_ip = db.Column(db.String(45), nullable=True)  # Store IP for anonymous tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.Index('idx_profile_views_profile_date', 'profile_id', 'created_at'),
    )

class AdminSession(db.Model):
    __tablename__ = 'admin_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import uuid
from datetime import datetime, timedelta
from app import db
from models import (AdminSettings, User, Profile, Message, AdminSession, 
                   HomepagePhoto, UpdatePost, Review, Payment, Plan, Subscription)
from services.email_service import EmailService

admin_bp = Blueprint('admin', __name__)

def is_admin_logged_in():
    """Check if admin is logged in"""
    admin_token = session.get('admin_token')
    if not admin_token:
        return False
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        if admin_session:
            db.session.delete(admin_session)
            db.session.commit()
        session.pop('admin_token', None)
        return False
    
    return True

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin_logged_in():
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        
        if not password:
            flash('Password is required.', 'error')
            return render_template('admin/login.html')
        
        try:
            settings = AdminSettings.query.first()
            
            # Check if custom admin password is set
            if settings and settings.admin_password_hash:
                if check_password_hash(settings.admin_password_hash, password):
                    # Create admin session
                    token = str(uuid.uuid4())
                    admin_session = AdminSession()
                    admin_session.session_token = token
                    admin_session.expires_at = datetime.utcnow() + timedelta(hours=2)  # Extended session
                    db.session.add(admin_session)
                    db.session.commit()
                    
                    session['admin_token'] = token
                    session.permanent = True
                    flash('Admin login successful!', 'success')
                    return redirect(url_for('admin.dashboard'))
                else:
                    flash('Invalid admin password.', 'error')
            else:
                # Use default password
                if password == 'SKILLBRIDGE':
                    # Create admin session
                    token = str(uuid.uuid4())
                    admin_session = AdminSession()
                    admin_session.session_token = token
                    admin_session.expires_at = datetime.utcnow() + timedelta(hours=2)
                    db.session.add(admin_session)
                    db.session.commit()
                    
                    session['admin_token'] = token
                    session.permanent = True
                    flash('Admin login successful! Please change the default password.', 'warning')
                    return redirect(url_for('admin.dashboard'))
                else:
                    flash('Invalid admin password. Default password is "SKILLBRIDGE".', 'error')
        except Exception as e:
            current_app.logger.error(f"Admin login error: {str(e)}")
            flash('Login system error. Please try again.', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@admin_required
def logout():
    admin_token = session.get('admin_token')
    if admin_token:
        admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
        if admin_session:
            db.session.delete(admin_session)
            db.session.commit()
        session.pop('admin_token', None)
    
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('public.index'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'verified_users': User.query.filter_by(email_verified=True).count(),
        'total_profiles': Profile.query.count(),
        'professional_profiles': Profile.query.filter_by(type='PROFESSIONAL').count(),
        'client_profiles': Profile.query.filter_by(type='CLIENT').count(),
        'total_messages': Message.query.count(),
        'total_reviews': Review.query.count(),
        'pending_payments': Payment.query.filter_by(status='PENDING').count(),
        'successful_payments': Payment.query.filter_by(status='SUCCESS').count()
    }
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_profiles = Profile.query.order_by(Profile.created_at.desc()).limit(5).all()
    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          stats=stats, recent_users=recent_users, 
                          recent_profiles=recent_profiles, recent_payments=recent_payments)

@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.email.contains(search))
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search)

@admin_bp.route('/user/<int:user_id>/toggle-active')
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "activated" if user.is_active else "deactivated"
    flash(f'User {user.email} has been {status}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/message', methods=['POST'])
@admin_required
def message_user(user_id):
    user = User.query.get_or_404(user_id)
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Message content is required.', 'error')
        return redirect(url_for('admin.users'))
    
    # Create admin message
    message = Message()
    message.sender_user_id = 1  # Admin ID
    message.recipient_user_id = user_id
    message.content = content
    message.is_admin_message = True
    
    db.session.add(message)
    db.session.commit()
    
    flash(f'Message sent to {user.email}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    settings = AdminSettings.query.first()
    if not settings:
        settings = AdminSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        # Media settings
        settings.media_photos_enabled = bool(request.form.get('media_photos_enabled'))
        settings.media_videos_enabled = bool(request.form.get('media_videos_enabled'))
        settings.global_override_enabled = bool(request.form.get('global_override_enabled'))
        
        # M-Pesa settings
        settings.mpesa_shortcode = request.form.get('mpesa_shortcode', '').strip()
        settings.mpesa_passkey = request.form.get('mpesa_passkey', '').strip()
        settings.mpesa_company_name = request.form.get('mpesa_company_name', 'SkillBridge Africa').strip()
        settings.mpesa_env = request.form.get('mpesa_env', 'SANDBOX')
        settings.callback_base_url = request.form.get('callback_base_url', '').strip()
        
        # Email settings
        settings.email_server = request.form.get('email_server', 'smtp.gmail.com').strip()
        settings.email_port = int(request.form.get('email_port', 587))
        settings.email_username = request.form.get('email_username', '').strip()
        settings.email_password = request.form.get('email_password', '').strip()
        
        # Customer support settings
        settings.support_whatsapp = request.form.get('support_whatsapp', '').strip()
        settings.support_phone = request.form.get('support_phone', '').strip()
        settings.support_email = request.form.get('support_email', '').strip()
        
        # Admin password
        new_password = request.form.get('admin_password', '').strip()
        if new_password:
            settings.admin_password_hash = generate_password_hash(new_password)
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filename = f"logo_{filename}"
                
                upload_dir = os.path.join(current_app.root_path, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                settings.logo_url = f"/uploads/{filename}"
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/homepage-photos', methods=['GET', 'POST'])
@admin_required
def homepage_photos():
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filename = f"homepage_{filename}"
                
                upload_dir = os.path.join(current_app.root_path, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                photo = HomepagePhoto()
                photo.url = f"/uploads/{filename}"
                photo.filename = filename
                photo.description = description
                photo.category = category
                photo.display_order = HomepagePhoto.query.count()
                
                db.session.add(photo)
                db.session.commit()
                
                flash('Photo uploaded successfully!', 'success')
        else:
            flash('Please select a photo to upload.', 'error')
        
        return redirect(url_for('admin.homepage_photos'))
    
    photos = HomepagePhoto.query.filter_by(is_active=True).order_by(HomepagePhoto.display_order).all()
    return render_template('admin/homepage_photos.html', photos=photos)

@admin_bp.route('/homepage-photos/<int:photo_id>/delete')
@admin_required
def delete_homepage_photo(photo_id):
    photo = HomepagePhoto.query.get_or_404(photo_id)
    
    # Delete file
    file_path = os.path.join(current_app.root_path, 'uploads', photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(photo)
    db.session.commit()
    
    flash('Photo deleted successfully.', 'success')
    return redirect(url_for('admin.homepage_photos'))

@admin_bp.route('/profile/<int:profile_id>/toggle-featured')
@admin_required
def toggle_profile_featured(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    profile.is_featured = not profile.is_featured
    db.session.commit()
    
    status = "featured" if profile.is_featured else "unfeatured"
    flash(f'Profile "{profile.title}" has been {status}.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/profile/<int:profile_id>/toggle-new')
@admin_required
def toggle_profile_new(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    profile.is_new_user_flag = not profile.is_new_user_flag
    db.session.commit()
    
    status = "marked as new" if profile.is_new_user_flag else "unmarked as new"
    flash(f'Profile "{profile.title}" has been {status}.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/reviews')
@admin_required
def reviews():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/reviews.html', reviews=reviews)

@admin_bp.route('/review/<int:review_id>/toggle-approval')
@admin_required
def toggle_review_approval(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = not review.is_approved
    db.session.commit()
    
    status = "approved" if review.is_approved else "disapproved"
    flash(f'Review has been {status}.', 'success')
    return redirect(url_for('admin.reviews'))

@admin_bp.route('/payments')
@admin_required
def payments():
    page = request.args.get('page', 1, type=int)
    payments = Payment.query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/payments.html', payments=payments)

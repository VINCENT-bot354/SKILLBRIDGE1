from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from models import Profile, ProfileType, AvailabilityStatus, UrgencyLevel, RateType, AdminSettings
from services.profanity_filter import ProfanityFilter

profiles_bp = Blueprint('profiles', __name__)

CATEGORIES = [
    'Plumbing', 'Electrical', 'Masonry', 'Carpentry', 'Painting', 'Roofing',
    'HVAC', 'Landscaping', 'Cleaning', 'Security', 'Catering', 'Photography',
    'Videography', 'Music/Entertainment', 'Education/Tutoring', 'Healthcare',
    'Legal Services', 'Accounting', 'IT/Technology', 'Marketing', 'Transportation',
    'Construction', 'Welding', 'Tailoring', 'Beauty/Salon', 'Mechanic', 'Other'
]

COUNTIES = [
    'Nairobi', 'Mombasa', 'Kwale', 'Kilifi', 'Tana River', 'Lamu', 'Taita Taveta',
    'Garissa', 'Wajir', 'Mandera', 'Marsabit', 'Isiolo', 'Meru', 'Tharaka Nithi',
    'Embu', 'Kitui', 'Machakos', 'Makueni', 'Nyandarua', 'Nyeri', 'Kirinyaga',
    'Murang\'a', 'Kiambu', 'Turkana', 'West Pokot', 'Samburu', 'Trans Nzoia',
    'Uasin Gishu', 'Elgeyo Marakwet', 'Nandi', 'Baringo', 'Laikipia', 'Nakuru',
    'Narok', 'Kajiado', 'Kericho', 'Bomet', 'Kakamega', 'Vihiga', 'Bungoma',
    'Busia', 'Siaya', 'Kisumu', 'Homa Bay', 'Migori', 'Kisii', 'Nyamira'
]

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profiles_bp.route('/my-profiles')
@login_required
def my_profiles():
    profiles = current_user.profiles.all()
    return render_template('dashboard/my_profiles.html', profiles=profiles)

@profiles_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_profile():
    # Check profile limit
    if current_user.profiles.count() >= 5:
        flash('You have reached the maximum limit of 5 profiles per account.', 'error')
        return redirect(url_for('profiles.my_profiles'))
    
    if request.method == 'POST':
        profile_type = request.form.get('type')
        title = request.form.get('title', '').strip()
        bio = request.form.get('bio', '').strip()
        location_country = request.form.get('location_country', '').strip()
        location_county = request.form.get('location_county', '').strip()
        location_town = request.form.get('location_town', '').strip()
        tags = request.form.get('tags', '').strip()
        
        # Validate required fields
        if not all([profile_type, title, bio, location_country, location_county, location_town]):
            flash('Please fill in all required fields.', 'error')
            return render_template('dashboard/create_profile.html', 
                                 categories=CATEGORIES, counties=COUNTIES)
        
        # Check for profanity
        if ProfanityFilter.contains_profanity(title) or ProfanityFilter.contains_profanity(bio):
            flash('Please use appropriate language in your profile.', 'error')
            return render_template('dashboard/create_profile.html', 
                                 categories=CATEGORIES, counties=COUNTIES)
        
        # Handle file upload
        avatar_url = None
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                # Check if photo uploads are enabled
                settings = AdminSettings.query.first()
                if not settings or not settings.media_photos_enabled:
                    flash('Photo uploads are currently disabled.', 'warning')
                else:
                    filename = secure_filename(file.filename)
                    filename = f"{current_user.id}_{filename}"
                    
                    # Ensure upload directory exists
                    upload_dir = os.path.join(current_app.root_path, 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    avatar_url = f"/uploads/{filename}"
        
        # Create profile
        profile = Profile()
        profile.user_id = current_user.id
        profile.type = ProfileType(profile_type)
        profile.title = title
        profile.bio = bio
        profile.location_country = location_country
        profile.location_county = location_county
        profile.location_town = location_town
        profile.tags = tags
        profile.avatar_url = avatar_url
        profile.availability = AvailabilityStatus.AVAILABLE
        profile.is_listed = True
        profile.is_new_user_flag = True  # Mark as new for first 30 days
        
        # Professional-specific fields
        if profile_type == 'PROFESSIONAL':
            category = request.form.get('category')
            rate_type = request.form.get('rate_type')
            rate_value = request.form.get('rate_value')
            years_experience = request.form.get('years_experience')
            certifications = request.form.get('certifications', '').strip()
            team_name = request.form.get('team_name', '').strip()
            is_group = bool(request.form.get('is_group'))
            
            if category:
                profile.category = category
            if rate_type:
                profile.rate_type = RateType(rate_type)
            if rate_value and rate_value.replace('.', '').isdigit():
                profile.rate_value = float(rate_value)
            if years_experience and years_experience.isdigit():
                profile.years_experience = int(years_experience)
            if certifications:
                profile.certifications = certifications
            if team_name:
                profile.team_name = team_name
            profile.is_group = is_group
        
        # Client-specific fields
        elif profile_type == 'CLIENT':
            what_looking_for = request.form.get('what_looking_for', '').strip()
            urgency = request.form.get('urgency')
            
            if what_looking_for:
                if ProfanityFilter.contains_profanity(what_looking_for):
                    flash('Please use appropriate language in your requirements.', 'error')
                    return render_template('dashboard/create_profile.html', 
                                         categories=CATEGORIES, counties=COUNTIES)
                profile.what_looking_for = what_looking_for
            if urgency:
                profile.urgency = UrgencyLevel(urgency)
        
        db.session.add(profile)
        db.session.commit()
        
        flash('Profile created successfully!', 'success')
        return redirect(url_for('profiles.my_profiles'))
    
    return render_template('dashboard/create_profile.html', 
                          categories=CATEGORIES, counties=COUNTIES)

@profiles_bp.route('/edit/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        bio = request.form.get('bio', '').strip()
        location_country = request.form.get('location_country', '').strip()
        location_county = request.form.get('location_county', '').strip()
        location_town = request.form.get('location_town', '').strip()
        tags = request.form.get('tags', '').strip()
        availability = request.form.get('availability')
        is_listed = bool(request.form.get('is_listed'))
        
        # Validate required fields
        if not all([title, bio, location_country, location_county, location_town]):
            flash('Please fill in all required fields.', 'error')
            return render_template('dashboard/edit_profile.html', 
                                 profile=profile, categories=CATEGORIES, counties=COUNTIES)
        
        # Check for profanity
        if ProfanityFilter.contains_profanity(title) or ProfanityFilter.contains_profanity(bio):
            flash('Please use appropriate language in your profile.', 'error')
            return render_template('dashboard/edit_profile.html', 
                                 profile=profile, categories=CATEGORIES, counties=COUNTIES)
        
        # Handle file upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                settings = AdminSettings.query.first()
                if settings and settings.media_photos_enabled:
                    filename = secure_filename(file.filename)
                    filename = f"{current_user.id}_{filename}"
                    
                    upload_dir = os.path.join(current_app.root_path, 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    profile.avatar_url = f"/uploads/{filename}"
        
        # Update basic fields
        profile.title = title
        profile.bio = bio
        profile.location_country = location_country
        profile.location_county = location_county
        profile.location_town = location_town
        profile.tags = tags
        profile.is_listed = is_listed
        
        if availability:
            profile.availability = AvailabilityStatus(availability)
        
        # Professional-specific fields
        if profile.type == ProfileType.PROFESSIONAL:
            category = request.form.get('category')
            rate_type = request.form.get('rate_type')
            rate_value = request.form.get('rate_value')
            years_experience = request.form.get('years_experience')
            certifications = request.form.get('certifications', '').strip()
            team_name = request.form.get('team_name', '').strip()
            is_group = bool(request.form.get('is_group'))
            
            if category:
                profile.category = category
            if rate_type:
                profile.rate_type = RateType(rate_type)
            if rate_value and rate_value.replace('.', '').isdigit():
                profile.rate_value = float(rate_value)
            else:
                profile.rate_value = None
            if years_experience and years_experience.isdigit():
                profile.years_experience = int(years_experience)
            else:
                profile.years_experience = None
            profile.certifications = certifications
            profile.team_name = team_name
            profile.is_group = is_group
        
        # Client-specific fields
        elif profile.type == ProfileType.CLIENT:
            what_looking_for = request.form.get('what_looking_for', '').strip()
            urgency = request.form.get('urgency')
            
            if what_looking_for:
                if ProfanityFilter.contains_profanity(what_looking_for):
                    flash('Please use appropriate language in your requirements.', 'error')
                    return render_template('dashboard/edit_profile.html', 
                                         profile=profile, categories=CATEGORIES, counties=COUNTIES)
                profile.what_looking_for = what_looking_for
            if urgency:
                profile.urgency = UrgencyLevel(urgency)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profiles.my_profiles'))
    
    return render_template('dashboard/edit_profile.html', 
                          profile=profile, categories=CATEGORIES, counties=COUNTIES)

@profiles_bp.route('/delete/<int:profile_id>')
@login_required
def delete_profile(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(profile)
    db.session.commit()
    
    flash('Profile deleted successfully.', 'success')
    return redirect(url_for('profiles.my_profiles'))

@profiles_bp.route('/view/<int:profile_id>')
def view_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    
    # Check if profile is listed (public)
    if not profile.is_listed and (not current_user.is_authenticated or current_user.id != profile.user_id):
        flash('This profile is not publicly available.', 'error')
        return redirect(url_for('public.browse'))
    
    return render_template('public/profile_detail.html', profile=profile)

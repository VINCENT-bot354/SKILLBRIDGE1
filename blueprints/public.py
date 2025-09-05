from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app import db
from models import Profile, ProfileType, User, HomepagePhoto, UpdatePost, AdminSettings, Review, Message
import os

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Homepage with hero banner and featured content"""
    # Get homepage photos
    homepage_photos = HomepagePhoto.query.filter_by(is_active=True).order_by(HomepagePhoto.display_order).limit(6).all()
    
    # Get featured new profiles
    featured_profiles = Profile.query.filter_by(
        is_listed=True,
        is_new_user_flag=True
    ).limit(8).all()
    
    # Get latest updates
    latest_updates = UpdatePost.query.filter_by(
        audience='PUBLIC'
    ).order_by(UpdatePost.created_at.desc()).limit(3).all()
    
    # Get admin settings for logo
    settings = AdminSettings.query.first()
    
    return render_template('index.html', 
                          homepage_photos=homepage_photos,
                          featured_profiles=featured_profiles,
                          latest_updates=latest_updates,
                          settings=settings)

@public_bp.route('/about')
def about():
    """About page with mission and how it works"""
    settings = AdminSettings.query.first()
    return render_template('about.html', settings=settings)

@public_bp.route('/browse')
def browse():
    """Browse profiles with search and filters"""
    # Get filter parameters
    profile_type = request.args.get('type', '')
    category = request.args.get('category', '')
    location_county = request.args.get('location', '')
    availability = request.args.get('availability', '')
    search_query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    # Build query
    query = Profile.query.filter_by(is_listed=True)
    
    if profile_type and profile_type in ['CLIENT', 'PROFESSIONAL']:
        query = query.filter_by(type=ProfileType(profile_type))
    
    if category:
        query = query.filter_by(category=category)
    
    if location_county:
        query = query.filter_by(location_county=location_county)
    
    if availability:
        query = query.filter_by(availability=availability)
    
    if search_query:
        search_filter = or_(
            Profile.title.contains(search_query),
            Profile.bio.contains(search_query),
            Profile.tags.contains(search_query)
        )
        query = query.filter(search_filter)
    
    # Order by featured, new, then created date
    query = query.order_by(
        Profile.is_featured.desc(),
        Profile.is_new_user_flag.desc(),
        Profile.created_at.desc()
    )
    
    # Paginate
    profiles = query.paginate(page=page, per_page=12, error_out=False)
    
    # Get filter options
    categories = db.session.query(Profile.category).filter(
        Profile.category.isnot(None),
        Profile.is_listed == True
    ).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    counties = db.session.query(Profile.location_county).filter(
        Profile.is_listed == True
    ).distinct().all()
    counties = [county[0] for county in counties if county[0]]
    
    settings = AdminSettings.query.first()
    
    return render_template('browse.html', 
                          profiles=profiles,
                          categories=categories,
                          counties=counties,
                          current_filters={
                              'type': profile_type,
                              'category': category,
                              'location': location_county,
                              'availability': availability,
                              'q': search_query
                          },
                          settings=settings)

@public_bp.route('/profile/<int:profile_id>')
def profile_detail(profile_id):
    """View profile details"""
    profile = Profile.query.get_or_404(profile_id)
    
    # Check if profile is listed (public)
    if not profile.is_listed:
        flash('This profile is not publicly available.', 'error')
        return redirect(url_for('public.browse'))
    
    # Get reviews for this profile
    reviews = Review.query.filter_by(
        reviewed_profile_id=profile_id,
        is_approved=True
    ).order_by(Review.created_at.desc()).limit(5).all()
    
    # Calculate average ratings
    if reviews:
        avg_professionalism = sum(r.professionalism_rating for r in reviews) / len(reviews)
        avg_skill = sum(r.skill_rating for r in reviews) / len(reviews)
        avg_ease = sum(r.ease_of_work_rating for r in reviews) / len(reviews)
        avg_overall = sum(r.overall_rating for r in reviews) / len(reviews)
        total_reviews = Review.query.filter_by(reviewed_profile_id=profile_id, is_approved=True).count()
    else:
        avg_professionalism = avg_skill = avg_ease = avg_overall = 0
        total_reviews = 0
    
    averages = {
        'professionalism': round(avg_professionalism, 1),
        'skill': round(avg_skill, 1),
        'ease_of_work': round(avg_ease, 1),
        'overall': round(avg_overall, 1),
        'total_reviews': total_reviews
    }
    
    settings = AdminSettings.query.first()
    
    return render_template('public/profile_detail.html', 
                          profile=profile, 
                          reviews=reviews,
                          averages=averages,
                          settings=settings)

@public_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user's profiles
    user_profiles = current_user.profiles.all()
    
    # Get recent messages
    recent_messages = db.session.query(Message).filter(
        or_(
            Message.sender_user_id == current_user.id,
            Message.recipient_user_id == current_user.id
        )
    ).order_by(Message.created_at.desc()).limit(5).all()
    
    # Get unread message count
    unread_count = Message.query.filter_by(
        recipient_user_id=current_user.id,
        is_read=False
    ).count()
    
    # Get recent updates for logged-in users
    recent_updates = UpdatePost.query.filter(
        UpdatePost.audience.in_(['PUBLIC', 'LOGGED_IN'])
    ).order_by(UpdatePost.created_at.desc()).limit(3).all()
    
    settings = AdminSettings.query.first()
    
    return render_template('dashboard/dashboard.html',
                          user_profiles=user_profiles,
                          recent_messages=recent_messages,
                          unread_count=unread_count,
                          recent_updates=recent_updates,
                          settings=settings)

@public_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_dir = os.path.join(current_app.root_path, 'uploads')
    return send_from_directory(upload_dir, filename)


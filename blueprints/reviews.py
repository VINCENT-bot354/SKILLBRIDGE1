from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import Review, User, Profile
from services.profanity_filter import ProfanityFilter

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/write/<int:user_id>/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def write_review(user_id, profile_id):
    # Validate user and profile exist
    user = User.query.get_or_404(user_id)
    profile = Profile.query.get_or_404(profile_id)
    
    # Don't allow self-reviews
    if user.id == current_user.id:
        flash('You cannot review yourself.', 'error')
        return redirect(url_for('profiles.view_profile', profile_id=profile_id))
    
    # Check if user already reviewed this profile
    existing_review = Review.query.filter_by(
        reviewer_user_id=current_user.id,
        reviewed_user_id=user_id,
        reviewed_profile_id=profile_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this user.', 'error')
        return redirect(url_for('profiles.view_profile', profile_id=profile_id))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        professionalism_rating = request.form.get('professionalism_rating')
        skill_rating = request.form.get('skill_rating')
        ease_of_work_rating = request.form.get('ease_of_work_rating')
        
        # Validation
        if not content:
            flash('Please write a review.', 'error')
            return render_template('reviews/write_review.html', user=user, profile=profile)
        
        if not all([professionalism_rating, skill_rating, ease_of_work_rating]):
            flash('Please provide all ratings.', 'error')
            return render_template('reviews/write_review.html', user=user, profile=profile)
        
        # Check for profanity
        if ProfanityFilter.contains_profanity(content):
            profane_words = ProfanityFilter.get_profane_words(content)
            flash(f'Please remove inappropriate language: {", ".join(profane_words)}', 'error')
            return render_template('reviews/write_review.html', user=user, profile=profile)
        
        # Validate ratings (1-5)
        try:
            prof_rating = int(professionalism_rating)
            skill_rating = int(skill_rating)
            ease_rating = int(ease_of_work_rating)
            
            if not all(1 <= rating <= 5 for rating in [prof_rating, skill_rating, ease_rating]):
                flash('Ratings must be between 1 and 5 stars.', 'error')
                return render_template('reviews/write_review.html', user=user, profile=profile)
            
        except ValueError:
            flash('Invalid rating values.', 'error')
            return render_template('reviews/write_review.html', user=user, profile=profile)
        
        # Calculate overall rating
        overall_rating = (prof_rating + skill_rating + ease_rating) / 3.0
        
        # Create review
        review = Review(
            reviewer_user_id=current_user.id,
            reviewed_user_id=user_id,
            reviewed_profile_id=profile_id,
            content=content,
            professionalism_rating=prof_rating,
            skill_rating=skill_rating,
            ease_of_work_rating=ease_rating,
            overall_rating=overall_rating,
            is_approved=True  # Auto-approve for now, admin can moderate later
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('profiles.view_profile', profile_id=profile_id))
    
    return render_template('reviews/write_review.html', user=user, profile=profile)

@reviews_bp.route('/profile/<int:profile_id>')
def profile_reviews(profile_id):
    """View all reviews for a profile"""
    profile = Profile.query.get_or_404(profile_id)
    
    reviews = Review.query.filter_by(
        reviewed_profile_id=profile_id,
        is_approved=True
    ).order_by(Review.created_at.desc()).all()
    
    # Calculate average ratings
    if reviews:
        avg_professionalism = sum(r.professionalism_rating for r in reviews) / len(reviews)
        avg_skill = sum(r.skill_rating for r in reviews) / len(reviews)
        avg_ease = sum(r.ease_of_work_rating for r in reviews) / len(reviews)
        avg_overall = sum(r.overall_rating for r in reviews) / len(reviews)
    else:
        avg_professionalism = avg_skill = avg_ease = avg_overall = 0
    
    averages = {
        'professionalism': round(avg_professionalism, 1),
        'skill': round(avg_skill, 1),
        'ease_of_work': round(avg_ease, 1),
        'overall': round(avg_overall, 1)
    }
    
    return render_template('reviews/profile_reviews.html', 
                          profile=profile, reviews=reviews, averages=averages)

@reviews_bp.route('/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    """Edit a review (only by the reviewer)"""
    review = Review.query.get_or_404(review_id)
    
    # Only reviewer can edit
    if review.reviewer_user_id != current_user.id:
        flash('You can only edit your own reviews.', 'error')
        return redirect(url_for('profiles.view_profile', profile_id=review.reviewed_profile_id))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        professionalism_rating = request.form.get('professionalism_rating')
        skill_rating = request.form.get('skill_rating')
        ease_of_work_rating = request.form.get('ease_of_work_rating')
        
        # Validation
        if not content:
            flash('Please write a review.', 'error')
            return render_template('reviews/edit_review.html', review=review)
        
        if not all([professionalism_rating, skill_rating, ease_of_work_rating]):
            flash('Please provide all ratings.', 'error')
            return render_template('reviews/edit_review.html', review=review)
        
        # Check for profanity
        if ProfanityFilter.contains_profanity(content):
            profane_words = ProfanityFilter.get_profane_words(content)
            flash(f'Please remove inappropriate language: {", ".join(profane_words)}', 'error')
            return render_template('reviews/edit_review.html', review=review)
        
        # Validate ratings
        try:
            prof_rating = int(professionalism_rating)
            skill_rating = int(skill_rating)
            ease_rating = int(ease_of_work_rating)
            
            if not all(1 <= rating <= 5 for rating in [prof_rating, skill_rating, ease_rating]):
                flash('Ratings must be between 1 and 5 stars.', 'error')
                return render_template('reviews/edit_review.html', review=review)
            
        except ValueError:
            flash('Invalid rating values.', 'error')
            return render_template('reviews/edit_review.html', review=review)
        
        # Update review
        review.content = content
        review.professionalism_rating = prof_rating
        review.skill_rating = skill_rating
        review.ease_of_work_rating = ease_rating
        review.overall_rating = (prof_rating + skill_rating + ease_rating) / 3.0
        
        db.session.commit()
        
        flash('Review updated successfully!', 'success')
        return redirect(url_for('profiles.view_profile', profile_id=review.reviewed_profile_id))
    
    return render_template('reviews/edit_review.html', review=review)

@reviews_bp.route('/delete/<int:review_id>')
@login_required
def delete_review(review_id):
    """Delete a review (only by the reviewer)"""
    review = Review.query.get_or_404(review_id)
    
    # Only reviewer can delete
    if review.reviewer_user_id != current_user.id:
        flash('You can only delete your own reviews.', 'error')
        return redirect(url_for('profiles.view_profile', profile_id=review.reviewed_profile_id))
    
    profile_id = review.reviewed_profile_id
    db.session.delete(review)
    db.session.commit()
    
    flash('Review deleted successfully.', 'success')
    return redirect(url_for('profiles.view_profile', profile_id=profile_id))

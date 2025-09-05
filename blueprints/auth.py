from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User, UserRole
from services.email_service import EmailService
from services.profanity_filter import ProfanityFilter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('auth/signup.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/signup.html')

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return render_template('auth/signup.html')

        # Create user
        new_user = User()
        new_user.email = email
        new_user.password_hash = generate_password_hash(password)
        new_user.role = UserRole.USER
        new_user.is_active = True
        new_user.email_verified = False

        db.session.add(new_user)
        db.session.commit()

        # Send OTP
        try:
            otp = EmailService.generate_otp()
            EmailService.save_otp(new_user.id, otp)

            # Configure email from admin settings if needed
            EmailService.configure_mail_from_settings()

            if EmailService.send_otp(email, otp):
                session['signup_user_id'] = new_user.id
                flash('Account created! Please check your email for the verification code.', 'success')
                return redirect(url_for('auth.verify_otp'))
            else:
                db.session.delete(new_user)
                db.session.commit()
                flash('Verification email could not be sent. Please check email settings in admin panel.', 'error')
        except Exception as e:
            current_app.logger.error(f"Signup email error: {str(e)}")
            db.session.delete(new_user)
            db.session.commit()
            flash('Account creation failed. Please try again or contact support.', 'error')


    return render_template('auth/signup.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    pending_user_id = session.get('signup_user_id') # Changed from 'pending_user_id' to 'signup_user_id'
    if not pending_user_id:
        flash('No pending verification found.', 'error')
        return redirect(url_for('auth.signup'))

    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()

        if not otp:
            flash('Please enter the verification code.', 'error')
            return render_template('auth/verify_otp.html')

        if EmailService.verify_otp(pending_user_id, otp):
            user = User.query.get(pending_user_id)
            if user:
                login_user(user)
                session.pop('signup_user_id', None) # Changed from 'pending_user_id' to 'signup_user_id'

                # Send welcome email
                EmailService.send_welcome_email(user.email, user.email.split('@')[0])

                flash('Account verified successfully! Welcome to SkillBridge Africa.', 'success')
                return redirect(url_for('profiles.my_profiles'))
            else:
                flash('User not found.', 'error')
        else:
            flash('Invalid or expired verification code.', 'error')

    return render_template('auth/verify_otp.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if not user.email_verified:
                flash('Please verify your email before logging in.', 'error')
                return render_template('auth/login.html')

            if not user.is_active:
                flash('Your account has been deactivated.', 'error')
                return render_template('auth/login.html')

            login_user(user)

            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Check if user has profiles
            if user.profiles.count() == 0:
                flash('Welcome! Please create your first profile to get started.', 'info')
                return redirect(url_for('profiles.create_profile'))

            return redirect(url_for('public.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('public.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        superpassword = request.form.get('superpassword', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([email, superpassword, new_password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('auth/forgot_password.html')

        # Check superpassword
        import os
        if superpassword != os.environ.get('SUPERPASSWORD', 'SKILLBRIDGE'):
            flash('Invalid super password.', 'error')
            return render_template('auth/forgot_password.html')

        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/forgot_password.html')

        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/forgot_password.html')

        # Update user password
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Password reset successfully. You can now log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('No account found with this email address.', 'error')

    return render_template('auth/forgot_password.html')

@auth_bp.route('/resend-otp')
def resend_otp():
    pending_user_id = session.get('signup_user_id') # Changed from 'pending_user_id' to 'signup_user_id'
    if not pending_user_id:
        flash('No pending verification found.', 'error')
        return redirect(url_for('auth.signup'))

    user = User.query.get(pending_user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.signup'))

    # Generate and send new OTP
    otp = EmailService.generate_otp()
    if EmailService.save_otp(user.id, otp) and EmailService.send_otp(user.email, otp):
        flash('Verification code sent again. Please check your email.', 'info')
    else:
        flash('Failed to send verification email. Please try again.', 'error')

    return redirect(url_for('auth.verify_otp'))
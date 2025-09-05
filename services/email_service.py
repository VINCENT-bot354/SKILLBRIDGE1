import os
import random
import string
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message, Mail
from app import mail, db
from models import User, AdminSettings

class EmailService:
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def send_otp(email, otp):
        """Send OTP to user's email"""
        try:
            # Ensure mail is configured
            if not EmailService.configure_mail_from_settings():
                current_app.logger.error("Email configuration failed")
                return False
                
            subject = "SkillBridge Africa - Email Verification Code"
            body = f"""
            Welcome to SkillBridge Africa!
            
            Your email verification code is: {otp}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            SkillBridge Africa Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[email],
                body=body
            )
            
            mail.send(msg)
            current_app.logger.info(f"OTP email sent successfully to {email}")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send OTP email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(email, name):
        """Send welcome email after successful verification"""
        try:
            subject = "Welcome to SkillBridge Africa!"
            body = f"""
            Hello {name},
            
            Welcome to SkillBridge Africa! Your account has been successfully created.
            
            You can now:
            - Create professional or client profiles
            - Connect with service providers and clients
            - Access our messaging system
            - Explore opportunities across Africa
            
            Get started by creating your first profile.
            
            Best regards,
            SkillBridge Africa Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[email],
                body=body
            )
            
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send welcome email: {e}")
            return False
    
    @staticmethod
    def save_otp(user_id, otp):
        """Save OTP to user record with expiry"""
        user = User.query.get(user_id)
        if user:
            user.otp_code = otp
            user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def verify_otp(user_id, otp):
        """Verify OTP code"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        if (user.otp_code == otp and 
            user.otp_expires_at and 
            user.otp_expires_at > datetime.utcnow()):
            
            # Clear OTP and mark email as verified
            user.otp_code = None
            user.otp_expires_at = None
            user.email_verified = True
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def configure_mail_from_settings():
        """Configure mail settings from admin settings"""
        try:
            settings = AdminSettings.query.first()
            if settings and settings.email_username and settings.email_password:
                current_app.config['MAIL_SERVER'] = settings.email_server or 'smtp.gmail.com'
                current_app.config['MAIL_PORT'] = settings.email_port or 587
                current_app.config['MAIL_USE_TLS'] = True
                current_app.config['MAIL_USE_SSL'] = False
                current_app.config['MAIL_USERNAME'] = settings.email_username
                current_app.config['MAIL_PASSWORD'] = settings.email_password
                current_app.config['MAIL_DEFAULT_SENDER'] = settings.email_username
                
                # Reinitialize mail with new settings
                mail.init_app(current_app)
                return True
            elif current_app.config.get('MAIL_USERNAME'):
                return True  # Environment variables are already configured
            else:
                current_app.logger.error("No email configuration found in admin settings or environment")
                return False
        except Exception as e:
            current_app.logger.error(f"Email configuration error: {str(e)}")
            return False
    
    @staticmethod
    def send_notification(email, subject, message):
        """Send general notification email"""
        try:
            msg = Message(
                subject=f"SkillBridge Africa - {subject}",
                recipients=[email],
                body=message
            )
            
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send notification email: {e}")
            return False

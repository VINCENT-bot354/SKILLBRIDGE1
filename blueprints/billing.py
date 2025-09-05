from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
import uuid
from app import db
from models import Plan, Payment, Subscription, Profile, PaymentStatus
from services.mpesa_service import MPesaService

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/')
@login_required
def plans():
    # Get current profile context if provided
    profile_id = request.args.get('profile_id')
    profile = None
    if profile_id:
        profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    
    # Get available plans based on profile type or show all
    if profile:
        plans = Plan.query.filter_by(
            audience=profile.type.value,
            is_active=True
        ).all()
    else:
        plans = Plan.query.filter_by(is_active=True).all()
    
    # Get user's profiles for plan selection
    user_profiles = current_user.profiles.all()
    
    # Get current subscriptions
    subscriptions = Subscription.query.filter_by(
        user_id=current_user.id,
        status='ACTIVE'
    ).all()
    
    return render_template('dashboard/billing.html', 
                          plans=plans, profiles=user_profiles, 
                          current_profile=profile, subscriptions=subscriptions)

@billing_bp.route('/start-payment', methods=['POST'])
@login_required
def start_payment():
    profile_id = request.form.get('profile_id')
    plan_id = request.form.get('plan_id')
    mpesa_phone = request.form.get('mpesa_phone', '').strip()
    
    # Validation
    if not all([profile_id, plan_id, mpesa_phone]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('billing.plans'))
    
    # Validate profile belongs to user
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        flash('Invalid profile selected.', 'error')
        return redirect(url_for('billing.plans'))
    
    # Validate plan
    plan = Plan.query.get(plan_id)
    if not plan or not plan.is_active:
        flash('Invalid plan selected.', 'error')
        return redirect(url_for('billing.plans'))
    
    # Validate phone number format
    if not mpesa_phone.isdigit() or len(mpesa_phone) not in [9, 10, 12]:
        flash('Please enter a valid M-Pesa phone number.', 'error')
        return redirect(url_for('billing.plans'))
    
    # Generate unique account reference
    timestamp = int(datetime.utcnow().timestamp())
    account_reference = f"u{current_user.id}-p{profile_id}-pl{plan_id}-{timestamp}"
    
    # Create payment record
    payment = Payment()
    payment.user_id = current_user.id
    payment.profile_id = profile_id
    payment.plan_id = plan_id
    payment.mpesa_phone = mpesa_phone
    payment.amount_kes = plan.price_kes
    payment.status = PaymentStatus.PENDING
    payment.account_reference = account_reference
    
    db.session.add(payment)
    db.session.commit()
    
    # Initiate M-Pesa STK Push
    transaction_desc = f"SkillBridge {plan.name} Plan"
    result = MPesaService.initiate_stk_push(
        phone_number=mpesa_phone,
        amount=plan.price_kes,
        account_reference=account_reference,
        transaction_desc=transaction_desc
    )
    
    if result.get('success'):
        # Update payment with checkout request ID
        payment.provider_ref = result.get('checkout_request_id')
        db.session.commit()
        
        flash('Payment request sent to your phone. Please enter your M-Pesa PIN to complete the payment.', 'info')
        return redirect(url_for('billing.payment_status', payment_id=payment.id))
    else:
        # Payment initiation failed
        payment.status = PaymentStatus.FAILED
        db.session.commit()
        
        error_msg = result.get('error', 'Payment initiation failed')
        flash(f'Payment failed: {error_msg}', 'error')
        return redirect(url_for('billing.plans'))

@billing_bp.route('/payment-status/<int:payment_id>')
@login_required
def payment_status(payment_id):
    payment = Payment.query.filter_by(
        id=payment_id, 
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('billing/payment_status.html', payment=payment)

@billing_bp.route('/callback/mpesa', methods=['POST'])
def mpesa_callback():
    """M-Pesa callback endpoint"""
    try:
        callback_data = request.get_json()
        
        if not callback_data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
        
        # Process the callback
        success = MPesaService.process_callback(callback_data)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Callback processed'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Callback processing failed'}), 500
            
    except Exception as e:
        current_app.logger.error(f"M-Pesa callback error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@billing_bp.route('/payment-history')
@login_required
def payment_history():
    """View user's payment history"""
    page = request.args.get('page', 1, type=int)
    payments = Payment.query.filter_by(
        user_id=current_user.id
    ).order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('billing/payment_history.html', payments=payments)

@billing_bp.route('/subscriptions')
@login_required
def subscriptions():
    """View user's active subscriptions"""
    user_subscriptions = Subscription.query.filter_by(
        user_id=current_user.id
    ).order_by(Subscription.created_at.desc()).all()
    
    return render_template('billing/subscriptions.html', subscriptions=user_subscriptions)

@billing_bp.route('/check-payment-status/<int:payment_id>')
@login_required
def check_payment_status(payment_id):
    """AJAX endpoint to check payment status"""
    payment = Payment.query.filter_by(
        id=payment_id,
        user_id=current_user.id
    ).first()
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    return jsonify({
        'status': payment.status.value,
        'provider_ref': payment.provider_ref,
        'amount': float(payment.amount_kes)
    })

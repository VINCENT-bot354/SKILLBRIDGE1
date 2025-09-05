import os
import json
import base64
import requests
from datetime import datetime, timedelta
from flask import current_app
from app import db
from models import AdminSettings, Payment, Subscription, Plan, PaymentStatus, SubscriptionStatus

class MPesaService:
    @staticmethod
    def get_access_token():
        """Get M-Pesa access token"""
        settings = AdminSettings.query.first()
        if not settings or not settings.mpesa_shortcode:
            return None
        
        consumer_key = os.environ.get('MPESA_CONSUMER_KEY')
        consumer_secret = os.environ.get('MPESA_CONSUMER_SECRET')
        
        if not consumer_key or not consumer_secret:
            current_app.logger.error("M-Pesa consumer key/secret not configured")
            return None
        
        # Encode credentials
        api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        if settings.mpesa_env.value == "LIVE":
            api_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {credentials}"
        }
        
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            current_app.logger.error(f"Failed to get M-Pesa access token: {e}")
            return None
    
    @staticmethod
    def generate_password():
        """Generate M-Pesa API password"""
        settings = AdminSettings.query.first()
        if not settings or not settings.mpesa_shortcode or not settings.mpesa_passkey:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data_to_encode = f"{settings.mpesa_shortcode}{settings.mpesa_passkey}{timestamp}"
        encoded_string = base64.b64encode(data_to_encode.encode()).decode()
        
        return encoded_string, timestamp
    
    @staticmethod
    def initiate_stk_push(phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push payment"""
        settings = AdminSettings.query.first()
        if not settings:
            return {"success": False, "error": "Admin settings not configured"}
        
        access_token = MPesaService.get_access_token()
        if not access_token:
            return {"success": False, "error": "Failed to get access token"}
        
        password_data = MPesaService.generate_password()
        if not password_data:
            return {"success": False, "error": "Failed to generate password"}
        
        password, timestamp = password_data
        
        # API URL
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        if settings.mpesa_env.value == "LIVE":
            api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        
        # Format phone number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]
        
        # Callback URL
        callback_url = settings.callback_base_url or "https://yourapp.com"
        callback_url = f"{callback_url}/billing/callback/mpesa"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": settings.mpesa_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": settings.mpesa_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "checkout_request_id": result.get("CheckoutRequestID"),
                "merchant_request_id": result.get("MerchantRequestID"),
                "response_code": result.get("ResponseCode"),
                "response_description": result.get("ResponseDescription")
            }
        except Exception as e:
            current_app.logger.error(f"STK Push failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def process_callback(callback_data):
        """Process M-Pesa callback"""
        try:
            # Extract callback data
            stk_callback = callback_data.get("Body", {}).get("stkCallback", {})
            result_code = stk_callback.get("ResultCode")
            result_desc = stk_callback.get("ResultDesc")
            checkout_request_id = stk_callback.get("CheckoutRequestID")
            
            # Find payment by checkout request ID (stored in provider_ref during STK push)
            payment = Payment.query.filter_by(provider_ref=checkout_request_id).first()
            if not payment:
                current_app.logger.error(f"Payment not found for checkout request ID: {checkout_request_id}")
                return False
            
            # Update payment with callback data
            payment.raw_callback_json = json.dumps(callback_data)
            
            if result_code == 0:  # Success
                # Extract transaction details
                callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
                transaction_id = None
                phone_number = None
                amount = None
                
                for item in callback_metadata:
                    name = item.get("Name")
                    if name == "MpesaReceiptNumber":
                        transaction_id = item.get("Value")
                    elif name == "PhoneNumber":
                        phone_number = item.get("Value")
                    elif name == "Amount":
                        amount = item.get("Value")
                
                # Update payment status
                payment.status = PaymentStatus.SUCCESS
                payment.provider_ref = transaction_id
                
                # Create or extend subscription
                plan = Plan.query.get(payment.plan_id)
                if plan:
                    # Check if user already has an active subscription for this profile
                    existing_sub = Subscription.query.filter_by(
                        user_id=payment.user_id,
                        profile_id=payment.profile_id,
                        status=SubscriptionStatus.ACTIVE
                    ).first()
                    
                    if existing_sub:
                        # Extend existing subscription
                        existing_sub.end_at = existing_sub.end_at + timedelta(days=plan.duration_days)
                    else:
                        # Create new subscription
                        subscription = Subscription()
                        subscription.user_id = payment.user_id
                        subscription.profile_id = payment.profile_id
                        subscription.plan_id = payment.plan_id
                        subscription.status = SubscriptionStatus.ACTIVE
                        subscription.start_at = datetime.utcnow()
                        subscription.end_at = datetime.utcnow() + timedelta(days=plan.duration_days)
                        db.session.add(subscription)
                
                # Send success message to user
                from models import Message, User
                user = User.query.get(payment.user_id)
                if user:
                    success_message = Message()
                    success_message.sender_user_id = 1  # System/Admin
                    success_message.recipient_user_id = payment.user_id
                    success_message.content = f"Payment successful! Your {plan.name} subscription is now active. Transaction ID: {transaction_id}"
                    success_message.is_admin_message = True
                    db.session.add(success_message)
            
            else:  # Failed
                payment.status = PaymentStatus.FAILED
                
                # Send failure message to user
                from models import Message, User
                user = User.query.get(payment.user_id)
                if user:
                    failure_message = Message()
                    failure_message.sender_user_id = 1  # System/Admin
                    failure_message.recipient_user_id = payment.user_id
                    failure_message.content = f"Payment failed: {result_desc}. Please try again or contact support."
                    failure_message.is_admin_message = True
                    db.session.add(failure_message)
            
            db.session.commit()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to process M-Pesa callback: {e}")
            return False

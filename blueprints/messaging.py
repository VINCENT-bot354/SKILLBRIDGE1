from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import Message, User, Profile
from services.profanity_filter import ProfanityFilter

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/')
@login_required
def inbox():
    # Get conversations (unique users with latest message)
    conversations = db.session.query(
        Message.sender_user_id,
        Message.recipient_user_id,
        Message.content,
        Message.created_at,
        Message.is_read,
        User.email
    ).select_from(Message).join(
        User, 
        db.or_(
            db.and_(Message.sender_user_id == User.id, Message.recipient_user_id == current_user.id),
            db.and_(Message.recipient_user_id == User.id, Message.sender_user_id == current_user.id)
        )
    ).filter(
        db.or_(
            Message.sender_user_id == current_user.id,
            Message.recipient_user_id == current_user.id
        )
    ).order_by(Message.created_at.desc()).all()
    
    # Group by conversation partner
    conversation_dict = {}
    for conv in conversations:
        partner_id = conv.sender_user_id if conv.sender_user_id != current_user.id else conv.recipient_user_id
        if partner_id not in conversation_dict:
            conversation_dict[partner_id] = {
                'user_id': partner_id,
                'email': conv.email,
                'last_message': conv.content,
                'last_message_time': conv.created_at,
                'is_read': conv.is_read,
                'unread_count': 0
            }
    
    # Count unread messages for each conversation
    for partner_id in conversation_dict:
        unread_count = Message.query.filter_by(
            sender_user_id=partner_id,
            recipient_user_id=current_user.id,
            is_read=False
        ).count()
        conversation_dict[partner_id]['unread_count'] = unread_count
    
    conversations = list(conversation_dict.values())
    conversations.sort(key=lambda x: x['last_message_time'], reverse=True)
    
    return render_template('dashboard/messages.html', conversations=conversations)

@messaging_bp.route('/conversation/<int:user_id>')
@login_required
def conversation(user_id):
    user = User.query.get_or_404(user_id)
    
    # Get all messages between current user and this user
    messages = Message.query.filter(
        db.or_(
            db.and_(Message.sender_user_id == current_user.id, Message.recipient_user_id == user_id),
            db.and_(Message.sender_user_id == user_id, Message.recipient_user_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    Message.query.filter_by(
        sender_user_id=user_id,
        recipient_user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    return render_template('dashboard/conversation.html', user=user, messages=messages)

@messaging_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    recipient_id = request.form.get('recipient_id')
    content = request.form.get('content', '').strip()
    profile_context_id = request.form.get('profile_context_id')
    
    if not recipient_id or not content:
        flash('Recipient and message content are required.', 'error')
        return redirect(url_for('messaging.inbox'))
    
    # Check for profanity
    if ProfanityFilter.contains_profanity(content):
        profane_words = ProfanityFilter.get_profane_words(content)
        flash(f'Please remove inappropriate language: {", ".join(profane_words)}', 'error')
        return redirect(url_for('messaging.conversation', user_id=recipient_id))
    
    # Validate recipient exists
    recipient = User.query.get(recipient_id)
    if not recipient:
        flash('Recipient not found.', 'error')
        return redirect(url_for('messaging.inbox'))
    
    # Don't allow messaging self
    if int(recipient_id) == current_user.id:
        flash('You cannot send messages to yourself.', 'error')
        return redirect(url_for('messaging.inbox'))
    
    # Create message
    message = Message()
    message.sender_user_id = current_user.id
    message.recipient_user_id = recipient_id
    message.content = content
    message.profile_context_id = profile_context_id if profile_context_id else None
    message.is_read = False
    
    db.session.add(message)
    db.session.commit()
    
    flash('Message sent successfully!', 'success')
    return redirect(url_for('messaging.conversation', user_id=recipient_id))

@messaging_bp.route('/start/<int:user_id>')
@login_required
def start_conversation(user_id):
    """Start a conversation with a user (from profile view)"""
    user = User.query.get_or_404(user_id)
    
    # Check if conversation already exists
    existing_message = Message.query.filter(
        db.or_(
            db.and_(Message.sender_user_id == current_user.id, Message.recipient_user_id == user_id),
            db.and_(Message.sender_user_id == user_id, Message.recipient_user_id == current_user.id)
        )
    ).first()
    
    if existing_message:
        return redirect(url_for('messaging.conversation', user_id=user_id))
    else:
        # Create new conversation view
        return render_template('dashboard/conversation.html', user=user, messages=[])

@messaging_bp.route('/check-profanity', methods=['POST'])
@login_required
def check_profanity():
    """AJAX endpoint to check message for profanity in real-time"""
    content = request.json.get('content', '')
    
    if ProfanityFilter.contains_profanity(content):
        profane_words = ProfanityFilter.get_profane_words(content)
        return jsonify({
            'has_profanity': True,
            'words': profane_words,
            'message': 'Inappropriate language detected. Please use polite language.'
        })
    
    return jsonify({'has_profanity': False})

@messaging_bp.route('/delete/<int:message_id>')
@login_required
def delete_message(message_id):
    """Delete a message (only sender can delete)"""
    message = Message.query.get_or_404(message_id)
    
    if message.sender_user_id != current_user.id:
        flash('You can only delete your own messages.', 'error')
        return redirect(url_for('messaging.inbox'))
    
    recipient_id = message.recipient_user_id
    db.session.delete(message)
    db.session.commit()
    
    flash('Message deleted.', 'success')
    return redirect(url_for('messaging.conversation', user_id=recipient_id))

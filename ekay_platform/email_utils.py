from flask import render_template, current_app, url_for
from flask_mail import Message
from .extensions import mail
from .models import User, Property
from datetime import datetime, timedelta

def send_email(subject, sender, recipients, text_body, html_body, **kwargs):
    """Fonction générique pour envoyer des emails"""
    msg = Message(
        subject=subject,
        sender=sender,
        recipients=recipients,
        **kwargs
    )
    msg.body = text_body
    msg.html = html_body
    
    try:
        mail.send(msg)
        current_app.logger.info(f"Email envoyé à {', '.join(recipients)}: {subject}")
        return True
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi d'email à {', '.join(recipients)}: {str(e)}")
        return False

def send_verification_email(user):
    """Envoie un email de vérification d'adresse email"""
    # Générer un token de vérification valide 24h
    token = user.generate_auth_token('email_verification', expires_in=86400)
    
    # Construire l'URL de vérification
    verify_url = url_for('auth.verify_email', token=token.token, _external=True)
    
    # Envoyer l'email
    return send_email(
        subject="Vérifiez votre adresse email - E-KAY",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/verify_email.txt', user=user, verify_url=verify_url),
        html_body=render_template('email/verify_email.html', user=user, verify_url=verify_url)
    )

def send_password_reset_email(user):
    """Envoie un email de réinitialisation de mot de passe"""
    # Générer un token de réinitialisation valide 1h
    token = user.generate_auth_token('password_reset', expires_in=3600)
    
    # Construire l'URL de réinitialisation
    reset_url = url_for('auth.reset_password', token=token.token, _external=True)
    
    # Envoyer l'email
    return send_email(
        subject='Réinitialiser votre mot de passe - E-KAY',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, reset_url=reset_url),
        html_body=render_template('email/reset_password.html', user=user, reset_url=reset_url)
    )

def send_property_approved_email(property_id):
    """Envoie un email au propriétaire lorsque sa propriété est approuvée"""
    property = Property.query.get_or_404(property_id)
    
    # Construire l'URL de la propriété
    property_url = url_for('properties.view_property', id=property.id, _external=True)
    
    # Envoyer l'email
    return send_email(
        subject=f"Votre annonce \"{property.title}\" a été approuvée - E-KAY",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[property.user.email],
        text_body=render_template('email/property_approved.txt', 
                                user=property.user, 
                                property=property,
                                property_url=property_url),
        html_body=render_template('email/property_approved.html', 
                                user=property.user, 
                                property=property,
                                property_url=property_url)
    )

def send_booking_confirmation(booking):
    """Envoie un email de confirmation de réservation au voyageur"""
    # Construire l'URL de la réservation
    booking_url = url_for('properties.booking_details', booking_id=booking.id, _external=True)
    property_url = url_for('properties.view_property', id=booking.property.id, _external=True)
    
    # Formater les dates
    check_in = booking.start_date.strftime('%A %d %B %Y')
    check_out = booking.end_date.strftime('%A %d %B %Y')
    nights = (booking.end_date - booking.start_date).days
    
    # Calculer le total
    total = booking.property.price * 1.1 * (nights // 30)  # 10% de frais de service
    
    # Envoyer l'email
    return send_email(
        subject=f"Confirmation de votre réservation - {booking.property.title}",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[booking.user.email],
        text_body=render_template('email/booking_confirmation.txt',
                                booking=booking,
                                user=booking.user,
                                property=booking.property,
                                check_in=check_in,
                                check_out=check_out,
                                nights=nights,
                                total=total,
                                booking_url=booking_url,
                                property_url=property_url),
        html_body=render_template('email/booking_confirmation.html',
                                booking=booking,
                                user=booking.user,
                                property=booking.property,
                                check_in=check_in,
                                check_out=check_out,
                                nights=nights,
                                total=total,
                                booking_url=booking_url,
                                property_url=property_url)
    )

def send_booking_notification(booking, host):
    """Envoie une notification au propriétaire pour une nouvelle demande de réservation"""
    # Construire les URLs
    booking_url = url_for('properties.booking_details', booking_id=booking.id, _external=True)
    property_url = url_for('properties.view_property', id=booking.property.id, _external=True)
    
    # Formater les dates
    check_in = booking.start_date.strftime('%A %d %B %Y')
    check_out = booking.end_date.strftime('%A %d %B %Y')
    nights = (booking.end_date - booking.start_date).days
    
    # Calculer le total
    total = booking.property.price * 1.1 * (nights // 30)  # 10% de frais de service
    
    # Envoyer l'email
    return send_email(
        subject=f"Nouvelle demande de réservation pour {booking.property.title}",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[host.email],
        text_body=render_template('email/booking_notification.txt',
                                booking=booking,
                                host=host,
                                guest=booking.user,
                                property=booking.property,
                                check_in=check_in,
                                check_out=check_out,
                                nights=nights,
                                total=total,
                                booking_url=booking_url,
                                property_url=property_url),
        html_body=render_template('email/booking_notification.html',
                                booking=booking,
                                host=host,
                                guest=booking.user,
                                property=booking.property,
                                check_in=check_in,
                                check_out=check_out,
                                nights=nights,
                                total=total,
                                booking_url=booking_url,
                                property_url=property_url)
    )

def send_booking_status_update(booking):
    """Envoie une notification de mise à jour de statut de réservation au voyageur"""
    if booking.status not in ['confirmed', 'cancelled']:
        return False
        
    # Construire l'URL de la réservation
    booking_url = url_for('properties.booking_details', booking_id=booking.id, _external=True)
    
    # Déterminer le template en fonction du statut
    template_base = 'booking_confirmed' if booking.status == 'confirmed' else 'booking_cancelled'
    
    # Envoyer l'email
    return send_email(
        subject=f"Mise à jour de votre réservation - {booking.property.title}" if booking.status == 'confirmed' else f"Annulation de votre réservation - {booking.property.title}",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[booking.user.email],
        text_body=render_template(f'email/{template_base}.txt',
                                booking=booking,
                                user=booking.user,
                                property=booking.property,
                                booking_url=booking_url),
        html_body=render_template(f'email/{template_base}.html',
                                booking=booking,
                                user=booking.user,
                                property=booking.property,
                                booking_url=booking_url)
    )

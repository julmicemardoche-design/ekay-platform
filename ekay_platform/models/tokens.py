from datetime import datetime, timedelta, timezone
import secrets
from .. import db

class Token(db.Model):
    """Modèle pour stocker les tokens de vérification email"""
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token_type = db.Column(db.String(20), nullable=False)  # 'email_verification' or 'password_reset'
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, user_id, token_type, expires_in=3600):
        self.user_id = user_id
        self.token_type = token_type
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    def is_valid(self):
        """Vérifie si le token est valide et n'a pas expiré"""
        now = datetime.now(timezone.utc)
        # Si expires_at n'a pas de fuseau horaire, on le considère comme UTC
        if self.expires_at.tzinfo is None:
            return not self.used and now < self.expires_at.replace(tzinfo=timezone.utc)
        return not self.used and now < self.expires_at

    def mark_as_used(self):
        """Marque le token comme utilisé"""
        self.used = True
        db.session.add(self)
        db.session.commit()

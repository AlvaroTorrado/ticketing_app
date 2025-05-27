from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp

# Cargar usuario para sesión
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modelo de Usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='usuario')  # usuario, manager, admin
    last_login = db.Column(db.DateTime, default=None)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(32), nullable=True)
    mfa_confirmed = db.Column(db.Boolean, default=False)


    def get_totp_uri(self):
        return f"otpauth://totp/TicketSystem:{self.username}?secret={self.mfa_secret}&issuer=TicketSystem"

    def verify_totp(self, token):
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(token)

# Modelo de Ticket
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pendiente')  # pendiente, abierto, completado
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to = db.relationship('User', backref='tickets')
    
class TicketHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))
    timestamp = db.Column(db.DateTime, default=db.func.now())
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    changed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    changed_by = db.relationship('User', backref='history_changes')
    ticket = db.relationship('Ticket', backref='history')
    
class RoleChangeHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    changed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    old_role = db.Column(db.String(20))
    new_role = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship('User', foreign_keys=[user_id], backref='role_changes')
    changed_by = db.relationship('User', foreign_keys=[changed_by_id])

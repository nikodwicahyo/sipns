from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    siswa_id = db.Column(db.Integer, db.ForeignKey('siswa.id'), nullable=True)
    guru_id = db.Column(db.Integer, db.ForeignKey('guru.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_guru(self):
        return self.role == 'guru'

    def is_siswa(self):
        return self.role == 'siswa'

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}: {self.role}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'siswa_id': self.siswa_id,
            'guru_id': self.guru_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

from datetime import datetime
from models import db

class EmployerProfile(db.Model):
    __tablename__ = 'employer_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    contact_person = db.Column(db.String(100), nullable=True)
    business_description = db.Column(db.Text, nullable=True)
    business_address = db.Column(db.String(255), nullable=True)
    work_location = db.Column(db.String(100), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    jobs = db.relationship('Job', backref='employer_profile', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'contact_person': self.contact_person or (self.user.full_name if self.user else ''),
            'email': self.user.email if self.user else '',
            'contact_phone': self.contact_phone or (self.user.phone if self.user else ''),
            'business_description': self.business_description,
            'business_address': self.business_address,
            'work_location': self.work_location or (self.user.location if self.user else ''),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<EmployerProfile {self.company_name} (User={self.user_id})>"

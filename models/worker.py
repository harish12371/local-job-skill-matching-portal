from datetime import datetime, timezone
from models import db

def utc_now():
    return datetime.now(timezone.utc)

class WorkerProfile(db.Model):
    __tablename__ = 'worker_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    skills = db.Column(db.String(255), default='')  # Comma-separated list e.g. "Painting, Masonry, Helper"
    experience_years = db.Column(db.Float, default=0.0)
    expected_wage = db.Column(db.Float, default=500.0)  # Daily wage in INR
    availability = db.Column(db.String(20), default='Available')  # 'Available', 'Busy', 'Unavailable'
    short_description = db.Column(db.Text, nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationship to applications
    applications = db.relationship('Application', backref='worker_profile', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.user.full_name if self.user else '',
            'email': self.user.email if self.user else '',
            'phone': self.user.phone if self.user else '',
            'location': self.user.location if self.user else '',
            'address': self.user.address if self.user else '',
            'skills': self.skills,
            'skills_list': self.skills_list,
            'experience_years': self.experience_years,
            'expected_wage': self.expected_wage,
            'availability': self.availability,
            'short_description': self.short_description,
            'profile_photo': self.profile_photo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<WorkerProfile User={self.user_id} Skills='{self.skills}'>"

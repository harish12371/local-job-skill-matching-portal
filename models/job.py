from datetime import datetime, timezone
from models import db

def utc_now():
    return datetime.now(timezone.utc)

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer_profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default='General Helper', index=True)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.String(255), nullable=False)  # Comma-separated: "Painting, Helper"
    location = db.Column(db.String(100), nullable=False, index=True)
    wage = db.Column(db.Float, nullable=False)  # Daily wage
    wage_type = db.Column(db.String(30), default='Daily')  # Daily, Per Job, Hourly
    working_hours = db.Column(db.String(50), default='8 Hours / Day (9:00 AM - 5:00 PM)')
    duration = db.Column(db.String(50), default='1-3 Days')
    workers_needed = db.Column(db.Integer, default=1)
    contact_phone = db.Column(db.String(20), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), default='active', index=True)  # 'active', 'closed'
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    applications = db.relationship('Application', backref='job', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def required_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'employer_id': self.employer_id,
            'employer_name': self.employer_profile.company_name if self.employer_profile else 'Employer',
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'required_skills': self.required_skills,
            'required_skills_list': self.required_skills_list,
            'location': self.location,
            'wage': self.wage,
            'wage_type': self.wage_type,
            'working_hours': self.working_hours,
            'duration': self.duration,
            'workers_needed': self.workers_needed,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'applications_count': self.applications.count()
        }

    def __repr__(self):
        return f"<Job {self.id}: {self.title} at {self.location}>"

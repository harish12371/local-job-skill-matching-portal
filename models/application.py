from datetime import datetime
from models import db

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.String(20), default='Pending', nullable=False, index=True)  # 'Pending', 'Accepted', 'Rejected'
    cover_note = db.Column(db.Text, nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ensure a worker cannot apply twice to the same job
    __table_args__ = (
        db.UniqueConstraint('job_id', 'worker_id', name='uq_job_worker_application'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'worker_id': self.worker_id,
            'job_title': self.job.title if self.job else '',
            'employer_name': self.job.employer_profile.company_name if (self.job and self.job.employer_profile) else '',
            'worker_name': self.worker_profile.user.full_name if (self.worker_profile and self.worker_profile.user) else '',
            'worker_phone': self.worker_profile.user.phone if (self.worker_profile and self.worker_profile.user) else '',
            'worker_location': self.worker_profile.user.location if (self.worker_profile and self.worker_profile.user) else '',
            'worker_skills': self.worker_profile.skills if self.worker_profile else '',
            'status': self.status,
            'cover_note': self.cover_note,
            'applied_at': self.applied_at.strftime('%Y-%m-%d %H:%M') if self.applied_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None
        }

    def __repr__(self):
        return f"<Application Job={self.job_id} Worker={self.worker_id} Status={self.status}>"

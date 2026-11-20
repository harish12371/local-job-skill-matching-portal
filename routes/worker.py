from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.worker import WorkerProfile
from models.application import Application
from models.job import Job
from routes.decorators import worker_required
from services.matching_service import get_recommended_jobs

worker_bp = Blueprint('worker', __name__)

@worker_bp.route('/dashboard')
@worker_required
def dashboard():
    worker_profile = current_user.worker_profile
    if not worker_profile:
        # Auto-create if missing
        worker_profile = WorkerProfile(user_id=current_user.id)
        db.session.add(worker_profile)
        db.session.commit()

    # Get applications
    applications = Application.query.filter_by(worker_id=worker_profile.id).order_by(Application.applied_at.desc()).all()
    pending_apps = [a for a in applications if a.status == 'Pending']
    accepted_apps = [a for a in applications if a.status == 'Accepted']
    rejected_apps = [a for a in applications if a.status == 'Rejected']

    # Recommended Jobs based on skills + location matching
    recommended_jobs = get_recommended_jobs(worker_profile, limit=6)

    # Calculate profile completion percentage
    completion_score = 0
    if current_user.full_name: completion_score += 20
    if current_user.phone: completion_score += 20
    if current_user.location: completion_score += 20
    if worker_profile.skills: completion_score += 20
    if worker_profile.short_description: completion_score += 20

    return render_template(
        'worker_dashboard.html',
        profile=worker_profile,
        applications=applications,
        pending_apps=pending_apps,
        accepted_apps=accepted_apps,
        rejected_apps=rejected_apps,
        recommended_jobs=recommended_jobs,
        completion_score=completion_score
    )

@worker_bp.route('/profile', methods=['GET', 'POST'])
@worker_required
def profile():
    worker_profile = current_user.worker_profile
    if not worker_profile:
        worker_profile = WorkerProfile(user_id=current_user.id)
        db.session.add(worker_profile)
        db.session.commit()

    if request.method == 'POST':
        # Update user fields
        current_user.full_name = request.form.get('full_name', '').strip() or current_user.full_name
        current_user.phone = request.form.get('phone', '').strip() or current_user.phone
        current_user.location = request.form.get('location', '').strip() or current_user.location
        current_user.address = request.form.get('address', '').strip()

        # Update profile fields
        worker_profile.skills = request.form.get('skills', '').strip()
        worker_profile.experience_years = float(request.form.get('experience_years') or 0.0)
        worker_profile.expected_wage = float(request.form.get('expected_wage') or 500.0)
        worker_profile.availability = request.form.get('availability', 'Available')
        worker_profile.short_description = request.form.get('short_description', '').strip()

        db.session.commit()
        flash('Your profile has been updated successfully.', 'success')
        return redirect(url_for('worker.dashboard'))

    return render_template('worker_dashboard.html', profile=worker_profile, edit_mode=True)

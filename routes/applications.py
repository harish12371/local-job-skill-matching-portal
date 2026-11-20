from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template
from flask_login import login_required, current_user
from models import db
from models.job import Job
from models.application import Application
from routes.decorators import worker_required, employer_required

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/apply/<int:job_id>', methods=['POST'])
@worker_required
def apply(job_id):
    job = Job.query.get_or_404(job_id)
    worker_profile = current_user.worker_profile

    if not worker_profile:
        flash('Please complete your worker profile before applying.', 'warning')
        return redirect(url_for('worker.dashboard'))

    # Check duplicate application
    existing_application = Application.query.filter_by(
        job_id=job.id,
        worker_id=worker_profile.id
    ).first()

    if existing_application:
        flash('You have already applied for this job. Check your dashboard for updates.', 'info')
        return redirect(url_for('jobs.job_details', job_id=job.id))

    cover_note = request.form.get('cover_note', '').strip()

    application = Application(
        job_id=job.id,
        worker_id=worker_profile.id,
        cover_note=cover_note,
        status='Pending'
    )
    db.session.add(application)
    db.session.commit()

    flash('Application submitted successfully! The employer will review your profile.', 'success')
    return redirect(url_for('jobs.job_details', job_id=job.id))

@applications_bp.route('/<int:app_id>/status', methods=['POST'])
@employer_required
def update_status(app_id):
    application = Application.query.get_or_404(app_id)
    job = application.job
    profile = current_user.employer_profile

    if job.employer_id != profile.id:
        flash('Unauthorized to update this application status.', 'danger')
        return redirect(url_for('employer.dashboard'))

    new_status = request.form.get('status', '').capitalize()
    if new_status in ['Accepted', 'Rejected', 'Pending']:
        application.status = new_status
        db.session.commit()
        flash(f'Application for {application.worker_profile.user.full_name} marked as {new_status}.', 'success')
    else:
        flash('Invalid status provided.', 'danger')

    return redirect(url_for('employer.dashboard'))

@applications_bp.route('/')
@login_required
def list_applications():
    if current_user.is_worker():
        worker_profile = current_user.worker_profile
        apps = Application.query.filter_by(worker_id=worker_profile.id).order_by(Application.applied_at.desc()).all() if worker_profile else []
        return render_template('applications.html', applications=apps, is_worker=True)
    elif current_user.is_employer():
        employer_profile = current_user.employer_profile
        job_ids = [j.id for j in employer_profile.jobs] if employer_profile else []
        apps = Application.query.filter(Application.job_id.in_(job_ids)).order_by(Application.applied_at.desc()).all() if job_ids else []
        return render_template('applications.html', applications=apps, is_worker=False)
    return redirect(url_for('main.index'))

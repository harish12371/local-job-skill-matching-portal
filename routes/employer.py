from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.employer import EmployerProfile
from models.job import Job
from models.application import Application
from routes.decorators import employer_required

employer_bp = Blueprint('employer', __name__)

@employer_bp.route('/dashboard')
@employer_required
def dashboard():
    profile = current_user.employer_profile
    if not profile:
        profile = EmployerProfile(
            user_id=current_user.id,
            company_name=current_user.full_name,
            contact_person=current_user.full_name,
            contact_phone=current_user.phone,
            work_location=current_user.location
        )
        db.session.add(profile)
        db.session.commit()

    jobs = Job.query.filter_by(employer_id=profile.id).order_by(Job.created_at.desc()).all()
    job_ids = [j.id for j in jobs]

    applications = []
    if job_ids:
        applications = Application.query.filter(Application.job_id.in_(job_ids)).order_by(Application.applied_at.desc()).all()

    total_jobs = len(jobs)
    active_jobs = sum(1 for j in jobs if j.status == 'active')
    total_applications = len(applications)
    pending_applications = sum(1 for a in applications if a.status == 'Pending')
    accepted_workers = sum(1 for a in applications if a.status == 'Accepted')

    return render_template(
        'employer_dashboard.html',
        profile=profile,
        jobs=jobs,
        applications=applications,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_applications=total_applications,
        pending_applications=pending_applications,
        accepted_workers=accepted_workers
    )

@employer_bp.route('/profile', methods=['GET', 'POST'])
@employer_required
def profile():
    profile = current_user.employer_profile
    if not profile:
        profile = EmployerProfile(user_id=current_user.id, company_name=current_user.full_name)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        # Update user basics
        current_user.full_name = request.form.get('contact_person', '').strip() or current_user.full_name
        current_user.phone = request.form.get('phone', '').strip() or current_user.phone
        current_user.location = request.form.get('work_location', '').strip() or current_user.location

        # Update employer profile
        profile.company_name = request.form.get('company_name', '').strip() or profile.company_name
        profile.contact_person = request.form.get('contact_person', '').strip()
        profile.contact_phone = request.form.get('phone', '').strip()
        profile.business_description = request.form.get('business_description', '').strip()
        profile.business_address = request.form.get('business_address', '').strip()
        profile.work_location = request.form.get('work_location', '').strip()

        db.session.commit()
        flash('Employer profile updated successfully.', 'success')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer_dashboard.html', profile=profile, edit_mode=True)

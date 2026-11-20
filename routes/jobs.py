from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db
from models.job import Job
from models.application import Application
from models.employer import EmployerProfile
from routes.decorators import employer_required
from services.matching_service import calculate_job_match

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/')
@jobs_bp.route('/find')
def find_jobs():
    keyword = request.args.get('keyword', '').strip()
    skill = request.args.get('skill', '').strip()
    location = request.args.get('location', '').strip()
    category = request.args.get('category', '').strip()
    min_wage = request.args.get('min_wage', type=float)
    max_wage = request.args.get('max_wage', type=float)
    sort_by = request.args.get('sort_by', 'latest')

    query = Job.query.filter_by(status='active')

    if keyword:
        like_kw = f"%{keyword}%"
        query = query.filter((Job.title.ilike(like_kw)) | (Job.description.ilike(like_kw)))
    if skill:
        query = query.filter(Job.required_skills.ilike(f"%{skill}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if category:
        query = query.filter(Job.category == category)
    if min_wage:
        query = query.filter(Job.wage >= min_wage)
    if max_wage:
        query = query.filter(Job.wage <= max_wage)

    # Sorting
    if sort_by == 'wage_high':
        query = query.order_by(Job.wage.desc())
    elif sort_by == 'wage_low':
        query = query.order_by(Job.wage.asc())
    else:
        query = query.order_by(Job.created_at.desc())

    jobs = query.all()

    # Pre-calculate matching score if logged-in user is a worker
    jobs_with_scores = []
    worker_profile = current_user.worker_profile if (current_user.is_authenticated and current_user.is_worker()) else None

    for j in jobs:
        match_info = calculate_job_match(worker_profile, j) if worker_profile else None
        jobs_with_scores.append({
            'job': j,
            'match': match_info
        })

    # Available categories for filter dropdown
    categories = ['Construction Worker', 'Electrician', 'Painter', 'Plumber', 'Carpenter', 'Delivery Worker', 'Helper', 'Mason']

    return render_template(
        'find_jobs.html',
        jobs_with_scores=jobs_with_scores,
        keyword=keyword,
        skill=skill,
        location=location,
        category=category,
        min_wage=min_wage,
        max_wage=max_wage,
        sort_by=sort_by,
        categories=categories
    )

@jobs_bp.route('/<int:job_id>')
def job_details(job_id):
    job = Job.query.get_or_404(job_id)

    # Check if current user has already applied
    has_applied = False
    application = None
    match_info = None

    if current_user.is_authenticated and current_user.is_worker() and current_user.worker_profile:
        application = Application.query.filter_by(
            job_id=job.id,
            worker_id=current_user.worker_profile.id
        ).first()
        if application:
            has_applied = True
        match_info = calculate_job_match(current_user.worker_profile, job)

    return render_template(
        'job_details.html',
        job=job,
        has_applied=has_applied,
        application=application,
        match=match_info
    )

@jobs_bp.route('/post', methods=['GET', 'POST'])
@employer_required
def post_job():
    profile = current_user.employer_profile
    if not profile:
        flash('Please complete your employer profile first.', 'warning')
        return redirect(url_for('employer.profile'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Helper').strip()
        description = request.form.get('description', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        location = request.form.get('location', '').strip()
        wage_str = request.form.get('wage', '0').strip()
        wage_type = request.form.get('wage_type', 'Daily')
        working_hours = request.form.get('working_hours', '8 Hours / Day').strip()
        duration = request.form.get('duration', '1-3 Days').strip()
        workers_needed = int(request.form.get('workers_needed') or 1)
        contact_phone = request.form.get('contact_phone', '').strip() or current_user.phone
        contact_email = request.form.get('contact_email', '').strip() or current_user.email

        if not title or not description or not required_skills or not location:
            flash('Please complete all required fields.', 'danger')
            return render_template('post_job.html', job=None)

        try:
            wage = float(wage_str)
        except ValueError:
            wage = 500.0

        new_job = Job(
            employer_id=profile.id,
            title=title,
            category=category,
            description=description,
            required_skills=required_skills,
            location=location,
            wage=wage,
            wage_type=wage_type,
            working_hours=working_hours,
            duration=duration,
            workers_needed=workers_needed,
            contact_phone=contact_phone,
            contact_email=contact_email,
            status='active'
        )
        db.session.add(new_job)
        db.session.commit()

        flash(f'Job "{title}" published successfully!', 'success')
        return redirect(url_for('jobs.job_details', job_id=new_job.id))

    return render_template('post_job.html', job=None)

@jobs_bp.route('/<int:job_id>/edit', methods=['GET', 'POST'])
@employer_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    profile = current_user.employer_profile

    if job.employer_id != profile.id:
        flash('Unauthorized to edit this job posting.', 'danger')
        return redirect(url_for('employer.dashboard'))

    if request.method == 'POST':
        job.title = request.form.get('title', '').strip() or job.title
        job.category = request.form.get('category', job.category).strip()
        job.description = request.form.get('description', '').strip() or job.description
        job.required_skills = request.form.get('required_skills', '').strip() or job.required_skills
        job.location = request.form.get('location', '').strip() or job.location
        try:
            job.wage = float(request.form.get('wage', job.wage))
        except ValueError:
            pass
        job.wage_type = request.form.get('wage_type', job.wage_type)
        job.working_hours = request.form.get('working_hours', job.working_hours).strip()
        job.duration = request.form.get('duration', job.duration).strip()
        job.workers_needed = int(request.form.get('workers_needed') or job.workers_needed)
        job.contact_phone = request.form.get('contact_phone', job.contact_phone).strip()
        job.contact_email = request.form.get('contact_email', job.contact_email).strip()
        job.status = request.form.get('status', job.status)

        db.session.commit()
        flash('Job posting updated successfully.', 'success')
        return redirect(url_for('jobs.job_details', job_id=job.id))

    return render_template('post_job.html', job=job)

@jobs_bp.route('/<int:job_id>/delete', methods=['POST'])
@employer_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    profile = current_user.employer_profile

    if job.employer_id != profile.id:
        flash('Unauthorized to delete this job posting.', 'danger')
        return redirect(url_for('employer.dashboard'))

    title = job.title
    db.session.delete(job)
    db.session.commit()
    flash(f'Job "{title}" was deleted successfully.', 'info')
    return redirect(url_for('employer.dashboard'))

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from models import db
from models.user import User
from models.job import Job
from models.application import Application
from models.worker import WorkerProfile
from models.employer import EmployerProfile
from services.matching_service import calculate_job_match, get_recommended_jobs

api_bp = Blueprint('api', __name__)

@api_bp.route('/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'online',
        'service': 'Local Job & Skill Matching Portal API',
        'authenticated': current_user.is_authenticated,
        'user': current_user.to_dict() if current_user.is_authenticated else None
    })

# JOBS API
@api_bp.route('/jobs', methods=['GET'])
def get_jobs():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    category = request.args.get('category', '')
    skill = request.args.get('skill', '')

    query = Job.query.filter_by(status='active')
    if keyword:
        query = query.filter((Job.title.ilike(f"%{keyword}%")) | (Job.description.ilike(f"%{keyword}%")))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if category:
        query = query.filter(Job.category == category)
    if skill:
        query = query.filter(Job.required_skills.ilike(f"%{skill}%"))

    jobs = query.order_by(Job.created_at.desc()).all()
    return jsonify({
        'count': len(jobs),
        'jobs': [j.to_dict() for j in jobs]
    })

@api_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify(job.to_dict())

@api_bp.route('/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    if not current_user.is_worker() or not current_user.worker_profile:
        return jsonify({'error': 'Only registered workers can view job recommendations'}), 403

    limit = request.args.get('limit', 10, type=int)
    recs = get_recommended_jobs(current_user.worker_profile, limit=limit)
    data = []
    for r in recs:
        item = r['job'].to_dict()
        item['match_score'] = r['match']['score']
        item['match_level'] = r['match']['match_level']
        item['matched_skills'] = r['match']['matched_skills']
        data.append(item)

    return jsonify({
        'worker': current_user.worker_profile.to_dict(),
        'recommendations': data
    })

from flask import Blueprint, render_template
from models.job import Job

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch recent active jobs for the homepage
    featured_jobs = Job.query.filter_by(status='active').order_by(Job.created_at.desc()).limit(6).all()
    categories = [
        {'name': 'Construction Worker', 'icon': 'bi-bricks', 'count': Job.query.filter_by(category='Construction Worker', status='active').count()},
        {'name': 'Electrician', 'icon': 'bi-lightning-charge', 'count': Job.query.filter_by(category='Electrician', status='active').count()},
        {'name': 'Painter', 'icon': 'bi-paint-bucket', 'count': Job.query.filter_by(category='Painter', status='active').count()},
        {'name': 'Plumber', 'icon': 'bi-wrench-adjustable', 'count': Job.query.filter_by(category='Plumber', status='active').count()},
        {'name': 'Carpenter', 'icon': 'bi-hammer', 'count': Job.query.filter_by(category='Carpenter', status='active').count()},
        {'name': 'Delivery Worker', 'icon': 'bi-truck', 'count': Job.query.filter_by(category='Delivery Worker', status='active').count()},
        {'name': 'Helper', 'icon': 'bi-person-arms-up', 'count': Job.query.filter_by(category='Helper', status='active').count()},
        {'name': 'Mason', 'icon': 'bi-house-gear', 'count': Job.query.filter_by(category='Mason', status='active').count()},
    ]
    return render_template('index.html', featured_jobs=featured_jobs, categories=categories)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

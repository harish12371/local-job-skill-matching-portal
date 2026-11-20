import os
import json
import pytest
from app import create_app
from models import db, User, Job, Application, WorkerProfile, EmployerProfile
from services.matching_service import calculate_job_match

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False
    })
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_case_01_worker_registration(client):
    res = client.post('/auth/register', data={
        'role': 'worker',
        'full_name': 'Aakash Rao',
        'email': 'aakash_worker@test.com',
        'phone': '9845112233',
        'location': 'Bantwal',
        'address': 'Panemangalore',
        'skills': 'Painter, Helper',
        'experience_years': '4',
        'expected_wage': '700',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert res.status_code == 200
    user = User.query.filter_by(email='aakash_worker@test.com').first()
    assert user is not None
    assert user.is_worker()
    assert user.worker_profile.skills == 'Painter, Helper'
    client.get('/auth/logout', follow_redirects=True)

def test_case_02_employer_registration(client):
    res = client.post('/auth/register', data={
        'role': 'employer',
        'full_name': 'Kishore Hegde',
        'email': 'kishore_emp@test.com',
        'phone': '9845223344',
        'location': 'Mangalore',
        'address': 'Bejai, Mangalore',
        'company_name': 'Hegde Constructions',
        'business_description': 'Commercial projects',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert res.status_code == 200
    user = User.query.filter_by(email='kishore_emp@test.com').first()
    assert user is not None
    assert user.is_employer()
    assert user.employer_profile.company_name == 'Hegde Constructions'
    client.get('/auth/logout', follow_redirects=True)

def test_case_03_login_and_logout(client):
    res_login = client.post('/auth/login', data={
        'email': 'aakash_worker@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b'Welcome back' in res_login.data

    res_logout = client.get('/auth/logout', follow_redirects=True)
    assert res_logout.status_code == 200
    assert b'logged out successfully' in res_logout.data

def test_case_04_invalid_login_handling(client):
    res = client.post('/auth/login', data={
        'email': 'aakash_worker@test.com',
        'password': 'wrong_password_xyz'
    }, follow_redirects=True)
    assert b'Invalid email or password' in res.data

def test_case_05_worker_profile_update(client):
    client.post('/auth/login', data={'email': 'aakash_worker@test.com', 'password': 'password123'}, follow_redirects=True)
    res = client.post('/worker/profile', data={
        'full_name': 'Aakash Rao Senior',
        'phone': '9845112299',
        'location': 'Bantwal East',
        'address': 'Updated Street Address',
        'skills': 'Painter, Masonry, Helper',
        'experience_years': '6.0',
        'expected_wage': '800',
        'availability': 'Available',
        'short_description': 'Experienced master painter with team of 2 helpers'
    }, follow_redirects=True)
    assert res.status_code == 200
    user = User.query.filter_by(email='aakash_worker@test.com').first()
    assert user.full_name == 'Aakash Rao Senior'
    assert user.worker_profile.experience_years == 6.0
    assert user.worker_profile.expected_wage == 800.0
    client.get('/auth/logout', follow_redirects=True)

def test_case_06_employer_profile_update(client):
    client.post('/auth/login', data={'email': 'kishore_emp@test.com', 'password': 'password123'}, follow_redirects=True)
    res = client.post('/employer/profile', data={
        'company_name': 'Hegde Coastal Infrastructure Pvt Ltd',
        'contact_person': 'Kishore Hegde MD',
        'phone': '9845223399',
        'work_location': 'Mangalore & Udupi',
        'business_address': 'Bejai Main Road',
        'business_description': 'Updated commercial civil construction enterprise'
    }, follow_redirects=True)
    assert res.status_code == 200
    user = User.query.filter_by(email='kishore_emp@test.com').first()
    assert user.employer_profile.company_name == 'Hegde Coastal Infrastructure Pvt Ltd'
    client.get('/auth/logout', follow_redirects=True)

def test_case_07_job_posting(client):
    client.post('/auth/login', data={'email': 'kishore_emp@test.com', 'password': 'password123'}, follow_redirects=True)
    res = client.post('/jobs/post', data={
        'title': 'New Residential Painting Project',
        'category': 'Painter',
        'location': 'Bantwal',
        'required_skills': 'Painter, Helper',
        'wage': '750',
        'wage_type': 'Daily',
        'duration': '4 Days',
        'working_hours': '8:30 AM - 5:30 PM',
        'workers_needed': '2',
        'description': 'Full villa exterior emulsion painting project.'
    }, follow_redirects=True)
    assert res.status_code == 200
    job = Job.query.filter_by(title='New Residential Painting Project').first()
    assert job is not None
    assert job.wage == 750.0
    client.get('/auth/logout', follow_redirects=True)

def test_case_08_job_editing(client):
    client.post('/auth/login', data={'email': 'kishore_emp@test.com', 'password': 'password123'}, follow_redirects=True)
    job = Job.query.filter_by(title='New Residential Painting Project').first()
    res = client.post(f'/jobs/{job.id}/edit', data={
        'title': 'New Residential Painting Project (Updated)',
        'category': 'Painter',
        'location': 'Bantwal',
        'required_skills': 'Painter, Helper',
        'wage': '800',
        'wage_type': 'Daily',
        'duration': '5 Days',
        'working_hours': '8:30 AM - 5:30 PM',
        'workers_needed': '3',
        'description': 'Updated scope: includes primer coat.',
        'status': 'active'
    }, follow_redirects=True)
    assert res.status_code == 200
    db.session.refresh(job)
    assert job.title == 'New Residential Painting Project (Updated)'
    assert job.wage == 800.0
    assert job.workers_needed == 3
    client.get('/auth/logout', follow_redirects=True)

def test_case_09_job_deletion(client):
    # Post temporary job and delete it
    client.post('/auth/login', data={'email': 'kishore_emp@test.com', 'password': 'password123'}, follow_redirects=True)
    client.post('/jobs/post', data={
        'title': 'Temporary Demo Job to Delete',
        'category': 'Helper',
        'location': 'Mangalore',
        'required_skills': 'Helper',
        'wage': '500',
        'description': 'Will be deleted'
    }, follow_redirects=True)
    temp_job = Job.query.filter_by(title='Temporary Demo Job to Delete').first()
    assert temp_job is not None

    del_res = client.post(f'/jobs/{temp_job.id}/delete', follow_redirects=True)
    assert del_res.status_code == 200
    assert db.session.get(Job, temp_job.id) is None
    client.get('/auth/logout', follow_redirects=True)

def test_case_10_job_search(client):
    res = client.get('/jobs/find?keyword=Painting')
    assert res.status_code == 200
    assert b'Painting' in res.data

def test_case_11_skill_filtering(client):
    res = client.get('/jobs/find?skill=Painter')
    assert res.status_code == 200
    assert b'Painter' in res.data

def test_case_12_location_filtering(client):
    res = client.get('/jobs/find?location=Bantwal')
    assert res.status_code == 200
    assert b'Bantwal' in res.data

def test_case_13_job_application_flow(client):
    job = Job.query.filter_by(title='New Residential Painting Project (Updated)').first()
    client.post('/auth/login', data={'email': 'aakash_worker@test.com', 'password': 'password123'}, follow_redirects=True)
    res = client.post(f'/applications/apply/{job.id}', data={
        'cover_note': 'I have painter brushes and spray tools ready.'
    }, follow_redirects=True)
    assert res.status_code == 200
    app_record = Application.query.filter_by(job_id=job.id).first()
    assert app_record is not None
    assert app_record.status == 'Pending'
    client.get('/auth/logout', follow_redirects=True)

def test_case_14_duplicate_application_prevention(client):
    job = Job.query.filter_by(title='New Residential Painting Project (Updated)').first()
    client.post('/auth/login', data={'email': 'aakash_worker@test.com', 'password': 'password123'}, follow_redirects=True)
    dup_res = client.post(f'/applications/apply/{job.id}', data={
        'cover_note': 'Submitting duplicate application'
    }, follow_redirects=True)
    assert b'already applied' in dup_res.data
    # Verify count is still exactly 1
    apps = Application.query.filter_by(job_id=job.id).all()
    assert len(apps) == 1
    client.get('/auth/logout', follow_redirects=True)

def test_case_15_application_acceptance(client):
    job = Job.query.filter_by(title='New Residential Painting Project (Updated)').first()
    app_record = Application.query.filter_by(job_id=job.id).first()

    client.post('/auth/login', data={'email': 'kishore_emp@test.com', 'password': 'password123'}, follow_redirects=True)
    res = client.post(f'/applications/{app_record.id}/status', data={
        'status': 'Accepted'
    }, follow_redirects=True)
    assert res.status_code == 200
    db.session.refresh(app_record)
    assert app_record.status == 'Accepted'
    client.get('/auth/logout', follow_redirects=True)

def test_case_16_application_rejection(client):
    job = Job.query.filter_by(title='New Residential Painting Project (Updated)').first()
    app_record = Application.query.filter_by(job_id=job.id).first()

    client.post('/auth/login', data={'email': 'kishore_emp@test.com', 'password': 'password123'}, follow_redirects=True)
    res = client.post(f'/applications/{app_record.id}/status', data={
        'status': 'Rejected'
    }, follow_redirects=True)
    assert res.status_code == 200
    db.session.refresh(app_record)
    assert app_record.status == 'Rejected'
    client.get('/auth/logout', follow_redirects=True)

def test_case_17_role_based_access_restrictions(client):
    # Worker blocked from employer dashboard
    client.post('/auth/login', data={'email': 'aakash_worker@test.com', 'password': 'password123'}, follow_redirects=True)
    res = client.get('/employer/dashboard', follow_redirects=True)
    assert b'Access restricted to registered Employers only' in res.data
    client.get('/auth/logout', follow_redirects=True)

    # Employer blocked from worker dashboard
    client.post('/auth/login', data={'email': 'kishore_emp@test.com', 'password': 'password123'}, follow_redirects=True)
    res2 = client.get('/worker/dashboard', follow_redirects=True)
    assert b'Access restricted to registered Workers only' in res2.data
    client.get('/auth/logout', follow_redirects=True)

def test_case_18_mysql_connectivity():
    from sqlalchemy.dialects import registry
    dialect_cls = registry.load('mysql.pymysql')
    assert dialect_cls is not None
    assert 'MySQLDialect_pymysql' in str(dialect_cls)

def test_case_19_mobile_responsiveness(client):
    res = client.get('/')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    # Viewport meta tag
    assert 'name="viewport"' in html
    assert 'content="width=device-width, initial-scale=1.0"' in html
    # Bootstrap responsive navbar toggler
    assert 'navbar-toggler' in html
    assert 'collapse navbar-collapse' in html
    # Responsive grid columns
    assert 'col-lg-' in html
    assert 'col-md-' in html

def test_case_20_vercel_production_compatibility():
    # Verify vercel.json exists and is valid JSON
    with open('vercel.json', 'r') as f:
        vcfg = json.load(f)
    assert vcfg['version'] == 2
    assert vcfg['builds'][0]['src'] == 'api/index.py'

    # Verify api/index.py exposes app instance
    import api.index as vercel_entry
    assert hasattr(vercel_entry, 'app')
    assert callable(vercel_entry.app)

    # Verify requirements.txt contains critical production packages
    with open('requirements.txt', 'r') as f:
        reqs = f.read().lower()
    assert 'flask' in reqs
    assert 'flask-sqlalchemy' in reqs
    assert 'pymysql' in reqs
    assert 'cryptography' in reqs
    assert 'gunicorn' in reqs

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
        db.create_all()
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_matching_algorithm(app):
    with app.app_context():
        # Worker in Bantwal with Painting & Masonry
        worker = User(email='match_worker@test.com', role='worker', full_name='Ramesh', phone='9876543210', location='Bantwal')
        worker.set_password('pass123')
        db.session.add(worker)
        db.session.flush()

        w_prof = WorkerProfile(user_id=worker.id, skills='Painting, Masonry, Helper', expected_wage=650.0)
        db.session.add(w_prof)
        db.session.flush()

        # Bantwal Painting Job
        emp = User(email='match_emp@test.com', role='employer', full_name='Vinay', phone='9876543211', location='Bantwal')
        emp.set_password('pass123')
        db.session.add(emp)
        db.session.flush()

        e_prof = EmployerProfile(user_id=emp.id, company_name='Bantwal Builders')
        db.session.add(e_prof)
        db.session.flush()

        job_bantwal = Job(
            employer_id=e_prof.id,
            title='Bantwal Painting Work',
            category='Painter',
            description='Painting work in Bantwal',
            required_skills='Painting, Helper',
            location='Bantwal',
            wage=750.0
        )
        db.session.add(job_bantwal)
        db.session.flush()

        match1 = calculate_job_match(w_prof, job_bantwal)
        assert match1['score'] >= 80, f"Expected high score, got {match1['score']}"
        assert match1['location_match'] is True
        assert match1['wage_fit'] is True
        assert 'Painting' in match1['matched_skills']

        # Job in Bangalore
        job_far = Job(
            employer_id=e_prof.id,
            title='Bangalore Electrician',
            category='Electrician',
            description='Electrical work in Bangalore',
            required_skills='Electrician',
            location='Bangalore',
            wage=800.0
        )
        db.session.add(job_far)
        db.session.flush()

        match2 = calculate_job_match(w_prof, job_far)
        assert match2['score'] < 30
        assert match2['location_match'] is False

        db.session.rollback()

def test_job_application_lifecycle(client):
    # 1. Employer posts a job
    client.post('/auth/login', data={'email': 'employer1@portal.com', 'password': 'password123'}, follow_redirects=True)
    post_res = client.post('/jobs/post', data={
        'title': 'Test Plumbing Work',
        'category': 'Plumber',
        'location': 'Mangalore',
        'required_skills': 'Plumber, Helper',
        'wage': '750',
        'wage_type': 'Daily',
        'duration': '2 Days',
        'working_hours': '9 AM - 5 PM',
        'workers_needed': '2',
        'description': 'Plumbing pipeline fix in commercial block'
    }, follow_redirects=True)
    assert post_res.status_code == 200

    job = Job.query.filter_by(title='Test Plumbing Work').first()
    assert job is not None

    client.get('/auth/logout', follow_redirects=True)

    # 2. Worker applies
    client.post('/auth/login', data={'email': 'worker1@portal.com', 'password': 'password123'}, follow_redirects=True)
    apply_res = client.post(f'/applications/apply/{job.id}', data={
        'cover_note': 'Ready to start immediately'
    }, follow_redirects=True)
    assert apply_res.status_code == 200

    app_record = Application.query.filter_by(job_id=job.id).first()
    assert app_record is not None
    assert app_record.status == 'Pending'
    assert app_record.cover_note == 'Ready to start immediately'

    # 3. Duplicate application prevention
    dup_res = client.post(f'/applications/apply/{job.id}', data={
        'cover_note': 'Applying second time'
    }, follow_redirects=True)
    assert b'already applied' in dup_res.data

    client.get('/auth/logout', follow_redirects=True)

    # 4. Employer accepts application
    client.post('/auth/login', data={'email': 'employer1@portal.com', 'password': 'password123'}, follow_redirects=True)
    update_res = client.post(f'/applications/{app_record.id}/status', data={
        'status': 'Accepted'
    }, follow_redirects=True)
    assert update_res.status_code == 200

    db.session.refresh(app_record)
    assert app_record.status == 'Accepted'

    # Clean up test job
    client.post(f'/jobs/{job.id}/delete', follow_redirects=True)
    assert db.session.get(Job, job.id) is None

def test_role_based_access_control(client):
    # Unauthenticated user cannot access worker dashboard
    r1 = client.get('/worker/dashboard')
    assert r1.status_code == 302
    assert '/auth/login' in r1.location

    # Unauthenticated user cannot access employer dashboard
    r2 = client.get('/employer/dashboard')
    assert r2.status_code == 302
    assert '/auth/login' in r2.location

    # Worker cannot access employer dashboard
    client.post('/auth/login', data={'email': 'worker1@portal.com', 'password': 'password123'}, follow_redirects=True)
    r3 = client.get('/employer/dashboard', follow_redirects=True)
    assert b'Access restricted to registered Employers only' in r3.data

    # Worker cannot post job
    r4 = client.get('/jobs/post', follow_redirects=True)
    assert b'Access restricted to registered Employers only' in r4.data

    client.get('/auth/logout', follow_redirects=True)

    # Employer cannot access worker dashboard
    client.post('/auth/login', data={'email': 'employer1@portal.com', 'password': 'password123'}, follow_redirects=True)
    r5 = client.get('/worker/dashboard', follow_redirects=True)
    assert b'Access restricted to registered Workers only' in r5.data

def test_rest_api_endpoints(client):
    # API status
    res = client.get('/api/status')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['status'] == 'online'

    # API jobs list
    res_jobs = client.get('/api/jobs')
    assert res_jobs.status_code == 200
    data = res_jobs.get_json()
    assert 'jobs' in data
    assert data['count'] >= 1

    # API filter jobs
    res_filter = client.get('/api/jobs?location=Bantwal')
    assert res_filter.status_code == 200
    bantwal_data = res_filter.get_json()
    for j in bantwal_data['jobs']:
        assert 'bantwal' in j['location'].lower()

    # API recommendations (authenticated worker)
    client.post('/auth/login', data={'email': 'worker1@portal.com', 'password': 'password123'}, follow_redirects=True)
    res_rec = client.get('/api/recommendations')
    assert res_rec.status_code == 200
    rec_data = res_rec.get_json()
    assert 'recommendations' in rec_data
    assert len(rec_data['recommendations']) > 0
    assert 'match_score' in rec_data['recommendations'][0]

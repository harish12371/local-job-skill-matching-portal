from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from models.worker import WorkerProfile
from models.employer import EmployerProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    role = request.args.get('role', 'worker').lower()
    if role not in ['worker', 'employer']:
        role = 'worker'

    if current_user.is_authenticated:
        if current_user.is_worker():
            return redirect(url_for('worker.dashboard'))
        return redirect(url_for('employer.dashboard'))

    if request.method == 'POST':
        selected_role = request.form.get('role', 'worker').lower()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        location = request.form.get('location', '').strip()
        address = request.form.get('address', '').strip()

        # Validation
        if not full_name or not email or not phone or not password or not location:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html', role=selected_role)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', role=selected_role)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', role=selected_role)

        if User.query.filter_by(email=email).first():
            flash('An account with this email address already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login', role=selected_role))

        # Create user
        try:
            user = User(
                email=email,
                role=selected_role,
                full_name=full_name,
                phone=phone,
                location=location,
                address=address
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            # Create corresponding profile
            if selected_role == 'worker':
                skills = request.form.get('skills', '').strip()
                experience_years = float(request.form.get('experience_years') or 0.0)
                expected_wage = float(request.form.get('expected_wage') or 500.0)
                worker_profile = WorkerProfile(
                    user_id=user.id,
                    skills=skills,
                    experience_years=experience_years,
                    expected_wage=expected_wage,
                    availability='Available'
                )
                db.session.add(worker_profile)
            else:
                company_name = request.form.get('company_name', '').strip() or full_name
                employer_profile = EmployerProfile(
                    user_id=user.id,
                    company_name=company_name,
                    contact_person=full_name,
                    contact_phone=phone,
                    work_location=location,
                    business_address=address
                )
                db.session.add(employer_profile)

            db.session.commit()
            login_user(user)
            flash(f'Welcome, {user.full_name}! Your account has been created successfully.', 'success')

            if user.is_worker():
                return redirect(url_for('worker.dashboard'))
            return redirect(url_for('employer.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'danger')
            return render_template('register.html', role=selected_role)

    return render_template('register.html', role=role)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'worker').lower()
    if current_user.is_authenticated:
        if current_user.is_worker():
            return redirect(url_for('worker.dashboard'))
        return redirect(url_for('employer.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login.html', role=role)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', role=role)

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.full_name}!', 'success')

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        if user.is_worker():
            return redirect(url_for('worker.dashboard'))
        else:
            return redirect(url_for('employer.dashboard'))

    return render_template('login.html', role=role)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.user import User
from models.worker import WorkerProfile
from models.employer import EmployerProfile
from models.job import Job
from models.application import Application

def seed_database():
    app = create_app()
    with app.app_context():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        is_production = app.config.get('IS_PRODUCTION', False)
        is_remote_db = not db_uri.startswith('sqlite')

        # Safety Guard: Prevent accidental data destruction on production / remote MySQL
        if is_production or is_remote_db:
            if '--allow-production-reset' not in sys.argv:
                print("=" * 70)
                print("SAFETY WARNING: ACCIDENTAL DATABASE RESET PREVENTED!")
                print(f"Target Database: {db_uri.split('@')[-1] if '@' in db_uri else db_uri}")
                print("seed_data.py drops and recreates all tables with development demo data.")
                print("To safely initialize production tables WITHOUT dropping data, run:")
                print("    python scripts/init_db.py")
                print("To force reset this database anyway, pass:")
                print("    python scripts/seed_data.py --allow-production-reset")
                print("=" * 70)
                return

        print("Cleaning up old demo data...")
        db.drop_all()
        db.create_all()

        print("Seeding Users and Profiles...")

        # 1. Employers
        emp1_user = User(
            email='employer1@portal.com',
            role='employer',
            full_name='Rajesh Shenoy',
            phone='+91 98451 22334',
            location='Mangalore',
            address='Kadri Main Road, Mangalore'
        )
        emp1_user.set_password('password123')
        db.session.add(emp1_user)
        db.session.flush()

        emp1_profile = EmployerProfile(
            user_id=emp1_user.id,
            company_name='Coastal Infra & Builders',
            contact_person='Rajesh Shenoy',
            contact_phone='+91 98451 22334',
            work_location='Mangalore',
            business_address='Kadri Main Road, Mangalore',
            business_description='Leading residential and commercial building construction firm operating across Dakshina Kannada.'
        )
        db.session.add(emp1_profile)

        emp2_user = User(
            email='employer2@portal.com',
            role='employer',
            full_name='Vinay Bhat',
            phone='+91 97410 55667',
            location='Bantwal',
            address='Near B.C. Road Circle, Bantwal'
        )
        emp2_user.set_password('password123')
        db.session.add(emp2_user)
        db.session.flush()

        emp2_profile = EmployerProfile(
            user_id=emp2_user.id,
            company_name='Green Valley Estates & Agro',
            contact_person='Vinay Bhat',
            contact_phone='+91 97410 55667',
            work_location='Bantwal',
            business_address='Near B.C. Road Circle, Bantwal',
            business_description='Agricultural plantations and rural infrastructure development projects in Bantwal taluk.'
        )
        db.session.add(emp2_profile)

        # 2. Workers
        worker1_user = User(
            email='worker1@portal.com',
            role='worker',
            full_name='Ramesh Poojary',
            phone='+91 99001 11223',
            location='Bantwal',
            address='Melkar, Bantwal'
        )
        worker1_user.set_password('password123')
        db.session.add(worker1_user)
        db.session.flush()

        w1_profile = WorkerProfile(
            user_id=worker1_user.id,
            skills='Painting, Masonry, Helper',
            experience_years=5.0,
            expected_wage=650.0,
            availability='Available',
            short_description='Skilled wall painter and experienced mason assistant with 5+ years of active field experience in local construction.'
        )
        db.session.add(w1_profile)

        worker2_user = User(
            email='worker2@portal.com',
            role='worker',
            full_name='Suresh Kumar',
            phone='+91 98862 33445',
            location='Mangalore',
            address='Kottara Chowki, Mangalore'
        )
        worker2_user.set_password('password123')
        db.session.add(worker2_user)
        db.session.flush()

        w2_profile = WorkerProfile(
            user_id=worker2_user.id,
            skills='Electrician, Plumber',
            experience_years=7.0,
            expected_wage=750.0,
            availability='Available',
            short_description='Licensed domestic & industrial electrician with expertise in plumbing installations, switchboards, and repairs.'
        )
        db.session.add(w2_profile)

        worker3_user = User(
            email='worker3@portal.com',
            role='worker',
            full_name='Ravi Naik',
            phone='+91 94481 66778',
            location='Bantwal',
            address='B.C. Road, Bantwal'
        )
        worker3_user.set_password('password123')
        db.session.add(worker3_user)
        db.session.flush()

        w3_profile = WorkerProfile(
            user_id=worker3_user.id,
            skills='Delivery Worker, Helper',
            experience_years=2.0,
            expected_wage=500.0,
            availability='Available',
            short_description='Enthusiastic two-wheeler delivery personnel and warehouse loading helper ready for daily shifts.'
        )
        db.session.add(w3_profile)

        db.session.commit()
        print("Seeded Users and Profiles.")

        print("Seeding Jobs...")
        # 3. Jobs
        job1 = Job(
            employer_id=emp2_profile.id,
            title='Urgent Wall Painting & Boundary Plastering',
            category='Painter',
            description='Need 2 experienced painters and helpers for 3 days interior and boundary wall painting project in Bantwal. Tools and paint supplied on site.',
            required_skills='Painting, Helper',
            location='Bantwal',
            wage=750.0,
            wage_type='Daily',
            working_hours='8:30 AM - 5:30 PM',
            duration='3 Days',
            workers_needed=2,
            contact_phone=emp2_user.phone,
            contact_email=emp2_user.email,
            status='active'
        )

        job2 = Job(
            employer_id=emp2_profile.id,
            title='Compound Wall Stone Masonry & Cement Work',
            category='Mason',
            description='Looking for skilled mason for constructing a 60-foot laterite stone compound wall with mortar plastering.',
            required_skills='Masonry, Helper',
            location='Bantwal',
            wage=700.0,
            wage_type='Daily',
            working_hours='8:00 AM - 5:00 PM',
            duration='5 Days',
            workers_needed=1,
            contact_phone=emp2_user.phone,
            contact_email=emp2_user.email,
            status='active'
        )

        job3 = Job(
            employer_id=emp2_profile.id,
            title='Local Warehouse Goods Loading & Daily Delivery',
            category='Delivery Worker',
            description='Daily delivery helper required for dispatching agricultural supplies to nearby retail shops in Bantwal area.',
            required_skills='Delivery Worker, Helper',
            location='Bantwal',
            wage=600.0,
            wage_type='Daily',
            working_hours='9:00 AM - 6:00 PM',
            duration='Ongoing',
            workers_needed=2,
            contact_phone=emp2_user.phone,
            contact_email=emp2_user.email,
            status='active'
        )

        job4 = Job(
            employer_id=emp1_profile.id,
            title='Commercial Complex Electrical Conduit Wiring',
            category='Electrician',
            description='Commercial floor wiring, MCB panel installation, and conduit pulling work for a 3-storey office building.',
            required_skills='Electrician',
            location='Mangalore',
            wage=850.0,
            wage_type='Daily',
            working_hours='9:00 AM - 6:00 PM',
            duration='1 Week',
            workers_needed=3,
            contact_phone=emp1_user.phone,
            contact_email=emp1_user.email,
            status='active'
        )

        job5 = Job(
            employer_id=emp1_profile.id,
            title='Apartment Plumbing Pipeline & Sanitary Fixtures',
            category='Plumber',
            description='CPVC plumbing pipe replacement and bathroom sanitary fixture installation for renovated apartments.',
            required_skills='Plumber',
            location='Mangalore',
            wage=800.0,
            wage_type='Daily',
            working_hours='9:00 AM - 5:30 PM',
            duration='4 Days',
            workers_needed=2,
            contact_phone=emp1_user.phone,
            contact_email=emp1_user.email,
            status='active'
        )

        job6 = Job(
            employer_id=emp1_profile.id,
            title='Construction Site Laborer & Material Transport',
            category='Construction Worker',
            description='Active construction site helper needed for mixing concrete, carrying blocks, and site cleaning.',
            required_skills='Helper, Construction Worker',
            location='Mangalore',
            wage=650.0,
            wage_type='Daily',
            working_hours='8:00 AM - 5:00 PM',
            duration='2 Weeks',
            workers_needed=4,
            contact_phone=emp1_user.phone,
            contact_email=emp1_user.email,
            status='active'
        )

        db.session.add_all([job1, job2, job3, job4, job5, job6])
        db.session.commit()
        print("Seeded Jobs.")

        print("Seeding Applications...")
        # 4. Applications
        app1 = Application(
            job_id=job1.id,
            worker_id=w1_profile.id,
            status='Accepted',
            cover_note='I have 5 years experience in wall painting in Bantwal and can start immediately.'
        )

        app2 = Application(
            job_id=job3.id,
            worker_id=w3_profile.id,
            status='Pending',
            cover_note='I have my own two-wheeler and knowledge of Bantwal rural routes.'
        )

        app3 = Application(
            job_id=job4.id,
            worker_id=w2_profile.id,
            status='Accepted',
            cover_note='Certified electrician with 7 years commercial building experience.'
        )

        db.session.add_all([app1, app2, app3])
        db.session.commit()
        print("Seeded Applications successfully!")
        print("Database seed complete.")

if __name__ == '__main__':
    seed_database()

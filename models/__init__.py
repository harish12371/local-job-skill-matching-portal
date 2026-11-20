from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# Import models to ensure they are registered with SQLAlchemy
from models.user import User
from models.worker import WorkerProfile
from models.employer import EmployerProfile
from models.job import Job
from models.application import Application

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

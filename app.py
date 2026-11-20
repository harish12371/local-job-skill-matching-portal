import os
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, login_manager

csrf = CSRFProtect()

def create_app(config_class=Config):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static'),
        static_url_path='/static'
    )
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.worker import worker_bp
    from routes.employer import employer_bp
    from routes.jobs import jobs_bp
    from routes.applications import applications_bp
    from routes.api import api_bp

    # Exempt REST API blueprint from CSRF for API clients
    csrf.exempt(api_bp)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(worker_bp, url_prefix='/worker')
    app.register_blueprint(employer_bp, url_prefix='/employer')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Context processors
    @app.context_processor
    def inject_globals():
        from datetime import datetime, timezone
        return {
            'current_year': datetime.now(timezone.utc).year,
            'app_name': 'Local Job & Skill Matching Portal'
        }

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Ensure tables exist safely
    with app.app_context():
        # Only create instance folder if using local SQLite database
        if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
            try:
                os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
            except OSError:
                pass  # Read-only filesystem in serverless
        try:
            db.create_all()
        except Exception as err:
            app.logger.warning(f"Database table initialization notice: {err}")

    return app

# Top-level instance for WSGI / Vercel
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

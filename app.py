import os
from flask import Flask, render_template
from config import Config
from models import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.worker import worker_bp
    from routes.employer import employer_bp
    from routes.jobs import jobs_bp
    from routes.applications import applications_bp
    from routes.api import api_bp

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
        from datetime import datetime
        return {
            'current_year': datetime.utcnow().year,
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

    # Ensure tables exist
    with app.app_context():
        try:
            # Create instance folder if needed
            os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
            db.create_all()
        except Exception as err:
            app.logger.error(f"Database table initialization error: {err}")

    return app

# Top-level instance for WSGI / Vercel
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

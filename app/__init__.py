import os as _os

_gtk_path = r'C:\Program Files\GTK3-Runtime Win64\bin'
if _os.path.isdir(_gtk_path) and _gtk_path not in _os.environ.get('PATH', ''):
    _os.environ['PATH'] = _gtk_path + _os.pathsep + _os.environ.get('PATH', '')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from app.config import config_map

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    if config_name is None:
        import os
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    app.permanent_session_lifetime = app.config.get('PERMANENT_SESSION_LIFETIME', 7200)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu untuk mengakses halaman ini.'
    login_manager.login_message_category = 'warning'

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.guru import guru_bp
    from app.blueprints.siswa import siswa_bp
    from app.blueprints.laporan import laporan_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(guru_bp, url_prefix='/guru')
    app.register_blueprint(siswa_bp, url_prefix='/siswa')
    app.register_blueprint(laporan_bp, url_prefix='/laporan')

    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif current_user.is_guru():
                return redirect(url_for('guru.dashboard'))
            elif current_user.is_siswa():
                return redirect(url_for('siswa.dashboard'))
        return redirect(url_for('auth.login'))

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {
            'current_year': datetime.utcnow().year,
            'app_name': 'SIPNS',
        }

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    @app.before_request
    def make_session_permanent():
        from flask import session
        session.permanent = True

    from app.seed import register_commands
    register_commands(app)

    return app

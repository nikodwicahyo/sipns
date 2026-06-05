"""
Modul: __init__.py
Deskripsi: Application factory untuk SIPNS (Flask).

Memuat konfigurasi berdasarkan ``FLASK_ENV`` (development | production | testing),
mendaftarkan extension (db, migrate, login, csrf), mendaftarkan semua blueprint,
mendefinisikan error handler, global template context, dan CLI command.

Performance/cold-start optimizations:
- WhiteNoise dipasang di depan WSGI stack agar static file dilayani
  langsung dari middleware (sub-ms response) tanpa overhead Flask.
- /healthz TIDAK menyentuh DB — sub-10ms response, cocok untuk Render
  health check (default timeout 3s).
- /healthz/deep menyentuh DB (untuk uptime monitor eksternal).
- ``os.makedirs('logs', exist_ok=True)`` dipanggil SEBELUM extension apapun
  agar ProductionConfig.LOG_FILE tidak gagal tulis di cold start pertama.
"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from whitenoise import WhiteNoise

from app.config import config_map

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    """Application factory SIPNS.

    Args:
        config_name (str, optional): Salah satu key ``config_map``:
            ``'development'``, ``'production'``, ``'testing'``.
            Default: baca dari ``FLASK_ENV`` env var, fallback ``'development'``.

    Returns:
        Flask: Instance aplikasi Flask yang sudah terinisialisasi penuh.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Pastikan folder logs ada SEBELUM logger apapun menulis ke file.
    # Penting untuk ProductionConfig yang default-nya log ke logs/sipns.log.
    os.makedirs('logs', exist_ok=True)

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # WhiteNoise: serve static files dari WSGI middleware, lebih cepat
    # dari Flask's built-in static handler (penting untuk cold start
    # karena first request tidak perlu instantiate Flask static view).
    # ``root=app.static_folder`` -> otomatis mengarah ke app/static/.
    app.wsgi_app = WhiteNoise(
        app.wsgi_app,
        root=app.static_folder,
        prefix='static/',
        max_age=31536000 if not app.config.get('DEBUG') else 0,
    )

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
        from flask import redirect, url_for, render_template
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif current_user.is_guru():
                return redirect(url_for('guru.dashboard'))
            elif current_user.is_siswa():
                return redirect(url_for('siswa.dashboard'))
        return render_template('landing.html')

    @app.route('/healthz')
    def healthz():
        """Lightweight health check untuk Render (sub-10ms, no DB touch).

        Render health check default timeout 3s, jadi endpoint ini harus
        secepat mungkin. Jangan query DB di sini; pakai /healthz/deep.
        """
        return {'status': 'ok'}, 200

    @app.route('/healthz/deep')
    def healthz_deep():
        """Deep health check yang memverifikasi koneksi database.

        Cocok untuk uptime monitor eksternal (UptimeRobot, BetterStack).
        Return 503 jika DB tidak reachable.
        """
        from sqlalchemy import text
        try:
            db.session.execute(text('SELECT 1'))
            return {'status': 'ok', 'db': 'ok'}, 200
        except Exception as e:
            return {'status': 'degraded', 'db': 'error', 'error': str(e)[:200]}, 503

    from app.utils.time import format_jakarta, current_year_jakarta

    @app.template_filter('jakarta')
    def jakarta_filter(dt, fmt='%d/%m/%Y %H:%M'):
        return format_jakarta(dt, fmt)

    @app.context_processor
    def inject_globals():
        return {
            'current_year': current_year_jakarta(),
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

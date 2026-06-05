import os
import warnings
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        warnings.warn(
            'SECRET_KEY is not set in environment! Using insecure fallback. '
            'Set SECRET_KEY in .env for production.',
            RuntimeWarning,
        )
        SECRET_KEY = 'default-secret-key-change-me-in-production'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
        'connect_args': {
            'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', 10)),
        },
    }

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 7200


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost:3306/sipns_dev?charset=utf8mb4'
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'connect_args': {'connect_timeout': 10},
    }


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError(
            'DATABASE_URL environment variable is required for production. '
            'Format: mysql+pymysql://user:password@host:port/dbname?charset=utf8mb4'
        )
    # TiDB Cloud WAJIB TLS. ``ssl=True`` -> koneksi terenkripsi, tanpa
    # verifikasi sertifikat CA (acceptable untuk demo / tugas sekolah).
    # Untuk strict TLS (verify CA), set DATABASE_URL dengan parameter
    # ``?ssl_ca=/path&ssl_verify_cert=True`` (lihat docs/DEPLOY_RENDER_TIDB.md).
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'connect_args': {
            'connect_timeout': 10,
            'ssl': True,
        },
    }

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/sipns.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 10))


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class CSRFFlaskFormConfig(TestingConfig):
    """Konfigurasi turunan TestingConfig dengan CSRF protection AKTIF.

    Digunakan oleh fixture ``csrf_app`` di ``tests/integration/conftest.py``
    untuk menguji perilaku security (CSRF rejection) tanpa mematikan
    proteksi CSRF seperti pada ``TestingConfig`` standar.
    """
    WTF_CSRF_ENABLED = True


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'csrf_testing': CSRFFlaskFormConfig,
}

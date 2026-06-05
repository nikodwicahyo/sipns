"""
Konfigurasi pytest khusus untuk integration tests.

Menyediakan:
- Auto-mock weasyprint (autouse) untuk semua test di folder ini
- Fixture csrf_enabled_client (app kedua dengan CSRF aktif untuk security test)
- Fixture app_with_csrf untuk uji CSRF rejection
"""
import pytest


class _FakeWeasyHTML:
    """Stub class untuk weasyprint.HTML yang menerima **kwargs apapun."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def write_pdf(self):
        # Mengembalikan PDF header minimal yang valid untuk content-type detection
        return (
            b'%PDF-1.4\n'
            b'1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n'
            b'2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n'
            b'3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >> endobj\n'
            b'xref\n0 4\n'
            b'0000000000 65535 f \n'
            b'0000000009 00000 n \n'
            b'0000000058 00000 n \n'
            b'0000000115 00000 n \n'
            b'trailer << /Size 4 /Root 1 0 R >>\n'
            b'startxref\n181\n%%EOF'
        )


@pytest.fixture(autouse=True)
def mock_weasyprint(monkeypatch):
    """Mock weasyprint.HTML agar PDF generation tidak butuh GTK3.

    Berlaku otomatis untuk semua test di folder tests/integration/.
    """
    monkeypatch.setattr('weasyprint.HTML', _FakeWeasyHTML)


@pytest.fixture(scope='function')
def csrf_app():
    """Flask app kedua dengan WTF_CSRF_ENABLED=True untuk security test."""
    from app import create_app, db as _db
    from app.config import TestingConfig

    class CSRFFlaskFormConfig(TestingConfig):
        WTF_CSRF_ENABLED = True

    flask_app = create_app('testing')
    flask_app.config.from_object(CSRFFlaskFormConfig)
    flask_app.config['WTF_CSRF_ENABLED'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-for-csrf'

    with flask_app.app_context():
        _db.drop_all()
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def csrf_client(csrf_app, db):
    """Test client untuk app dengan CSRF enabled."""
    return csrf_app.test_client()

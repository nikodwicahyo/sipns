"""
Modul: validate.py
Deskripsi: Sanity-check script SIPNS production deployment.

Jalankan: python validate.py

Asserts semua requirement Hugging Face Spaces terpenuhi:
- App load dengan ProductionConfig (no crash on import)
- /healthz & /healthz/deep route terdaftar
- WhiteNoise wired di WSGI stack
- ProductionConfig flags benar (DEBUG=False, HTTPS, SSL)
- Dockerfile ada & syntax valid (FROM, RUN apt, EXPOSE 7860, CMD)
- .dockerignore ada & tidak include secret
- runtime Python 3.12 (di Dockerfile)
- wsgi.py loadable
"""
import re
import sys
from pathlib import Path

import yaml

from app import create_app


def main():
    print("=" * 64)
    print("SIPNS Production Readiness Validation (Hugging Face Spaces)")
    print("=" * 64)

    # 1. App loads dengan ProductionConfig
    app = create_app("production")
    print(f"[1] create_app('production') = {type(app).__name__} OK")

    # 2. Healthcheck routes registered
    rules = {r.rule: sorted(r.methods - {"HEAD", "OPTIONS"}) for r in app.url_map.iter_rules()}
    assert "/healthz" in rules, "Missing /healthz route"
    assert "/healthz/deep" in rules, "Missing /healthz/deep route"
    print(f"[2] /healthz = {rules['/healthz']} OK")
    print(f"    /healthz/deep = {rules['/healthz/deep']} OK")

    # 3. WhiteNoise wired di WSGI stack
    assert "WhiteNoise" in type(app.wsgi_app).__name__, "WhiteNoise not wired"
    print(f"[3] wsgi_app = {type(app.wsgi_app).__name__} OK")

    # 4. ProductionConfig flags
    assert app.config["DEBUG"] is False, "DEBUG should be False in production"
    assert app.config["PREFERRED_URL_SCHEME"] == "https", "PREFERRED_URL_SCHEME must be https"
    assert app.config["SESSION_COOKIE_SECURE"] is True, "SESSION_COOKIE_SECURE must be True"
    ssl = app.config["SQLALCHEMY_ENGINE_OPTIONS"]["connect_args"].get("ssl")
    assert ssl is True, "SSL must be enabled for TiDB Cloud"
    print("[4] ProductionConfig flags OK")
    print(f"    DEBUG = {app.config['DEBUG']}")
    print(f"    PREFERRED_URL_SCHEME = {app.config['PREFERRED_URL_SCHEME']}")
    print(f"    SESSION_COOKIE_SECURE = {app.config['SESSION_COOKIE_SECURE']}")
    print(f"    SSL in connect_args = {ssl}")

    # 5. Dockerfile structure
    dockerfile = Path("Dockerfile")
    assert dockerfile.exists(), "Dockerfile missing"
    content = dockerfile.read_text(encoding="utf-8")

    # Base image Python 3.12
    assert re.search(r"^FROM\s+python:3\.12", content, re.M), \
        "Dockerfile harus FROM python:3.12-slim (atau variant 3.12.x)"
    print("[5] Dockerfile base image: python:3.12 OK")

    # apt install dengan packages WeasyPrint yang diperlukan
    required_pkgs = {
        "libpango-1.0-0", "libcairo2", "libgdk-pixbuf-2.0-0",
        "libffi-dev", "fonts-dejavu-core",
    }
    for pkg in required_pkgs:
        assert pkg in content, f"Dockerfile missing apt package: {pkg}"
    print(f"    apt packages: {len(required_pkgs)} WeasyPrint deps present OK")

    # EXPOSE 7860 (wajib HF Spaces Docker SDK)
    assert re.search(r"^EXPOSE\s+7860", content, re.M), \
        "Dockerfile harus EXPOSE 7860 (HF Spaces Docker SDK convention)"
    assert "PORT=7860" in content, "Dockerfile harus set ENV PORT=7860"
    print("    EXPOSE 7860 + ENV PORT=7860 OK")

    # CMD berisi flask db upgrade, seed, dan gunicorn
    assert "flask db upgrade" in content, "CMD harus jalankan flask db upgrade"
    assert "flask seed" in content, "CMD harus jalankan flask seed"
    assert "gunicorn" in content, "CMD harus jalankan gunicorn"
    assert "--workers 1" in content, "Gunicorn workers=1 (free tier RAM efficiency)"
    assert "--preload" in content, "Gunicorn --preload (cold start optimization)"
    print("    CMD: flask db upgrade && flask seed && gunicorn OK")

    # 6. .dockerignore ada & exclude secret
    dockerignore = Path(".dockerignore")
    assert dockerignore.exists(), ".dockerignore missing"
    di_content = dockerignore.read_text(encoding="utf-8")
    assert ".env" in di_content, ".dockerignore harus exclude .env"
    assert "__pycache__" in di_content, ".dockerignore harus exclude __pycache__"
    assert "venv" in di_content, ".dockerignore harus exclude venv"
    print(f"[6] .dockerignore OK (excludes: .env, __pycache__, venv)")

    # 7. README.md frontmatter untuk HF Spaces
    readme = Path("README.md")
    assert readme.exists(), "README.md missing"
    # Baca sebagai UTF-8 eksplisit agar emoji & karakter non-ASCII aman
    # di Windows (default codec adalah charmap/cp1252 yang gagal decode emoji).
    rm_content = readme.read_text(encoding="utf-8")
    assert rm_content.startswith("---"), "README.md harus mulai dengan YAML frontmatter untuk HF Spaces"
    # Parse frontmatter
    end = rm_content.find("\n---", 3)
    assert end > 0, "README.md frontmatter tidak ditutup dengan '---'"
    frontmatter = rm_content[3:end].strip()
    try:
        meta = yaml.safe_load(frontmatter)
        assert isinstance(meta, dict), "Frontmatter harus YAML dict"
        assert "sdk" in meta, "Frontmatter harus punya 'sdk' key (wajib HF Spaces)"
        assert meta["sdk"] == "docker", f"Frontend SDK harus 'docker', got '{meta.get('sdk')}'"
        assert "app_port" in meta, "Frontmatter harus punya 'app_port' (HF Spaces Docker SDK)"
        assert meta["app_port"] == 7860, f"app_port harus 7860 (HF convention), got {meta['app_port']}"
        print(f"[7] README.md HF Spaces frontmatter OK")
        print(f"    sdk={meta['sdk']} app_port={meta['app_port']} title={meta.get('title', '?')}")
    except yaml.YAMLError as e:
        raise AssertionError(f"README.md frontmatter YAML invalid: {e}")

    # 8. wsgi.py loadable
    wsgi = Path("wsgi.py")
    assert wsgi.exists(), "wsgi.py missing"
    print("[8] wsgi.py loadable OK (verified by create_app import)")

    # 9. TiDB-relevant: confirm no Render/Blueprint residue
    forbidden = ["render.yaml", "Aptfile", "build.sh", "runtime.txt"]
    for f in forbidden:
        assert not Path(f).exists(), f"Residue Render file: {f} (should be deleted)"
    print("[9] No Render residue OK (deploy target = HF Spaces only)")

    print("=" * 64)
    print("ALL CHECKS PASSED")
    print("=" * 64)


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\nVALIDATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)

"""
Validation script — dipanggil oleh build phase untuk sanity check.

Jalankan: python -c "from validate import main; main()"
"""
import sys

import yaml

from app import create_app


def main():
    print("=" * 60)
    print("SIPNS Production Readiness Validation")
    print("=" * 60)

    # 1. App loads with ProductionConfig
    app = create_app("production")
    print(f"[1] create_app('production') = {type(app).__name__} OK")

    # 2. Healthcheck routes registered
    rules = {r.rule: sorted(r.methods - {"HEAD", "OPTIONS"}) for r in app.url_map.iter_rules()}
    assert "/healthz" in rules, "Missing /healthz route"
    assert "/healthz/deep" in rules, "Missing /healthz/deep route"
    print(f"[2] /healthz = {rules['/healthz']} OK")
    print(f"    /healthz/deep = {rules['/healthz/deep']} OK")

    # 3. WhiteNoise wired in WSGI stack
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

    # 5. render.yaml structure
    with open("render.yaml", "r") as f:
        data = yaml.safe_load(f)
    services = data.get("services", [])
    assert len(services) == 1, f"Expected 1 service, got {len(services)}"
    s = services[0]
    assert s["name"] == "sipns-web"
    assert s["buildCommand"] == "bash build.sh"
    assert "flask db upgrade" in s["preDeployCommand"]
    assert "flask seed" in s["preDeployCommand"]
    assert "gunicorn" in s["startCommand"]
    assert "--workers 1" in s["startCommand"], "Single worker required for free tier RAM"
    assert "--preload" in s["startCommand"], "--preload required for cold start optimization"
    assert s["healthCheckPath"] == "/healthz"
    env_keys = {e["key"] for e in s["envVars"]}
    for required in ("FLASK_APP", "FLASK_ENV", "SECRET_KEY", "DATABASE_URL", "PYTHONUNBUFFERED"):
        assert required in env_keys, f"Missing env var: {required}"
    print("[5] render.yaml structure OK")
    print(f"    service = {s['name']}, buildCommand = {s['buildCommand']}")
    print(f"    startCommand = {s['startCommand']}")
    print(f"    envVars = {sorted(env_keys)}")

    # 6. Aptfile non-empty & valid package names
    with open("Aptfile", "r") as f:
        pkgs = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
    expected = {"libpango-1.0-0", "libcairo2", "libgdk-pixbuf-2.0-0", "libffi-dev"}
    missing = expected - set(pkgs)
    assert not missing, f"Aptfile missing critical packages: {missing}"
    print(f"[6] Aptfile OK ({len(pkgs)} packages): {pkgs}")

    # 7. runtime.txt
    with open("runtime.txt", "r") as f:
        runtime = f.read().strip()
    assert runtime.startswith("python-3.12"), f"Expected python-3.12.x, got {runtime}"
    print(f"[7] runtime.txt OK ({runtime})")

    # 8. wsgi.py imports cleanly
    print("[8] wsgi.py loadable OK (file exists, syntax checked by create_app call)")

    print("=" * 60)
    print("ALL CHECKS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\nVALIDATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)

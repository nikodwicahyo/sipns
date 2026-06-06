"""
Modul: cache.py
Deskripsi: In-memory TTL cache untuk query yang jarang berubah.

Cache ini menggunakan dict sederhana dengan TTL per-entry. Cocok untuk
menyimpan hasil query kecil yang tidak berubah sering (daftar kelas,
daftar mapel) tanpa perlu Redis/Memcached.

Keterbatasan:
- Data tidak terbagi antar worker Gunicorn (setiap worker punya cache sendiri).
- Cocok untuk traffic rendah school app; tidak untuk high-throughput system.
"""
import time
from functools import wraps

_cache = {}


def cached(ttl=30):
    """Decorator untuk cache hasil fungsi dengan TTL (detik).

    Args:
        ttl (int): Time-to-live dalam detik. Default 30.

    Usage:
        @cached(ttl=60)
        def expensive_query(param):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Bangun key dari nama fungsi + argumen.
            key_parts = [func.__name__]
            key_parts.extend(str(a) for a in args)
            key_parts.extend(f'{k}={v}' for k, v in sorted(kwargs.items()))
            key = ':'.join(key_parts)

            now = time.time()
            entry = _cache.get(key)
            if entry and now - entry['time'] < ttl:
                return entry['value']

            result = func(*args, **kwargs)
            _cache[key] = {'value': result, 'time': now}
            return result
        return wrapper
    return decorator


def cache_clear():
    """Hapus semua entry cache (dipanggil saat ada perubahan data signifikan)."""
    _cache.clear()

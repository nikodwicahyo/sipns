from app import db
from datetime import datetime


class Siswa(db.Model):
    __tablename__ = 'siswa'

    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(20), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    nilai = db.relationship('Nilai', backref='siswa', lazy='dynamic',
                            foreign_keys='Nilai.siswa_id')
    user = db.relationship('User', backref='siswa', uselist=False,
                           foreign_keys='User.siswa_id')

    def __repr__(self):
        return f'<Siswa {self.nis}: {self.nama}>'

    def nilai_akhir_all(self):
        return [n.nilai_akhir for n in self.nilai if n.nilai_akhir is not None]

    def rata_rata_nilai(self):
        nilai_list = self.nilai_akhir_all()
        return round(sum(nilai_list) / len(nilai_list), 2) if nilai_list else 0.0

    def status_kelulusan_global(self):
        nilai_records = self.nilai.filter_by(is_locked=True).all()
        if not nilai_records:
            return 'Belum Ada Nilai'
        return 'Lulus' if all(n.status_lulus for n in nilai_records) else 'Tidak Lulus'

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'nis': self.nis,
            'nama': self.nama,
            'kelas': self.kelas,
            'rata_rata': self.rata_rata_nilai(),
            'status': self.status_kelulusan_global(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def cari_by_nis(cls, nis):
        return cls.query.filter_by(nis=nis, deleted_at=None).first()

    @classmethod
    def daftar_kelas(cls):
        result = db.session.query(cls.kelas).filter(
            cls.deleted_at.is_(None)
        ).distinct().order_by(cls.kelas).all()
        return [r[0] for r in result]

from app import db
from datetime import datetime
from app.services.nilai_service import hitung_nilai_akhir, tentukan_status_kelulusan


class Nilai(db.Model):
    __tablename__ = 'nilai'

    id = db.Column(db.Integer, primary_key=True)
    siswa_id = db.Column(db.Integer, db.ForeignKey('siswa.id'), nullable=False)
    guru_id = db.Column(db.Integer, db.ForeignKey('guru.id'), nullable=False)
    mata_pelajaran = db.Column(db.String(100), nullable=False)
    nilai_tugas = db.Column(db.Numeric(5, 2), nullable=False)
    nilai_uts = db.Column(db.Numeric(5, 2), nullable=False)
    nilai_uas = db.Column(db.Numeric(5, 2), nullable=False)
    nilai_akhir = db.Column(db.Numeric(5, 2), nullable=True)
    status_lulus = db.Column(db.Boolean, nullable=True)
    is_locked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('siswa_id', 'mata_pelajaran', name='uq_siswa_mapel'),
    )

    def __repr__(self):
        return f'<Nilai siswa_id={self.siswa_id} mapel={self.mata_pelajaran} akhir={self.nilai_akhir}>'

    def hitung_dan_simpan(self):
        self.nilai_akhir = hitung_nilai_akhir(
            float(self.nilai_tugas),
            float(self.nilai_uts),
            float(self.nilai_uas)
        )
        status = tentukan_status_kelulusan(float(self.nilai_akhir))
        self.status_lulus = status['lulus']

    def lock(self):
        if not self.is_locked:
            self.is_locked = True

    def unlock(self):
        self.is_locked = False

    def get_detail_kalkulasi(self):
        return {
            'tugas': {'nilai': float(self.nilai_tugas), 'bobot': 30, 'kontribusi': round(float(self.nilai_tugas) * 0.30, 2)},
            'uts': {'nilai': float(self.nilai_uts), 'bobot': 30, 'kontribusi': round(float(self.nilai_uts) * 0.30, 2)},
            'uas': {'nilai': float(self.nilai_uas), 'bobot': 40, 'kontribusi': round(float(self.nilai_uas) * 0.40, 2)},
            'nilai_akhir': float(self.nilai_akhir),
            'status_lulus': self.status_lulus,
            'kkm': 70,
        }

    def to_dict(self):
        return {
            'id': self.id,
            'mata_pelajaran': self.mata_pelajaran,
            'nilai_tugas': float(self.nilai_tugas),
            'nilai_uts': float(self.nilai_uts),
            'nilai_uas': float(self.nilai_uas),
            'nilai_akhir': float(self.nilai_akhir) if self.nilai_akhir else None,
            'status_lulus': self.status_lulus,
            'is_locked': self.is_locked,
        }

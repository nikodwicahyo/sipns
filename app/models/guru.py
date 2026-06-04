from app import db
from datetime import datetime


class Guru(db.Model):
    __tablename__ = 'guru'

    id = db.Column(db.Integer, primary_key=True)
    id_guru = db.Column(db.String(20), unique=True, nullable=False)
    nama_guru = db.Column(db.String(100), nullable=False)
    mata_pelajaran = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    nilai_diinput = db.relationship('Nilai', backref='guru', lazy='dynamic',
                                     foreign_keys='Nilai.guru_id')
    user = db.relationship('User', backref='guru', uselist=False,
                           foreign_keys='User.guru_id')

    def __repr__(self):
        return f'<Guru {self.id_guru}: {self.nama_guru}>'

    def get_siswa_diajar(self):
        from app.models.siswa import Siswa
        siswa_ids = db.session.query(Nilai.siswa_id).filter_by(
            guru_id=self.id
        ).distinct().all()
        return Siswa.query.filter(
            Siswa.id.in_([s[0] for s in siswa_ids])
        ).all()

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'id_guru': self.id_guru,
            'nama_guru': self.nama_guru,
            'mata_pelajaran': self.mata_pelajaran,
        }

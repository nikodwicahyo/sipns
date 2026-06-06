"""add composite indexes and is_locked nullable fix

Revision ID: f7g8h9i0j1k2
Revises: a1b2c3d4e5f6
Create Date: 2026-06-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = 'f7g8h9i0j1k2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_siswa_deleted_at_kelas', 'siswa', ['deleted_at', 'kelas'])
    op.create_index('ix_nilai_guru_id_is_locked', 'nilai', ['guru_id', 'is_locked'])
    op.create_index('ix_nilai_siswa_id_status_lulus', 'nilai', ['siswa_id', 'status_lulus'])
    op.create_index('ix_nilai_guru_id_mata_pelajaran', 'nilai', ['guru_id', 'mata_pelajaran'])
    op.create_index('ix_nilai_siswa_id_nilai_akhir', 'nilai', ['siswa_id', 'nilai_akhir'])
    op.create_index('ix_audit_log_user_id_created_at', 'audit_log', ['user_id', 'created_at'])
    op.create_index('ix_nilai_is_locked', 'nilai', ['is_locked'])
    op.alter_column('nilai', 'is_locked',
                    existing_type=mysql.TINYINT(display_width=1),
                    nullable=False)


def downgrade():
    op.alter_column('nilai', 'is_locked',
                    existing_type=mysql.TINYINT(display_width=1),
                    nullable=True)
    op.drop_index('ix_nilai_is_locked', table_name='nilai')
    op.drop_index('ix_audit_log_user_id_created_at', table_name='audit_log')
    op.drop_index('ix_nilai_siswa_id_nilai_akhir', table_name='nilai')
    op.drop_index('ix_nilai_guru_id_mata_pelajaran', table_name='nilai')
    op.drop_index('ix_nilai_siswa_id_status_lulus', table_name='nilai')
    op.drop_index('ix_nilai_guru_id_is_locked', table_name='nilai')
    op.drop_index('ix_siswa_deleted_at_kelas', table_name='siswa')

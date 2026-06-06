"""Add performance indexes for FK columns and filtered columns

Revision ID: a1b2c3d4e5f6
Revises: 85cddd831f8c
Create Date: 2026-06-05 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '85cddd831f8c'
branch_labels = None
depends_on = None


def upgrade():
    # === users table ===
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_siswa_id', 'users', ['siswa_id'])
    op.create_index('ix_users_guru_id', 'users', ['guru_id'])

    # === guru table ===
    op.create_index('ix_guru_id_guru', 'guru', ['id_guru'])
    op.create_index('ix_guru_mata_pelajaran', 'guru', ['mata_pelajaran'])
    op.create_index('ix_guru_deleted_at', 'guru', ['deleted_at'])

    # === siswa table ===
    op.create_index('ix_siswa_deleted_at', 'siswa', ['deleted_at'])

    # === nilai table ===
    op.create_index('ix_nilai_siswa_id', 'nilai', ['siswa_id'])
    op.create_index('ix_nilai_guru_id', 'nilai', ['guru_id'])
    op.create_index('ix_nilai_mata_pelajaran', 'nilai', ['mata_pelajaran'])
    op.create_index('ix_nilai_status_lulus', 'nilai', ['status_lulus'])
    op.create_index('ix_nilai_is_locked', 'nilai', ['is_locked'])
    op.create_index('ix_nilai_created_at', 'nilai', ['created_at'])

    # === audit_log table ===
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])
    op.create_index('ix_audit_log_created_at', 'audit_log', ['created_at'])


def downgrade():
    op.drop_index('ix_audit_log_created_at')
    op.drop_index('ix_audit_log_action')
    op.drop_index('ix_audit_log_user_id')
    op.drop_index('ix_nilai_created_at')
    op.drop_index('ix_nilai_is_locked')
    op.drop_index('ix_nilai_status_lulus')
    op.drop_index('ix_nilai_mata_pelajaran')
    op.drop_index('ix_nilai_guru_id')
    op.drop_index('ix_nilai_siswa_id')
    op.drop_index('ix_siswa_deleted_at')
    op.drop_index('ix_guru_deleted_at')
    op.drop_index('ix_guru_mata_pelajaran')
    op.drop_index('ix_guru_id_guru')
    op.drop_index('ix_users_guru_id')
    op.drop_index('ix_users_siswa_id')
    op.drop_index('ix_users_is_active')
    op.drop_index('ix_users_role')

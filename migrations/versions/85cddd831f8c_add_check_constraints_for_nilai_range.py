"""Add CHECK constraints for nilai range

Revision ID: 85cddd831f8c
Revises: 9472af43883e
Create Date: 2026-06-04 17:54:32.870484

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85cddd831f8c'
down_revision = '9472af43883e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        'ck_nilai_tugas_range',
        'nilai',
        'nilai_tugas >= 0 AND nilai_tugas <= 100',
    )
    op.create_check_constraint(
        'ck_nilai_uts_range',
        'nilai',
        'nilai_uts >= 0 AND nilai_uts <= 100',
    )
    op.create_check_constraint(
        'ck_nilai_uas_range',
        'nilai',
        'nilai_uas >= 0 AND nilai_uas <= 100',
    )
    op.create_check_constraint(
        'ck_nilai_akhir_range',
        'nilai',
        'nilai_akhir >= 0 AND nilai_akhir <= 100',
    )


def downgrade():
    op.drop_constraint('ck_nilai_akhir_range', 'nilai', type_='check')
    op.drop_constraint('ck_nilai_uas_range', 'nilai', type_='check')
    op.drop_constraint('ck_nilai_uts_range', 'nilai', type_='check')
    op.drop_constraint('ck_nilai_tugas_range', 'nilai', type_='check')

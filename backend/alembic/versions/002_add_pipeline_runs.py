"""002_add_pipeline_runs

Revision ID: 002_add_pipeline_runs
Revises: 001_initial_schema
Create Date: 2026-10-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_add_pipeline_runs'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. pipeline_runs table
    op.create_table(
        'pipeline_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('character_id', sa.String(length=36), sa.ForeignKey('characters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('character_version', sa.Integer(), nullable=False),
        sa.Column('user_prompt', sa.Text(), nullable=False),
        sa.Column('blueprint_json', sa.Text(), nullable=False),
        sa.Column('total_scenes', sa.Integer(), nullable=False),
        sa.Column('completed_scenes', sa.Integer(), server_default='0', nullable=False),
        sa.Column('status', sa.String(length=30), server_default='PLANNED', nullable=False),
        sa.Column('created_at', sa.String(length=32), nullable=True),
        sa.Column('updated_at', sa.String(length=32), nullable=True),
    )
    op.create_index('idx_pipeline_runs_character_id', 'pipeline_runs', ['character_id'])
    op.create_index('idx_pipeline_runs_status', 'pipeline_runs', ['status'])

    # 2. Add columns to generation_jobs
    with op.batch_alter_table('generation_jobs') as batch_op:
        batch_op.add_column(sa.Column('pipeline_run_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('scene_number', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('camera_angle', sa.String(length=50), nullable=True))
        batch_op.create_foreign_key('fk_generation_jobs_pipeline_run_id', 'pipeline_runs', ['pipeline_run_id'], ['id'], ondelete='SET NULL')
        batch_op.create_index('idx_generation_jobs_pipeline_run', ['pipeline_run_id'])

def downgrade() -> None:
    with op.batch_alter_table('generation_jobs') as batch_op:
        batch_op.drop_constraint('fk_generation_jobs_pipeline_run_id', type_='foreignkey')
        batch_op.drop_index('idx_generation_jobs_pipeline_run')
        batch_op.drop_column('camera_angle')
        batch_op.drop_column('scene_number')
        batch_op.drop_column('pipeline_run_id')

    op.drop_index('idx_pipeline_runs_status', table_name='pipeline_runs')
    op.drop_index('idx_pipeline_runs_character_id', table_name='pipeline_runs')
    op.drop_table('pipeline_runs')

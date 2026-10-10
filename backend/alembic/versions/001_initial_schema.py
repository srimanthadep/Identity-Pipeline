"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-10

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. characters
    op.create_table(
        'characters',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('character_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('physical_traits', sa.Text(), server_default='{}', nullable=True),
        sa.Column('gender', sa.String(length=30), nullable=True),
        sa.Column('age_range', sa.String(length=30), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.String(length=32), nullable=True),
        sa.Column('updated_at', sa.String(length=32), nullable=True),
    )
    op.create_index('idx_characters_char_id', 'characters', ['character_id'])

    # 2. character_assets
    op.create_table(
        'character_assets',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('character_id', sa.String(length=36), sa.ForeignKey('characters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('storage_uri', sa.String(length=500), nullable=False),
        sa.Column('mime_type', sa.String(length=50), server_default='image/png', nullable=True),
        sa.Column('is_canonical', sa.Integer(), server_default='0', nullable=False),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.String(length=32), nullable=True),
    )
    op.create_index('idx_character_assets_char', 'character_assets', ['character_id'])

    # 3. generation_jobs
    op.create_table(
        'generation_jobs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('character_id', sa.String(length=36), sa.ForeignKey('characters.id'), nullable=False),
        sa.Column('character_version', sa.Integer(), nullable=False),
        sa.Column('reference_asset_id', sa.String(length=36), sa.ForeignKey('character_assets.id'), nullable=False),
        sa.Column('reference_asset_version', sa.Integer(), nullable=False),
        sa.Column('reference_asset_uri', sa.String(length=500), nullable=False),
        sa.Column('scene_prompt', sa.Text(), nullable=False),
        sa.Column('identity_block', sa.Text(), nullable=False),
        sa.Column('video_blueprint', sa.Text(), nullable=False),
        sa.Column('adapter_type', sa.String(length=50), server_default='simulated', nullable=False),
        sa.Column('status', sa.String(length=30), server_default='PENDING', nullable=False),
        sa.Column('output_uri', sa.String(length=500), nullable=True),
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('max_retries', sa.Integer(), server_default='3', nullable=False),
        sa.Column('adapter_config', sa.Text(), server_default='{}', nullable=True),
        sa.Column('seed', sa.Integer(), nullable=True),
        sa.Column('is_simulated', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.String(length=32), nullable=True),
        sa.Column('updated_at', sa.String(length=32), nullable=True),
    )
    op.create_index('idx_generation_jobs_char', 'generation_jobs', ['character_id'])
    op.create_index('idx_generation_jobs_status', 'generation_jobs', ['status'])

    # 4. qa_reports
    op.create_table(
        'qa_reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('job_id', sa.String(length=36), sa.ForeignKey('generation_jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('character_id', sa.String(length=36), sa.ForeignKey('characters.id'), nullable=False),
        sa.Column('identity_score', sa.Float(), nullable=True),
        sa.Column('appearance_score', sa.Float(), nullable=True),
        sa.Column('decision', sa.String(length=30), nullable=False),
        sa.Column('metrics', sa.Text(), server_default='{}', nullable=True),
        sa.Column('reference_asset_uri', sa.String(length=500), nullable=True),
        sa.Column('evaluated_asset_uri', sa.String(length=500), nullable=True),
        sa.Column('is_simulated', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.String(length=32), nullable=True),
    )
    op.create_index('idx_qa_reports_job', 'qa_reports', ['job_id'])

def downgrade() -> None:
    op.drop_table('qa_reports')
    op.drop_table('generation_jobs')
    op.drop_table('character_assets')
    op.drop_table('characters')

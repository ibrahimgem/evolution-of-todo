"""rename metadata column to meta in conversation table

Revision ID: 002
Revises: 001
Create Date: 2026-01-04

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename 'metadata' column to 'meta' in conversation table
    op.alter_column('conversation', 'metadata', new_column_name='meta')


def downgrade() -> None:
    # Rename 'meta' column back to 'metadata' in conversation table
    op.alter_column('conversation', 'meta', new_column_name='metadata')

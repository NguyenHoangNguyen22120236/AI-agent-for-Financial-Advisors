"""Add embedding column to emails

Revision ID: 677e58ac8e82
Revises: 8a05572798ea
Create Date: 2025-06-22 14:03:15.104088

"""
from typing import Sequence, Union
from pgvector.sqlalchemy import Vector

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '677e58ac8e82'
down_revision: Union[str, Sequence[str], None] = '8a05572798ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('emails', sa.Column('embedding', Vector(1536), nullable=True))

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('emails', 'embedding')
    # ### end Alembic commands ###

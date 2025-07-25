"""Update

Revision ID: 2695dd7de985
Revises: 69fbc55f6586
Create Date: 2025-06-23 09:49:09.516718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2695dd7de985'
down_revision: Union[str, Sequence[str], None] = '69fbc55f6586'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('external_reference', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'external_reference')
    # ### end Alembic commands ###

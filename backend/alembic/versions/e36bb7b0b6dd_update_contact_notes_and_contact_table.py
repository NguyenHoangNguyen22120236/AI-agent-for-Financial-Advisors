"""Update contact_notes and contact table

Revision ID: e36bb7b0b6dd
Revises: 5e4b22877fff
Create Date: 2025-06-23 07:12:28.370143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e36bb7b0b6dd'
down_revision: Union[str, Sequence[str], None] = '5e4b22877fff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

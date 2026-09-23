"""enable pgvector extension

Revision ID: 654094b659d2
Revises: 7f7304112143
Create Date: 2026-09-23 10:26:19.770951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '654094b659d2'
down_revision: Union[str, Sequence[str], None] = '7f7304112143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS vector")

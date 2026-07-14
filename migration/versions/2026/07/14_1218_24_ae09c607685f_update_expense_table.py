"""Update expense table

Revision ID: ae09c607685f
Revises: d7ee44bccff8
Create Date: 2026-07-14 12:18:24.436782

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ae09c607685f"
down_revision: Union[str, Sequence[str], None] = "d7ee44bccff8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "expenses",
        sa.Column(
            "is_harmful", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )


def downgrade() -> None:
    op.drop_column("expenses", "is_harmful")

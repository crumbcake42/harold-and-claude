"""audit metadata columns

Revision ID: 162ac1ebc916
Revises: 6dd5906ef088
Create Date: 2026-05-21 09:40:03.969037

Materializes ADR-0072's four audit-metadata columns -- created_at /
created_by / updated_at / updated_by -- on Contract and User (Step
2.2b-C-2). The columns are a dispatcher-maintained read projection
(ADR-0075); going forward the pipeline stamps them on every command.

Contract is empty, so its four columns add as NOT NULL directly. The user
table holds the bootstrap superadmin (one row), so its columns add
nullable, the row is backfilled, then NOT NULL is enforced. The backfill is
the honest reconstruction available: the bootstrap user predates the
Command pipeline and has no command_audit_log row, so created_at is taken
from the earliest UserRole.granted_at (the bootstrap grant, written in the
same transaction as the user) and created_by / updated_by from the user's
own id -- self-attributed, exactly as bootstrap_admin does for
UserRole.granted_by.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '162ac1ebc916'
down_revision: Union[str, Sequence[str], None] = '6dd5906ef088'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # contract -- empty table, NOT NULL columns add directly.
    op.add_column('contract', sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.add_column('contract', sa.Column('created_by', sa.Uuid(), nullable=False))
    op.add_column('contract', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False))
    op.add_column('contract', sa.Column('updated_by', sa.Uuid(), nullable=False))

    # user -- existing rows: add nullable, backfill, then enforce NOT NULL.
    op.add_column('user', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user', sa.Column('created_by', sa.Uuid(), nullable=True))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user', sa.Column('updated_by', sa.Uuid(), nullable=True))
    op.execute(
        """
        UPDATE "user" SET
            created_at = COALESCE(
                (SELECT MIN(granted_at) FROM user_role WHERE user_role.user_id = "user".id),
                now()
            ),
            updated_at = COALESCE(
                (SELECT MIN(granted_at) FROM user_role WHERE user_role.user_id = "user".id),
                now()
            ),
            created_by = "user".id,
            updated_by = "user".id
        """
    )
    op.alter_column('user', 'created_at', nullable=False)
    op.alter_column('user', 'created_by', nullable=False)
    op.alter_column('user', 'updated_at', nullable=False)
    op.alter_column('user', 'updated_by', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'updated_by')
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_by')
    op.drop_column('user', 'created_at')
    op.drop_column('contract', 'updated_by')
    op.drop_column('contract', 'updated_at')
    op.drop_column('contract', 'created_by')
    op.drop_column('contract', 'created_at')

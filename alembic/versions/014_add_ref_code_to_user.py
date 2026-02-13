"""014_add_ref_code_to_user

Revision ID: 014_ref_code
Revises: 1b254e7d2c0a
Create Date: 2026-02-13

"""

from alembic import op
import sqlalchemy as sa
import uuid

revision = "014_ref_code"
down_revision = "1b254e7d2c0a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("ref_code", sa.String(32), nullable=True),
    )
    op.create_index(op.f("ix_users_ref_code"), "users", ["ref_code"], unique=True)

    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM users WHERE ref_code IS NULL"))
    rows = result.fetchall()
    for (user_id,) in rows:
        code = uuid.uuid4().hex
        conn.execute(
            sa.text("UPDATE users SET ref_code = :code WHERE id = :id"),
            {"code": code, "id": user_id},
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_users_ref_code"), table_name="users")
    op.drop_column("users", "ref_code")

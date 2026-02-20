"""015_add_results_table

Revision ID: 2c9a91f0d8b1
Revises: 014_ref_code
Create Date: 2026-02-20 18:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c9a91f0d8b1"
down_revision = "014_ref_code"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("theme_id", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["theme_id"], ["themes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_results_user_id"), "results", ["user_id"], unique=False)
    op.create_index(op.f("ix_results_theme_id"), "results", ["theme_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_results_theme_id"), table_name="results")
    op.drop_index(op.f("ix_results_user_id"), table_name="results")
    op.drop_table("results")

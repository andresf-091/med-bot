"""005_themes_items_m2m

Revision ID: 005_m2m
Revises: 0d7ac87f86e0
Create Date: 2026-02-04

"""

from alembic import op
import sqlalchemy as sa


revision = "005_m2m"
down_revision = "0d7ac87f86e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "theme_items",
        sa.Column("theme_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["theme_id"], ["themes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("theme_id", "item_id"),
    )
    op.create_index(
        op.f("ix_theme_items_item_id"), "theme_items", ["item_id"], unique=False
    )
    op.create_index(
        op.f("ix_theme_items_theme_id"), "theme_items", ["theme_id"], unique=False
    )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            'INSERT INTO theme_items (theme_id, item_id, "order") '
            "SELECT theme_id, id, \"order\" FROM items"
        )
    )

    op.drop_constraint("uq_item_theme_order_type", "items", type_="unique")
    op.drop_index(op.f("ix_items_theme_id"), table_name="items")
    op.drop_column("items", "theme_id")
    op.drop_column("items", "order")


def downgrade() -> None:
    op.add_column(
        "items",
        sa.Column("theme_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "items",
        sa.Column("order", sa.Integer(), nullable=True),
    )

    conn = op.get_bind()
    conn.execute(
        sa.text("""
            UPDATE items SET theme_id = t.theme_id, "order" = t."order"
            FROM (
                SELECT DISTINCT ON (item_id) item_id, theme_id, "order"
                FROM theme_items ORDER BY item_id, "order"
            ) AS t
            WHERE items.id = t.item_id
        """)
    )

    op.alter_column(
        "items",
        "theme_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "items",
        "order",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "items_theme_id_fkey",
        "items",
        "themes",
        ["theme_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_items_theme_id"), "items", ["theme_id"], unique=False)
    op.create_unique_constraint(
        "uq_item_theme_order_type", "items", ["theme_id", "order", "type"]
    )

    op.drop_index(op.f("ix_theme_items_theme_id"), table_name="theme_items")
    op.drop_index(op.f("ix_theme_items_item_id"), table_name="theme_items")
    op.drop_table("theme_items")

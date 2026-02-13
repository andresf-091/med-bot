"""initial migration

Revision ID: 001_initial
Revises:
Create Date: 2026-01-25 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    enum_types = {
        "userrole": ["USER", "ADMIN"],
        "usersubscription": ["PREMIUM", "FREE", "TRIAL", "EXPIRED"],
        "userlanguage": ["RU", "EN"],
        "contenttype": ["THEORY", "QUESTION", "TASK", "SLIDE"],
    }

    for enum_name, enum_values in enum_types.items():
        result = conn.execute(
            sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :name)"),
            {"name": enum_name},
        )
        exists = result.scalar()
        if not exists:
            enum_values_str = "', '".join(enum_values)
            conn.execute(
                sa.text(f"CREATE TYPE {enum_name} AS ENUM ('{enum_values_str}')")
            )
            conn.commit()

    userrole_enum = postgresql.ENUM("USER", "ADMIN", name="userrole", create_type=False)
    usersubscription_enum = postgresql.ENUM(
        "PREMIUM",
        "FREE",
        "TRIAL",
        "EXPIRED",
        name="usersubscription",
        create_type=False,
    )
    userlanguage_enum = postgresql.ENUM(
        "RU", "EN", name="userlanguage", create_type=False
    )
    contenttype_enum = postgresql.ENUM(
        "THEORY", "QUESTION", "TASK", "SLIDE", name="contenttype", create_type=False
    )

    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')"
        )
    )
    users_exists = result.scalar()

    if not users_exists:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("tg_id", sa.Integer(), nullable=False),
            sa.Column("role", userrole_enum, nullable=False),
            sa.Column("subscription", usersubscription_enum, nullable=False),
            sa.Column("language", userlanguage_enum, nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tg_id", name="uq_user_tg_id"),
        )
        op.create_index(op.f("ix_users_tg_id"), "users", ["tg_id"], unique=False)

    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'themes')"
        )
    )
    themes_exists = result.scalar()

    if not themes_exists:
        op.create_table(
            "themes",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("order", sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'items')"
        )
    )
    items_exists = result.scalar()

    if not items_exists:
        op.create_table(
            "items",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("type", contenttype_enum, nullable=False),
            sa.Column("theme_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=500), nullable=True),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("explanation", sa.Text(), nullable=True),
            sa.Column("options", sa.JSON(), nullable=True),
            sa.Column("difficulty", sa.Integer(), nullable=True),
            sa.Column("other", sa.JSON(), nullable=True),
            sa.Column("order", sa.Integer(), nullable=False),
            sa.Column("relevant", sa.Boolean(), nullable=False),
            sa.ForeignKeyConstraint(["theme_id"], ["themes.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.CheckConstraint(
                "difficulty >= 1 AND difficulty <= 5", name="ck_item_difficulty_range"
            ),
            sa.UniqueConstraint(
                "theme_id", "order", "type", name="uq_item_theme_order_type"
            ),
        )
        op.create_index(op.f("ix_items_theme_id"), "items", ["theme_id"], unique=False)
        op.create_index(op.f("ix_items_type"), "items", ["type"], unique=False)

    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'images')"
        )
    )
    images_exists = result.scalar()

    if not images_exists:
        op.create_table(
            "images",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("content", sa.String(length=500), nullable=False),
            sa.Column("caption", sa.Text(), nullable=True),
            sa.Column("item_id", sa.Integer(), nullable=False),
            sa.Column("order", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_images_item_id"), "images", ["item_id"], unique=False)

    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_favorite_theory')"
        )
    )
    uft_exists = result.scalar()

    if not uft_exists:
        op.create_table(
            "user_favorite_theory",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("item_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "item_id", name="uq_user_favorite_theory"),
        )
        op.create_index(
            op.f("ix_user_favorite_theory_item_id"),
            "user_favorite_theory",
            ["item_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_user_favorite_theory_user_id"),
            "user_favorite_theory",
            ["user_id"],
            unique=False,
        )

    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_favorite_exam')"
        )
    )
    ufe_exists = result.scalar()

    if not ufe_exists:
        op.create_table(
            "user_favorite_exam",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("item_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "item_id", name="uq_user_favorite_exam"),
        )
        op.create_index(
            op.f("ix_user_favorite_exam_item_id"),
            "user_favorite_exam",
            ["item_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_user_favorite_exam_user_id"),
            "user_favorite_exam",
            ["user_id"],
            unique=False,
        )

    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_favorite_task')"
        )
    )
    uftask_exists = result.scalar()

    if not uftask_exists:
        op.create_table(
            "user_favorite_task",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("item_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "item_id", name="uq_user_favorite_task"),
        )
        op.create_index(
            op.f("ix_user_favorite_task_item_id"),
            "user_favorite_task",
            ["item_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_user_favorite_task_user_id"),
            "user_favorite_task",
            ["user_id"],
            unique=False,
        )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_favorite_task_user_id"), table_name="user_favorite_task"
    )
    op.drop_index(
        op.f("ix_user_favorite_task_item_id"), table_name="user_favorite_task"
    )
    op.drop_table("user_favorite_task")
    op.drop_index(
        op.f("ix_user_favorite_exam_user_id"), table_name="user_favorite_exam"
    )
    op.drop_index(
        op.f("ix_user_favorite_exam_item_id"), table_name="user_favorite_exam"
    )
    op.drop_table("user_favorite_exam")
    op.drop_index(
        op.f("ix_user_favorite_theory_user_id"), table_name="user_favorite_theory"
    )
    op.drop_index(
        op.f("ix_user_favorite_theory_item_id"), table_name="user_favorite_theory"
    )
    op.drop_table("user_favorite_theory")
    op.drop_index(op.f("ix_images_item_id"), table_name="images")
    op.drop_table("images")
    op.drop_index(op.f("ix_items_type"), table_name="items")
    op.drop_index(op.f("ix_items_theme_id"), table_name="items")
    op.drop_table("items")
    op.drop_table("themes")
    op.drop_index(op.f("ix_users_tg_id"), table_name="users")
    op.drop_table("users")

    sa.Enum(name="contenttype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="userlanguage").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="usersubscription").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)

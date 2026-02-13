"""009_add_subscriptions_table

Revision ID: 5b3c63f6716f
Revises: 1462faa278a5
Create Date: 2026-02-07 19:32:58.456954

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "5b3c63f6716f"
down_revision = "1462faa278a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Проверяем, существует ли таблица subscriptions
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscriptions')"
        )
    )
    subscriptions_exists = result.scalar()

    if not subscriptions_exists:
        usersubscription_enum = postgresql.ENUM(
            "PREMIUM",
            "FREE",
            "TRIAL",
            "EXPIRED",
            name="usersubscription",
            create_type=False,
        )

        # Создаем таблицу subscriptions
        op.create_table(
            "subscriptions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("type", usersubscription_enum, nullable=False),
            sa.Column("activation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("expiration", sa.DateTime(timezone=True), nullable=True),
            sa.Column("renewal", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"], unique=True
        )

    # Проверяем, существует ли колонка subscription в users
    column_exists_result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'subscription')"
        )
    )
    column_exists = column_exists_result.scalar()

    if column_exists:
        # Переносим данные из users.subscription в subscriptions
        # Проверяем, есть ли данные для переноса
        count_result = conn.execute(
            sa.text("SELECT COUNT(*) FROM users WHERE subscription IS NOT NULL")
        )
        count = count_result.scalar()

        if count > 0:
            # Проверяем, есть ли уже данные в subscriptions
            subscriptions_count_result = conn.execute(
                sa.text("SELECT COUNT(*) FROM subscriptions")
            )
            subscriptions_count = subscriptions_count_result.scalar()

            if subscriptions_count == 0:
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO subscriptions (user_id, type, activation)
                        SELECT id, subscription, created_at
                        FROM users
                        WHERE subscription IS NOT NULL
                        """
                    )
                )
                conn.commit()

        # Удаляем колонку subscription из users
        op.drop_column("users", "subscription")


def downgrade() -> None:
    conn = op.get_bind()

    usersubscription_enum = postgresql.ENUM(
        "PREMIUM",
        "FREE",
        "TRIAL",
        "EXPIRED",
        name="usersubscription",
        create_type=False,
    )

    # Добавляем колонку subscription обратно в users
    op.add_column(
        "users",
        sa.Column("subscription", usersubscription_enum, nullable=True),
    )

    # Восстанавливаем данные из subscriptions
    # Берем последнюю активную подписку или первую по дате активации
    conn.execute(
        sa.text(
            """
            UPDATE users
            SET subscription = sub.type
            FROM (
                SELECT DISTINCT ON (user_id)
                    user_id,
                    type
                FROM subscriptions
                ORDER BY user_id, activation DESC NULLS LAST, id DESC
            ) AS sub
            WHERE users.id = sub.user_id
            """
        )
    )
    conn.commit()

    # Устанавливаем дефолтное значение для пользователей без подписки
    conn.execute(
        sa.text(
            """
            UPDATE users
            SET subscription = 'FREE'
            WHERE subscription IS NULL
            """
        )
    )
    conn.commit()

    # Делаем subscription NOT NULL
    op.alter_column("users", "subscription", nullable=False)

    # Удаляем таблицу subscriptions
    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_table("subscriptions")

# migrations/env.py

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from app import create_app, db

# Это конфигурация Alembic, взятая из файла .ini
config = context.config

# Устанавливаем логирование на основе конфигурации файла .ini
fileConfig(config.config_file_name)

# Импортируем все модели, чтобы Alembic мог видеть их
app = create_app()
with app.app_context():
    target_metadata = db.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

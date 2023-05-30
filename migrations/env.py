"""
This file is auto-generated by Alembic. It was updated manually to:
- set `target_metadata` so that Alembic can read the Indexd model and
auto-generate migrations;
- load the Indexd configuration in order to set `sqlalchemy.url` to the
configured DB URL;
- lock the DB during migrations to ensure only 1 migration runs at a time.
"""


import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.declarative import declarative_base

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("indexd.alembic")
logger.setLevel(logging.INFO)

Base = declarative_base()
target_metadata = Base.metadata

try:
    from local_settings import settings
except ImportError:
    logger.info("Can't import local_settings, import from default")
    from indexd.default_settings import settings
conn_url = str(settings["config"]["INDEX"]["driver"].engine.url)
config.set_main_option("sqlalchemy.url", conn_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            if connection.dialect.name == "postgresql":
                logger.info(
                    "Locking database to ensure only 1 process can run migrations at a time"
                )
                connection.execute(
                    f"SELECT pg_advisory_xact_lock({settings['config'].get('DB_MIGRATION_POSTGRES_LOCK_KEY', 100)});"
                )
            else:
                logger.info(
                    "Not running on Postgres: not locking database before migrating"
                )
            context.run_migrations()
        if connection.dialect.name == "postgresql":
            # The lock is released when the transaction ends.
            logger.info("Releasing database lock")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
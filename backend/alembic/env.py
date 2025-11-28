from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
import os
from backend.app.db import Base
from backend.app import models

"""
Alembic env script adjusted to avoid executing migration logic at import time.
This file should only run its migration routines when executed directly by Alembic
or when called as a script. Importing this module now will not trigger
`context`-dependent calls that are only available during alembic runtime.
"""

def run_migrations_offline(url):
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online(url):
    connectable = engine_from_config({}, url=url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()


def main():
    url = os.getenv("DATABASE_URL", "sqlite:///./culinaai.db")

    # Only attempt to run migrations when Alembic supplies the proper context
    try:
        if context.is_offline_mode():
            run_migrations_offline(url)
        else:
            run_migrations_online(url)
    except AttributeError:
        # When imported by the application (not via alembic CLI), `context` may
        # not have the expected runtime state. In that case, skip automatic
        # migration execution to avoid import-time errors.
        pass


if __name__ == "__main__":
    main()

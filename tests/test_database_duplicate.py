"""Integration tests for database duplication via create_database(template=…).

Requires:
    - A running PostgreSQL server with pg_service 'oqtopus_test'
"""

import psycopg
import pytest

from oqtopus.libs.pgserviceparser import (
    service_config as pgserviceparser_service_config,
)
from oqtopus.libs.pum.database import create_database, drop_database

DUP_DB_NAME = "oqtopus_test_dup"


def _service_params(pg_service, *, dbname=None):
    """Build connection params dict from a pg_service name."""
    params = {"service": pg_service}
    if dbname:
        params["dbname"] = dbname
    return params


def _source_dbname(pg_service):
    """Return the actual database name for the given pg_service."""
    return pgserviceparser_service_config(pg_service).get("dbname", pg_service)


@pytest.fixture()
def _cleanup_dup_db(pg_service):
    """Ensure the duplicated database is dropped after the test."""
    yield
    try:
        drop_database(_service_params(pg_service, dbname="postgres"), DUP_DB_NAME)
    except Exception:
        pass  # already gone


class TestDatabaseDuplicate:
    """Test CREATE DATABASE … TEMPLATE via create_database()."""

    def test_duplicate_copies_data(self, pg_service, clean_db, _cleanup_dup_db):
        """Duplicated database contains the same tables and data as the source."""
        source_db = None
        try:
            # Insert a marker table into the source database
            source_db = psycopg.connect(f"service={pg_service}")
            source_db.autocommit = True
            source_db.execute("CREATE TABLE IF NOT EXISTS dup_test_marker (id int PRIMARY KEY)")
            source_db.execute("INSERT INTO dup_test_marker VALUES (42) ON CONFLICT DO NOTHING")
        finally:
            if source_db:
                source_db.close()

        # Duplicate: connect via 'postgres' maintenance DB, just like the fixed dialog
        create_database(
            _service_params(pg_service, dbname="postgres"),
            DUP_DB_NAME,
            template=_source_dbname(pg_service),
        )

        # Verify the marker table exists in the duplicate
        dup_db = None
        try:
            dup_db = psycopg.connect(f"service={pg_service} dbname={DUP_DB_NAME}")
            row = dup_db.execute("SELECT id FROM dup_test_marker").fetchone()
            assert row is not None
            assert row[0] == 42
        finally:
            if dup_db:
                dup_db.close()

    def test_duplicate_fails_with_open_connection_to_source(
        self, pg_service, clean_db, _cleanup_dup_db
    ):
        """Duplication fails when another session is connected to the source DB.

        This reproduces the original bug: if the caller connects to the source
        database instead of the maintenance ``postgres`` database, PostgreSQL
        rejects CREATE DATABASE … TEMPLATE because the template is in use.
        """
        source_db = None
        blocking_conn = None
        try:
            # Seed the source with a marker
            source_db = psycopg.connect(f"service={pg_service}")
            source_db.autocommit = True
            source_db.execute("CREATE TABLE IF NOT EXISTS dup_block_marker (val text PRIMARY KEY)")
            source_db.execute(
                "INSERT INTO dup_block_marker VALUES ('present') ON CONFLICT DO NOTHING"
            )
            source_db.close()
            source_db = None

            # Open a blocking connection to the source DB (simulates the old bug)
            blocking_conn = psycopg.connect(f"service={pg_service}")
            blocking_conn.execute("SELECT 1")  # ensure it's truly active

            # Duplication must fail because the template is in use
            with pytest.raises(psycopg.errors.ObjectInUse):
                create_database(
                    _service_params(pg_service, dbname="postgres"),
                    DUP_DB_NAME,
                    template=_source_dbname(pg_service),
                )
        finally:
            if source_db:
                source_db.close()
            if blocking_conn:
                blocking_conn.close()

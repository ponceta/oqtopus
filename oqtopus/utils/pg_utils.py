"""Utilities for finding PostgreSQL command-line tools."""

import glob
import os
import shutil
import sys


def find_pg_executable(name: str) -> str:
    """Find a PostgreSQL executable, preferring the newest version.

    Searches versioned PostgreSQL installation directories first (picking
    the highest version), then falls back to PATH and common locations.

    Args:
        name: The executable name, e.g. "pg_dump" or "pg_restore".

    Returns:
        The full path to the executable, or *name* unchanged if not found
        (letting the OS raise a clear error at execution time).
    """
    # 1. Search versioned installation directories (newest first)
    versioned_patterns = []
    if sys.platform == "darwin":
        versioned_patterns.extend(
            [
                "/opt/homebrew/opt/postgresql@*/bin",
                "/usr/local/opt/postgresql@*/bin",
                "/Applications/Postgres.app/Contents/Versions/*/bin",
            ]
        )
    elif sys.platform == "win32":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        versioned_patterns.append(os.path.join(program_files, "PostgreSQL", "*", "bin"))
    else:
        versioned_patterns.extend(
            [
                "/usr/lib/postgresql/*/bin",
            ]
        )

    versioned_dirs = []
    for pattern in versioned_patterns:
        versioned_dirs.extend(glob.glob(pattern))
    # Sort descending so newest version is tried first
    versioned_dirs.sort(reverse=True)

    for directory in versioned_dirs:
        candidate = os.path.join(directory, name)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    # 2. Fall back to PATH
    found = shutil.which(name)
    if found:
        return found

    # 3. Common non-versioned locations
    fallback_dirs = []
    if sys.platform == "darwin":
        fallback_dirs.extend(["/opt/homebrew/bin", "/usr/local/bin"])
    elif sys.platform != "win32":
        fallback_dirs.extend(["/usr/bin", "/usr/local/bin"])

    for directory in fallback_dirs:
        candidate = os.path.join(directory, name)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return name

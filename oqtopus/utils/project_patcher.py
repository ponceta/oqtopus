import os
import re
import shutil
import tempfile
import zipfile

from .plugin_utils import logger

# Regex patterns for service= in QGIS project XML.
# Matches: service='name'  service=&apos;name&apos;  service=&quot;name&quot;
_SERVICE_PATTERNS = [
    (re.compile(r"service='[^']+'"), "service='{service}'"),
    (re.compile(r"service=&apos;[^&]+&apos;"), "service=&apos;{service}&apos;"),
    (re.compile(r"service=&quot;[^&]+&quot;"), "service=&quot;{service}&quot;"),
]


def replace_service_in_content(content: str, service: str) -> str:
    """Replace all PG service references in a QGIS project XML string."""
    for pattern, replacement_template in _SERVICE_PATTERNS:
        content = pattern.sub(replacement_template.format(service=service), content)
    return content


def patch_qgs_file(source_path: str, dest_path: str, service: str) -> None:
    """Read a .qgs file, replace the PG service name, and write to dest_path."""
    with open(source_path, encoding="utf-8") as f:
        contents = f.read()
    contents = replace_service_in_content(contents, service)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(contents)


def patch_qgz_file(source_path: str, dest_path: str, service: str) -> None:
    """Open a .qgz (ZIP), patch the inner .qgs, and write a new .qgz to dest_path."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Extract
        with zipfile.ZipFile(source_path, "r") as zin:
            zin.extractall(tmp_dir)

        # Patch inner .qgs files
        for root, _dirs, files in os.walk(tmp_dir):
            for fname in files:
                if fname.endswith(".qgs"):
                    fpath = os.path.join(root, fname)
                    with open(fpath, encoding="utf-8") as f:
                        contents = f.read()
                    contents = replace_service_in_content(contents, service)
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(contents)

        # Re-pack into a new .qgz
        with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for root, _dirs, files in os.walk(tmp_dir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, tmp_dir)
                    zout.write(fpath, arcname)


def patch_project_file(source_path: str, dest_path: str, service: str | None) -> None:
    """Patch a QGIS project file (.qgs or .qgz) replacing the PG service name.

    If *service* is None the file is copied without modification.
    *source_path* and *dest_path* may be the same path (in-place patching).
    """
    if service is None:
        logger.warning("No service set, skipping service replacement in project file.")
        if os.path.abspath(source_path) != os.path.abspath(dest_path):
            shutil.copy2(source_path, dest_path)
        return

    if source_path.endswith(".qgs"):
        patch_qgs_file(source_path, dest_path, service)
    elif source_path.endswith(".qgz"):
        patch_qgz_file(source_path, dest_path, service)
    else:
        logger.warning(f"Unknown project file format: {source_path}, copying without patching.")
        if os.path.abspath(source_path) != os.path.abspath(dest_path):
            shutil.copy2(source_path, dest_path)

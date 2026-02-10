#!/usr/bin/env bash
set -e

# Download bundled libraries from requirements-libs.txt
while IFS= read -r line; do
  # Skip empty lines and comments
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
  pip download "$line" --no-deps --only-binary :all: -d temp/
done < requirements-libs.txt

unzip -o "temp/*.whl" -d oqtopus/libs
rm -rf temp

# Create __init__.py to make libs a package
touch oqtopus/libs/__init__.py

# set write rights to group (because qgis-plugin-ci needs it)
chmod -R g+w oqtopus/libs

#!/usr/bin/env bash

pip download -r requirements.txt --only-binary :all: -d temp/
            unzip -o "temp/*.whl" -d oqtopus/libs
            rm -r temp
            # set write rights to group (because qgis-plugin-ci needs it)
            chmod -R g+w oqtopus/libs

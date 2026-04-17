# Keep this module minimal so QGIS can always locate ``classFactory`` even
# if the package is picked up from an unexpected ``sys.path`` entry on
# Windows (see issue #84 / plugin-load failures on blank profiles).
# Standalone-mode fake ``qgis.PyQt`` modules live in ``_qgis_shim.py`` and
# are imported only by the standalone entry point.


def classFactory(iface):
    from .oqtopus_plugin import OqtopusPlugin

    return OqtopusPlugin(iface)

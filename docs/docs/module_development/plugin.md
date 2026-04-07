# Plugin

## Releases

oQtopus looks in the GitHub release assets for an asset labeled **`oqtopus.plugin`**.
The asset should be the ZIP archive of the QGIS plugin, ready to be installed.

## Development branches and pull requests

For development branches and pull requests, oQtopus looks for a **GitHub Actions workflow artifact** named **`oqtopus.plugin`**.
This allows testers to install the plugin directly from a branch or PR without waiting for a release.

To enable this, name the artifact `oqtopus.plugin` in your workflow's `upload-artifact` step:

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: oqtopus.plugin
    path: my-plugin.zip
```

!!! note
    Downloading workflow artifacts requires a GitHub personal access token.
    Users without a token will still be able to use the source archive but won't have access to the built plugin asset.

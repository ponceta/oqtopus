# QGIS Projects

## Releases

oQtopus looks in the GitHub release assets for an asset labeled **`oqtopus.project`**.
The asset should be a ZIP archive containing a `.qgs` or `.qgz` QGIS project file (and any accompanying files).

## Development branches and pull requests

For development branches and pull requests, oQtopus looks for a **GitHub Actions workflow artifact** named **`oqtopus.project`**.
This allows testers to use the project directly from a branch or PR without waiting for a release.

To enable this, name the artifact `oqtopus.project` in your workflow's `upload-artifact` step:

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: oqtopus.project
    path: project/
```

!!! note
    Downloading workflow artifacts requires a GitHub personal access token.
    Users without a token will still be able to use the source archive but won't have access to the built project asset.

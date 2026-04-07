import requests
from qgis.PyQt.QtCore import QDateTime, Qt

from .module_asset import ModuleAsset
from .settings import Settings


class ModulePackage:

    # enum for package type
    class Type:
        RELEASE = "release"
        BRANCH = "branch"
        PULL_REQUEST = "pull_request"
        FROM_ZIP = "from_zip"
        FROM_DIRECTORY = "from_directory"

    def __init__(
        self,
        module,
        organisation,
        repository,
        json_payload: dict,
        type=Type.RELEASE,
        name=None,
        branch=None,
        commit_sha=None,
    ):
        self.module = module
        self.organisation = organisation
        self.repository = repository
        self.type = type
        self.name = name
        self.branch = branch
        self.commit_sha = commit_sha
        self.created_at = None
        self.prerelease = False
        self.html_url = None

        self.asset_project = None
        self.asset_plugin = None

        self.source_package_zip = None
        self.source_package_dir = None

        if self.type == ModulePackage.Type.RELEASE:
            self.__parse_release(json_payload)
        elif self.type == ModulePackage.Type.BRANCH:
            pass
        elif self.type == ModulePackage.Type.PULL_REQUEST:
            self.__parse_pull_request(json_payload)
        elif self.type == ModulePackage.Type.FROM_ZIP:
            return
        elif self.type == ModulePackage.Type.FROM_DIRECTORY:
            return
        else:
            raise ValueError(f"Unknown type '{type}'")

        type = "heads"
        if self.type == ModulePackage.Type.RELEASE:
            type = "tags"

        self.download_url = f"https://github.com/{self.organisation}/{self.repository}/archive/refs/{type}/{self.branch}.zip"

    def display_name(self):
        if self.prerelease:
            return f"{self.name} (prerelease)"

        return self.name

    def fetch_commit_sha(self):
        """Fetch the latest commit SHA for the branch from GitHub API."""
        if self.type not in (ModulePackage.Type.BRANCH, ModulePackage.Type.PULL_REQUEST):
            return

        try:
            # For branches: use refs/heads/{branch}
            # For PRs: use refs/heads/{branch} from the head repo
            url = f"https://api.github.com/repos/{self.organisation}/{self.repository}/commits/{self.branch}"
            r = requests.get(url, headers=Settings.get_github_headers(), timeout=10)
            r.raise_for_status()
            commit_data = r.json()
            self.commit_sha = commit_data["sha"]
        except Exception as e:
            # If we can't fetch the commit SHA, we'll fall back to not caching
            from ..utils.plugin_utils import logger

            logger.warning(f"Failed to fetch commit SHA for branch '{self.branch}': {e}")
            self.commit_sha = None

    def fetch_workflow_assets(self):
        """Fetch workflow artifact URLs for branch/PR packages from GitHub Actions API.

        Requires a GitHub token. Looks for artifacts named 'oqtopus.project'
        and 'oqtopus.plugin' from the latest successful workflow run on the branch.
        """
        from ..utils.plugin_utils import logger

        if self.type not in (ModulePackage.Type.BRANCH, ModulePackage.Type.PULL_REQUEST):
            return

        headers = Settings.get_github_headers()
        if not headers.get("Authorization"):
            logger.info("No GitHub token configured — skipping workflow artifact lookup.")
            return

        try:
            # Find the latest successful workflow run on this branch
            url = (
                f"https://api.github.com/repos/{self.organisation}/{self.repository}"
                f"/actions/runs?branch={self.branch}&status=success&per_page=5"
            )
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            runs = r.json().get("workflow_runs", [])

            if not runs:
                logger.info(f"No successful workflow runs found for branch '{self.branch}'.")
                return

            # Check each run (most recent first) for matching artifacts
            for run in runs:
                artifacts_url = run["artifacts_url"]
                r = requests.get(artifacts_url, headers=headers, timeout=10)
                r.raise_for_status()
                artifacts = r.json().get("artifacts", [])

                for artifact in artifacts:
                    artifact_name = artifact["name"]
                    if artifact["expired"]:
                        continue

                    download_url = (
                        f"https://api.github.com/repos/{self.organisation}/{self.repository}"
                        f"/actions/artifacts/{artifact['id']}/zip"
                    )

                    if (
                        artifact_name == ModuleAsset.Type.PROJECT.value
                        and self.asset_project is None
                    ):
                        self.asset_project = ModuleAsset(
                            name=artifact_name,
                            label=artifact_name,
                            download_url=download_url,
                            size=artifact["size_in_bytes"],
                            type=ModuleAsset.Type.PROJECT,
                        )
                        logger.info(
                            f"Found workflow artifact '{artifact_name}' (run #{run['run_number']})"
                        )

                    elif (
                        artifact_name == ModuleAsset.Type.PLUGIN.value
                        and self.asset_plugin is None
                    ):
                        self.asset_plugin = ModuleAsset(
                            name=artifact_name,
                            label=artifact_name,
                            download_url=download_url,
                            size=artifact["size_in_bytes"],
                            type=ModuleAsset.Type.PLUGIN,
                        )
                        logger.info(
                            f"Found workflow artifact '{artifact_name}' (run #{run['run_number']})"
                        )

                if self.asset_project and self.asset_plugin:
                    # Found both artifacts, stop searching older runs
                    break

        except Exception as e:
            logger.warning(f"Failed to fetch workflow artifacts for branch '{self.branch}': {e}")

    def __parse_release(self, json_payload: dict):
        if self.name is None:
            self.name = json_payload["name"]

        if self.name is None or self.name == "":
            self.name = json_payload["tag_name"]

        self.branch = self.name
        self.created_at = QDateTime.fromString(json_payload["created_at"], Qt.DateFormat.ISODate)
        self.prerelease = json_payload["prerelease"]
        self.html_url = json_payload["html_url"]

        # Use assets directly from the release payload (already included in releases API response)
        self.__parse_release_assets(json_payload.get("assets", []))

    def __parse_release_assets(self, json_assets: list):
        """Parse release assets from the already-fetched release data."""
        for json_asset in json_assets:
            asset = ModuleAsset(
                name=json_asset["name"],
                label=json_asset["label"],
                download_url=json_asset["browser_download_url"],
                size=json_asset["size"],
                type=None,
            )

            if asset.label == ModuleAsset.Type.PROJECT.value:
                asset.type = ModuleAsset.Type.PROJECT
                self.asset_project = asset
                continue

            if asset.label == ModuleAsset.Type.PLUGIN.value:
                asset.type = ModuleAsset.Type.PLUGIN
                self.asset_plugin = asset
                continue

            if self.asset_project and self.asset_plugin:
                # We already have all assets we need
                break

    def __parse_pull_request(self, json_payload: dict):
        if self.name is None:
            self.name = f"#{json_payload['number']} {json_payload['title']}"
        self.branch = json_payload["head"]["ref"]
        self.commit_sha = json_payload["head"]["sha"]
        self.created_at = QDateTime.fromString(json_payload["created_at"], Qt.DateFormat.ISODate)
        self.prerelease = False
        self.html_url = json_payload["html_url"]

        is_on_a_fork = json_payload["head"]["repo"]["fork"]
        if is_on_a_fork:
            self.organisation = json_payload["head"]["repo"]["owner"]["login"]
            self.repository = json_payload["head"]["repo"]["name"]

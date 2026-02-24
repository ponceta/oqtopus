from pydantic import BaseModel


class ModuleConfig(BaseModel):
    """Configuration for a single module.

    Attributes:
        name: **Required.** Display name of the module.
        id: **Required.** Unique identifier for the module (used for loading).
        organisation: **Required.** GitHub organisation where the module is hosted.
        repository: **Required.** GitHub repository name for the module.
        exclude_releases: *Optional.* Regex pattern to exclude certain releases.
        experimental: *Optional.* Whether this module is experimental (not shown by default).
    """

    name: str
    id: str
    organisation: str
    repository: str
    exclude_releases: str | None = None  # Regexp pattern to exclude releases
    experimental: bool = False  # Whether this module is experimental


class ModulesConfig(BaseModel):
    """
    Configuration for all modules.

    Attributes:
        modules: List of module configurations.
    """

    modules: list[ModuleConfig]

from pydantic import BaseModel


class ModuleConfig(BaseModel):
    """Configuration for a single module.

    Attributes:
        name: Display name of the module.
        id: Unique identifier for the module (used for loading).
        organisation: GitHub organisation where the module is hosted.
        repository: GitHub repository name for the module.
        exclude_releases: Optional regex pattern to exclude certain releases.
        experimental: Whether this module is experimental (not shown by default).
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

from typing import List

import tomli
from pydantic import BaseModel


class ModuleConfig(BaseModel):
    name: str
    organisation: str
    repository: str


class ModulesConfig(BaseModel):
    modules: List[ModuleConfig]


def load_modules_from_conf(conf_path: str) -> ModulesConfig:
    with open(conf_path, "rb") as f:
        data = tomli.load(f)
    return ModulesConfig(**data)

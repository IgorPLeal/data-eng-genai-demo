"""Módulo responsável pelo carregamento da configuração."""

import os
from typing import Any, Dict

import yaml

from src.core.exceptions import ConfigNotFoundError


class ConfigLoader:
    """Carrega e disponibiliza a configuração do pipeline a partir de um arquivo YAML."""

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..")
            )
            config_path = os.path.join(project_root, "config", "config.yaml")

        if not os.path.isfile(config_path):
            raise ConfigNotFoundError(config_path)

        with open(config_path, "r", encoding="utf-8") as f:
            self._config: Dict[str, Any] = yaml.safe_load(f)

    @property
    def catalogo(self) -> Dict[str, Any]:
        """Retorna o catálogo de datasets."""
        return self._config.get("catalogo", {})

    @property
    def datasets(self) -> Dict[str, str]:
        """Retorna as configurações de repositórios de datasets."""
        return self._config.get("datasets", {})

    @property
    def logging_config(self) -> Dict[str, str]:
        """Retorna as configurações de logging."""
        return self._config.get("logging", {})

    def get(self, key: str, default: Any = None) -> Any:
        """Retorna um valor da configuração pelo nome da chave."""
        return self._config.get(key, default)

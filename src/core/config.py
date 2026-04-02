import os
from typing import Any, Dict

import yaml

from src.core.exceptions import ConfigNotFoundException


class ConfigLoader:
    """Carrega e fornece acesso à configuração do pipeline.

    Lê a configuração a partir de um arquivo YAML.
    """

    DEFAULT_CONFIG_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "config",
        "config.yaml",
    )

    def __init__(self, config_path: str = ""):
        self._config_path = self._resolve_path(config_path)
        self._config: Dict[str, Any] = {}

    def _resolve_path(self, config_path: str) -> str:
        if config_path:
            return config_path

        env_path = os.environ.get("CONFIG_PATH")
        if env_path:
            return env_path

        return self.DEFAULT_CONFIG_PATH

    def load(self) -> Dict[str, Any]:
        """Carrega o arquivo YAML e retorna o dicionário de configuração."""
        resolved = os.path.normpath(self._config_path)

        if not os.path.isfile(resolved):
            raise ConfigNotFoundException(resolved)

        with open(resolved, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

        return self._config

    @property
    def config(self) -> Dict[str, Any]:
        """Retorna a configuração carregada."""
        if not self._config:
            self.load()
        return self._config

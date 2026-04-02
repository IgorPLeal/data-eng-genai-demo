"""Módulo de configuração centralizada de logging."""

import logging
from typing import Any, Dict


class LoggingSetup:
    """Configura o logging da aplicação."""

    def __init__(self, config: Dict[str, Any]):
        self._level = config.get("level", "INFO")
        self._format = config.get(
            "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self._configure()

    def _configure(self) -> None:
        """Aplica a configuração de logging."""
        logging.basicConfig(
            level=getattr(logging, self._level.upper(), logging.INFO),
            format=self._format,
        )

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Retorna um logger com o nome especificado."""
        return logging.getLogger(name)

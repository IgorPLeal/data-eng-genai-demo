"""Módulo de gerenciamento e configuração do Pandas."""

import logging

import pandas as pd

from src.utils.logging_setup import LoggingSetup


class PandasManager:
    """Configura opções globais do Pandas e inicializa logging."""

    def __init__(self, logging_config: dict):
        self._logging_setup = LoggingSetup(logging_config)
        self._logger = LoggingSetup.get_logger(self.__class__.__name__)
        self._configure_pandas()

    def _configure_pandas(self) -> None:
        """Aplica configurações globais do Pandas."""
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", 100)
        pd.set_option("display.width", None)
        self._logger.info("Pandas configurado com sucesso.")

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Retorna um logger da aplicação."""
        return LoggingSetup.get_logger(name)

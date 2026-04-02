import logging
from typing import Any, Dict

from pyspark.sql import SparkSession

logger = logging.getLogger("top10_pipeline")


class SparkManager:
    """Factory para criação e gerenciamento da SparkSession."""

    def __init__(self, spark_config: Dict[str, Any]):
        self._app_name = spark_config.get("app_name", "SparkApp")
        self._master = spark_config.get("master", "local[*]")
        self._session: SparkSession | None = None

    def get_or_create(self) -> SparkSession:
        """Cria ou retorna a SparkSession existente."""
        if self._session is None:
            logger.info(
                "Criando SparkSession: app_name=%s, master=%s",
                self._app_name,
                self._master,
            )
            self._session = (
                SparkSession.builder.appName(self._app_name)
                .master(self._master)
                .getOrCreate()
            )
            self._session.sparkContext.setLogLevel("WARN")

        return self._session

    def stop(self) -> None:
        """Encerra a SparkSession."""
        if self._session is not None:
            logger.info("Encerrando SparkSession.")
            self._session.stop()
            self._session = None

    def __enter__(self) -> SparkSession:
        return self.get_or_create()

    def __exit__(  # type: ignore[no-untyped-def]
        self, exc_type, exc_val, exc_tb
    ) -> None:
        self.stop()

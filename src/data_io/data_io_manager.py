import logging
from typing import Any, Dict

from pyspark.sql import DataFrame, SparkSession

from src.core.exceptions import DataSourceNotFoundException

logger = logging.getLogger("top10_pipeline")


class DataIOManager:
    """Gerencia leitura e escrita de dados com base no catálogo de configuração.

    Implementa o Strategy Pattern para abstrair diferentes formatos de I/O.
    """

    def __init__(
        self,
        spark: SparkSession,
        data_catalog: Dict[str, Any],
        output_config: Dict[str, Any],
    ):
        self._spark = spark
        self._data_catalog = data_catalog
        self._output_config = output_config

    def read(self, source_id: str) -> DataFrame:
        """Lê dados de uma fonte registrada no catálogo.

        Args:
            source_id: Identificador lógico da fonte (ex: 'clientes', 'pedidos').

        Returns:
            DataFrame com os dados lidos.

        Raises:
            DataSourceNotFoundException: Se o source_id não existir no catálogo.
        """
        if source_id not in self._data_catalog:
            raise DataSourceNotFoundException(source_id)

        source_config = self._data_catalog[source_id]
        path = source_config["path"]
        fmt = source_config["format"]
        options = source_config.get("options", {})

        logger.info("Lendo fonte '%s' [formato=%s, caminho=%s]", source_id, fmt, path)

        reader = self._spark.read.format(fmt)
        for key, value in options.items():
            reader = reader.option(key, value)

        return reader.load(path)

    def write(self, df: DataFrame, target_id: str) -> None:
        """Escreve um DataFrame em um destino registrado no output config.

        Args:
            df: DataFrame a ser salvo.
            target_id: Identificador lógico do destino (ex: 'top_10_clientes').

        Raises:
            DataSourceNotFoundException: Se o target_id não existir no output config.
        """
        if target_id not in self._output_config:
            raise DataSourceNotFoundException(target_id)

        target = self._output_config[target_id]
        path = target["path"]
        fmt = target.get("format", "parquet")
        mode = target.get("mode", "overwrite")

        logger.info(
            "Escrevendo destino '%s' [formato=%s, modo=%s, caminho=%s]",
            target_id,
            fmt,
            mode,
            path,
        )

        df.write.format(fmt).mode(mode).save(path)

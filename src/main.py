"""Ponto de entrada da aplicação - Composition Root.

Responsável por instanciar e injetar as dependências nos jobs.
"""

import sys

from src.core.config import ConfigLoader
from src.core.exceptions import ConfigNotFoundException, DataSourceNotFoundException
from src.data_io.data_io_manager import DataIOManager
from src.jobs.run_top_10 import RunTop10Job
from src.utils.logging_setup import setup_logging
from src.utils.spark_manager import SparkManager


def main() -> None:
    logger = setup_logging()

    try:
        logger.info("Carregando configuração...")
        config_loader = ConfigLoader()
        config = config_loader.load()

        spark_config = config["spark"]
        data_catalog = config["data_catalog"]
        output_config = config["output"]

        with SparkManager(spark_config) as spark:
            data_io = DataIOManager(spark, data_catalog, output_config)
            job = RunTop10Job(data_io)
            job.execute()

    except ConfigNotFoundException as e:
        logger.error("Configuração não encontrada: %s", e)
        sys.exit(1)
    except DataSourceNotFoundException as e:
        logger.error("Fonte de dados não encontrada: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.error("Erro inesperado: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

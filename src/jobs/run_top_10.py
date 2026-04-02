"""Job de orquestração do pipeline Top 10 Clientes."""

import logging

from src.data_io.data_io_manager import DataIOManager
from src.transforms.vendas_transforms import VendasTransforms
from src.utils.logging_setup import LoggingSetup


class RunTop10Job:
    """Orquestra o pipeline de identificação dos Top 10 Clientes."""

    def __init__(self, data_io: DataIOManager):
        self._data_io = data_io
        self._transforms = VendasTransforms()
        self._logger: logging.Logger = LoggingSetup.get_logger(self.__class__.__name__)

    def execute(self) -> None:
        """Executa o pipeline completo: leitura, transformação e escrita."""
        self._logger.info("Iniciando pipeline Top 10 Clientes...")

        # 1. Leitura dos dados
        self._logger.info("Lendo dados de pedidos...")
        pedidos_df = self._data_io.read("pedidos_bronze")
        self._logger.info("Pedidos carregados: %d registros.", len(pedidos_df))

        self._logger.info("Lendo dados de clientes...")
        clientes_df = self._data_io.read("clientes_bronze")
        self._logger.info("Clientes carregados: %d registros.", len(clientes_df))

        # 2. Transformações
        self._logger.info("Calculando valor total por pedido...")
        pedidos_com_total = self._transforms.calcular_valor_total(pedidos_df)

        self._logger.info("Agregando por cliente...")
        agregado = self._transforms.agregar_por_cliente(pedidos_com_total)

        self._logger.info("Calculando Top 10 Clientes...")
        top_10 = self._transforms.top_10_clientes(agregado, clientes_df)

        self._logger.info("Top 10 Clientes:\n%s", top_10.to_string(index=False))

        # 3. Escrita do resultado
        self._logger.info("Salvando resultado...")
        self._data_io.write(top_10, "top_10_clientes")

        self._logger.info("Pipeline Top 10 Clientes finalizado com sucesso.")

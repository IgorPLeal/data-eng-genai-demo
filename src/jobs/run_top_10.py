import logging

from src.data_io.data_io_manager import DataIOManager
from src.transforms.vendas_transforms import VendasTransforms

logger = logging.getLogger("top10_pipeline")


class RunTop10Job:
    """Orquestra o pipeline de identificação dos Top 10 Clientes.

    Recebe as dependências via injeção (DataIOManager) e executa o pipeline
    completo de leitura, transformação e escrita.
    """

    def __init__(self, data_io: DataIOManager):
        self._data_io = data_io

    def execute(self) -> None:
        """Executa o pipeline completo do Top 10 Clientes."""
        logger.info("Iniciando pipeline Top 10 Clientes...")

        logger.info("Lendo dados de pedidos...")
        df_pedidos = self._data_io.read("pedidos")

        logger.info("Lendo dados de clientes...")
        df_clientes = self._data_io.read("clientes")

        logger.info("Calculando valor total por pedido...")
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)

        logger.info("Agregando compras por cliente...")
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)

        logger.info("Rankeando Top 10 clientes...")
        df_top10 = VendasTransforms.rankear_top_n(df_agregado, n=10)

        logger.info("Enriquecendo ranking com dados cadastrais...")
        df_resultado = VendasTransforms.enriquecer_com_clientes(df_top10, df_clientes)

        logger.info("Resultado - Top 10 Clientes:")
        df_resultado.show(truncate=False)

        logger.info("Salvando resultado...")
        self._data_io.write(df_resultado, "top_10_clientes")

        logger.info("Pipeline Top 10 Clientes finalizado com sucesso!")

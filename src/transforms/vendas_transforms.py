from pyspark.sql import DataFrame
from pyspark.sql import functions as F


class VendasTransforms:
    """Transformações puras sobre DataFrames de vendas.

    Todos os métodos são estáticos, recebem DataFrames e retornam DataFrames,
    garantindo testabilidade total sem efeitos colaterais.
    """

    @staticmethod
    def calcular_valor_total(df_pedidos: DataFrame) -> DataFrame:
        """Adiciona coluna VALOR_TOTAL = VALOR_UNITARIO * QUANTIDADE."""
        return df_pedidos.withColumn(
            "VALOR_TOTAL", F.col("VALOR_UNITARIO") * F.col("QUANTIDADE")
        )

    @staticmethod
    def agregar_por_cliente(df_pedidos: DataFrame) -> DataFrame:
        """Agrupa por ID_CLIENTE e calcula a soma de VALOR_TOTAL."""
        return df_pedidos.groupBy("ID_CLIENTE").agg(
            F.sum("VALOR_TOTAL").alias("TOTAL_COMPRAS")
        )

    @staticmethod
    def rankear_top_n(df_agregado: DataFrame, n: int = 10) -> DataFrame:
        """Retorna os top N clientes ordenados por TOTAL_COMPRAS descendente."""
        return df_agregado.orderBy(F.col("TOTAL_COMPRAS").desc()).limit(n)

    @staticmethod
    def enriquecer_com_clientes(
        df_ranking: DataFrame, df_clientes: DataFrame
    ) -> DataFrame:
        """Enriquece o ranking com dados cadastrais dos clientes.

        Faz o join entre o ranking (ID_CLIENTE) e clientes (id).
        """
        return (
            df_ranking.join(
                df_clientes, df_ranking["ID_CLIENTE"] == df_clientes["id"], "left"
            )
            .select(
                df_ranking["ID_CLIENTE"],
                df_clientes["nome"],
                df_clientes["email"],
                df_ranking["TOTAL_COMPRAS"],
            )
            .orderBy(F.col("TOTAL_COMPRAS").desc())
        )

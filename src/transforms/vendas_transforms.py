"""Módulo de transformações puras sobre DataFrames de vendas.

Todas as funções recebem DataFrames e retornam DataFrames,
garantindo testabilidade total sem dependência de I/O.
"""

import pandas as pd


class VendasTransforms:
    """Transformações de dados de vendas para cálculo do Top 10 Clientes."""

    @staticmethod
    def calcular_valor_total(pedidos_df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona a coluna VALOR_TOTAL = VALOR_UNITARIO * QUANTIDADE.

        Args:
            pedidos_df: DataFrame de pedidos com colunas VALOR_UNITARIO e QUANTIDADE.

        Returns:
            DataFrame com a coluna VALOR_TOTAL adicionada.
        """
        df = pedidos_df.copy()
        df["VALOR_TOTAL"] = df["VALOR_UNITARIO"] * df["QUANTIDADE"]
        return df

    @staticmethod
    def agregar_por_cliente(pedidos_df: pd.DataFrame) -> pd.DataFrame:
        """Agrega os pedidos por ID_CLIENTE, somando o VALOR_TOTAL.

        Args:
            pedidos_df: DataFrame de pedidos com colunas ID_CLIENTE e VALOR_TOTAL.

        Returns:
            DataFrame agrupado por ID_CLIENTE com a soma de VALOR_TOTAL.
        """
        agregado = (
            pedidos_df.groupby("ID_CLIENTE", as_index=False)["VALOR_TOTAL"]
            .sum()
            .rename(columns={"VALOR_TOTAL": "TOTAL_COMPRAS"})
        )
        return agregado

    @staticmethod
    def top_10_clientes(
        agregado_df: pd.DataFrame, clientes_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Faz join com a tabela de clientes e retorna os Top 10 por TOTAL_COMPRAS.

        Args:
            agregado_df: DataFrame agrupado com ID_CLIENTE e TOTAL_COMPRAS.
            clientes_df: DataFrame de clientes com id e nome.

        Returns:
            DataFrame com os 10 clientes de maior volume de compras.
        """
        merged = agregado_df.merge(
            clientes_df[["id", "nome"]],
            left_on="ID_CLIENTE",
            right_on="id",
            how="inner",
        )
        top_10 = (
            merged.sort_values("TOTAL_COMPRAS", ascending=False)
            .head(10)
            .reset_index(drop=True)
        )
        top_10 = top_10[["ID_CLIENTE", "nome", "TOTAL_COMPRAS"]]
        return top_10

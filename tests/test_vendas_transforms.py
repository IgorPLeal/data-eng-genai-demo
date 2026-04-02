"""Testes unitários para as transformações de vendas."""

import pandas as pd
import pytest

from src.transforms.vendas_transforms import VendasTransforms


@pytest.fixture
def pedidos_df():
    """DataFrame sintético de pedidos."""
    return pd.DataFrame(
        {
            "ID_PEDIDO": ["p1", "p2", "p3", "p4", "p5", "p6"],
            "PRODUTO": [
                "NOTEBOOK",
                "CELULAR",
                "GELADEIRA",
                "NOTEBOOK",
                "CELULAR",
                "TV",
            ],
            "VALOR_UNITARIO": [1500.0, 1000.0, 2000.0, 1500.0, 1000.0, 3000.0],
            "QUANTIDADE": [2, 3, 1, 1, 2, 1],
            "DATA_CRIACAO": [
                "2026-01-01",
                "2026-01-02",
                "2026-01-03",
                "2026-01-04",
                "2026-01-05",
                "2026-01-06",
            ],
            "UF": ["SP", "RJ", "MG", "SP", "RJ", "BA"],
            "ID_CLIENTE": [1, 2, 3, 1, 2, 4],
        }
    )


@pytest.fixture
def clientes_df():
    """DataFrame sintético de clientes."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "nome": [
                "Alice",
                "Bob",
                "Carlos",
                "Diana",
                "Eduardo",
                "Fernanda",
                "Gabriel",
                "Helena",
                "Igor",
                "Julia",
                "Kevin",
                "Laura",
            ],
        }
    )


class TestCalcularValorTotal:
    """Testes para calcular_valor_total."""

    def test_coluna_valor_total_criada(self, pedidos_df):
        resultado = VendasTransforms.calcular_valor_total(pedidos_df)
        assert "VALOR_TOTAL" in resultado.columns

    def test_valores_corretos(self, pedidos_df):
        resultado = VendasTransforms.calcular_valor_total(pedidos_df)
        esperado = [3000.0, 3000.0, 2000.0, 1500.0, 2000.0, 3000.0]
        assert resultado["VALOR_TOTAL"].tolist() == esperado

    def test_nao_modifica_original(self, pedidos_df):
        colunas_originais = list(pedidos_df.columns)
        VendasTransforms.calcular_valor_total(pedidos_df)
        assert list(pedidos_df.columns) == colunas_originais


class TestAgregarPorCliente:
    """Testes para agregar_por_cliente."""

    def test_agrupamento_correto(self, pedidos_df):
        com_total = VendasTransforms.calcular_valor_total(pedidos_df)
        resultado = VendasTransforms.agregar_por_cliente(com_total)
        assert len(resultado) == 4  # 4 clientes distintos

    def test_soma_correta(self, pedidos_df):
        com_total = VendasTransforms.calcular_valor_total(pedidos_df)
        resultado = VendasTransforms.agregar_por_cliente(com_total)
        cliente_1 = resultado[resultado["ID_CLIENTE"] == 1]["TOTAL_COMPRAS"].iloc[0]
        assert cliente_1 == 4500.0  # 3000 + 1500

    def test_coluna_renomeada(self, pedidos_df):
        com_total = VendasTransforms.calcular_valor_total(pedidos_df)
        resultado = VendasTransforms.agregar_por_cliente(com_total)
        assert "TOTAL_COMPRAS" in resultado.columns
        assert "VALOR_TOTAL" not in resultado.columns


class TestTop10Clientes:
    """Testes para top_10_clientes."""

    def test_retorna_no_maximo_10(self, pedidos_df, clientes_df):
        com_total = VendasTransforms.calcular_valor_total(pedidos_df)
        agregado = VendasTransforms.agregar_por_cliente(com_total)
        resultado = VendasTransforms.top_10_clientes(agregado, clientes_df)
        assert len(resultado) <= 10

    def test_ordenacao_decrescente(self, pedidos_df, clientes_df):
        com_total = VendasTransforms.calcular_valor_total(pedidos_df)
        agregado = VendasTransforms.agregar_por_cliente(com_total)
        resultado = VendasTransforms.top_10_clientes(agregado, clientes_df)
        valores = resultado["TOTAL_COMPRAS"].tolist()
        assert valores == sorted(valores, reverse=True)

    def test_contém_nome_do_cliente(self, pedidos_df, clientes_df):
        com_total = VendasTransforms.calcular_valor_total(pedidos_df)
        agregado = VendasTransforms.agregar_por_cliente(com_total)
        resultado = VendasTransforms.top_10_clientes(agregado, clientes_df)
        assert "nome" in resultado.columns

    def test_primeiro_lugar(self, pedidos_df, clientes_df):
        com_total = VendasTransforms.calcular_valor_total(pedidos_df)
        agregado = VendasTransforms.agregar_por_cliente(com_total)
        resultado = VendasTransforms.top_10_clientes(agregado, clientes_df)
        primeiro = resultado.iloc[0]
        assert primeiro["nome"] == "Bob"
        assert primeiro["TOTAL_COMPRAS"] == 5000.0

    def test_colunas_resultado(self, pedidos_df, clientes_df):
        com_total = VendasTransforms.calcular_valor_total(pedidos_df)
        agregado = VendasTransforms.agregar_por_cliente(com_total)
        resultado = VendasTransforms.top_10_clientes(agregado, clientes_df)
        assert list(resultado.columns) == ["ID_CLIENTE", "nome", "TOTAL_COMPRAS"]

    def test_top_10_com_mais_de_10_clientes(self, clientes_df):
        """Testa que retorna exatamente 10 quando há mais de 10 clientes."""
        pedidos_grande = pd.DataFrame(
            {
                "ID_PEDIDO": [f"p{i}" for i in range(12)],
                "PRODUTO": ["PRODUTO"] * 12,
                "VALOR_UNITARIO": [100.0 * (i + 1) for i in range(12)],
                "QUANTIDADE": [1] * 12,
                "DATA_CRIACAO": ["2026-01-01"] * 12,
                "UF": ["SP"] * 12,
                "ID_CLIENTE": list(range(1, 13)),
            }
        )
        com_total = VendasTransforms.calcular_valor_total(pedidos_grande)
        agregado = VendasTransforms.agregar_por_cliente(com_total)
        resultado = VendasTransforms.top_10_clientes(agregado, clientes_df)
        assert len(resultado) == 10

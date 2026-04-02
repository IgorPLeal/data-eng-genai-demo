import pytest
from pyspark.sql import SparkSession

from src.transforms.vendas_transforms import VendasTransforms


@pytest.fixture(scope="module")
def spark():
    """Cria uma SparkSession para os testes."""
    session = (
        SparkSession.builder.appName("TestVendasTransforms")
        .master("local[*]")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("WARN")
    yield session
    session.stop()


@pytest.fixture
def df_pedidos(spark):
    """Cria um DataFrame sintético de pedidos."""
    data = [
        ("p1", "NOTEBOOK", 1500.0, 2, "2026-01-01T10:00:00", "SP", 1),
        ("p2", "CELULAR", 1000.0, 3, "2026-01-02T11:00:00", "RJ", 2),
        ("p3", "GELADEIRA", 2000.0, 1, "2026-01-03T12:00:00", "MG", 1),
        ("p4", "TV", 2500.0, 1, "2026-01-04T13:00:00", "SP", 3),
        ("p5", "NOTEBOOK", 1500.0, 1, "2026-01-05T14:00:00", "RJ", 2),
    ]
    columns = [
        "ID_PEDIDO",
        "PRODUTO",
        "VALOR_UNITARIO",
        "QUANTIDADE",
        "DATA_CRIACAO",
        "UF",
        "ID_CLIENTE",
    ]
    return spark.createDataFrame(data, columns)


@pytest.fixture
def df_clientes(spark):
    """Cria um DataFrame sintético de clientes."""
    data = [
        (1, "Alice Silva", "alice@email.com"),
        (2, "Bruno Santos", "bruno@email.com"),
        (3, "Carla Souza", "carla@email.com"),
    ]
    columns = ["id", "nome", "email"]
    return spark.createDataFrame(data, columns)


class TestCalcularValorTotal:
    def test_calcula_valor_total_corretamente(self, df_pedidos):
        resultado = VendasTransforms.calcular_valor_total(df_pedidos)

        assert "VALOR_TOTAL" in resultado.columns

        rows = resultado.select("ID_PEDIDO", "VALOR_TOTAL").collect()
        valores = {row["ID_PEDIDO"]: row["VALOR_TOTAL"] for row in rows}

        assert valores["p1"] == 3000.0  # 1500 * 2
        assert valores["p2"] == 3000.0  # 1000 * 3
        assert valores["p3"] == 2000.0  # 2000 * 1
        assert valores["p4"] == 2500.0  # 2500 * 1
        assert valores["p5"] == 1500.0  # 1500 * 1


class TestAgregarPorCliente:
    def test_agrega_por_cliente_corretamente(self, df_pedidos):
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        resultado = VendasTransforms.agregar_por_cliente(df_com_total)

        assert "ID_CLIENTE" in resultado.columns
        assert "TOTAL_COMPRAS" in resultado.columns

        rows = resultado.collect()
        totais = {row["ID_CLIENTE"]: row["TOTAL_COMPRAS"] for row in rows}

        assert totais[1] == 5000.0  # 3000 + 2000
        assert totais[2] == 4500.0  # 3000 + 1500
        assert totais[3] == 2500.0  # 2500


class TestRankearTopN:
    def test_retorna_top_n_correto(self, df_pedidos):
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)
        resultado = VendasTransforms.rankear_top_n(df_agregado, n=2)

        assert resultado.count() == 2

        rows = resultado.collect()
        assert rows[0]["TOTAL_COMPRAS"] >= rows[1]["TOTAL_COMPRAS"]

    def test_retorna_todos_quando_n_maior_que_total(self, df_pedidos):
        df_com_total = VendasTransforms.calcular_valor_total(df_pedidos)
        df_agregado = VendasTransforms.agregar_por_cliente(df_com_total)
        resultado = VendasTransforms.rankear_top_n(df_agregado, n=100)

        assert resultado.count() == 3

    def test_rankear_com_empate(self, spark):
        data = [
            (1, 5000.0),
            (2, 5000.0),
            (3, 3000.0),
        ]
        df = spark.createDataFrame(data, ["ID_CLIENTE", "TOTAL_COMPRAS"])
        resultado = VendasTransforms.rankear_top_n(df, n=2)

        assert resultado.count() == 2
        rows = resultado.collect()
        assert rows[0]["TOTAL_COMPRAS"] == 5000.0
        assert rows[1]["TOTAL_COMPRAS"] == 5000.0


class TestEnriquecerComClientes:
    def test_enriquece_ranking_com_dados_clientes(self, spark, df_clientes):
        data_ranking = [
            (1, 5000.0),
            (2, 4500.0),
        ]
        df_ranking = spark.createDataFrame(
            data_ranking, ["ID_CLIENTE", "TOTAL_COMPRAS"]
        )

        resultado = VendasTransforms.enriquecer_com_clientes(df_ranking, df_clientes)

        assert "nome" in resultado.columns
        assert "email" in resultado.columns
        assert "TOTAL_COMPRAS" in resultado.columns

        rows = resultado.collect()
        assert len(rows) == 2

        primeiro = rows[0]
        assert primeiro["nome"] == "Alice Silva"
        assert primeiro["TOTAL_COMPRAS"] == 5000.0

    def test_cliente_sem_cadastro_retorna_null(self, spark, df_clientes):
        data_ranking = [
            (999, 10000.0),
        ]
        df_ranking = spark.createDataFrame(
            data_ranking, ["ID_CLIENTE", "TOTAL_COMPRAS"]
        )

        resultado = VendasTransforms.enriquecer_com_clientes(df_ranking, df_clientes)

        rows = resultado.collect()
        assert len(rows) == 1
        assert rows[0]["nome"] is None
        assert rows[0]["email"] is None

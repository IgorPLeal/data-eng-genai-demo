"""Ponto de entrada da aplicação (Composition Root).

Responsável por instanciar e injetar todas as dependências,
clonar os datasets de exemplo e executar o pipeline.
"""

import os
import subprocess
import sys

from src.core.config import ConfigLoader
from src.data_io.data_io_manager import DataIOManager
from src.jobs.run_top_10 import RunTop10Job
from src.utils.pandas_manager import PandasManager


def clone_dataset(repo_url: str, local_path: str) -> None:
    """Clona um repositório de dataset se o diretório local não existir."""
    if os.path.isdir(local_path):
        print(f"Dataset já existe em '{local_path}'. Pulando clone.")
        return

    print(f"Clonando dataset de '{repo_url}' para '{local_path}'...")
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    subprocess.run(
        ["git", "clone", repo_url, local_path],
        check=True,
        capture_output=True,
        text=True,
    )
    print(f"Dataset clonado com sucesso em '{local_path}'.")


def main() -> None:
    """Função principal: composition root do pipeline."""
    # Determina a raiz do projeto
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(project_root)

    # 1. Carrega configuração
    config_loader = ConfigLoader()

    # 2. Inicializa PandasManager (configura Pandas + logging)
    pandas_manager = PandasManager(config_loader.logging_config)
    logger = pandas_manager.get_logger("main")

    # 3. Clona datasets de exemplo
    datasets_config = config_loader.datasets
    logger.info("Verificando datasets de exemplo...")
    clone_dataset(
        datasets_config["clientes_repo"],
        datasets_config["clientes_local"],
    )
    clone_dataset(
        datasets_config["pedidos_repo"],
        datasets_config["pedidos_local"],
    )

    # 4. Instancia DataIOManager com catálogo
    data_io = DataIOManager(
        catalogo=config_loader.catalogo,
        base_path=project_root,
    )

    # 5. Injeta dependências e executa o job
    job = RunTop10Job(data_io=data_io)
    job.execute()

    logger.info("Aplicação finalizada com sucesso.")


if __name__ == "__main__":
    sys.exit(main() or 0)

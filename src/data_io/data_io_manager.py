"""Módulo de abstração de I/O para leitura e escrita de dados."""

import glob
import logging
import os
from typing import Any, Dict

import pandas as pd

from src.core.exceptions import DataReadError, DataWriteError
from src.utils.logging_setup import LoggingSetup


class DataIOManager:
    """Gerencia leitura e escrita de DataFrames via catálogo de dados (Strategy Pattern)."""

    def __init__(self, catalogo: Dict[str, Any], base_path: str = "."):
        self._catalogo = catalogo
        self._base_path = base_path
        self._logger: logging.Logger = LoggingSetup.get_logger(self.__class__.__name__)

    def _resolve_path(self, relative_path: str) -> str:
        """Resolve um caminho relativo em relação ao base_path."""
        return os.path.join(self._base_path, relative_path)

    def read(self, dataset_id: str) -> pd.DataFrame:
        """Lê um dataset do catálogo pelo seu ID lógico.

        Args:
            dataset_id: Identificador lógico do dataset no catálogo.

        Returns:
            pd.DataFrame com os dados carregados.

        Raises:
            DataReadError: Se o dataset_id não existir no catálogo ou ocorrer erro de leitura.
        """
        if dataset_id not in self._catalogo:
            raise DataReadError(dataset_id, "Dataset não encontrado no catálogo.")

        config = self._catalogo[dataset_id]
        fmt = config.get("format", "csv")
        raw_path = config["path"]
        resolved_path = self._resolve_path(raw_path)

        self._logger.info(
            "Lendo dataset '%s' de '%s' (formato: %s)", dataset_id, resolved_path, fmt
        )

        try:
            if fmt == "json":
                return self._read_json(resolved_path, config)
            elif fmt == "csv":
                return self._read_csv(resolved_path, config)
            else:
                raise DataReadError(dataset_id, f"Formato '{fmt}' não suportado.")
        except DataReadError:
            raise
        except Exception as e:
            raise DataReadError(dataset_id, str(e)) from e

    def _read_json(self, path: str, config: Dict[str, Any]) -> pd.DataFrame:
        """Lê um arquivo JSON/JSON Lines."""
        lines = config.get("lines", True)
        orient = config.get("orient", "records")
        return pd.read_json(path, orient=orient, lines=lines)

    def _read_csv(self, path: str, config: Dict[str, Any]) -> pd.DataFrame:
        """Lê arquivo(s) CSV. Suporta glob_pattern para múltiplos arquivos."""
        separator = config.get("separator", ",")
        glob_pattern = config.get("glob_pattern")

        if glob_pattern:
            pattern = os.path.join(path, glob_pattern)
            files = sorted(glob.glob(pattern))
            if not files:
                raise DataReadError(
                    "csv",
                    f"Nenhum arquivo encontrado para o padrão '{pattern}'.",
                )
            self._logger.info("Encontrados %d arquivo(s) CSV.", len(files))
            dfs = [pd.read_csv(f, sep=separator) for f in files]
            return pd.concat(dfs, ignore_index=True)
        else:
            return pd.read_csv(path, sep=separator)

    def write(self, df: pd.DataFrame, dataset_id: str) -> None:
        """Escreve um DataFrame no destino definido pelo catálogo.

        Args:
            df: DataFrame a ser salvo.
            dataset_id: Identificador lógico do dataset de saída.

        Raises:
            DataWriteError: Se ocorrer erro na escrita.
        """
        if dataset_id not in self._catalogo:
            raise DataWriteError(dataset_id, "Dataset não encontrado no catálogo.")

        config = self._catalogo[dataset_id]
        fmt = config.get("format", "csv")
        raw_path = config["path"]
        resolved_path = self._resolve_path(raw_path)

        self._logger.info(
            "Escrevendo dataset '%s' em '%s' (formato: %s)",
            dataset_id,
            resolved_path,
            fmt,
        )

        try:
            os.makedirs(resolved_path, exist_ok=True)
            output_file = os.path.join(resolved_path, f"{dataset_id}.{fmt}")

            if fmt == "csv":
                separator = config.get("separator", ",")
                df.to_csv(output_file, sep=separator, index=False)
            elif fmt == "parquet":
                df.to_parquet(output_file, index=False)
            else:
                raise DataWriteError(dataset_id, f"Formato '{fmt}' não suportado.")

            self._logger.info(
                "Dataset '%s' salvo com sucesso em '%s'.", dataset_id, output_file
            )
        except DataWriteError:
            raise
        except Exception as e:
            raise DataWriteError(dataset_id, str(e)) from e

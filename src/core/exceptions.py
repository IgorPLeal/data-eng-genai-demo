"""Exceções customizadas para o pipeline de dados."""


class ConfigNotFoundError(Exception):
    """Exceção levantada quando o arquivo de configuração não é encontrado."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        super().__init__(f"Arquivo de configuração não encontrado: {config_path}")


class DataReadError(Exception):
    """Exceção levantada quando ocorre erro na leitura de dados."""

    def __init__(self, dataset_id: str, detail: str = ""):
        self.dataset_id = dataset_id
        msg = f"Erro ao ler dataset '{dataset_id}'"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class DataWriteError(Exception):
    """Exceção levantada quando ocorre erro na escrita de dados."""

    def __init__(self, dataset_id: str, detail: str = ""):
        self.dataset_id = dataset_id
        msg = f"Erro ao escrever dataset '{dataset_id}'"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)

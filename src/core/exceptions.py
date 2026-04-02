class ConfigNotFoundException(Exception):
    """Exceção lançada quando o arquivo config.yaml não é encontrado."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Arquivo de configuração não encontrado: {path}")


class DataSourceNotFoundException(Exception):
    """Exceção lançada quando uma fonte de dados não é encontrada no catálogo."""

    def __init__(self, source_id: str):
        self.source_id = source_id
        super().__init__(
            f"Fonte de dados '{source_id}' não encontrada no catálogo de dados."
        )


class TransformationException(Exception):
    """Exceção lançada quando ocorre um erro durante a transformação de dados."""

    def __init__(self, message: str):
        super().__init__(f"Erro na transformação: {message}")

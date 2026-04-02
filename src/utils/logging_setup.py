import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configura o logging padrão da aplicação.

    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Logger configurado para a aplicação.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger("top10_pipeline")
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# config/__init__.py
from .settings import get_config, update_config, SystemConfig, DATA_DIR, MODEL_DIR, INDEX_DIR

__all__ = ["get_config", "update_config", "SystemConfig", "DATA_DIR", "MODEL_DIR", "INDEX_DIR"]


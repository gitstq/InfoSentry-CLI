"""
InfoSentry-CLI: Lightweight Open Source Intelligence Aggregation & Analysis Engine
轻量级开源情报聚合与智能分析引擎

Author: gitstq
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .core.engine import InfoEngine
from .core.config import Config

__all__ = ["InfoEngine", "Config"]

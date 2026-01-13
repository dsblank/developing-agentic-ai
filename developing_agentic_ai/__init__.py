"""
developing-agentic-ai: A Python package for developing agentic AI systems.
"""

import warnings

from ._version import __version__

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic.main")

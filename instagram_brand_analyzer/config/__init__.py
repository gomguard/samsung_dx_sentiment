"""Instagram Brand Analyzer Configuration"""
from . import settings

try:
    from . import db_manager
except ImportError:
    # DB manager might not be available in all contexts
    pass

# routers/__init__.py
from .nid_router import router as nid_router
from .identity_router import router as identity_router
from .transaction_router import router as transaction_router
from .rules_router import router as rules_router
from .loan_router import router as loan_router

__all__ = ["nid_router", "identity_router", "transaction_router", "rules_router", "loan_router"]

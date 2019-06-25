import importlib

from .handler import TermxHandler  # noqa

components = importlib.import_module('.api', package=__name__)

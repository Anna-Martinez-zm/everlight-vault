"""Everlight — Configuration mirror, template library, and versioning system."""

__version__ = "0.5.0"
__author__ = "Everlight Vault Maintainers"
__all__ = ["ConfigMirror", "ConfigTemplate", "ConfigSnapshot", "TemplateLibrary"]

from .mirror import ConfigMirror, ConfigTemplate, ConfigSnapshot
from .library import TemplateLibrary

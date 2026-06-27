"""Template library — deduplication and organization of config snapshots."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from .mirror import ConfigSnapshot, ConfigTemplate, ConfigFormat


@dataclass
class TemplateLibrary:
    """Organizes configuration snapshots into deduplicated templates.

    Groups configs by key-set similarity, generates canonical templates
    with placeholder types, and tracks template usage frequency.
    """

    templates: Dict[str, ConfigTemplate] = field(default_factory=dict)
    _key_signatures: Dict[str, List[str]] = field(default_factory=dict)

    def ingest(self, snapshots: List[ConfigSnapshot]) -> int:
        """Ingest snapshots into the library, returning new templates created."""
        new_count = 0
        for snap in snapshots:
            sig = self._signature(snap)
            if sig in self._key_signatures:
                self._key_signatures[sig].append(snap.path)
                tpl = self.templates[sig]
                tpl.source_count += 1
            else:
                self._key_signatures[sig] = [snap.path]
                placeholders = {k: "str" for k in snap.keys}
                tpl = ConfigTemplate(
                    name=self._template_name(snap),
                    format=snap.format,
                    keys=snap.keys,
                    placeholders=placeholders,
                    raw_stripped=snap.anonymized,
                    source_count=1,
                )
                self.templates[sig] = tpl
                new_count += 1
        return new_count

    def most_common(self, n: int = 10) -> List[ConfigTemplate]:
        sorted_tpls = sorted(
            self.templates.values(), key=lambda t: -t.source_count
        )
        return sorted_tpls[:n]

    def by_format(self, fmt: ConfigFormat) -> List[ConfigTemplate]:
        return [t for t in self.templates.values() if t.format == fmt]

    @staticmethod
    def _signature(snap: ConfigSnapshot) -> str:
        return "|".join(sorted(snap.keys))

    @staticmethod
    def _template_name(snap: ConfigSnapshot) -> str:
        import hashlib
        h = hashlib.md5(snap.path.encode()).hexdigest()[:8]
        fmt = snap.format.name.lower()
        return f"{fmt}_{h}"

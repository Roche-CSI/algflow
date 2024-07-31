from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class CacheEntry:
    flushed: bool
    data: Any


@dataclass
class DataCache:
    cache_size: int = 1024*1024*1024  # 1GB
    entries: Dict[str, CacheEntry] = field(default_factory=dict)

    def set(self, name: str, value: Any, flushed: bool = True) -> Any:
        self.entries[name] = CacheEntry(flushed, value)
        return value

    def get(self, name: str) -> Any:
        return self.entries[name].data

    def iter_dirty_entries(self):
        for name, entry in self.entries.items():
            if not entry.flushed:
                yield name, entry

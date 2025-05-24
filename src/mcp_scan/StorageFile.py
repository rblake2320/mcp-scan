import json
import os
from datetime import datetime
from typing import Dict, Tuple

from .models import entity_type_to_str, hash_entity, Entity
from .utils import upload_whitelist_entry


class StorageFile:
    """Simplified storage handling for tests."""

    def __init__(self, path: str):
        self.path = os.path.expanduser(path)
        self.scanned_entities: Dict[str, Dict] = {}
        self.whitelist: Dict[str, str] = {}

        if os.path.isdir(self.path):
            self._load()

    def _load(self) -> None:
        se_path = os.path.join(self.path, "scanned_entities.json")
        if os.path.exists(se_path):
            with open(se_path, "r") as f:
                self.scanned_entities = json.load(f)
        wl_path = os.path.join(self.path, "whitelist.json")
        if os.path.exists(wl_path):
            with open(wl_path, "r") as f:
                self.whitelist = json.load(f)

    def reset_whitelist(self) -> None:
        self.whitelist = {}
        self.save()

    def check_and_update(self, server_name: str, entity: Entity, verified: bool | None) -> Tuple[bool, list[str]]:
        entity_type = entity_type_to_str(entity)
        key = f"{server_name}.{entity_type}.{entity.name}"
        hash_val = hash_entity(entity)
        new_data = {
            "hash": hash_val,
            "type": entity_type,
            "verified": verified,
            "timestamp": datetime.now().isoformat(),
            "description": getattr(entity, "description", None),
        }
        changed = False
        messages = []
        if key in self.scanned_entities:
            prev = self.scanned_entities[key]
            changed = prev.get("hash") != hash_val
            if changed:
                messages.append(f"Previous description ({prev.get('timestamp')})")
                messages.append(prev.get("description"))
        self.scanned_entities[key] = new_data
        return changed, messages

    def print_whitelist(self) -> None:
        for key in sorted(self.whitelist.keys()):
            if "." in key:
                entity_type, name = key.split(".", 1)
            else:
                entity_type, name = "tool", key
            print(entity_type, name, self.whitelist[key])
        print(f"{len(self.whitelist)} entries in whitelist")

    def add_to_whitelist(self, entity_type: str, name: str, hash_val: str, base_url: str | None = None) -> None:
        key = f"{entity_type}.{name}"
        self.whitelist[key] = hash_val
        self.save()
        if base_url is not None:
            try:
                import asyncio

                asyncio.run(upload_whitelist_entry(name, hash_val, base_url))
            except Exception:
                pass

    def is_whitelisted(self, entity: Entity) -> bool:
        return hash_entity(entity) in self.whitelist.values()

    def save(self) -> None:
        os.makedirs(self.path, exist_ok=True)
        with open(os.path.join(self.path, "scanned_entities.json"), "w") as f:
            json.dump(self.scanned_entities, f)
        with open(os.path.join(self.path, "whitelist.json"), "w") as f:
            json.dump(self.whitelist, f)

import os
import json
from datetime import datetime
from hashlib import md5
from dataclasses import asdict as dataclass_asdict
from .models import Result, Entity, entity_type_to_str, ScannedEntities, ScannedEntity
import rich
from .utils import upload_whitelist_entry
from typing import Any

class StorageFile:
    def __init__(self, path: str):
        self.path = os.path.expanduser(path)
        # if path is a file
        self.scanned_entities: ScannedEntities = {}
        self.whitelist: dict[str, str] = {}

        self.save_scanned_entities: bool = True
        if os.path.isfile(path):
            rich.print(f"[bold]Legacy storage file detected at {path}, converting to new format[/bold]")
            # legacy format
            with open(path, "r") as f:
                legacy_data = json.load(f)
            if "__whitelist" in legacy_data:
                self.whitelist = legacy_data["__whitelist"]
                del legacy_data["__whitelist"]
            # legacy files stored a dictionary of scanned entities
            try:
                self.scanned_entities = {
                    k: ScannedEntity(**v) for k, v in legacy_data.items()
                }
            except Exception as e:
                rich.print(f"[bold red]Error loading legacy storage file: {e}[/bold red]")
                rich.print(f"[bold red]Please fix the file {self.path}, or delete it.[/bold red]")
                self.save_scanned_entities = False
            os.remove(path)
        
        if os.path.exists(path) and os.path.isdir(path):
            scanned_entities_path = os.path.join(path, "scanned_entities.json")
            if os.path.exists(scanned_entities_path):
                with open(scanned_entities_path, "r") as f:
                    try:
                        data = json.load(f)
                        self.scanned_entities = {
                            k: ScannedEntity(**v) for k, v in data.items()
                        }
                    except Exception as e:
                        print(f"[bold red]Error loading scanned entities file: {e}[/bold red]")
                        rich.print(f"[bold red]Please fix the file {scanned_entities_path}, or delete it.[/bold red]")
                        self.save_scanned_entities = False
            if os.path.exists(os.path.join(path, "whitelist.json")):
                with open(os.path.join(path, "whitelist.json"), "r") as f:
                    self.whitelist = json.load(f)
    
    def reset_whitelist(self) -> None:
        self.whitelist = {}
        self.save()
        
    def compute_hash(self, entity: Entity) -> str:
        return md5((entity.description or "no description").encode()).hexdigest()

    def check_and_update(self, server_name: str, entity: Entity, verified: Any) -> tuple[Result, ScannedEntity | None]:
        entity_type = entity_type_to_str(entity)
        key = f"{server_name}.{entity_type}.{entity.name}"
        hash = self.compute_hash(entity)
        new_data = ScannedEntity(
            hash=hash,
            type=entity_type,
            verified=verified,
            timestamp=datetime.now(),
            description=entity.description,
        )
        changed = False
        message = None
        prev_data = None
        if key in self.scanned_entities:
            prev_data = self.scanned_entities[key]
            changed = prev_data.hash != new_data.hash
            if changed:
                message = (
                    f"{entity_type} description changed since previous scan at "
                    + prev_data.timestamp.strftime("%d/%m/%Y, %H:%M:%S")
                )
        self.scanned_entities[key] = new_data
        return Result(changed, message), prev_data

    def print_whitelist(self) -> None:
        whitelist_keys = sorted(self.whitelist.keys())
        for key in whitelist_keys:
            if "." in key:
                entity_type, name = key.split(".", 1)
            else:
                entity_type, name = "tool", key
            rich.print(entity_type, name, self.whitelist[key])
        rich.print(f"[bold]{len(whitelist_keys)} entries in whitelist[/bold]")

    def add_to_whitelist(self, entity_type: str, name: str, hash: str, base_url: str | None = None) -> None:
        key = f"{entity_type}.{name}"
        self.whitelist[key] = hash
        self.save()
        if base_url is not None:
            upload_whitelist_entry(
                name, hash, base_url
            )

    def is_whitelisted(self, entity: Entity) -> bool:
        hash = self.compute_hash(entity)
        return hash in self.whitelist.values()

    def save(self) -> None:
        os.makedirs(self.path, exist_ok=True)
        with open(os.path.join(self.path, "scanned_entities.json"), "w") as f:
            json.dump({k: dataclass_asdict(v) for k, v in self.scanned_entities.items()}, f)
        with open(os.path.join(self.path, "whitelist.json"), "w") as f:
            json.dump(self.whitelist, f)
        


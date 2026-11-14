"""Load synthetic personas and paste blocks from TOML files."""
from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Variants every persona file must author by hand. Programmatic variants
# (pasted, phone_style, format_json, empty) are derived in probes.py.
AUTHORED_VARIANTS = (
    "base", "flawed", "aae", "l2", "zh_formal", "zh_casual", "verbose", "ai_polished",
)


@dataclass(frozen=True)
class Variant:
    name: str
    messages: tuple[str, ...]
    review: str  # "authored" | "needs-native-review" | "reviewed" | ...

    @property
    def lang(self) -> str:
        return "zh" if self.name.startswith("zh_") else "en"


@dataclass(frozen=True)
class Persona:
    id: str
    title: str
    notes: str
    paste: str | None
    variants: dict[str, Variant]


@dataclass(frozen=True)
class Paste:
    id: str
    intro: str
    text: str


def load_personas(data_dir: Path = DATA_DIR) -> dict[str, Persona]:
    personas: dict[str, Persona] = {}
    for path in sorted((data_dir / "personas").glob("*.toml")):
        with path.open("rb") as f:
            raw = tomllib.load(f)
        pid = raw["id"]
        if pid in personas:
            raise ValueError(f"duplicate persona id {pid!r} in {path}")
        variants = {
            name: Variant(name=name, messages=tuple(v["messages"]), review=v.get("review", "unknown"))
            for name, v in raw.get("variants", {}).items()
        }
        missing = [v for v in AUTHORED_VARIANTS if v not in variants]
        if missing:
            raise ValueError(f"{path.name}: missing variants {missing}")
        personas[pid] = Persona(
            id=pid,
            title=raw.get("title", pid),
            notes=raw.get("notes", ""),
            paste=raw.get("paste"),
            variants=variants,
        )
    if not personas:
        raise FileNotFoundError(f"no persona files in {data_dir / 'personas'}")
    return personas


def load_pastes(data_dir: Path = DATA_DIR) -> dict[str, Paste]:
    path = data_dir / "pastes.toml"
    with path.open("rb") as f:
        raw = tomllib.load(f)
    return {
        pid: Paste(id=pid, intro=p["intro"], text=p["text"])
        for pid, p in raw.get("pastes", {}).items()
    }


def data_fingerprint(data_dir: Path = DATA_DIR) -> str:
    """Hash of every data file, stored with each run so results can be tied to the exact texts."""
    h = hashlib.sha256()
    for path in sorted(data_dir.rglob("*.toml")):
        h.update(path.relative_to(data_dir).as_posix().encode())
        h.update(path.read_bytes())
    return h.hexdigest()[:16]

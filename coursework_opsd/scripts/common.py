"""All writable state is confined to this assignment directory."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
for subdir in ("tmp", "cache", "config"):
    (RUNTIME / subdir).mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = str(RUNTIME / "tmp")
os.environ["SKILLNET_CONFIG"] = str(RUNTIME / "config" / "skillnet.json")
# Public retrieval needs no model credential or personal user configuration.
for name in ("API_KEY", "BASE_URL", "GITHUB_TOKEN", "GITHUB_MIRROR", "SKILLNET_MODEL"):
    os.environ.pop(name, None)


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

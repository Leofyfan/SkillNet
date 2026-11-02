"""Create a portable submission ZIP; never includes environments or caches."""
import json
import os
import re
import zipfile
from datetime import datetime
from pathlib import Path

from common import ROOT, now, save, sha256


def included(path):
    parts = path.relative_to(ROOT).parts
    return (path.is_file() and not path.is_symlink()
            and not any(p in {".venv", ".runtime", "__pycache__", "build", "dist"}
                        or p.endswith(".egg-info") for p in parts)
            and path.name not in {"submission.zip", "submission.zip.sha256", "manifest.sha256", "package_check.json"}
            and path.suffix not in {".pyc", ".pyo"})


def main():
    validation = json.loads((ROOT / "logs/verification.json").read_text())
    if validation["status"] != "passed":
        raise ValueError("Run verify_submission.py successfully before packaging")
    start = datetime.fromisoformat((ROOT / "logs/started_at.txt").read_text().strip().replace("Z", "+00:00"))
    finish = datetime.fromisoformat(now())
    save("logs/usage_summary.json", dict(
        started_at=start.isoformat(), packaged_at=finish.isoformat(),
        elapsed_wall_seconds=round((finish-start).total_seconds(), 1),
        timing_scope="Current implementation turn, including setup, tools and waiting; excludes the earlier planning turn.",
        formal_sdk_search_calls=2, sdk_download_calls=1,
        observed_sdk_call_seconds=sum(json.loads((ROOT/p).read_text())["elapsed_seconds"] for p in
          ["outputs/search_round_1.json", "outputs/search_round_2.json", "outputs/download.json"]),
        candidate_inspection_attempts=3, candidate_content_successes=2,
        connectivity_search_endpoint_attempts=2,
        agent_model_requests=None, agent_tokens=None, agent_billed_cost=None,
        unavailable_usage_reason="The current Codex host does not expose exact routed model ID, per-task tokens or billing.",
        human_intervention="User chose paper and scope; no student review or question confirmation claimed."))
    paths = sorted(p for p in ROOT.rglob("*") if included(p))
    # Do not print possible credential matches or values.
    sensitive_values = [v.encode() for k, v in os.environ.items()
                        if any(s in k.upper() for s in ("API_KEY", "TOKEN", "SECRET")) and len(v) >= 16]
    for p in paths:
        if p.name in {".env", "credentials.json", "config.json"}:
            raise ValueError("Unexpected private configuration file in package inputs")
        raw = p.read_bytes()
        if any(value in raw for value in sensitive_values):
            raise ValueError("Potential environment credential found in package inputs")
        if p.suffix in {".py", ".sh", ".md", ".json", ".log", ".txt"} and re.search(
                rb"(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)", raw):
            raise ValueError("Potential credential pattern in package inputs")
    manifest = ROOT / "manifest.sha256"
    manifest.write_text("".join(f"{sha256(p)}  {p.relative_to(ROOT).as_posix()}\n" for p in paths))
    archive = ROOT / "submission.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for p in paths + [manifest]:
            output.write(p, Path(ROOT.name) / p.relative_to(ROOT))
    with zipfile.ZipFile(archive) as packaged:
        if packaged.testzip() is not None:
            raise ValueError("ZIP CRC check failed")
        for line in manifest.read_text().splitlines():
            digest, relative = line.split("  ", 1)
            import hashlib
            if hashlib.sha256(packaged.read(f"{ROOT.name}/{relative}")).hexdigest() != digest:
                raise ValueError("Packaged hash mismatch")
        members = len(packaged.namelist())
    (ROOT / "submission.zip.sha256").write_text(f"{sha256(archive)}  submission.zip\n")
    result = dict(checked_at=now(), status="passed", members=members,
                  archive_size_bytes=archive.stat().st_size, archive_sha256=sha256(archive),
                  checks=["credentials/configuration exclusion", "ZIP CRC", "all packaged manifest hashes"],
                  excludes=["virtual environment", "runtime/cache", "bytecode", "build/egg-info", "ZIP itself"])
    save("logs/package_check.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

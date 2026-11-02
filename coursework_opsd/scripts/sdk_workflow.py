"""Real SkillNet SDK search/download; preserves results and does not rerun successes."""
import argparse
import json
import time

from common import ROOT, now, save, sha256
from skillnet_ai import SkillNetClient


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    search = sub.add_parser("search")
    search.add_argument("--round", type=int, choices=(1, 2), required=True)
    search.add_argument("--query", required=True)
    search.add_argument("--mode", choices=("keyword", "vector"), default="keyword")
    search.add_argument("--endpoint", default="http://api-skillnet.openkg.cn")
    download = sub.add_parser("download")
    download.add_argument("--url", required=True)
    args = parser.parse_args()
    started, stamp = time.monotonic(), now()
    if args.action == "search":
        output = f"outputs/search_round_{args.round}.json"
        if (ROOT / output).exists():
            print("Cached result:", output)
            return
        params = dict(q=args.query, mode=args.mode, limit=3)
        if args.mode == "vector":
            params["threshold"] = 0.6
        record = dict(started_at=stamp, endpoint=args.endpoint, sdk="skillnet-ai 0.1.4", parameters=params)
        try:
            skills = SkillNetClient(skillnet_api_url=args.endpoint).search(**params)
            record.update(status="success", results=[s.model_dump(mode="json") for s in skills])
        except Exception as exc:
            record.update(status="error", error_type=type(exc).__name__, error=str(exc))
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        save(output, record)
        print(json.dumps(record, ensure_ascii=False, indent=2))
        if record["status"] == "error":
            raise SystemExit(1)
    else:
        output = "outputs/download.json"
        if (ROOT / output).exists():
            previous = json.loads((ROOT / output).read_text())
            if previous["status"] == "success":
                print("Cached download:", previous["installed_relative_path"])
                return
        record = dict(started_at=stamp, source=args.url)
        try:
            path = SkillNetClient().download(url=args.url, target_dir=str(ROOT / "skills"))
            from pathlib import Path
            package = Path(path)
            record.update(status="success", installed_relative_path=str(package.relative_to(ROOT)),
                          files={str(p.relative_to(package)): sha256(p) for p in package.rglob("*") if p.is_file()})
        except Exception as exc:
            record.update(status="error", error_type=type(exc).__name__, error=str(exc))
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        save(output, record)
        print(json.dumps(record, ensure_ascii=False, indent=2))
        if record["status"] == "error":
            raise SystemExit(1)


if __name__ == "__main__":
    main()

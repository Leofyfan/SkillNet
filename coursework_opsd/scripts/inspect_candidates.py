"""Snapshot at most three SDK candidates, resolving GitHub refs to commits."""
import argparse
import json
import urllib.parse
import urllib.request

from common import ROOT, now, save, sha256


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "SkillNet-coursework/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=int, choices=(1, 2), required=True)
    parser.add_argument("--indices", type=int, nargs="+", required=True)
    args = parser.parse_args()
    destination = ROOT / "outputs/candidate_inspection.json"
    records = json.loads(destination.read_text()) if destination.exists() else []
    search = json.loads((ROOT / f"outputs/search_round_{args.round}.json").read_text())
    if search["status"] != "success":
        raise ValueError("Search did not succeed")
    if any(i < 1 or i > len(search["results"]) for i in args.indices):
        raise ValueError("Candidate index out of range")
    for index in args.indices:
        if any(r["round"] == args.round and r["index"] == index for r in records):
            continue
        if len(records) >= 3:
            raise ValueError("The three-candidate inspection budget is exhausted")
        item = search["results"][index - 1]
        record = dict(round=args.round, index=index, skill_name=item["skill_name"], source=item["skill_url"], inspected_at=now())
        try:
            url = urllib.parse.urlsplit(item["skill_url"])
            parts = url.path.strip("/").split("/")
            if url.hostname != "github.com" or parts[2] not in ("tree", "blob"):
                raise ValueError("Candidate is not a GitHub skill directory")
            owner, repo, _, ref, *subpath = parts
            folder = "/".join(subpath)
            if folder.endswith("/SKILL.md"):
                folder = folder[:-len("/SKILL.md")]
            commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{urllib.parse.quote(ref, safe='')}"
            commit = json.loads(fetch(commit_url))["sha"]
            content_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{folder}/SKILL.md"
            content = fetch(content_url)
            path = ROOT / f"candidates/round{args.round}_{index:02}_{item['skill_name']}/SKILL.md"
            # Candidate names are untrusted catalog data: enforce containment.
            if not path.resolve().is_relative_to(ROOT / "candidates"):
                raise ValueError("Invalid candidate path")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            record.update(status="success", commit=commit,
                          pinned_url=f"https://github.com/{owner}/{repo}/tree/{commit}/{folder}",
                          file=str(path.relative_to(ROOT)), sha256=sha256(path))
        except Exception as exc:
            record.update(status="error", error_type=type(exc).__name__, error=str(exc))
        records.append(record)
        # Persist each candidate so partial progress survives a later network failure.
        save("outputs/candidate_inspection.json", records)
    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

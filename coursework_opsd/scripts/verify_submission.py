"""Offline checks of actual evidence and package structure; no model requests."""
import json
import platform
import re
import sys
from decimal import Decimal
from importlib.metadata import version

from common import ROOT, now, save, sha256
import pymupdf
from skillnet_ai.core.validation import validate_skill


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    checks = []
    source = json.loads((ROOT / "materials/source.json").read_text())
    pdf = ROOT / "materials/2601.18734v3.pdf"
    require(sha256(pdf) == source["sha256"], "Paper hash mismatch")
    checks.append("fixed-version paper hash")
    download = json.loads((ROOT / "outputs/download.json").read_text())
    require(download["status"] == "success", "SDK download did not succeed")
    package = ROOT / download["installed_relative_path"]
    for name, digest in download["files"].items():
        require(sha256(package / name) == digest, f"Skill file changed: {name}")
    validation = validate_skill(package)
    require(validation["valid"], f"Invalid skill: {validation}")
    checks.append("downloaded skill hashes and SDK structure validation")
    candidates = json.loads((ROOT / "outputs/candidate_inspection.json").read_text())
    require(len(candidates) <= 3, "Too many candidates inspected")
    for r in candidates:
        if r["status"] == "success":
            require(sha256(ROOT / r["file"]) == r["sha256"], "Candidate hash mismatch")
    searches = sorted((ROOT / "outputs").glob("search_round_*.json"))
    require(len(searches) <= 2, "Too many formal SDK search rounds")
    require(all(json.loads(p.read_text())["status"] == "success" for p in searches), "Search error")
    checks.append("two successful SDK searches; three candidate inspection attempts")

    with pymupdf.open(pdf) as doc:
        require(len(doc) == 15, "Unexpected paper page count")
        table = doc[6].get_text()
        block = table.split("Qwen3-1.7B", 1)[1].split("esize", 1)[0]
        values = re.findall(r"(?m)^\d+\.\d+$", block)
        expected = ["51.5", "36.7", "23.1", "37.1", "48.4", "36.3", "22.7", "35.8",
                    "51.1", "38.3", "23.7", "37.7", "57.2", "43.9", "29.2", "43.4"]
        require(values == expected, f"Unexpected Table 2 extraction: {values}")
        require(Decimal(values[15]) - Decimal(values[11]) == Decimal("5.7"), "GRPO difference")
        require(Decimal(values[15]) - Decimal(values[3]) == Decimal("6.3"), "Base difference")
        implementation = " ".join(doc[5].get_text().split())
        require("We fix the teacher policy to be the initial policy" in implementation, "Teacher evidence absent")
    save("evidence/table2_1p7b_values.json", dict(
        source="materials/2601.18734v3.pdf", pdf_page=7, table=2,
        columns=["AIME24", "AIME25", "HMMT25", "Average"],
        rows={label: expected[i*4:i*4+4] for i, label in enumerate(["Base", "SFT", "GRPO", "OPSD"])},
        opsd_minus_grpo_pp="5.7", opsd_minus_base_pp="6.3",
        note="Numeric extraction check; semantic and comparison-condition checks remain in claim_checks.md."))
    checks.append("Table 2 numbers extracted directly from PDF and differences recomputed")
    checks.append("teacher implementation sentence located on PDF page 6")

    required = ["README.md", "report.md", "outputs/skill_selection.md", "outputs/reading_notes.md",
                "outputs/claim_checks.md", "outputs/critical_analysis.md", "outputs/followup_question.md",
                "prompts/read_paper.md", "prompts/check_claims.md", "requirements.lock.txt"]
    for relative in required:
        require((ROOT / relative).is_file() and (ROOT / relative).stat().st_size > 0, f"Missing {relative}")
    for path in list(ROOT.glob("*.md")) + list((ROOT / "outputs").glob("*.md")):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            require((path.parent / target.split("#")[0]).exists(), f"Broken local link in {path.name}: {target}")
    checks.append("required artifacts and local Markdown links")
    for path in (ROOT / "scripts").glob("*.py"):
        compile(path.read_text(), str(path), "exec")
    checks.append("Python script syntax")
    save("logs/environment.json", dict(python=sys.version.split()[0], operating_system=platform.system(),
         release=platform.release(), architecture=platform.machine(),
         skillnet_ai=version("skillnet-ai"), pymupdf=version("pymupdf"),
         agent="Current Codex conversation; GPT-6 family per system role; exact deployed model ID unavailable",
         configuration="Public SkillNet search and public GitHub download; no model endpoint credentials"))
    result = dict(checked_at=now(), status="passed", checks=checks, skill_validation=validation,
                  limitation="Offline artifact checks do not reproduce OPSD training or provide independent human review.")
    save("logs/verification.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

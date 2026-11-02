"""Download the fixed version and create per-page text and evidence images."""
import urllib.request

from common import ROOT, now, save, sha256


def main():
    import pymupdf

    url = "https://arxiv.org/pdf/2601.18734v3"
    pdf = ROOT / "materials/2601.18734v3.pdf"
    if not pdf.exists():
        request = urllib.request.Request(url, headers={"User-Agent": "SkillNet-coursework/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
        if not data.startswith(b"%PDF"):
            raise ValueError("The downloaded response is not a PDF")
        pdf.write_bytes(data)
        save("materials/source.json", dict(url=url, retrieved_at=now(), sha256=sha256(pdf)))
    with pymupdf.open(pdf) as document:
        pages = []
        for index, page in enumerate(document, 1):
            # Preserve PDF text-block order. Coordinate sorting interleaves the
            # two columns in this paper and damages formulas and table headers.
            text = page.get_text(sort=False)
            (ROOT / f"materials/page_{index:02}.txt").write_text(text, encoding="utf-8")
            pages.append(f"\n===== PDF PAGE {index} =====\n{text}")
        (ROOT / "materials/paper.txt").write_text("\n".join(pages), encoding="utf-8")
        for index in (4, 5, 6, 7, 13, 14):
            document[index - 1].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(
                ROOT / f"evidence/page_{index:02}.png")
        print(f"PDF: {len(document)} pages; SHA-256 {sha256(pdf)}")


if __name__ == "__main__":
    main()

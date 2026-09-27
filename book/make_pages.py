"""Generate the Jupyter Book (MyST) pages from the repository: one page per slide figure.

Each page = the folder README + its figure + every script in the folder, included from the
repository files so the book never drifts from the code. Nothing is re-run here: the figure
pipelines need large downloads and credentials (see each README). Output: _pages/ (gitignored).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_pages"
LANG = {".py": "python", ".sh": "bash", ".yml": "yaml"}


def table_rows():
    rows = []
    for line in (ROOT / "README.md").read_text().splitlines():
        if line.startswith("| ") and "`" in line and not line.startswith("| Slide"):
            c = [x.strip() for x in line.strip("|").split("|")]
            rows.append((c[0].replace("*", ""), c[1].replace("*", ""), c[2].strip("`")))
    return rows


def body_without_title(readme: Path) -> tuple[str, str]:
    title, _, rest = readme.read_text().partition("\n")
    return title.lstrip("# ").strip(), rest.strip("\n")


def fence_indented(md: str) -> str:
    """Markdown indented code blocks (4 spaces after a blank line) -> fenced blocks; MyST has no indented code."""
    out, block, prev_blank = [], [], True
    for line in md.splitlines() + [""]:
        if line.startswith("    ") and (block or prev_blank):
            block.append(line[4:])
            continue
        if block:
            out += ["```bash", *block, "```"]
            block = []
        out.append(line)
        prev_blank = not line.strip()
    return "\n".join(out)


def figure_of(folder: Path):
    for sub in ("figure", "reference"):
        pngs = sorted((folder / sub).glob("*.png"))
        if pngs:
            return pngs[0]
    return None


def code_blocks(folder: Path, rel: str) -> str:
    out = []
    for f in sorted(p for p in folder.iterdir() if p.suffix in LANG and p.is_file()):
        out.append(f"### `{f.name}`\n\n```{{literalinclude}} ../{rel}/{f.name}\n:language: {LANG[f.suffix]}\n```\n")
    return "\n".join(out)


def page(folder_name: str, heading: str) -> str:
    folder = ROOT / folder_name
    title, body = body_without_title(folder / "README.md")
    body = fence_indented(body)
    # README-relative links and images point into the folder
    body = re.sub(r"\]\((?!https?://|#)([^)]+)\)", rf"](../{folder_name}/\1)", body)
    parts = [f"# {heading}\n", f"*{title}*\n", f"Source folder: [`{folder_name}/`](https://github.com/annefou/esa-frontiers-figures/tree/main/{folder_name})\n"]
    fig = figure_of(folder)
    if fig:
        parts.append(f"```{{figure}} ../{folder_name}/{fig.parent.name}/{fig.name}\n:width: 100%\n```\n")
    parts += ["## About this figure\n", body + "\n"]
    code = code_blocks(folder, folder_name)
    if code:
        parts += ["## Code\n", code]
    return "\n".join(parts)


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()
    rows = table_rows()
    for slide, title, folder in rows:
        (OUT / f"{folder}.md").write_text(page(folder, f"Slide {slide}: {title}"))
    (OUT / "beni-pipeline.md").write_text(page("beni-pipeline", "Beni lowlands pipeline (WGS84 HEALPix)"))
    # landing page: the repo README with folder names linked to their pages
    readme = (ROOT / "README.md").read_text()
    for _, _, folder in rows + [("", "", "beni-pipeline")]:
        readme = readme.replace(f"| `{folder}` |", f"| [{folder}]({folder}.md) |")
    readme = re.sub(r"\]\((DATA_LICENSES\.md|LICENSE|CITATION\.cff)\)", r"](https://github.com/annefou/esa-frontiers-figures/blob/main/\1)", readme)
    readme = re.sub(r" @([0-9a-f]{7})\b", r" at commit `\1`", readme)  # not MyST citations
    (OUT / "index.md").write_text(readme)


    print(f"{len(rows) + 2} pages written to {OUT}")


if __name__ == "__main__":
    main()

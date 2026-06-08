import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def iter_markdown_files():
    top_level = [
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "SECURITY.md",
        ROOT / "CODE_OF_CONDUCT.md",
        ROOT / "ROADMAP.md",
        ROOT / "CHANGELOG.md",
    ]
    yield from (path for path in top_level if path.exists())
    yield from sorted((ROOT / "docs").glob("*.md"))


def is_external_link(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def normalize_target(target: str) -> str:
    path_part = target.split("#", 1)[0].strip()
    if path_part.startswith("<") and path_part.endswith(">"):
        path_part = path_part[1:-1]
    return path_part


class DocumentationLinkTests(unittest.TestCase):
    def test_relative_markdown_links_exist(self):
        missing = []
        for markdown_path in iter_markdown_files():
            text = markdown_path.read_text(encoding="utf-8")
            for match in MARKDOWN_LINK.finditer(text):
                target = normalize_target(match.group(1))
                if not target or is_external_link(target):
                    continue
                resolved = (markdown_path.parent / target).resolve()
                try:
                    resolved.relative_to(ROOT)
                except ValueError:
                    missing.append(f"{markdown_path.relative_to(ROOT)} -> {target}")
                    continue
                if not resolved.exists():
                    missing.append(f"{markdown_path.relative_to(ROOT)} -> {target}")

        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()

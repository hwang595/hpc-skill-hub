#!/usr/bin/env python3
"""Build a static HTML registry site from registry/index.json."""

from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "registry" / "index.json"
DEFAULT_OUTPUT = ROOT / "site" / "index.html"
SUPPORT_PATHS = ["README.md", "LICENSE", "docs", "skills", "site-adapters", "registry"]


def load_index() -> Dict[str, Any]:
    with INDEX_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def badge(value: str, css_class: str = "") -> str:
    class_attr = f" badge-{css_class}" if css_class else ""
    return f'<span class="badge{class_attr}">{esc(value)}</span>'


def skill_rows(skills: List[Dict[str, Any]]) -> str:
    rows = []
    for skill in skills:
        categories = " ".join(badge(category) for category in skill["categories"])
        tags = " ".join(badge(tag, "tag") for tag in skill["tags"][:6])
        rows.append(
            f"""
            <tr data-search="{esc(' '.join([skill['id'], skill['name'], skill['summary'], ' '.join(skill['categories']), ' '.join(skill['tags'])]).lower())}">
              <td><a href="{esc(skill['readme'])}">{esc(skill['id'])}</a></td>
              <td>{esc(skill['summary'])}</td>
              <td>{badge(skill['risk_level'], skill['risk_level'])}</td>
              <td>{badge(skill['maturity'])}</td>
              <td>{categories}</td>
              <td>{tags}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def adapter_rows(adapters: List[Dict[str, Any]]) -> str:
    rows = []
    for adapter in adapters:
        rows.append(
            f"""
            <tr>
              <td><a href="{esc(adapter['readme'])}">{esc(adapter['id'])}</a></td>
              <td>{esc(adapter['summary'])}</td>
              <td>{badge(adapter['status'])}</td>
              <td>{esc(adapter['scheduler'])}</td>
              <td>{', '.join(esc(partition) for partition in adapter['partitions'])}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def stats(index: Dict[str, Any]) -> str:
    category_bits = " ".join(
        f"{badge(category)} <span class=\"count\">{count}</span>"
        for category, count in index["categories"].items()
    )
    return f"""
    <section class="stats" aria-label="Registry statistics">
      <div><strong>{index['skill_count']}</strong><span>Skills</span></div>
      <div><strong>{index['site_adapter_count']}</strong><span>Site adapters</span></div>
      <div><strong>{len(index['tools'])}</strong><span>Tools referenced</span></div>
      <div class="categories">{category_bits}</div>
    </section>
    """


def render(index: Dict[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HPC Skill Hub Registry</title>
  <style>
    :root {{
      --bg: #f7f8fb;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #5f6b7a;
      --line: #d9dee7;
      --accent: #0f766e;
      --accent-2: #2563eb;
      --warn: #a16207;
      --danger: #b42318;
      --ok: #0b6b3a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--text);
      background: var(--bg);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    header {{
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }}
    .wrap {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
    }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 0;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }}
    .mark {{
      width: 38px;
      height: 38px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      color: white;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      font-weight: 800;
    }}
    h1 {{
      margin: 0;
      font-size: 1.35rem;
      letter-spacing: 0;
    }}
    .subtitle {{
      color: var(--muted);
      margin: 2px 0 0;
      font-size: .95rem;
    }}
    nav {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    a {{ color: #1d4ed8; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    main {{ padding: 24px 0 42px; }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(120px, 1fr)) 2fr;
      gap: 12px;
      margin-bottom: 22px;
    }}
    .stats > div {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .stats strong {{
      display: block;
      font-size: 1.55rem;
    }}
    .stats span {{ color: var(--muted); }}
    .categories {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .count {{
      margin-right: 8px;
      font-size: .85rem;
    }}
    .toolbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 20px 0 10px;
    }}
    input[type="search"] {{
      width: min(420px, 100%);
      padding: 9px 11px;
      border: 1px solid var(--line);
      border-radius: 6px;
      font: inherit;
      background: white;
    }}
    h2 {{
      margin: 0;
      font-size: 1.05rem;
      letter-spacing: 0;
    }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 860px;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: .92rem;
    }}
    th {{
      color: var(--muted);
      background: #fbfcfe;
      font-weight: 650;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .badge {{
      display: inline-block;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 7px;
      margin: 0 3px 3px 0;
      color: #344054;
      background: #f8fafc;
      font-size: .78rem;
      white-space: nowrap;
    }}
    .badge-tag {{ background: #eef6ff; border-color: #cfe4ff; }}
    .badge-low {{ color: var(--ok); background: #ecfdf3; border-color: #b7e5c8; }}
    .badge-medium {{ color: var(--warn); background: #fffbeb; border-color: #f4d58d; }}
    .badge-high {{ color: var(--danger); background: #fff1f0; border-color: #f3b8b2; }}
    .section {{ margin-top: 26px; }}
    footer {{
      border-top: 1px solid var(--line);
      background: var(--panel);
      color: var(--muted);
      padding: 16px 0;
      font-size: .9rem;
    }}
    @media (max-width: 800px) {{
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .stats {{ grid-template-columns: 1fr; }}
      .toolbar {{ align-items: flex-start; flex-direction: column; }}
      h1 {{ font-size: 1.2rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <div class="brand">
        <div class="mark" aria-hidden="true">H</div>
        <div>
          <h1>HPC Skill Hub Registry</h1>
          <p class="subtitle">Reusable skills for HPC workflows, site policy, and operational debugging.</p>
        </div>
      </div>
      <nav aria-label="Project links">
        <a href="README.md">README</a>
        <a href="docs/SKILL_SPEC.md">Skill spec</a>
        <a href="docs/SITE_ADAPTERS.md">Site adapters</a>
        <a href="docs/ECOSYSTEM_PROPOSAL.md">Proposal</a>
      </nav>
    </div>
  </header>
  <main class="wrap">
    {stats(index)}
    <section class="section" aria-labelledby="skills-heading">
      <div class="toolbar">
        <h2 id="skills-heading">Skills</h2>
        <input id="skill-search" type="search" placeholder="Filter skills by id, tag, tool, or summary" aria-label="Filter skills">
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Skill</th>
              <th>Summary</th>
              <th>Risk</th>
              <th>Maturity</th>
              <th>Categories</th>
              <th>Tags</th>
            </tr>
          </thead>
          <tbody id="skill-table">
            {skill_rows(index['skills'])}
          </tbody>
        </table>
      </div>
    </section>
    <section class="section" aria-labelledby="adapters-heading">
      <div class="toolbar">
        <h2 id="adapters-heading">Site Adapters</h2>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Adapter</th>
              <th>Summary</th>
              <th>Status</th>
              <th>Scheduler</th>
              <th>Partitions</th>
            </tr>
          </thead>
          <tbody>
            {adapter_rows(index['site_adapters'])}
          </tbody>
        </table>
      </div>
    </section>
  </main>
  <footer>
    <div class="wrap">
      Generated by <code>tools/build_site.py</code> from <code>registry/index.json</code>.
    </div>
  </footer>
  <script>
    const input = document.getElementById('skill-search');
    const rows = Array.from(document.querySelectorAll('#skill-table tr'));
    input.addEventListener('input', () => {{
      const query = input.value.trim().toLowerCase();
      rows.forEach((row) => {{
        row.hidden = query && !row.dataset.search.includes(query);
      }});
    }});
  </script>
</body>
</html>
"""


def copy_supporting_content(site_root: Path) -> None:
    for relative in SUPPORT_PATHS:
        source = ROOT / relative
        target = site_root / relative
        if not source.exists():
            continue
        if source.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the static HPC Skill Hub site")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output HTML path")
    parser.add_argument(
        "--no-copy-content",
        action="store_true",
        help="Only write index.html; do not copy docs, skills, and registry content",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(load_index()), encoding="utf-8")
    if not args.no_copy_content:
        copy_supporting_content(output.parent)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

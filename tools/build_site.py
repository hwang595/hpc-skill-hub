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
SUPPORT_PATHS = [
    "README.md",
    "LICENSE",
    "assets",
    "benchmarks",
    "docs",
    "collections",
    "skills",
    "site-adapters",
    "registry",
]


def load_index() -> Dict[str, Any]:
    with INDEX_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def badge(value: str, css_class: str = "") -> str:
    class_attr = f" badge-{css_class}" if css_class else ""
    return f'<span class="badge{class_attr}">{esc(value)}</span>'


def skill_collection_membership(index: Dict[str, Any]) -> Dict[str, List[str]]:
    membership: Dict[str, List[str]] = {}
    for collection in index.get("collections", []):
        for skill_id in collection.get("skill_ids", []):
            membership.setdefault(skill_id, []).append(collection["id"])
    return {skill_id: sorted(collections) for skill_id, collections in membership.items()}


def data_attr_values(values: List[str]) -> str:
    return "|".join(value.lower() for value in values)


def option_tags(values: List[str], label: str) -> str:
    options = [f'<option value="">{esc(label)}</option>']
    for value in values:
        options.append(f'<option value="{esc(value.lower())}">{esc(value)}</option>')
    return "\n".join(options)


def filter_controls(index: Dict[str, Any]) -> str:
    schedulers = sorted(index["schedulers"])
    tools = sorted(index["tools"], key=str.lower)
    collections = sorted(collection["id"] for collection in index["collections"])
    return f"""
    <div class="filters" aria-label="Skill filters">
      <input id="skill-search" type="search" placeholder="Search id, tag, tool, or summary" aria-label="Search skills">
      <select id="filter-risk" aria-label="Filter by risk">
        {option_tags(['low', 'medium', 'high'], 'All risk levels')}
      </select>
      <select id="filter-maturity" aria-label="Filter by maturity">
        {option_tags(['seed', 'reviewed', 'field-tested', 'maintained'], 'All maturity')}
      </select>
      <select id="filter-category" aria-label="Filter by category">
        {option_tags(sorted(index['categories']), 'All categories')}
      </select>
      <select id="filter-scheduler" aria-label="Filter by scheduler">
        {option_tags(schedulers, 'All schedulers')}
      </select>
      <select id="filter-tool" aria-label="Filter by tool">
        {option_tags(tools, 'All tools')}
      </select>
      <select id="filter-collection" aria-label="Filter by collection">
        {option_tags(collections, 'All collections')}
      </select>
      <button id="clear-filters" type="button">Clear</button>
    </div>
    """


def skill_rows(skills: List[Dict[str, Any]], membership: Dict[str, List[str]]) -> str:
    rows = []
    for skill in skills:
        categories = " ".join(badge(category) for category in skill["categories"])
        tags = " ".join(badge(tag, "tag") for tag in skill["tags"][:6])
        schedulers = (
            " ".join(badge(scheduler) for scheduler in skill["schedulers"])
            if skill["schedulers"]
            else '<span class="muted">agnostic</span>'
        )
        collections = membership.get(skill["id"], [])
        search_text = " ".join(
            [
                skill["id"],
                skill["name"],
                skill["summary"],
                skill["description"],
                " ".join(skill["categories"]),
                " ".join(skill["tags"]),
                " ".join(skill["tools"]),
                " ".join(skill["schedulers"]),
                " ".join(collections),
            ]
        ).lower()
        rows.append(
            f"""
            <tr
              data-search="{esc(search_text)}"
              data-risk="{esc(skill['risk_level'].lower())}"
              data-maturity="{esc(skill['maturity'].lower())}"
              data-status="{esc(skill['status'].lower())}"
              data-categories="{esc(data_attr_values(skill['categories']))}"
              data-schedulers="{esc(data_attr_values(skill['schedulers']))}"
              data-tools="{esc(data_attr_values(skill['tools']))}"
              data-collections="{esc(data_attr_values(collections))}">
              <td><a href="{esc(skill['readme'])}">{esc(skill['id'])}</a></td>
              <td>{esc(skill['summary'])}</td>
              <td>{badge(skill['risk_level'], skill['risk_level'])}</td>
              <td>{badge(skill['maturity'])}</td>
              <td>{schedulers}</td>
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


def collection_rows(collections: List[Dict[str, Any]]) -> str:
    rows = []
    for collection in collections:
        rows.append(
            f"""
            <tr>
              <td><a href="{esc(collection['path'])}">{esc(collection['id'])}</a></td>
              <td>{esc(collection['summary'])}</td>
              <td>{badge(collection['status'])}</td>
              <td>{len(collection['skill_ids'])}</td>
              <td>{', '.join(esc(item) for item in collection['audience'])}</td>
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
      <div><strong>{index['collection_count']}</strong><span>Collections</span></div>
      <div><strong>{len(index['tools'])}</strong><span>Tools referenced</span></div>
      <div class="categories">{category_bits}</div>
    </section>
    """


def ecosystem_paths() -> str:
    paths = [
        (
            "Adopt",
            "Start with a curated collection, run public-safe checks, and share an adoption report.",
            "docs/ADOPTER_PLAYBOOK.md",
            "Adopter playbook",
        ),
        (
            "Contribute",
            "Request or author a skill with clear scope, conservative examples, and public references.",
            "docs/SKILL_LIFECYCLE.md",
            "Skill lifecycle",
        ),
        (
            "Adapt",
            "Map portable skills to public local policy without forking the core registry.",
            "docs/SITE_ADAPTERS.md",
            "Site adapters",
        ),
        (
            "Integrate",
            "Consume registry JSON, schemas, and CLI output from portals, assistants, and workflow tools.",
            "docs/INTEGRATION_GUIDE.md",
            "Integration guide",
        ),
    ]
    cards = []
    for title, text, href, cta in paths:
        cards.append(
            f"""
            <li>
              <strong>{esc(title)}</strong>
              <span>{esc(text)}</span>
              <a href="{esc(href)}">{esc(cta)}</a>
            </li>
            """
        )
    return "\n".join(cards)


def contribution_lanes() -> str:
    lanes = [
        ("Skill request", "docs/SKILL_LIFECYCLE.md"),
        ("Site adapter request", "docs/SITE_ADAPTERS.md"),
        ("Integration request", "docs/INTEGRATION_GUIDE.md"),
        ("Adoption report", "docs/ADOPTER_PLAYBOOK.md"),
        ("Safety review", "docs/SAFETY_MODEL.md"),
        ("RFC proposal", "docs/RFC_PROCESS.md"),
    ]
    return "\n".join(
        f'<a href="{esc(href)}">{esc(label)}</a>' for label, href in lanes
    )


def project_status(index: Dict[str, Any]) -> str:
    links = [
        (
            "Validate",
            "https://github.com/hwang595/hpc-skill-hub/actions/workflows/validate.yml?query=branch%3Amain",
        ),
        (
            "Package",
            "https://github.com/hwang595/hpc-skill-hub/actions/workflows/package.yml?query=branch%3Amain",
        ),
        (
            "Pages",
            "https://github.com/hwang595/hpc-skill-hub/actions/workflows/pages.yml?query=branch%3Amain",
        ),
    ]
    pills = [
        '<span class="status-pill">v0.2.0-dev</span>',
        '<span class="status-pill">Python 3.9+</span>',
        f'<span class="status-pill">{index["skill_count"]} skills</span>',
        f'<span class="status-pill">{index["collection_count"]} collections</span>',
        '<span class="status-pill">MIT</span>',
    ]
    return "\n".join(
        f'<a class="status-pill" href="{esc(href)}">{esc(label)} CI</a>'
        for label, href in links
    ) + "\n" + "\n".join(pills)


def render(index: Dict[str, Any]) -> str:
    membership = skill_collection_membership(index)
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
      width: 46px;
      height: 46px;
      border-radius: 50%;
      display: block;
      object-fit: cover;
      border: 1px solid var(--line);
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
    .project-status {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }}
    .status-pill {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 8px;
      background: #f8fafc;
      color: #344054;
      font-size: .78rem;
      white-space: nowrap;
    }}
    a.status-pill {{
      color: #1d4ed8;
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
      grid-template-columns: repeat(4, minmax(120px, 1fr)) 2fr;
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
    input[type="search"],
    select {{
      width: min(420px, 100%);
      padding: 9px 11px;
      border: 1px solid var(--line);
      border-radius: 6px;
      font: inherit;
      background: white;
    }}
    select {{
      width: min(210px, 100%);
      color: var(--text);
    }}
    button {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 12px;
      background: #ffffff;
      color: #1d4ed8;
      font: inherit;
      cursor: pointer;
    }}
    button:hover {{ background: #f8fafc; }}
    .intro {{
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(280px, .8fr);
      gap: 18px;
      align-items: start;
      margin-bottom: 22px;
    }}
    .intro-panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .intro h2 {{
      margin-bottom: 8px;
    }}
    .intro p {{
      margin: 0 0 12px;
      color: var(--muted);
    }}
    .path-list {{
      list-style: none;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      padding: 0;
      margin: 14px 0 0;
    }}
    .path-list li {{
      border-left: 3px solid var(--accent);
      padding: 2px 0 2px 10px;
    }}
    .path-list strong,
    .path-list span {{
      display: block;
    }}
    .path-list span {{
      color: var(--muted);
      margin: 4px 0 8px;
      font-size: .9rem;
    }}
    .lane-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }}
    .lane-links a {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 5px 9px;
      background: #f8fafc;
      color: #1d4ed8;
      font-size: .86rem;
    }}
    h2 {{
      margin: 0;
      font-size: 1.05rem;
      letter-spacing: 0;
    }}
    .filters {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 0 0 12px;
    }}
    .filters input[type="search"] {{
      flex: 1 1 280px;
    }}
    .result-count {{
      color: var(--muted);
      font-size: .92rem;
    }}
    .empty-state {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--muted);
      margin: 0 0 12px;
      padding: 12px;
    }}
    .muted {{ color: var(--muted); }}
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
    tr[hidden] {{ display: none; }}
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
      .intro {{ grid-template-columns: 1fr; }}
      .path-list {{ grid-template-columns: 1fr; }}
      .stats {{ grid-template-columns: 1fr; }}
      .toolbar {{ align-items: flex-start; flex-direction: column; }}
      .filters {{ display: grid; grid-template-columns: 1fr; }}
      .filters input[type="search"], select, button {{ width: 100%; }}
      h1 {{ font-size: 1.2rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <div class="brand">
        <img class="mark" src="assets/brand/hpc-skill-hub-logo.png" alt="" aria-hidden="true">
        <div>
          <h1>HPC Skill Hub Registry</h1>
          <p class="subtitle">Reusable skills for HPC workflows, site policy, and operational debugging.</p>
          <div class="project-status" aria-label="Project status">
            {project_status(index)}
          </div>
        </div>
      </div>
      <nav aria-label="Project links">
        <a href="README.md">README</a>
        <a href="docs/SKILL_LIFECYCLE.md">Contribute</a>
        <a href="docs/SKILL_SPEC.md">Skill spec</a>
        <a href="docs/COMPATIBILITY.md">Compatibility</a>
        <a href="docs/SITE_ADAPTERS.md">Site adapters</a>
        <a href="docs/ECOSYSTEM_PROPOSAL.md">Proposal</a>
      </nav>
    </div>
  </header>
  <main class="wrap">
    <section class="intro" aria-labelledby="ecosystem-heading">
      <div class="intro-panel">
        <h2 id="ecosystem-heading">Open HPC Skill Ecosystem</h2>
        <p>Use the registry to discover portable HPC skills, adapt them to public site policy, and grow reviewed workflows through community evidence.</p>
        <ul class="path-list">
          {ecosystem_paths()}
        </ul>
      </div>
      <div class="intro-panel" aria-labelledby="contribute-heading">
        <h2 id="contribute-heading">Contribution Lanes</h2>
        <p>Start with the issue type that matches the smallest public-safe change. Maintainers can route domain review, safety review, RFCs, and maturity promotion from there.</p>
        <div class="lane-links">
          {contribution_lanes()}
        </div>
      </div>
    </section>
    {stats(index)}
    <section class="section" aria-labelledby="skills-heading">
      <div class="toolbar">
        <h2 id="skills-heading">Skills</h2>
        <span id="skill-count" class="result-count">{index['skill_count']} matching skills</span>
      </div>
      {filter_controls(index)}
      <p id="empty-skills" class="empty-state" hidden>No skills match the current filters.</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Skill</th>
              <th>Summary</th>
              <th>Risk</th>
              <th>Maturity</th>
              <th>Schedulers</th>
              <th>Categories</th>
              <th>Tags</th>
            </tr>
          </thead>
          <tbody id="skill-table">
            {skill_rows(index['skills'], membership)}
          </tbody>
        </table>
      </div>
    </section>
    <section class="section" aria-labelledby="collections-heading">
      <div class="toolbar">
        <h2 id="collections-heading">Collections</h2>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Collection</th>
              <th>Summary</th>
              <th>Status</th>
              <th>Skills</th>
              <th>Audience</th>
            </tr>
          </thead>
          <tbody>
            {collection_rows(index['collections'])}
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
    const rows = Array.from(document.querySelectorAll('#skill-table tr'));
    const controls = {{
      search: document.getElementById('skill-search'),
      risk: document.getElementById('filter-risk'),
      maturity: document.getElementById('filter-maturity'),
      category: document.getElementById('filter-category'),
      scheduler: document.getElementById('filter-scheduler'),
      tool: document.getElementById('filter-tool'),
      collection: document.getElementById('filter-collection'),
    }};
    const count = document.getElementById('skill-count');
    const empty = document.getElementById('empty-skills');
    const clear = document.getElementById('clear-filters');

    function hasToken(row, key, value) {{
      if (!value) return true;
      const raw = row.dataset[key] || '';
      return raw.split('|').includes(value);
    }}

    function applyFilters() {{
      const query = controls.search.value.trim().toLowerCase();
      const active = {{
        risk: controls.risk.value,
        maturity: controls.maturity.value,
        category: controls.category.value,
        scheduler: controls.scheduler.value,
        tool: controls.tool.value,
        collection: controls.collection.value,
      }};
      let visible = 0;
      rows.forEach((row) => {{
        const matches =
          (!query || row.dataset.search.includes(query)) &&
          hasToken(row, 'risk', active.risk) &&
          hasToken(row, 'maturity', active.maturity) &&
          hasToken(row, 'categories', active.category) &&
          hasToken(row, 'schedulers', active.scheduler) &&
          hasToken(row, 'tools', active.tool) &&
          hasToken(row, 'collections', active.collection);
        row.hidden = !matches;
        if (matches) visible += 1;
      }});
      count.textContent = `${{visible}} matching skill${{visible === 1 ? '' : 's'}}`;
      empty.hidden = visible !== 0;
    }}

    Object.values(controls).forEach((control) => {{
      control.addEventListener('input', applyFilters);
      control.addEventListener('change', applyFilters);
    }});
    clear.addEventListener('click', () => {{
      controls.search.value = '';
      Object.values(controls).forEach((control) => {{
        if (control.tagName === 'SELECT') control.value = '';
      }});
      applyFilters();
    }});
    applyFilters();
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

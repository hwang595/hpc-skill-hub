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
RELEASE_STATUS_PATH = ROOT / "registry" / "release-status.json"
DEFAULT_OUTPUT = ROOT / "site" / "index.html"
SUPPORT_PATHS = [
    "README.md",
    "LICENSE",
    "agent-bench",
    "assets",
    "benchmarks",
    "docs",
    "collections",
    "skills",
    "site-adapters",
    "registry",
    "reviews",
]


def load_index() -> Dict[str, Any]:
    with INDEX_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_release_status() -> Dict[str, Any]:
    with RELEASE_STATUS_PATH.open("r", encoding="utf-8") as handle:
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
      <label class="search-field">
        <span class="sr-only">Search skills</span>
        <input id="skill-search" type="search" placeholder="Search id, tag, tool, or summary" autocomplete="off">
      </label>
      <label>
        <span class="sr-only">Filter by risk</span>
        <select id="filter-risk">
        {option_tags(['low', 'medium', 'high'], 'All risk levels')}
        </select>
      </label>
      <label>
        <span class="sr-only">Filter by maturity</span>
        <select id="filter-maturity">
        {option_tags(['seed', 'reviewed', 'field-tested', 'maintained'], 'All maturity')}
        </select>
      </label>
      <label>
        <span class="sr-only">Filter by category</span>
        <select id="filter-category">
        {option_tags(sorted(index['categories']), 'All categories')}
        </select>
      </label>
      <label>
        <span class="sr-only">Filter by scheduler</span>
        <select id="filter-scheduler">
        {option_tags(schedulers, 'All schedulers')}
        </select>
      </label>
      <label>
        <span class="sr-only">Filter by tool</span>
        <select id="filter-tool">
        {option_tags(tools, 'All tools')}
        </select>
      </label>
      <label>
        <span class="sr-only">Filter by collection</span>
        <select id="filter-collection">
        {option_tags(collections, 'All collections')}
        </select>
      </label>
      <label>
        <span class="sr-only">Sort skills</span>
        <select id="sort-skills">
          <option value="id">Sort by id</option>
          <option value="name">Sort by name</option>
          <option value="risk-desc">Risk: high first</option>
          <option value="maturity-desc">Maturity: high first</option>
        </select>
      </label>
      <button id="clear-filters" class="icon-button" type="button" aria-label="Clear filters" title="Clear filters" hidden>&times;</button>
    </div>
    """


def skill_attributes(skill: Dict[str, Any], collections: List[str]) -> str:
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
    attributes = {
        "search": search_text,
        "risk": skill["risk_level"].lower(),
        "maturity": skill["maturity"].lower(),
        "status": skill["status"].lower(),
        "categories": data_attr_values(skill["categories"]),
        "schedulers": data_attr_values(skill["schedulers"]),
        "tools": data_attr_values(skill["tools"]),
        "collections": data_attr_values(collections),
        "sort-id": skill["id"].lower(),
        "sort-name": skill["name"].lower(),
    }
    return " ".join(f'data-{key}="{esc(value)}"' for key, value in attributes.items())


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
        rows.append(
            f"""
            <tr {skill_attributes(skill, collections)}>
              <td>
                <a class="skill-name" href="{esc(skill['readme'])}">{esc(skill['name'])}</a>
                <code class="skill-id">{esc(skill['id'])}</code>
              </td>
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


def skill_cards(skills: List[Dict[str, Any]], membership: Dict[str, List[str]]) -> str:
    cards = []
    for skill in skills:
        collections = membership.get(skill["id"], [])
        schedulers = ", ".join(skill["schedulers"]) or "scheduler agnostic"
        tools = ", ".join(skill["tools"][:5]) or "none declared"
        categories = " ".join(badge(category) for category in skill["categories"])
        cards.append(
            f"""
            <article class="skill-card" {skill_attributes(skill, collections)}>
              <div class="skill-card-heading">
                <div>
                  <a class="skill-name" href="{esc(skill['readme'])}">{esc(skill['name'])}</a>
                  <code class="skill-id">{esc(skill['id'])}</code>
                </div>
                <span class="skill-version">v{esc(skill['version'])}</span>
              </div>
              <p>{esc(skill['summary'])}</p>
              <div class="skill-badges">
                {badge(skill['risk_level'], skill['risk_level'])}
                {badge(skill['maturity'])}
                {categories}
              </div>
              <dl>
                <div><dt>Schedulers</dt><dd>{esc(schedulers)}</dd></div>
                <div><dt>Tools</dt><dd>{esc(tools)}</dd></div>
              </dl>
            </article>
            """
        )
    return "\n".join(cards)


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


def collection_shortcuts(collections: List[Dict[str, Any]]) -> str:
    items = []
    for collection in sorted(collections, key=lambda item: item["name"].lower()):
        items.append(
            f"""
            <li>
              <a href="?collection={esc(collection['id'].lower())}#skills" data-collection-shortcut="{esc(collection['id'].lower())}">
                <span>{esc(collection['name'])}</span>
                <strong>{len(collection['skill_ids'])}</strong>
              </a>
            </li>
            """
        )
    return "\n".join(items)


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
        '<span class="status-pill">v0.5.0</span>',
        '<span class="status-pill">Python 3.9+</span>',
        f'<span class="status-pill">{index["skill_count"]} skills</span>',
        f'<span class="status-pill">{index["collection_count"]} collections</span>',
        '<span class="status-pill">MIT</span>',
    ]
    return "\n".join(
        f'<a class="status-pill" href="{esc(href)}">{esc(label)} CI</a>'
        for label, href in links
    ) + "\n" + "\n".join(pills)


def release_readiness(status: Dict[str, Any]) -> str:
    benchmark = status["capabilities"]["benchmark"]
    review = status["capabilities"]["review"]
    security = status["capabilities"]["security"]
    provenance = status["gates"]["release_provenance"]
    provenance_ready = provenance["status"] == "open"
    items = [
        (
            "Repository",
            "Ready",
            "ready",
            "Validated registry, package, MCP, and policy capabilities",
            "registry/release-status.json",
        ),
        (
            "Security",
            "Review",
            "review",
            f"{security['scanned_skill_count']} scanned, {security['blocking_count']} blocking",
            "docs/SKILL_SECURITY.md",
        ),
        (
            "Evidence",
            "Pending",
            "pending",
            f"{benchmark['scored_result_count']} scored of {benchmark['planned_run_count']} planned runs",
            "docs/AGENT_BENCHMARK_DASHBOARD.html",
        ),
        (
            "Promotion",
            "Pending",
            "pending",
            f"{review['promotion_ready_count']} ready of {review['candidate_count']} candidates",
            "docs/SKILL_REVIEW_DASHBOARD.html",
        ),
        (
            "Provenance",
            "Verified" if provenance_ready else provenance["status"].title(),
            "ready" if provenance_ready else "pending",
            (
                "Manifest, wheel, and sdist attestations verified"
                if provenance_ready
                else f"Awaiting the {status['release']} tag and attestations"
            ),
            (
                f"registry/provenance/{status['release']}.json"
                if provenance_ready
                else "docs/V0_5_COMPLETION.md"
            ),
        ),
    ]
    rendered = []
    for label, value, state, detail, href in items:
        rendered.append(
            f"""
            <a class="readiness-item" href="{esc(href)}">
              <span class="readiness-label">{esc(label)}</span>
              <strong><span class="state-dot state-{esc(state)}"></span>{esc(value)}</strong>
              <small>{esc(detail)}</small>
            </a>
            """
        )
    return "\n".join(rendered)


def render(index: Dict[str, Any], release_status: Dict[str, Any]) -> str:
    membership = skill_collection_membership(index)
    provenance_ready = release_status["gates"]["release_provenance"]["status"] == "open"
    release_summary = (
        "Repository release and tag provenance are verified; comparative evidence and independent promotion remain explicit gates."
        if provenance_ready
        else "Repository capability is ready; external evidence, independent promotion, and tag attestations remain explicit gates."
    )
    release_badge = "Released and verified" if provenance_ready else "Repository ready"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Search and compare {index['skill_count']} public, reviewable skills for HPC workflows, schedulers, containers, data movement, and operational debugging.">
  <meta property="og:title" content="HPC Skill Hub Registry">
  <meta property="og:description" content="A public registry of reusable, reviewable HPC workflow skills for people and coding agents.">
  <meta property="og:image" content="https://hwang595.github.io/hpc-skill-hub/assets/brand/hpc-skill-hub-social-preview.png">
  <meta property="og:url" content="https://hwang595.github.io/hpc-skill-hub/">
  <meta property="og:type" content="website">
  <link rel="icon" href="assets/brand/hpc-skill-hub-logo.png" type="image/png">
  <title>HPC Skill Hub Registry</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --panel: #ffffff;
      --text: #16212b;
      --muted: #5b6878;
      --line: #d5dce4;
      --line-strong: #b9c4cf;
      --accent: #08766d;
      --accent-soft: #e8f6f3;
      --link: #175cd3;
      --warn: #8a5600;
      --danger: #b42318;
      --ok: #067647;
      --focus: #7f56d9;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--text);
      background: var(--bg);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    [hidden] {{ display: none !important; }}
    a {{ color: var(--link); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    button, input, select {{ font: inherit; }}
    button:focus-visible, input:focus-visible, select:focus-visible, a:focus-visible, summary:focus-visible {{
      outline: 3px solid color-mix(in srgb, var(--focus) 35%, transparent);
      outline-offset: 2px;
    }}
    .sr-only {{
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }}
    .skip-link {{
      position: fixed;
      left: 16px;
      top: 10px;
      z-index: 20;
      padding: 8px 12px;
      background: var(--panel);
      border: 2px solid var(--focus);
      transform: translateY(-160%);
    }}
    .skip-link:focus {{ transform: translateY(0); }}
    .wrap {{ width: min(1240px, calc(100vw - 32px)); margin: 0 auto; }}
    header {{
      position: sticky;
      top: 0;
      z-index: 10;
      background: color-mix(in srgb, var(--panel) 96%, transparent);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(10px);
    }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      padding: 14px 0;
    }}
    .brand {{ display: flex; align-items: center; gap: 12px; min-width: 0; }}
    .mark {{
      width: 44px;
      height: 44px;
      border-radius: 50%;
      display: block;
      object-fit: cover;
      border: 1px solid var(--line);
      flex: 0 0 auto;
    }}
    h1, h2, h3 {{ margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: 1.25rem; }}
    h2 {{ font-size: 1.1rem; }}
    h3 {{ font-size: .95rem; }}
    .subtitle {{ color: var(--muted); margin: 1px 0 0; font-size: .9rem; }}
    .project-status {{ display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }}
    .status-pill {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 7px;
      background: #f8fafc;
      color: #344054;
      font-size: .74rem;
      white-space: nowrap;
    }}
    a.status-pill {{ color: var(--link); }}
    nav {{ display: flex; gap: 14px; flex-wrap: wrap; justify-content: flex-end; font-size: .88rem; }}
    main {{ padding: 20px 0 44px; }}
    .release-overview {{
      background: var(--panel);
      border: 1px solid var(--line-strong);
      border-left: 4px solid var(--accent);
      border-radius: 6px;
      margin-bottom: 14px;
    }}
    .release-heading {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
    }}
    .release-heading p {{ margin: 2px 0 0; color: var(--muted); font-size: .86rem; }}
    .release-badge {{ color: var(--ok); font-size: .8rem; font-weight: 700; white-space: nowrap; }}
    .readiness-grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); }}
    .readiness-item {{ min-width: 0; padding: 11px 14px; border-right: 1px solid var(--line); color: var(--text); }}
    .readiness-item:last-child {{ border-right: 0; }}
    .readiness-item:hover {{ background: #f9fbfc; text-decoration: none; }}
    .readiness-label, .readiness-item strong, .readiness-item small {{ display: block; }}
    .readiness-label {{ color: var(--muted); font-size: .74rem; text-transform: uppercase; font-weight: 700; }}
    .readiness-item strong {{ margin: 3px 0; font-size: .9rem; }}
    .readiness-item small {{ color: var(--muted); font-size: .76rem; }}
    .state-dot {{ display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 6px; background: var(--line-strong); }}
    .state-ready {{ background: var(--ok); }}
    .state-review {{ background: var(--warn); }}
    .state-pending {{ background: #667085; }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(105px, .72fr)) minmax(280px, 2.2fr);
      gap: 10px;
      margin-bottom: 18px;
    }}
    .stats > div {{ background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 11px 13px; }}
    .stats strong {{ display: block; font-size: 1.35rem; }}
    .stats span {{ color: var(--muted); font-size: .84rem; }}
    .categories {{ display: flex; align-items: center; gap: 5px; flex-wrap: wrap; }}
    .count {{ margin-right: 7px; }}
    .section {{ margin-top: 28px; }}
    .registry-section {{ scroll-margin-top: 116px; }}
    .toolbar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 0 0 10px; }}
    .toolbar-copy p {{ margin: 3px 0 0; color: var(--muted); font-size: .88rem; }}
    .explorer-actions {{ display: flex; align-items: center; gap: 10px; }}
    .result-count {{ color: var(--muted); font-size: .86rem; white-space: nowrap; }}
    .view-switch {{ display: inline-flex; border: 1px solid var(--line-strong); border-radius: 6px; overflow: hidden; }}
    .view-switch button {{
      width: 68px;
      height: 34px;
      border: 0;
      border-right: 1px solid var(--line);
      border-radius: 0;
      background: var(--panel);
      color: var(--muted);
      cursor: pointer;
    }}
    .view-switch button:last-child {{ border-right: 0; }}
    .view-switch button[aria-selected="true"] {{ background: var(--accent-soft); color: #075e57; font-weight: 700; }}
    .collection-browser {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px 14px;
      margin-bottom: 10px;
    }}
    .collection-browser-heading {{ display: flex; justify-content: space-between; gap: 12px; align-items: baseline; margin-bottom: 8px; }}
    .collection-browser-heading span {{ color: var(--muted); font-size: .8rem; }}
    .collection-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      list-style: none;
      padding: 0;
      margin: 0;
      border-top: 1px solid var(--line);
      border-left: 1px solid var(--line);
    }}
    .collection-grid li {{ min-width: 0; border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); }}
    .collection-grid a {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 7px 9px; color: var(--text); font-size: .82rem; }}
    .collection-grid a:hover {{ background: #f8fafc; text-decoration: none; }}
    .collection-grid a span {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .collection-grid a strong {{ color: var(--accent); font-size: .78rem; }}
    .filters {{
      display: grid;
      grid-template-columns: minmax(260px, 1.7fr) repeat(7, minmax(120px, 1fr)) 38px;
      gap: 7px;
      margin: 0 0 10px;
      align-items: stretch;
    }}
    .filters label, .filters input, .filters select {{ width: 100%; min-width: 0; }}
    input[type="search"], select {{
      height: 38px;
      padding: 7px 9px;
      border: 1px solid var(--line-strong);
      border-radius: 5px;
      color: var(--text);
      background: var(--panel);
    }}
    .icon-button {{
      width: 38px;
      height: 38px;
      padding: 0;
      border: 1px solid var(--line-strong);
      border-radius: 5px;
      background: var(--panel);
      color: var(--danger);
      font-size: 1.25rem;
      line-height: 1;
      cursor: pointer;
    }}
    .icon-button:hover, .secondary-button:hover {{ background: #f8fafc; }}
    .filter-summary {{ color: var(--muted); min-height: 20px; margin: 0 0 8px; font-size: .82rem; }}
    .empty-state {{ background: var(--panel); border: 1px solid var(--line); border-radius: 6px; color: var(--muted); margin: 0 0 10px; padding: 14px; }}
    .muted {{ color: var(--muted); }}
    .table-wrap {{ overflow: auto; border: 1px solid var(--line); background: var(--panel); border-radius: 6px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 960px; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; font-size: .85rem; }}
    th {{ position: sticky; top: 0; z-index: 1; color: var(--muted); background: #f8fafc; font-weight: 700; }}
    tr:last-child td {{ border-bottom: 0; }}
    tbody tr:hover {{ background: #fbfcfd; }}
    .skill-name {{ display: block; font-weight: 700; overflow-wrap: anywhere; }}
    .skill-id {{ display: block; color: var(--muted); font-size: .73rem; margin-top: 3px; overflow-wrap: anywhere; }}
    .badge {{
      display: inline-block;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 7px;
      margin: 0 3px 3px 0;
      color: #344054;
      background: #f8fafc;
      font-size: .72rem;
      white-space: nowrap;
    }}
    .badge-tag {{ background: #eef6ff; border-color: #cfe4ff; }}
    .badge-low {{ color: var(--ok); background: #ecfdf3; border-color: #b7e5c8; }}
    .badge-medium {{ color: var(--warn); background: #fffaeb; border-color: #efd08a; }}
    .badge-high {{ color: var(--danger); background: #fff1f0; border-color: #f3b8b2; }}
    .skill-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }}
    .skill-card {{
      min-width: 0;
      min-height: 220px;
      display: flex;
      flex-direction: column;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
    }}
    .skill-card-heading {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }}
    .skill-version {{ color: var(--muted); font-size: .73rem; white-space: nowrap; }}
    .skill-card p {{ color: #344054; margin: 10px 0; font-size: .87rem; }}
    .skill-badges {{ margin-bottom: 9px; }}
    .skill-card dl {{ margin: auto 0 0; border-top: 1px solid var(--line); padding-top: 8px; }}
    .skill-card dl div {{ display: grid; grid-template-columns: 78px 1fr; gap: 8px; margin-top: 4px; font-size: .78rem; }}
    .skill-card dt {{ color: var(--muted); }}
    .skill-card dd {{ margin: 0; overflow-wrap: anywhere; }}
    .show-more-wrap {{ display: flex; justify-content: center; margin-top: 12px; }}
    .secondary-button {{ min-width: 150px; height: 38px; border: 1px solid var(--line-strong); border-radius: 5px; background: var(--panel); color: var(--link); cursor: pointer; }}
    .intro {{ display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(280px, .75fr); gap: 14px; align-items: start; }}
    .intro-panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 16px; }}
    .intro h2 {{ margin-bottom: 7px; }}
    .intro p {{ margin: 0 0 10px; color: var(--muted); font-size: .88rem; }}
    .path-list {{ list-style: none; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; padding: 0; margin: 12px 0 0; }}
    .path-list li {{ border-left: 3px solid var(--accent); padding: 2px 0 2px 10px; }}
    .path-list strong, .path-list span {{ display: block; }}
    .path-list span {{ color: var(--muted); margin: 3px 0 6px; font-size: .83rem; }}
    .lane-links {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 12px; margin-top: 8px; }}
    .lane-links a {{ padding: 7px 0; border-bottom: 1px solid var(--line); font-size: .84rem; }}
    footer {{ border-top: 1px solid var(--line); background: var(--panel); color: var(--muted); padding: 17px 0; font-size: .84rem; }}
    .footer-row {{ display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap; }}
    .footer-links {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    @media (max-width: 1100px) {{
      .filters {{ grid-template-columns: minmax(260px, 2fr) repeat(3, minmax(130px, 1fr)); }}
      .icon-button {{ width: 100%; }}
      .readiness-grid {{ grid-template-columns: repeat(3, 1fr); }}
      .readiness-item:nth-child(3) {{ border-right: 0; }}
      .readiness-item:nth-child(n+4) {{ border-top: 1px solid var(--line); }}
      .skill-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 800px) {{
      html {{ scroll-behavior: auto; }}
      header {{ position: static; backdrop-filter: none; }}
      .topbar {{ align-items: flex-start; flex-direction: column; gap: 10px; }}
      nav {{ justify-content: flex-start; gap: 9px 13px; }}
      .readiness-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .readiness-item, .readiness-item:nth-child(3) {{ border-right: 1px solid var(--line); border-top: 1px solid var(--line); }}
      .readiness-item:nth-child(odd) {{ border-right: 1px solid var(--line); }}
      .readiness-item:nth-child(even) {{ border-right: 0; }}
      .readiness-item:first-child, .readiness-item:nth-child(2) {{ border-top: 0; }}
      .stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .stats .categories {{ grid-column: 1 / -1; }}
      .toolbar {{ align-items: flex-start; flex-direction: column; }}
      .explorer-actions {{ width: 100%; justify-content: space-between; }}
      .collection-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .filters {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .search-field {{ grid-column: 1 / -1; }}
      .intro {{ grid-template-columns: 1fr; }}
      .path-list {{ grid-template-columns: 1fr; }}
      .skill-grid {{ grid-template-columns: 1fr; }}
      .skill-card {{ min-height: 0; }}
    }}
    @media (max-width: 520px) {{
      .wrap {{ width: min(100% - 24px, 1240px); }}
      .brand {{ align-items: flex-start; }}
      h1 {{ font-size: 1.12rem; }}
      .subtitle {{ font-size: .84rem; }}
      .project-status .status-pill:nth-child(n+6) {{ display: none; }}
      .release-heading {{ align-items: flex-start; }}
      .release-heading p, .readiness-item small, .stats .categories {{ display: none; }}
      .readiness-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .readiness-item {{ padding: 8px 10px; }}
      .readiness-item:last-child {{ grid-column: 1 / -1; border-right: 0; }}
      .stats > div {{ padding: 9px 10px; }}
      .stats strong {{ font-size: 1.18rem; }}
      .collection-grid, .filters {{ grid-template-columns: 1fr; }}
      .search-field {{ grid-column: auto; }}
      .icon-button {{ width: 38px; justify-self: end; }}
      .lane-links {{ grid-template-columns: 1fr; }}
      .release-badge {{ white-space: normal; text-align: right; }}
    }}
    @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
  </style>
</head>
<body>
  <a class="skip-link" href="#skills">Skip to registry explorer</a>
  <header>
    <div class="wrap topbar">
      <div class="brand">
        <img class="mark" src="assets/brand/hpc-skill-hub-logo.png" alt="" aria-hidden="true">
        <div>
          <h1>HPC Skill Hub Registry</h1>
          <p class="subtitle">Reusable, reviewable skills for HPC workflows and coding agents.</p>
          <div class="project-status" aria-label="Project status">{project_status(index)}</div>
        </div>
      </div>
      <nav aria-label="Project links">
        <a href="#skills">Skills</a>
        <a href="#collections">Collections</a>
        <a href="#adapters">Adapters</a>
        <a href="docs/COMPATIBILITY.md">Compatibility</a>
        <a href="docs/AGENT_BENCHMARK_DASHBOARD.html">Evidence</a>
        <a href="docs/SKILL_REVIEW_DASHBOARD.html">Reviews</a>
        <a href="README.md">Docs</a>
      </nav>
    </div>
  </header>
  <main class="wrap">
    <section class="release-overview" aria-labelledby="release-heading">
      <div class="release-heading">
        <div>
          <h2 id="release-heading">{esc(release_status['release'])} Release Status</h2>
          <p>{esc(release_summary)}</p>
        </div>
        <span class="release-badge">{esc(release_badge)}</span>
      </div>
      <div class="readiness-grid">{release_readiness(release_status)}</div>
    </section>
    {stats(index)}
    <section id="skills" class="registry-section" aria-labelledby="skills-heading">
      <div class="toolbar">
        <div class="toolbar-copy">
          <h2 id="skills-heading">Registry Explorer</h2>
          <p>Find portable workflows by scheduler, tool, risk, maturity, or curated collection.</p>
        </div>
        <div class="explorer-actions">
          <span id="skill-count" class="result-count" aria-live="polite">{index['skill_count']} matching skills</span>
          <div class="view-switch" role="tablist" aria-label="Skill view">
            <button id="view-table" type="button" role="tab" data-view="table" aria-controls="table-view" aria-selected="true">Table</button>
            <button id="view-cards" type="button" role="tab" data-view="cards" aria-controls="card-view" aria-selected="false">Cards</button>
          </div>
        </div>
      </div>
      <div class="collection-browser" aria-labelledby="collection-browser-heading">
        <div class="collection-browser-heading">
          <h3 id="collection-browser-heading">Browse by Collection</h3>
          <span>{index['collection_count']} curated entry points</span>
        </div>
        <ul class="collection-grid">{collection_shortcuts(index['collections'])}</ul>
      </div>
      {filter_controls(index)}
      <p id="filter-summary" class="filter-summary">All skills are shown. Filter state is reflected in the page URL.</p>
      <p id="empty-skills" class="empty-state" hidden>No skills match the current filters.</p>
      <div id="table-view" class="view-panel table-wrap" role="tabpanel" aria-labelledby="view-table">
        <table>
          <thead>
            <tr>
              <th>Skill</th><th>Summary</th><th>Risk</th><th>Maturity</th><th>Schedulers</th><th>Categories</th><th>Tags</th>
            </tr>
          </thead>
          <tbody id="skill-table">{skill_rows(index['skills'], membership)}</tbody>
        </table>
      </div>
      <div id="card-view" class="view-panel" role="tabpanel" aria-labelledby="view-cards" hidden>
        <div id="skill-cards" class="skill-grid">{skill_cards(index['skills'], membership)}</div>
        <div class="show-more-wrap"><button id="show-more-skills" class="secondary-button" type="button" hidden>Show more</button></div>
      </div>
    </section>
    <section class="section intro" aria-labelledby="ecosystem-heading">
      <div class="intro-panel">
        <h2 id="ecosystem-heading">Open HPC Skill Ecosystem</h2>
        <p>Adopt portable skills, adapt them to public site policy, and improve them through community evidence.</p>
        <ul class="path-list">{ecosystem_paths()}</ul>
      </div>
      <div class="intro-panel" aria-labelledby="contribute-heading">
        <h2 id="contribute-heading">Contribution Lanes</h2>
        <p>Start with the issue type that matches the smallest public-safe change.</p>
        <div class="lane-links">{contribution_lanes()}</div>
      </div>
    </section>
    <section id="collections" class="section" aria-labelledby="collections-heading">
      <div class="toolbar"><h2 id="collections-heading">Collections</h2></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Collection</th><th>Summary</th><th>Status</th><th>Skills</th><th>Audience</th></tr></thead>
          <tbody>{collection_rows(index['collections'])}</tbody>
        </table>
      </div>
    </section>
    <section id="adapters" class="section" aria-labelledby="adapters-heading">
      <div class="toolbar"><h2 id="adapters-heading">Site Adapters</h2></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Adapter</th><th>Summary</th><th>Status</th><th>Scheduler</th><th>Partitions</th></tr></thead>
          <tbody>{adapter_rows(index['site_adapters'])}</tbody>
        </table>
      </div>
    </section>
  </main>
  <footer>
    <div class="wrap footer-row">
      <span>Generated from <code>registry/index.json</code> and <code>registry/release-status.json</code>.</span>
      <span class="footer-links">
        <a href="registry/release-status.json">Release status</a>
        <a href="registry/provenance/v0.5.0.json">Provenance receipt</a>
        <a href="registry/releases/v0.5.0.json">Release manifest</a>
        <a href="docs/RELEASE_NOTES_v0.5.0.md">Release notes</a>
        <a href="LICENSE">MIT License</a>
      </span>
    </div>
  </footer>
  <script>
    const tableRows = Array.from(document.querySelectorAll('#skill-table tr'));
    const cards = Array.from(document.querySelectorAll('#skill-cards .skill-card'));
    const tableBody = document.getElementById('skill-table');
    const cardGrid = document.getElementById('skill-cards');
    const controls = {{
      search: document.getElementById('skill-search'),
      risk: document.getElementById('filter-risk'),
      maturity: document.getElementById('filter-maturity'),
      category: document.getElementById('filter-category'),
      scheduler: document.getElementById('filter-scheduler'),
      tool: document.getElementById('filter-tool'),
      collection: document.getElementById('filter-collection'),
      sort: document.getElementById('sort-skills'),
    }};
    const filterKeys = ['search', 'risk', 'maturity', 'category', 'scheduler', 'tool', 'collection'];
    const count = document.getElementById('skill-count');
    const summary = document.getElementById('filter-summary');
    const empty = document.getElementById('empty-skills');
    const clear = document.getElementById('clear-filters');
    const showMore = document.getElementById('show-more-skills');
    const viewButtons = Array.from(document.querySelectorAll('[data-view]'));
    const tablePanel = document.getElementById('table-view');
    const cardPanel = document.getElementById('card-view');
    const pageSize = 24;
    let cardLimit = pageSize;
    let currentView = 'table';

    function hasToken(entry, key, value) {{
      if (!value) return true;
      return (entry.dataset[key] || '').split('|').includes(value);
    }}

    function matchesEntry(entry, query, active) {{
      return (!query || entry.dataset.search.includes(query)) &&
        hasToken(entry, 'risk', active.risk) &&
        hasToken(entry, 'maturity', active.maturity) &&
        hasToken(entry, 'categories', active.category) &&
        hasToken(entry, 'schedulers', active.scheduler) &&
        hasToken(entry, 'tools', active.tool) &&
        hasToken(entry, 'collections', active.collection);
    }}

    function compareEntries(a, b) {{
      const idOrder = a.dataset.sortId.localeCompare(b.dataset.sortId);
      if (controls.sort.value === 'name') return a.dataset.sortName.localeCompare(b.dataset.sortName) || idOrder;
      if (controls.sort.value === 'risk-desc') {{
        const ranks = {{ low: 1, medium: 2, high: 3 }};
        return (ranks[b.dataset.risk] - ranks[a.dataset.risk]) || idOrder;
      }}
      if (controls.sort.value === 'maturity-desc') {{
        const ranks = {{ seed: 1, reviewed: 2, 'field-tested': 3, maintained: 4 }};
        return (ranks[b.dataset.maturity] - ranks[a.dataset.maturity]) || idOrder;
      }}
      return idOrder;
    }}

    function sortEntries() {{
      tableRows.sort(compareEntries).forEach((row) => tableBody.appendChild(row));
      cards.sort(compareEntries).forEach((card) => cardGrid.appendChild(card));
    }}

    function updateUrl(query, active) {{
      const params = new URLSearchParams();
      if (query) params.set('q', query);
      Object.entries(active).forEach(([key, value]) => {{ if (value) params.set(key, value); }});
      if (controls.sort.value !== 'id') params.set('sort', controls.sort.value);
      params.set('view', currentView);
      const queryString = params.toString();
      history.replaceState(null, '', `${{location.pathname}}${{queryString ? '?' + queryString : ''}}${{location.hash}}`);
    }}

    function applyFilters(updateHistory = true) {{
      sortEntries();
      const query = controls.search.value.trim().toLowerCase();
      const active = {{
        risk: controls.risk.value,
        maturity: controls.maturity.value,
        category: controls.category.value,
        scheduler: controls.scheduler.value,
        tool: controls.tool.value,
        collection: controls.collection.value,
      }};
      const matchedRows = tableRows.filter((row) => matchesEntry(row, query, active));
      const matchedCards = cards.filter((card) => matchesEntry(card, query, active));
      tableRows.forEach((row) => {{ row.hidden = !matchedRows.includes(row); }});
      cards.forEach((card) => {{
        const position = matchedCards.indexOf(card);
        card.hidden = position < 0 || position >= cardLimit;
      }});
      const visible = matchedRows.length;
      const activeCount = Number(Boolean(query)) + Object.values(active).filter(Boolean).length;
      count.textContent = `${{visible}} matching skill${{visible === 1 ? '' : 's'}}`;
      summary.textContent = activeCount
        ? `${{activeCount}} active filter${{activeCount === 1 ? '' : 's'}}. This view can be shared from the current URL.`
        : 'All skills are shown. Filter state is reflected in the page URL.';
      clear.hidden = activeCount === 0;
      empty.hidden = visible !== 0;
      const remaining = Math.max(0, matchedCards.length - cardLimit);
      showMore.hidden = currentView !== 'cards' || remaining === 0;
      showMore.textContent = `Show ${{Math.min(pageSize, remaining)}} more`;
      if (updateHistory) updateUrl(query, active);
    }}

    function setView(view, updateHistory = true) {{
      currentView = view === 'cards' ? 'cards' : 'table';
      tablePanel.hidden = currentView !== 'table';
      cardPanel.hidden = currentView !== 'cards';
      viewButtons.forEach((button) => {{
        const selected = button.dataset.view === currentView;
        button.setAttribute('aria-selected', String(selected));
        button.tabIndex = selected ? 0 : -1;
      }});
      applyFilters(updateHistory);
    }}

    function restoreState() {{
      const params = new URLSearchParams(location.search);
      controls.search.value = params.get('q') || '';
      ['risk', 'maturity', 'category', 'scheduler', 'tool', 'collection', 'sort'].forEach((key) => {{
        const value = params.get(key);
        if (value && Array.from(controls[key].options).some((option) => option.value === value)) controls[key].value = value;
      }});
      const requestedView = params.get('view');
      const defaultView = matchMedia('(max-width: 800px)').matches ? 'cards' : 'table';
      setView(requestedView === 'cards' || requestedView === 'table' ? requestedView : defaultView);
    }}

    filterKeys.forEach((key) => {{
      controls[key].addEventListener('input', () => {{ cardLimit = pageSize; applyFilters(); }});
      controls[key].addEventListener('change', () => {{ cardLimit = pageSize; applyFilters(); }});
    }});
    controls.sort.addEventListener('change', () => {{ cardLimit = pageSize; applyFilters(); }});
    clear.addEventListener('click', () => {{
      controls.search.value = '';
      filterKeys.filter((key) => key !== 'search').forEach((key) => {{ controls[key].value = ''; }});
      cardLimit = pageSize;
      applyFilters();
      controls.search.focus();
    }});
    viewButtons.forEach((button) => button.addEventListener('click', () => {{ cardLimit = pageSize; setView(button.dataset.view); }}));
    document.querySelectorAll('[data-collection-shortcut]').forEach((link) => {{
      link.addEventListener('click', (event) => {{
        event.preventDefault();
        controls.collection.value = link.dataset.collectionShortcut;
        cardLimit = pageSize;
        applyFilters();
        controls.collection.focus();
      }});
    }});
    showMore.addEventListener('click', () => {{ cardLimit += pageSize; applyFilters(); }});
    restoreState();
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
    output.write_text(render(load_index(), load_release_status()), encoding="utf-8")
    if not args.no_copy_content:
        copy_supporting_content(output.parent)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

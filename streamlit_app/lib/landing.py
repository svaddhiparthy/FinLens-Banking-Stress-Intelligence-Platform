"""Bento-grid landing, data-engineering first: the pipeline/architecture owns the hero, the KPI
strip reports platform facts (DAGs, models, quality gate, CI) ahead of model metrics, and the ML
surfaces sit as consumers of the platform rather than as the headline. Rendered as one CSS-grid
block via st.markdown so it stays responsive and the links navigate natively.
"""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

_ASSETS = Path(__file__).resolve().parent.parent / "assets" / "landing"
_REPO = "https://github.com/vaddhiparthy/FinLens-Banking-Stress-Intelligence-Platform"

# Platform facts, verified from the repo: airflow/dags (7 DAGs), dbt/models (11 models),
# great_expectations/validation_result.json (20/20), tests/ (20 suites), .github/workflows (4),
# ml/artifacts panel_facts.json (448,661 bank-quarters).
_KPIS = [
    ("448,661", "bank-quarters in the gold mart"),
    ("7", "Airflow DAGs · ingest, transform, retrain, sync"),
    ("11", "dbt models · bronze → silver → gold"),
    ("20/20", "Great Expectations checks passing"),
    ("20", "pytest suites · run on every push"),
    ("$0", "infra · 100% public data"),
]


@lru_cache(maxsize=16)
def _data_uri(name: str) -> str:
    p = _ASSETS / name
    if not p.exists():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _img_tile(area: str, img: str, kicker: str, title: str, caption: str, href: str,
              badge: str = "", cta: str = "", overlay: str = "") -> str:
    badge_html = f'<span class="fl-badge">{badge}</span>' if badge else ""
    cta_html = (f'<span class="fl-cta">{cta} →</span>' if cta
                else '<span class="fl-cta">Open →</span>')
    return f"""
    <a class="fl-tile fl-img" style="grid-area:{area}" href="{href}" target="_self">
      <div class="fl-figwrap"><img src="{_data_uri(img)}" alt="{title}"/>{overlay}{badge_html}</div>
      <div class="fl-meta">
        <div><span class="fl-kicker">{kicker}</span>
        <span class="fl-title">{title}</span>
        <span class="fl-cap">{caption}</span></div>
        {cta_html}
      </div>
    </a>"""


def _fact_tile(area: str, kicker: str, number: str, label: str, caption: str, href: str,
               cta: str = "", external: bool = False) -> str:
    """Image-free stat tile for platform facts that have no chart (quality gate, CI)."""
    target = "_blank" if external else "_self"
    rel = ' rel="noopener"' if external else ""
    cta_html = (f'<span class="fl-cta">{cta} →</span>' if cta
                else '<span class="fl-cta">Open →</span>')
    return f"""
    <a class="fl-tile fl-fact" style="grid-area:{area}" href="{href}" target="{target}"{rel}>
      <span class="fl-kicker">{kicker}</span>
      <span class="fl-factnum">{number}</span>
      <span class="fl-factlabel">{label}</span>
      <div class="fl-meta"><span class="fl-cap">{caption}</span>{cta_html}</div>
    </a>"""


def _entry_tile(area: str, icon: str, title: str, caption: str, href: str,
                external: bool = False) -> str:
    target = "_blank" if external else "_self"
    rel = ' rel="noopener"' if external else ""
    return f"""
    <a class="fl-tile fl-entry" style="grid-area:{area}" href="{href}" target="{target}"{rel}>
      <span class="fl-ico">{icon}</span>
      <div><span class="fl-title">{title}</span><span class="fl-cap">{caption}</span></div>
      <span class="fl-arrow">→</span>
    </a>"""


def _render_architecture_window() -> None:
    """Inline, scrollable and zoomable architecture diagram, framed as a bento tile.

    The chart is drawn directly rather than through ``render_architecture`` so the landing owns
    the frame height and carries no stray caption: the title bar is overlaid into the drawing's
    blank top band, and the zoom/pan hint rides in the same bar. Same DOT source and
    svg-pan-zoom layer as the full-screen Architecture page, so one diagram definition.
    """
    from streamlit.components.v1 import html as _html

    from streamlit_app.lib.wiki_architecture import _PANZOOM_JS, ARCHITECTURE_DOT

    st.markdown(
        """
        <div class="fl-archbar">
          <span class="fl-kicker">Architecture</span>
          <span class="fl-archtitle">The whole platform, end to end</span>
          <span class="fl-archhint">Scroll to zoom &middot; drag to pan</span>
          <a class="fl-cta" href="Architecture" target="_self">Full screen &rarr;</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.graphviz_chart(ARCHITECTURE_DOT, use_container_width=True)
    _html(_PANZOOM_JS, height=0)


def render_landing() -> None:
    kpis = "".join(
        f'<div class="fl-kpi"><span class="fl-num">{num}</span>'
        f'<span class="fl-klabel">{label}</span></div>'
        for num, label in _KPIS
    )

    gauge_overlay = (
        '<div class="fl-gauge-overlay"><span class="fl-gauge-val">79.9%</span>'
        '<span class="fl-gauge-sub">probability of distress</span></div>'
    )
    tiles = [
        # Hero: the pipeline is the product. Sankey = source → bronze → silver → gold → serving.
        _img_tile("hero", "sankey.png", "Architecture & live pipeline",
                  "FDIC · FFIEC · FRED → Bronze → Silver → Gold → Serving",
                  "Seven Airflow DAGs feed eleven dbt models into a DuckDB warehouse of record, "
                  "quality-gated at every layer and served to dashboards and a scoring API.",
                  "Data_Engineering", cta="Data engineering"),
        _fact_tile("dq", "Data quality gate", "20 / 20", "expectations passing",
                   "Great Expectations contract on the gold mart: schema, null rates, value "
                   "ranges, freshness through 2026Q1. Non-zero exit on any failure.",
                   "Data_Engineering", cta="Quality"),
        _fact_tile("ci", "CI/CD & deployment", "4", "GitHub Actions workflows",
                   "Ruff + pytest on every PR, pytest on main, nightly run, Terraform plan. "
                   "Docker images and Kubernetes manifests committed.",
                   _REPO, cta="Repository", external=True),
        _img_tile("infer", "gauge.png", "Live model inference", "Score any U.S. bank",
                  "Calibrated four-quarter distress probability, backtested on a real failure.",
                  "Early_Warning", badge="HIGH RISK", cta="Score a bank", overlay=gauge_overlay),
        _img_tile("model", "prcurve.png", "Model quality", "Out-of-time evaluation",
                  "PR-AUC 0.301 · ROC-AUC 0.855 · SHAP-explained, against a 0.06% base rate.",
                  "Technical_Dashboard", cta="Technical"),
        _img_tile("map", "map.png", "Geography", "Where banks fail",
                  "FDIC failures by state, 2008–2026.", "Business_Dashboard", cta="Business"),
    ]
    entries = [
        _entry_tile("repo", "⌥", "Source code",
                    "Airflow · dbt · GX · Docker · k8s · Terraform",
                    _REPO, external=True),
        _entry_tile("wiki", "❖", "FinLens-Wiki", "The full encyclopedia.", "Wiki"),
        _entry_tile("arch", "▦", "Architecture wiki", "Design decisions and rationale.",
                    "Wiki?article=system-architecture"),
    ]

    top = f"""
<div class="fl-bento">
  <div class="fl-lede">A production-shaped batch data platform: public FDIC, FFIEC, and FRED feeds
    orchestrated through Airflow into a dbt-modeled DuckDB warehouse, quality-gated by Great
    Expectations, and served to a calibrated early-warning model and live dashboards.</div>
  <div class="fl-kpis">{kpis}</div>
  <div class="fl-grid fl-grid-top">{''.join(tiles)}</div>
</div>
{_CSS}
"""
    tail = f"""
<div class="fl-bento fl-bento-tail">
  <div class="fl-grid fl-grid-tail">{''.join(entries)}</div>
</div>
"""
    st.markdown(top, unsafe_allow_html=True)
    _render_architecture_window()
    st.markdown(tail, unsafe_allow_html=True)


_CSS = """
<style>
.fl-bento {max-width: 1180px; margin: .1rem auto 1rem; padding: 0 .4rem;}
.fl-lede {text-align:center; max-width: 760px; margin: 0 auto 1.1rem; color:#5a4d3e !important;
  font-size: 1.0rem; line-height: 1.55;}
/* Kill Streamlit's default link-blue everywhere inside the bento; brand colors win. */
.fl-bento a, .fl-bento a:link, .fl-bento a:visited, .fl-bento a:hover {color:#1f2933 !important;
  text-decoration:none !important;}
.fl-kpis {display:grid; grid-template-columns: repeat(6, 1fr); gap: 14px; margin-bottom: 1.25rem;}
.fl-kpi {background:#fffaf3; border:1px solid #ece1d0; border-top:3px solid #bf6d47;
  border-radius:12px; padding:1rem .6rem .85rem; text-align:center;}
.fl-num {display:block; font-size:1.9rem; font-weight:800; color:#1f2933 !important;
  letter-spacing:-.015em; font-variant-numeric: tabular-nums; line-height:1;}
.fl-klabel {display:block; font-size:.64rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.07em; color:#8a7a67 !important; margin-top:.4rem; line-height:1.25;}
.fl-grid {display:grid; grid-template-columns: repeat(6, 1fr); gap:18px;}
.fl-grid-top {grid-template-rows: 172px 172px 184px;
  grid-template-areas:
    "hero  hero  hero  hero  dq   dq"
    "hero  hero  hero  hero  ci   ci"
    "infer infer model model map  map";}
.fl-grid-tail {grid-template-rows: 108px;
  grid-template-areas: "repo  repo  wiki  wiki  arch arch";}
.fl-bento-tail {margin-top:.9rem !important;}
/* inline architecture window: the title bar sits INSIDE the frame, over the drawing's blank
   top band, and the frame is sized to the drawing instead of a fixed tall box. */
.fl-archbar {position:relative; z-index:5; max-width:1180px; margin:1.15rem auto -40px;
  padding:0 1.15rem; height:34px; display:flex; align-items:center; gap:.65rem;
  pointer-events:none;}
.fl-archbar .fl-kicker {flex:none;}
.fl-archtitle {font-weight:800; color:#1f2933 !important; font-size:.98rem; line-height:1;
  white-space:nowrap;}
.fl-archhint {font-size:.66rem; font-weight:700; color:#a2907c !important; white-space:nowrap;
  margin-left:.15rem;}
.fl-archbar a.fl-cta {margin-left:auto; white-space:nowrap; text-decoration:none !important;
  pointer-events:auto;}
[data-testid="stGraphVizChart"], .stGraphVizChart {max-width:1180px; margin:0 auto !important;
  height:300px; border:1px solid #e4d7c6; border-radius:16px; background:#fffaf3;
  overflow:hidden; box-shadow:0 8px 24px rgba(15,23,42,.05);}
[data-testid="stGraphVizChart"] > svg, .stGraphVizChart > svg {
  width:100% !important; height:100% !important;}
.svg-pan-zoom-control-background {fill:#fffaf3; opacity:.85;}
.svg-pan-zoom-control-element {fill:#bf6d47;}
/* the pan-zoom helper mounts a zero-height component iframe: do not let it add a gap */
iframe[title="streamlit.components.v1.html"] {height:0 !important; display:block;
  margin:0 !important;}
[data-testid="stGraphVizChart"] + div, .stGraphVizChart + div {margin-top:0 !important;}
.fl-tile {display:flex; flex-direction:column; background:#fffaf3; border:1px solid #e7dccb;
  border-radius:16px; padding:.75rem .85rem; overflow:hidden;
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;}
.fl-tile:hover {transform: translateY(-3px); border-color:#bf6d47;
  box-shadow: 0 16px 38px rgba(31,41,51,.14);}
.fl-img .fl-figwrap {position:relative; flex:1; min-height:0; display:flex; align-items:center;
  justify-content:center; padding:.1rem;}
.fl-img img {max-width:100%; max-height:100%; width:auto; object-fit:contain;}
.fl-badge {position:absolute; top:6px; right:6px; background:#8f3f22 !important;
  color:#fff7ef !important; font-size:.6rem; font-weight:800; letter-spacing:.07em;
  padding:.22rem .55rem; border-radius:999px;}
.fl-meta {display:flex; align-items:flex-end; justify-content:space-between; gap:.5rem;
  margin-top:.5rem;}
.fl-kicker {display:block; font-size:.57rem; font-weight:800; text-transform:uppercase;
  letter-spacing:.13em; color:#bf6d47 !important;}
.fl-title {display:block; font-weight:800; color:#1f2933 !important; font-size:.96rem;
  line-height:1.2; margin-top:.14rem;}
.fl-cap {display:block; font-size:.72rem; color:#8a7766 !important; line-height:1.35;
  margin-top:.2rem;}
.fl-cta, .fl-arrow {white-space:nowrap; font-size:.74rem; font-weight:800;
  color:#bf6d47 !important;}
.fl-tile[style*="hero"] {padding:1rem 1.1rem;}
.fl-tile[style*="hero"] .fl-title {font-size:1.3rem;}
.fl-tile[style*="hero"] .fl-cap {font-size:.84rem; max-width:64ch;}
.fl-tile[style*="hero"] .fl-figwrap {padding:.1rem .4rem;}
.fl-tile[style*="hero"] img {max-height:100%; width:auto;}
/* fact tiles: big number, no chart */
.fl-fact {justify-content:flex-start;}
.fl-factnum {display:block; font-size:2.1rem; font-weight:800; color:#1f2933 !important;
  letter-spacing:-.02em; font-variant-numeric:tabular-nums; line-height:1; margin-top:.35rem;}
.fl-factlabel {display:block; font-size:.66rem; font-weight:800; text-transform:uppercase;
  letter-spacing:.09em; color:#8a7a67 !important; margin-top:.3rem;}
.fl-fact .fl-meta {margin-top:auto; align-items:flex-end;}
/* gauge value overlaid as centered HTML on the arc-only chart (small inference tile) */
.fl-gauge-overlay {position:absolute; left:0; right:0; bottom:8%; text-align:center;
  pointer-events:none;}
.fl-gauge-val {display:block; font-size:1.6rem; font-weight:800; color:#1f2933 !important;
  line-height:1; letter-spacing:-.02em; font-variant-numeric:tabular-nums;}
.fl-gauge-sub {display:block; font-size:.52rem; font-weight:800; text-transform:uppercase;
  letter-spacing:.1em; color:#8a7766 !important; margin-top:.25rem;}
.fl-tile[style*="infer"] img {width:78%;}
.fl-entry {flex-direction:row; align-items:center; gap:.7rem; justify-content:flex-start;}
.fl-entry .fl-ico {font-size:1.15rem; color:#bf6d47 !important; background:#f4e8da;
  width:2.1rem; height:2.1rem; display:flex; align-items:center; justify-content:center;
  border-radius:10px; flex:none;}
.fl-entry .fl-arrow {margin-left:auto; font-size:1.05rem;}
/* trim the trailing empty band below the footer on the landing */
[data-testid="stMainBlockContainer"] {padding-bottom: 1.4rem !important;}
/* the map fills its tile (crops the redundant in-chart title + colorbar margins) */
.fl-tile[style*="map"] .fl-figwrap {padding:0;}
.fl-tile[style*="map"] img {object-fit:cover; width:100%; height:100%; object-position:50% 48%;}
@media (max-width: 820px) {
  .fl-tile[style*="map"] img {object-fit:contain;}
  .fl-kpis {grid-template-columns: repeat(2, 1fr); gap:10px;}
  .fl-kpi {padding:.6rem .5rem .55rem;}
  .fl-num {font-size:1.5rem;}
  .fl-klabel {margin-top:.25rem; font-size:.6rem;}
  .fl-grid {grid-template-columns: 1fr; grid-template-rows: none; gap:14px;}
  .fl-grid-top {grid-template-areas: "hero" "dq" "ci" "infer" "model" "map";}
  .fl-grid-tail {grid-template-areas: "repo" "wiki" "arch";}
  .fl-archbar {margin:1rem auto .45rem; height:auto; padding:0 .2rem; flex-wrap:wrap;
    gap:.4rem .6rem;}
  .fl-archtitle {white-space:normal;}
  .fl-archhint {display:none;}
  [data-testid="stGraphVizChart"], .stGraphVizChart {height:220px;}
  .fl-img .fl-figwrap {min-height: 160px;}
  .fl-tile[style*="hero"] .fl-figwrap {min-height: 220px;}
  .fl-fact {min-height: 150px;}
  .hdr-name {text-align:center !important;}
}
</style>
"""

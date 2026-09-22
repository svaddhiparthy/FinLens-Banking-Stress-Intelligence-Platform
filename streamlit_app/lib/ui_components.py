# ruff: noqa: E501
from html import escape

import pandas as pd
import streamlit as st


def inject_styles(css: str) -> None:
    st.markdown(css, unsafe_allow_html=True)


def metric_card(label: str, value: str, subtext: str, tone: str | None = None) -> None:
    """tone in {"ok","warn","bad"} adds a status-colored left edge so a Failed/Deferred card is
    scannable at a glance against the Success cards (defaults to the neutral card)."""
    edge = {"ok": "#2f8f6b", "warn": "#bf6d47", "bad": "#be123c"}.get(tone or "")
    style = f' style="border-left:4px solid {edge}"' if edge else ""
    # Non-numeric states (e.g. "Not published", "Deferred") render in a quieter, smaller
    # treatment so they don't compete typographically with the big numeric values in a KPI row.
    vcls = "metric-value" if any(ch.isdigit() for ch in str(value)) else "metric-value metric-value-text"
    st.markdown(
        f"""
        <div class="metric-card"{style}>
            <div class="metric-label">{label}</div>
            <div class="{vcls}">{value}</div>
            <div class="metric-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_tone(status: str | None) -> str | None:
    """Map a pipeline/platform status string to a metric_card tone."""
    s = (status or "").strip().lower()
    if s in {"success", "ready", "pass", "active", "live"}:
        return "ok"
    if s in {"failed", "missing data", "missing", "unavailable", "blocked"}:
        return "bad"
    if s in {"deferred", "not activated", "scaffolded", "pending", "running"}:
        return "warn"
    return None


def section_heading(title: str, copy: str | None = None) -> None:
    st.markdown(f'<div class="section-label">{title}</div>', unsafe_allow_html=True)
    if copy:
        st.markdown(f'<div class="subsection-copy">{copy}</div>', unsafe_allow_html=True)


def empty_state(message: str) -> None:
    st.markdown(f'<div class="empty-card">{message}</div>', unsafe_allow_html=True)


def chart_note(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="chart-note">
            <div class="chart-note-title">{escape(title)}</div>
            <div class="chart-note-copy">{escape(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def styled_table(frame: pd.DataFrame) -> None:
    header = "".join(f"<th>{escape(str(column))}</th>" for column in frame.columns)
    rows = []
    for _, row in frame.fillna(", ").iterrows():
        cells = "".join(f"<td>{escape(str(value))}</td>" for value in row.tolist())
        rows.append(f"<tr>{cells}</tr>")
    st.markdown(
        f"""
        <div class="finlens-table-wrap">
            <table class="finlens-table">
                <thead><tr>{header}</tr></thead>
                <tbody>{"".join(rows)}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tech_bulletin(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="tech-bulletin">
            <div class="tech-bulletin-title">{title}</div>
            <div class="tech-bulletin-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pipeline_stage_flow(stages: list[dict[str, object]]) -> None:
    html_parts: list[str] = ['<div class="flow-grid">']
    for index, stage in enumerate(stages):
        html_parts.append(
            f"""
            <div class="flow-card">
                <div class="flow-step">Stage {index + 1}</div>
                <div class="flow-name">{stage["name"]}</div>
                <div class="flow-copy">{stage["copy"]}</div>
                <div class="flow-metric">{stage["metric_1"]}</div>
                <div class="flow-metric">{stage["metric_2"]}</div>
                <div class="flow-metric">{stage["metric_3"]}</div>
            </div>
            """
        )
        if index < len(stages) - 1:
            html_parts.append('<div class="flow-arrow">→</div>')
    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)

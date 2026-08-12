from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas import AnalysisResult

TEMPLATES_DIR = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
    )

def _format_pct(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.2%}"

def _format_num(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:,.4f}"
    return f"{value:,}"

def render_html_report(result: AnalysisResult) -> str:
    template = env.get_template("report.html.j2")

    html = template.render(
    result=result,
    format_pct=_format_pct,
    format_num=_format_num,
    )
    return html
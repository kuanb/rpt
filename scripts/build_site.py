#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
PUBLIC_DIR = ROOT / "public"


@dataclass(frozen=True)
class Page:
    title: str
    href: str
    published_on: date


def read_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if title_match:
        return re.sub(r"\s+", " ", html.unescape(title_match.group(1))).strip()

    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.IGNORECASE | re.DOTALL)
    if h1_match:
        return re.sub(r"\s+", " ", html.unescape(h1_match.group(1))).strip()

    return path.parent.name.replace("-", " ").title()


def discover_pages() -> list[Page]:
    pages: list[Page] = []
    for index_path in CONTENT_DIR.glob("[0-9][0-9][0-9][0-9]/*/*/*/index.html"):
        rel = index_path.relative_to(CONTENT_DIR)
        year, month, day = rel.parts[:3]
        pages.append(
            Page(
                title=read_title(index_path),
                href="/".join(rel.parent.parts) + "/",
                published_on=date(int(year), int(month), int(day)),
            )
        )

    return sorted(pages, key=lambda page: (page.published_on, page.title), reverse=True)


def render_index(pages: list[Page]) -> str:
    page_items = "\n".join(
        f'        <li><time datetime="{page.published_on.isoformat()}">'
        f'{page.published_on.strftime("%B %-d, %Y")}</time> '
        f'<a href="{html.escape(page.href)}">{html.escape(page.title)}</a></li>'
        for page in pages
    )
    if not page_items:
        page_items = "        <li>No published files yet.</li>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rose Park Terrace HOA Content</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #202124;
      --muted: #5f6368;
      --line: #d9dce1;
      --paper: #ffffff;
      --wash: #f7f8fa;
      --accent: #246b5f;
    }}
    body {{
      margin: 0;
      background: var(--wash);
      color: var(--ink);
      font: 16px/1.55 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 760px;
      margin: 0 auto;
      padding: 56px 24px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(2rem, 5vw, 3.25rem);
      line-height: 1.05;
    }}
    p {{
      max-width: 64ch;
      color: var(--muted);
      margin: 0 0 32px;
    }}
    section {{
      border-top: 1px solid var(--line);
      padding-top: 24px;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 1rem;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: var(--muted);
    }}
    ul {{
      list-style: none;
      padding: 0;
      margin: 0;
      background: var(--paper);
      border: 1px solid var(--line);
    }}
    li {{
      display: grid;
      grid-template-columns: 11.5rem 1fr;
      gap: 16px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
    }}
    li:last-child {{
      border-bottom: 0;
    }}
    time {{
      color: var(--muted);
      white-space: nowrap;
    }}
    a {{
      color: var(--accent);
      font-weight: 650;
      text-decoration-thickness: .08em;
      text-underline-offset: .18em;
    }}
    @media (max-width: 560px) {{
      main {{
        padding: 36px 18px;
      }}
      li {{
        grid-template-columns: 1fr;
        gap: 4px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>Rose Park Terrace HOA Content</h1>
    <p>This path is dedicated to Rose Park Terrace homeowner association analysis, reference material, and static reports.</p>
    <section aria-labelledby="available-files">
      <h2 id="available-files">Available Files</h2>
      <ul>
{page_items}
      </ul>
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir()

    if CONTENT_DIR.exists():
        shutil.copytree(CONTENT_DIR, PUBLIC_DIR, dirs_exist_ok=True)

    (PUBLIC_DIR / ".nojekyll").write_text("", encoding="utf-8")
    (PUBLIC_DIR / "index.html").write_text(render_index(discover_pages()), encoding="utf-8")


if __name__ == "__main__":
    main()

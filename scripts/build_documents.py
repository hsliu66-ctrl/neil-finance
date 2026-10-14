#!/usr/bin/env python3
"""Neil Financial Desk: safely convert approved public documents to Markdown/HTML.

- content/drafts/*: create workflow artifact previews (not Pages content).
- content/approved/<category>/*: generate Pages documents and Markdown downloads.
- NOTE: any uploaded file is visible in the PUBLIC source repository regardless
  of whether it's excluded from Pages. Do not upload confidential/licensed docs.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

import markdown
import nh3
from markitdown import MarkItDown

ROOT = Path(__file__).resolve().parents[1]
TYPES = {'.pdf', '.docx', '.xlsx'}
CATEGORIES = {
    'market': '美股投資晨報', 'macro': '全球總經', 'rates': '美債殖利率',
    'fx': '匯率週報', 'etf': 'ETF 投資研究', 'earnings': '財報洞察',
}
MAX_SOURCE_BYTES = 25 * 1024 * 1024
MAX_MD_CHARS = 2_000_000


def e(s: object) -> str:
    return html.escape(str(s), quote=True)


def safe_url(value: object) -> str:
    value = str(value or '').strip()
    parts = urlsplit(value)
    return value if parts.scheme in ('https', 'http') and parts.netloc else ''


def name_and_date(source: Path) -> tuple[str, str]:
    stem = source.stem
    match = re.match(r'^(\d{4}-\d{2}-\d{2})[_\s-]+(.+)$', stem)
    if match:
        try:
            datetime.strptime(match.group(1), '%Y-%m-%d')
            return match.group(2).replace('_', ' ').strip(), match.group(1)
        except ValueError:
            pass
    return stem.replace('_', ' ').strip(), ''


def identifier(path: Path) -> str:
    return hashlib.sha256(path.as_posix().encode('utf-8')).hexdigest()[:12]


def markdown_html(markdown_text: str) -> str:
    raw_html = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code', 'sane_lists'])
    tags = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
            'strong', 'em', 'ul', 'ol', 'li', 'blockquote', 'a',
            'pre', 'code', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'del'}
    return nh3.clean(raw_html, tags=tags, attributes={'a': {'href', 'title'},
                                                       'td': {'align'}, 'th': {'align'}})


STYLE = '''
:root{color-scheme:light}*{box-sizing:border-box}
body{background:#f7f5ee;color:#142b36;font-family:-apple-system,BlinkMacSystemFont,"Noto Sans TC","Microsoft JhengHei",sans-serif;margin:0}
.doc-head{border-bottom:1px solid #d9dcd5;background:#fffefa}
.doc-head-inner{max-width:1080px;margin:auto;display:flex;gap:18px;align-items:center;justify-content:space-between;padding:20px 24px}
.doc-logo{max-width:150px;width:28%;height:auto}.doc-head a,.doc-back{color:#285b4d;text-decoration:none;font-weight:700}
.doc-wrap{max-width:920px;padding:36px 24px 110px;margin:auto}
.doc-kicker{color:#285b4d;font-size:13px;letter-spacing:1.6px;font-weight:800}
h1.doc-title{font-size:clamp(30px,5vw,48px);line-height:1.35;margin:16px 0 22px}
.doc-meta{padding:16px 20px;background:#fffefa;border-left:4px solid #b48a48;margin-bottom:24px;line-height:1.8;font-size:15px;overflow-wrap:anywhere}
.doc-meta a,.doc-article a{color:#285b4d}
.doc-article{border:1px solid #d9dcd5;background:#fffefa;padding:clamp(18px,4vw,45px);font-size:clamp(17px,2.5vw,21px);line-height:1.8;overflow-wrap:anywhere}
.doc-article h1,.doc-article h2,.doc-article h3{line-height:1.45;color:#142b36;margin-top:1.8em}
.doc-article h2{border-bottom:1px solid #d9dcd5;padding-bottom:8px}
.doc-article blockquote{border-left:3px solid #b48a48;padding-left:1em;color:#3c5662;margin:1.5em 0}
.doc-article table{border-collapse:collapse;display:block;max-width:100%;overflow-x:auto;font-size:.79em;white-space:nowrap}
.doc-article th,.doc-article td{border:1px solid #d9dcd5;padding:9px 11px;text-align:left}
.doc-article th{background:#e9eee8}
.doc-article pre{overflow-x:auto;background:#e9eee8;padding:17px;font-size:.74em}
.doc-warning{padding:14px 20px;margin-top:26px;font-size:13px;line-height:1.7;color:#4c5e63}
.doc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.doc-card{background:#fffefa;border:1px solid #d9dcd5;padding:24px;color:inherit;text-decoration:none}
.doc-card:hover{border-color:#b48a48}.doc-card b{display:block;font-size:21px;line-height:1.45;margin:8px 0}
.doc-tag{color:#285b4d;font-size:12px;letter-spacing:.07em;font-weight:800}
.doc-empty{padding:40px;background:#fffefa;border:1px solid #d9dcd5}
@media(max-width:600px){.doc-head-inner{padding:15px 18px}.doc-wrap{padding:28px 15px 75px}.doc-article{padding:22px 18px}}
'''


def shell(title: str, body: str, description: str = '') -> str:
    return f'''<!doctype html><html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}｜Neil Financial Desk</title><meta name="description" content="{e(description[:165])}">
<style>{STYLE}</style></head><body>
<header class="doc-head"><div class="doc-head-inner">
<a href="../index.html"><img class="doc-logo" src="../neil-logo.webp" alt="Neil 整理"></a>
<a href="../index.html">← 返回財經研究室</a></div></header>
<main class="doc-wrap">{body}</main></body></html>'''


def report_page(title: str, date: str, category: str, md_text: str,
                md_href: str, source: str, source_url: str, is_draft: bool) -> str:
    date_text = date or '日期未提供（請查核）'
    source_text = e(source or '未提供原始資料來源（請查核）')
    if source_url:
        source_text = f'<a href="{e(source_url)}" target="_blank" rel="noopener noreferrer">{source_text}</a>'
    preview = '<strong>僅供預覽、尚未發布。</strong><br>' if is_draft else ''
    body = f'''<div class="doc-kicker">NEIL / DOCUMENT RESEARCH · {e(CATEGORIES.get(category, '文件草稿'))}</div>
<h1 class="doc-title">{e(title)}</h1>
<div class="doc-meta">{preview}資料日期：{e(date_text)}<br>來源：{source_text}<br>
<a href="{e(md_href)}" download>↓ 下載 Markdown</a> · <a href="index.html">返回文件庫</a></div>
<article class="doc-article">{markdown_html(md_text)}</article>
<div class="doc-warning">📝 Neil 整理｜此頁為文件結構化轉換，未自動查證行情、財務數據或著作權。
讀者需對照原始來源；僅供資訊參考，非投資建議。</div>'''
    return shell(title, body, md_text[:165])


def discover(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in TYPES)


def read_catalog() -> dict:
    cat = ROOT / 'content' / 'catalog.json'
    if not cat.exists():
        return {}
    data = json.loads(cat.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('content/catalog.json must be a JSON object')
    return data


def run(site: Path, previews: Path) -> None:
    site_docs = site / 'documents'
    site_docs.mkdir(parents=True, exist_ok=True)
    approved = ROOT / 'content' / 'approved'
    drafts = ROOT / 'content' / 'drafts'
    catalog = read_catalog()
    converter = MarkItDown(enable_plugins=False)
    entries = []

    for path in discover(approved) + discover(drafts):
        rel = path.relative_to(ROOT / 'content')
        is_draft = rel.parts[0] == 'drafts'
        category = rel.parts[1] if not is_draft and len(rel.parts) >= 3 else ''
        if not is_draft and category not in CATEGORIES:
            raise ValueError(f'Unknown approved category for {rel}: {category}')
        if path.stat().st_size > MAX_SOURCE_BYTES:
            raise ValueError(f'Document exceeds 25 MB: {rel}')
        metadata = catalog.get(rel.as_posix(), {})
        if not isinstance(metadata, dict):
            raise ValueError(f'Metadata must be an object for: {rel}')
        derived_title, derived_date = name_and_date(path)
        title = str(metadata.get('title') or derived_title).strip()
        date = str(metadata.get('date') or derived_date).strip()
        if date:
            datetime.strptime(date, '%Y-%m-%d')
        source = str(metadata.get('source') or '').strip()
        source_url = safe_url(metadata.get('source_url', ''))
        uid = identifier(rel)
        slug = (date + '-' if date else 'undated-') + uid
        result = converter.convert(str(path))
        md_text = (result.markdown or '').strip()
        if not md_text:
            raise ValueError(f'Empty converted text: {rel} (scanned PDF? OCR needed)')
        if len(md_text) > MAX_MD_CHARS:
            raise ValueError(f'Converted Markdown over 2M characters: {rel}')
        out = previews if is_draft else site_docs
        md_folder = out / 'markdown'
        md_folder.mkdir(parents=True, exist_ok=True)
        (md_folder / f'{slug}.md').write_text(md_text + '\n', encoding='utf-8')
        (out / f'{slug}.html').write_text(report_page(
            title, date, category, md_text, f'markdown/{slug}.md', source, source_url, is_draft
        ), encoding='utf-8')
        if not is_draft:
            entries.append({'id': slug, 'title': title, 'date': date,
                            'category': category, 'category_label': CATEGORIES[category],
                            'source': source, 'source_url': source_url,
                            'url': f'{slug}.html', 'markdown': f'markdown/{slug}.md'})
        print(('PREVIEW' if is_draft else 'PUBLISH'), rel, f'=> {slug}.html')

    entries.sort(key=lambda d: (d['date'], d['title']), reverse=True)
    cards = ''.join(f'''<a class="doc-card" href="{e(d['url'])}"><span class="doc-tag">{e(d['category_label'])} · {e(d['date'] or '日期待查')}</span>
<b>{e(d['title'])}</b><small>{e(d['source'] or '來源待查核')}　→</small></a>''' for d in entries)
    if not cards:
        cards = '<p class="doc-empty">尚無已核准公開的研究文件。上傳可公開文件至 content/approved/ 對應分類後，GitHub Actions 將自動產生網頁。</p>'
    body = f'''<div class="doc-kicker">NEIL / RESEARCH DOCUMENT LIBRARY</div><h1 class="doc-title">研究文件庫<span style="color:#b48a48">.</span></h1>
<p style="font-size:19px;line-height:1.8;color:#3c5662">將公開授權的 PDF、Word 與 Excel 結構化為可閱讀的 Markdown 與財經研究網頁。</p>
<div class="doc-grid">{cards}</div><div class="doc-warning">資料來自使用者核准的公開文件，轉換程式不驗證內容真偽或來源授權。非投資建議。</div>'''
    (site_docs / 'index.html').write_text(shell('研究文件庫', body, 'Neil 財經研究 PDF Word Excel 轉 Markdown 文件庫'), encoding='utf-8')
    (site_docs / 'index.json').write_text(json.dumps({'schema': 1, 'documents': entries}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    homepage = site / 'index.html'
    if homepage.exists():
        text = homepage.read_text(encoding='utf-8')
        marker = '<a href="research-lab.html">研究工具</a>'
        if marker in text and '<a href="documents/index.html">研究文件庫</a>' not in text:
            text = text.replace(marker, '<a href="documents/index.html">研究文件庫</a>' + marker, 1)
            homepage.write_text(text, encoding='utf-8')
            print('Homepage navigation: research document library link added (site build only)')
    print('Approved published:', len(entries), '; draft previews:', len(discover(drafts)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, default=ROOT / '_site')
    parser.add_argument('--previews', type=Path, default=ROOT / 'build-previews')
    args = parser.parse_args()
    try:
        run(args.site, args.previews)
    except Exception as exc:
        print(f'MarkItDown build failed: {exc}', file=sys.stderr)
        raise

import os, time, feedparser, requests, datetime as dt
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import trafilatura

from sources import DEFAULT_FEEDS
from summarize import summarize_with_gemini
from sheets import open_sheet, compute_key, existing_keys, append_rows
from emailer import send_email

def host(url):
    try:
        return urlparse(url).hostname.replace('www.','')
    except Exception:
        return ''

def primary_or_secondary(link: str, type_: str) -> str:
    h = host(link)
    if type_ == 'Research' and any(d in h for d in ['arxiv.org','openreview.net','aclweb.org','research.google','deepmind.google']):
        return 'Primary'
    if type_ == 'Regulation' and any(d in h for d in ['iapp.org','europa.eu','ec.europa.eu']):
        return 'Primary'
    return 'Secondary'

def fetch_feed_items(feed):
    parsed = feedparser.parse(feed["url"])
    items = []
    for e in parsed.entries[:30]:
        title = getattr(e, 'title', '')
        link = getattr(e, 'link', '')
        author = getattr(e, 'author', '')
        date = getattr(e, 'published', '') or getattr(e, 'updated', '')
        summary = BeautifulSoup(getattr(e, 'summary', '') or '', 'html.parser').get_text().strip()
        items.append({
            "type": feed["type"], "title": title, "link": link, "author": author, "date": date, "summary": summary
        })
    return items

def extract_text(url):
    try:
        downloaded = trafilatura.fetch_url(url, timeout=20)
        if not downloaded:
            return ""
        txt = trafilatura.extract(downloaded) or ""
        return txt.strip()
    except Exception:
        return ""

def build_digest_text(collected):
    top = sorted(collected, key=lambda x: ((0 if x['priSec']=='Primary' else 1), -x['score']))[:3]
    lines = []
    for i,x in enumerate(top, start=1):
        lines.append(f"#{i} [{x['type']}] {x['title']}\nWhy it matters: {x['insight']}\n{x['canon'] or x['link']}")
    if not lines:
        return "No new high-relevance items today."
    today = dt.datetime.utcnow().strftime('%Y-%m-%d')
    return f"Today's AI highlights ({today} UTC):\n\n" + "\n\n".join(lines)

def run():
    ws = open_sheet()
    seen = existing_keys(ws)
    new_rows = []
    collected_for_digest = []

    for feed in DEFAULT_FEEDS:
        items = fetch_feed_items(feed)
        for it in items:
            date_str = (it['date'] or dt.datetime.utcnow().isoformat())[:10]
            key = compute_key(it['title'], host(it['link']), date_str)
            if key in seen:
                continue

            full_text = extract_text(it['link']) or it['summary'] or it['title']
            source = host(it['link']) or feed['url']
            s = summarize_with_gemini(feed['type'], source, it['title'], full_text)
            canon = s.get('CanonicalLink') or it['link']
            priSec = primary_or_secondary(canon, feed['type'])
            score = int(s.get('RelevanceScore', 0)) if isinstance(s.get('RelevanceScore', 0), int) else 0

            row = [
                feed['type'],
                source,
                it['title'],
                it['author'] or '',
                date_str,
                s.get('ExecutiveSummary',''),
                s.get('BusinessInsight',''),
                score,
                it['link'],
                canon,
                priSec,
                key,
                'New'
            ]
            new_rows.append(row)
            seen.add(key)
            collected_for_digest.append({
                "type": feed['type'],
                "title": it['title'],
                "insight": s.get('BusinessInsight',''),
                "score": score,
                "priSec": priSec,
                "link": it['link'],
                "canon": canon
            })

    append_rows(ws, new_rows)

    if collected_for_digest:
        digest = build_digest_text(collected_for_digest)
        subject = "AI highlights — " + dt.datetime.utcnow().strftime('%Y-%m-%d')
        send_email(subject, digest)
    else:
        print("Nothing new to email.")

if __name__ == "__main__":
    run()

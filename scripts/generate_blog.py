#!/usr/bin/env python3
import os
import re
import json
import time
import datetime
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
import anthropic

CEST = ZoneInfo("Europe/Berlin")
TOPIC_LOG_PATH = "scripts/topic-log.json"
BLOG_DIR = "src/content/blog"
MODEL = "claude-haiku-4-5-20251001"

RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://hnrss.org/frontpage",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "https://openai.com/news/rss.xml",
]

AUTHOR = {
    "name": "Bohdan Shvchk",
    "role": "Founder & Shopify Developer",
    "bio": "Shopify developer and web agency founder. Covering the tech and AI news that matters for modern businesses.",
    "linkedin": "https://www.linkedin.com/in/bogdan-shevchuk-b3827414a/",
}


# ── Telegram ──────────────────────────────────────────────────────────────────

def send_telegram(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print(f"[Telegram skipped] {message}")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": message}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Telegram failed: {e}")


# ── RSS fetching ───────────────────────────────────────────────────────────────

def fetch_rss(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read()
    except Exception:
        return None


def parse_date(date_str):
    if not date_str:
        return None
    date_str = date_str.strip()
    # RFC 2822 (standard RSS pubDate: "Thu, 08 May 2026 12:00:00 GMT")
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        pass
    # ISO 8601 (Atom: "2026-05-08T12:00:00Z" or "+02:00")
    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"]:
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def parse_feed(xml_bytes, start, end):
    if not xml_bytes:
        return []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        if not title:
            continue
        pub_date = parse_date(item.findtext("pubDate", ""))
        if not pub_date or not (start <= pub_date.astimezone(CEST) <= end):
            continue
        items.append({
            "title": title,
            "link": item.findtext("link", "").strip(),
            "description": item.findtext("description", "").strip()[:200],
        })

    for entry in root.findall(".//atom:entry", ns):
        title = entry.findtext("atom:title", namespaces=ns, default="").strip()
        if not title:
            continue
        published = (entry.findtext("atom:published", namespaces=ns, default="")
                     or entry.findtext("atom:updated", namespaces=ns, default=""))
        pub_date = parse_date(published)
        if not pub_date or not (start <= pub_date.astimezone(CEST) <= end):
            continue
        link_el = entry.find("atom:link", ns)
        items.append({
            "title": title,
            "link": link_el.get("href", "") if link_el is not None else "",
            "description": entry.findtext("atom:summary", namespaces=ns, default="").strip()[:200],
        })

    return items


def gather_news(start, end):
    seen = set()
    all_items = []
    for url in RSS_FEEDS:
        for item in parse_feed(fetch_rss(url), start, end):
            key = item["title"].lower()
            if key not in seen:
                seen.add(key)
                all_items.append(item)
    return all_items


# ── Claude with retry ──────────────────────────────────────────────────────────

def call_claude(client, attempt_label, **kwargs):
    # Fast retries: 5s, 15s, 30s  |  Hourly retries: 3x 3600s
    delays = [5, 15, 30, 3600, 3600, 3600]
    for attempt in range(1, 7):
        try:
            return client.messages.create(**kwargs)
        except Exception as e:
            print(f"{attempt_label} attempt {attempt} failed: {e}")
            if attempt >= 3:
                if attempt < 6:
                    next_delay = delays[attempt - 1]
                    retry_msg = "Retrying in 30 seconds..." if next_delay < 60 else "Retrying in 1 hour..."
                    send_telegram(
                        f"Blog poster: {attempt_label} attempt {attempt}/6 failed.\n"
                        f"Error: {str(e)[:200]}\n"
                        f"{retry_msg}"
                    )
                else:
                    send_telegram(
                        f"Blog poster: {attempt_label} failed after 6 attempts. Skipping today.\n"
                        f"Error: {str(e)[:200]}"
                    )
            if attempt < 6:
                time.sleep(delays[attempt - 1])

    return None


# ── Topic log ──────────────────────────────────────────────────────────────────

def load_topic_log():
    if not os.path.exists(TOPIC_LOG_PATH):
        return []
    with open(TOPIC_LOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_topic_log(log):
    with open(TOPIC_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


# ── Claude steps ───────────────────────────────────────────────────────────────

def check_conflicts(client, news_items, topic_log):
    recent = topic_log[-30:]
    news_text = "\n".join(
        f"{i+1}. {item['title']}: {item['description'][:100]}"
        for i, item in enumerate(news_items[:15])
    )
    log_text = "\n".join(
        f"- [{e['date']}] {e['title']} (slug: {e.get('slug', '')})"
        for e in recent
    )

    prompt = f"""You are checking whether today's news overlaps with recently published blog posts.

Recent posts:
{log_text if log_text else "(none yet)"}

Today's news (numbered):
{news_text}

Rules:
- CONFLICT: essentially the same event already covered, no new developments
- CONTINUATION: same entity/product but a genuinely new development (new version, new vulnerability, confirmed rumor, etc.)
- NEW: topic not covered before

Return ONLY a JSON object:
{{
  "verdict": "NEW" | "CONTINUATION" | "ALL_CONFLICT",
  "selected_indices": [list of news indices 0-based to cover today],
  "related_post": {{"slug": "...", "title": "..."}} or null
}}"""

    resp = call_claude(client, "Conflict check", model=MODEL, max_tokens=512,
                       messages=[{"role": "user", "content": prompt}])
    if not resp:
        return None
    try:
        content = resp.content[0].text.strip()
        content = re.search(r'\{.*\}', content, re.DOTALL).group(0)
        return json.loads(content)
    except Exception as e:
        print(f"Conflict parse error: {e}")
        return None


def select_style(client, news_items, topic_log):
    recent_styles = [e.get("style") for e in topic_log[-5:] if e.get("style")]
    news_text = "\n".join(f"- {item['title']}" for item in news_items[:10])

    prompt = f"""Select the best article style for today's news.

Today's news:
{news_text}

Recently used styles (avoid repeating back-to-back): {recent_styles}

Styles:
- News Roundup: 4-6 equal-weight stories
- Deep Dive: one dominant story, deep analysis
- Rumor Report: leaks and unconfirmed info
- Quick Hits: few items, short punchy format
- Trend Analysis: multiple stories forming a trend
- Breaking Down: complex announcement explained simply

Return ONLY: {{"style": "Style Name"}}"""

    resp = call_claude(client, "Style selection", model=MODEL, max_tokens=64,
                       messages=[{"role": "user", "content": prompt}])
    if not resp:
        return "News Roundup"
    try:
        content = resp.content[0].text.strip()
        content = re.search(r'\{.*\}', content, re.DOTALL).group(0)
        return json.loads(content).get("style", "News Roundup")
    except Exception:
        return "News Roundup"


def generate_article(client, news_items, style, yesterday_str, continuation_context):
    news_text = "\n".join(
        f"- {item['title']}: {item['description'][:150]} ({item['link']})"
        for item in news_items[:15]
    )
    cont_note = ""
    if continuation_context:
        cont_note = (
            f"\nThis is a continuation of a previous story. "
            f"Naturally reference the earlier article '{continuation_context['title']}' "
            f"with a markdown link to /{continuation_context['slug']} in the text.\n"
        )

    style_guides = {
        "News Roundup": "Cover 4-6 stories, each with its own H2, 2-3 paragraphs per story.",
        "Deep Dive": "Focus on ONE major story across 6-8 sections with deep analysis and context.",
        "Rumor Report": "Clearly label confirmed vs unconfirmed. Use hedging language. Cover 3-5 rumors.",
        "Quick Hits": "Short punchy format. Bullet summaries. Under 700 words total.",
        "Trend Analysis": "Connect multiple stories into a coherent narrative about an emerging trend.",
        "Breaking Down": "Explain complex tech in simple terms. Use analogies. Step-by-step breakdown.",
    }

    prompt = f"""You are an IT/AI/Tech news journalist writing a daily news blog post.

Style: {style}
Style guide: {style_guides.get(style, '')}
Date of news: {yesterday_str}
{cont_note}
News items:
{news_text}

Write a complete blog post. The title MUST reflect the specific news covered today — never generic.

Return ONLY a valid markdown file with this exact frontmatter followed by the article body:

---
title: ""
description: ""
publishedAt: {yesterday_str}
author: "{AUTHOR['name']}"
authorRole: "{AUTHOR['role']}"
authorBio: "{AUTHOR['bio']}"
authorLinkedIn: "{AUTHOR['linkedin']}"
category: "Tech News"
tags: []
readingTime: 5
metaTitle: ""
metaDescription: ""
keyTakeaways:
  - ""
  - ""
  - ""
faq:
  - question: ""
    answer: ""
  - question: ""
    answer: ""
---

Rules:
- metaTitle: max 60 chars
- metaDescription: max 160 chars
- tags: 3-5 relevant tags as YAML list
- readingTime: integer, estimate from word count (200 words ≈ 1 min)
- Return ONLY the markdown, nothing else"""

    return call_claude(client, "Article generation", model=MODEL, max_tokens=4096,
                       messages=[{"role": "user", "content": prompt}])


# ── Helpers ────────────────────────────────────────────────────────────────────

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    if len(text) > 60:
        text = text[:60]
        last_dash = text.rfind('-')
        if last_dash > 20:
            text = text[:last_dash]
    return text


def validate_frontmatter(content):
    for field in ["title:", "description:", "publishedAt:", "category:", "readingTime:"]:
        if field not in content:
            return False, f"Missing: {field}"
    if content.count("---") < 2:
        return False, "Missing frontmatter delimiters"
    return True, None


def fix_frontmatter(content):
    # Strip markdown code block wrapper if Claude added one
    if content.startswith("```"):
        content = re.sub(r'^```[^\n]*\n', '', content)
        content = re.sub(r'\n```\s*$', '', content).strip()
    # Fix missing closing ---
    if content.count("---") < 2:
        lines = content.split("\n")
        insert_at = next((i for i, l in enumerate(lines) if l.startswith("##")), len(lines))
        lines.insert(insert_at, "---\n")
        content = "\n".join(lines)
    return content


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    import sys
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    now_cest = datetime.datetime.now(CEST)
    yesterday = now_cest.date() - datetime.timedelta(days=1)
    yesterday_str = yesterday.isoformat()
    start = datetime.datetime.combine(yesterday, datetime.time.min, tzinfo=CEST)
    end = datetime.datetime.combine(yesterday, datetime.time.max, tzinfo=CEST)

    print(f"Fetching news for {yesterday_str} (CEST)...")
    news_items = gather_news(start, end)
    print(f"Found {len(news_items)} articles")

    if not news_items:
        extended_start = start - datetime.timedelta(hours=12)
        news_items = gather_news(extended_start, end)
        print(f"Extended window: {len(news_items)} articles")

    if not news_items:
        send_telegram(f"Blog poster: No news found for {yesterday_str}. Skipping.")
        return

    topic_log = load_topic_log()

    print("Checking conflicts...")
    conflict = check_conflicts(client, news_items, topic_log)
    if conflict is None:
        return

    forced = False
    continuation_context = None
    verdict = conflict.get("verdict", "NEW")
    indices = conflict.get("selected_indices", list(range(min(5, len(news_items)))))
    selected_items = [news_items[i] for i in indices if i < len(news_items)] or news_items[:5]

    if verdict == "CONTINUATION":
        related = conflict.get("related_post")
        if related:
            continuation_context = next(
                (e for e in topic_log if e.get("slug") == related.get("slug")), None
            )
    elif verdict == "ALL_CONFLICT":
        forced = True
        titles = [item["title"] for item in news_items[:5]]
        send_telegram(
            f"Blog poster: All topics for {yesterday_str} are conflicts.\n"
            f"Publishing least-similar topic anyway:\n" +
            "\n".join(f"- {t}" for t in titles)
        )

    print("Selecting style...")
    style = select_style(client, selected_items, topic_log)
    print(f"Style: {style}")

    print("Generating article...")
    resp = generate_article(client, selected_items, style, yesterday_str, continuation_context)
    if not resp:
        return

    article = fix_frontmatter(resp.content[0].text.strip())

    valid, error = validate_frontmatter(article)
    if not valid:
        send_telegram(f"Blog poster: Invalid frontmatter for {yesterday_str}. Error: {error}")
        print(f"Frontmatter invalid: {error}")
        sys.exit(1)

    title_match = re.search(r'^title:\s*"(.+?)"', article, re.MULTILINE)
    title = title_match.group(1) if title_match else f"tech-news-{yesterday_str}"
    slug = slugify(title)

    output_path = f"{BLOG_DIR}/{slug}.md"
    if os.path.exists(output_path):
        slug = f"{slug}-{yesterday_str}"
        output_path = f"{BLOG_DIR}/{slug}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(article)
    print(f"Saved: {output_path}")

    topic_log.append({
        "date": yesterday_str,
        "title": title,
        "slug": slug,
        "style": style,
        "forced": forced,
        "topic_summary": f"{style}: {', '.join(item['title'][:50] for item in selected_items[:3])}",
    })
    save_topic_log(topic_log)
    send_telegram(f"Blog poster: Published - {title}")
    print(f"Done. Style: {style}, Slug: {slug}")


if __name__ == "__main__":
    main()

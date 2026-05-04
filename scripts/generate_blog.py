#!/usr/bin/env python3
import os
import re
import datetime
import urllib.request
import xml.etree.ElementTree as ET
import anthropic

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"].strip()

RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://www.wired.com/feed/rss",
]

def fetch_rss(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read()
    except Exception:
        return None

def parse_feed(xml_bytes):
    if not xml_bytes:
        return []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = []
    # RSS
    for item in root.findall(".//item")[:5]:
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        desc = item.findtext("description", "").strip()
        if title:
            items.append(f"- {title}: {desc[:120]}... ({link})")
    # Atom
    for entry in root.findall(".//atom:entry", ns)[:5]:
        title = entry.findtext("atom:title", namespaces=ns, default="").strip()
        link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        summary = entry.findtext("atom:summary", namespaces=ns, default="").strip()
        if title:
            items.append(f"- {title}: {summary[:120]}... ({link})")
    return items

def gather_news():
    all_items = []
    for feed_url in RSS_FEEDS:
        xml_bytes = fetch_rss(feed_url)
        all_items.extend(parse_feed(xml_bytes))
    return all_items[:20]

def call_claude(prompt):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60]

def main():
    print("Fetching news...")
    news = gather_news()
    if not news:
        print("No news fetched, exiting.")
        return

    news_block = "\n".join(news)
    today = datetime.date.today().isoformat()

    print("Generating article with Claude...")
    prompt = f"""You are an SEO content writer for a web agency blog run by Bohdan Shvchk, a Webflow and Shopify developer.

Here are today's top AI and Tech headlines:
{news_block}

Pick the single most interesting and relevant topic for a web agency audience. Write a complete, publication-ready blog post in English.

Return ONLY a valid markdown file with this exact frontmatter schema followed by the article body:

---
title: ""
description: ""
publishedAt: {today}
author: "Bohdan Shvchk"
authorRole: "Founder & Shopify and Webflow Developer"
authorBio: "5+ years building on Webflow, 2+ years on Shopify. Previously at a digital agency. Obsessed with performance and clean architecture."
authorLinkedIn: "https://www.linkedin.com/in/bogdan-shevchuk-b3827414a/"
category: ""
tags: []
readingTime: 6
metaTitle: ""
metaDescription: ""
keyTakeaways:
  - ""
  - ""
  - ""
  - ""
faq:
  - question: ""
    answer: ""
  - question: ""
    answer: ""
  - question: ""
    answer: ""
---

Rules:
- Write 1200-1800 words
- Structure: intro → H2/H3 sections → Key Takeaways → FAQ
- Tone: professional but conversational
- Do not invent statistics — cite real sources or frame as observations
- Optimize for AI search: clear headings, specific answers, FAQ matches real search queries
- Return ONLY the markdown content, nothing else
"""

    article = call_claude(prompt)

    # Extract title for slug
    title_match = re.search(r'^title:\s*"(.+?)"', article, re.MULTILINE)
    title = title_match.group(1) if title_match else "ai-tech-update"
    slug = slugify(title)

    output_path = f"src/content/blog/{slug}.md"

    # Check if file already exists
    if os.path.exists(output_path):
        slug = f"{slug}-{today}"
        output_path = f"src/content/blog/{slug}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(article)

    print(f"Article saved: {output_path}")
    print(f"Slug: {slug}")

if __name__ == "__main__":
    main()

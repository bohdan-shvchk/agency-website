#!/usr/bin/env python3
import os
import re
import datetime
import urllib.request
import xml.etree.ElementTree as ET
from groq import Groq

GROQ_API_KEY = os.environ["GROQ_API_KEY"].strip()

RSS_FEEDS = [
    "https://www.shopify.com/blog.atom",
    "https://webflow.com/blog/rss.xml",
    "https://css-tricks.com/feed/",
    "https://web.dev/feed.xml",
    "https://www.smashingmagazine.com/feed/",
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
    for item in root.findall(".//item")[:5]:
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        desc = item.findtext("description", "").strip()
        if title:
            items.append(f"- {title}: {desc[:120]}... ({link})")
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

def generate_article(prompt):
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.7,
    )
    content = response.choices[0].message.content.strip()
    # Ensure frontmatter has opening and closing ---
    if content.count("---") < 2:
        lines = content.split("\n")
        insert_at = next(
            (i for i, l in enumerate(lines) if l.startswith("##")), len(lines)
        )
        lines.insert(insert_at, "---\n")
        content = "\n".join(lines)
    return content

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

    print("Generating article with Groq...")
    prompt = f"""You are an SEO content writer for a web agency blog run by Bohdan Shvchk, a Webflow and Shopify developer.

Here are today's headlines from Shopify, Webflow, and web-dev publications:
{news_block}

Audience: small-to-mid e-commerce founders and marketing leads evaluating Shopify/Webflow agencies. Pick a topic that helps them either (a) make a build/redesign decision, (b) improve store performance or conversion, or (c) evaluate trade-offs between platforms, tools, or approaches. Skip pure consumer-tech, AI gadget reviews, or industry politics.

Write a complete, publication-ready blog post in English.

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

    article = generate_article(prompt)

    title_match = re.search(r'^title:\s*"(.+?)"', article, re.MULTILINE)
    title = title_match.group(1) if title_match else "ai-tech-update"
    slug = slugify(title)

    output_path = f"src/content/blog/{slug}.md"

    if os.path.exists(output_path):
        slug = f"{slug}-{today}"
        output_path = f"src/content/blog/{slug}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(article)

    print(f"Article saved: {output_path}")
    print(f"Slug: {slug}")

if __name__ == "__main__":
    main()

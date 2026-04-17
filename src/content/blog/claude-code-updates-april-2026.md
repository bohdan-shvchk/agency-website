---
title: "Claude Code April 2026: Every New Feature From 5 Weeks of Non-Stop Shipping"
description: "A data-driven week-by-week breakdown of every Claude Code feature released between March 17 and April 17, 2026 — from Auto Mode and Computer Use to the desktop redesign, Routines, and Opus 4.7 xhigh."
publishedAt: 2026-04-17
author: "Bohdan Shvchk"
authorRole: "Founder & Shopify and Webflow Developer"
authorBio: "5+ years building on Webflow, 2+ years on Shopify. Previously at a digital agency. Obsessed with performance and clean architecture."
authorLinkedIn: "https://www.linkedin.com/in/bogdan-shevchuk-b3827414a/"
category: "AI Tools"
tags: ["claude code", "anthropic", "AI coding", "developer tools", "2026"]
readingTime: 15
metaTitle: "Claude Code Updates April 2026: Every New Feature, Week by Week"
metaDescription: "Complete breakdown of Claude Code's March–April 2026 updates across 30+ versions: Auto Mode, Computer Use, Routines, desktop redesign, Ultraplan, Opus 4.7 xhigh, and more."
keyTakeaways:
  - "Anthropic shipped 30+ Claude Code versions between March 17 and April 17, 2026 — roughly one every 8 hours on peak days"
  - "The desktop app was fully rebuilt around parallel sessions: drag-and-drop workspace, integrated terminal, in-app editor, rebuilt diff viewer"
  - "Routines enable scheduled and event-triggered automations that run on Anthropic's cloud infrastructure, no local machine needed"
  - "Auto Mode, Ultraplan, and Computer Use CLI are all in research/early preview — the autonomous coding loop is nearly closed"
faq:
  - question: "What is the biggest Claude Code update in April 2026?"
    answer: "The desktop redesign released on April 14, 2026 is the most visible structural change — it introduced parallel session management via a persistent sidebar, a drag-and-drop workspace, integrated terminal, in-app file editor, and a rebuilt diff viewer optimized for large changesets. Routines launched alongside it in research preview."
  - question: "What is Claude Code Routines and how does it work?"
    answer: "Routines are automated workflows that bundle a prompt, a repository, and any connectors into a single configuration. They can run on a fixed schedule, trigger from an API call, or fire on a GitHub event like a new pull request. Crucially, they run on Anthropic's cloud infrastructure — your local machine doesn't need to be online."
  - question: "What is Claude Code Auto Mode?"
    answer: "Auto Mode (research preview) uses a classifier to evaluate each pending action. Safe actions proceed without a permission prompt; risky ones are blocked automatically. For Max plan subscribers using Claude Opus 4.7, Auto Mode is available with full autonomous execution capability."
  - question: "What is Ultraplan in Claude Code?"
    answer: "Ultraplan lets you draft an execution plan from your CLI, review and annotate it in a cloud-based web editor, then either execute it remotely or pull it back to run locally. It entered early preview in Week 15 (April 6–10, 2026) and represents Anthropic's push toward human-in-the-loop agentic workflows."
  - question: "Does Claude Code Computer Use work from the terminal?"
    answer: "Yes, as of Week 14 (March 30 – April 3, 2026). Computer Use arrived in the CLI as a research preview, enabling Claude to open native apps, navigate UI elements, test its own changes, and correct failures — all triggered from your terminal session."
  - question: "What is Claude Opus 4.7 xhigh effort level?"
    answer: "xhigh is a new effort tier between the existing 'high' and 'max' levels, introduced with Claude Opus 4.7. It became the default effort level in Claude Code for all plans. The /effort command now opens an interactive slider for tuning the speed-to-intelligence tradeoff directly from the CLI."
---

If you track Claude Code releases, you already know the pace has been aggressive. Between March 17 and April 17, 2026, Anthropic pushed more than 30 versioned releases — from 2.1.69 to 2.1.112. That's not a feature-per-week cadence; that's a feature-per-working-day cadence, often faster.

The result is a tool that looks substantially different from what it was four weeks ago. A rebuilt desktop app. A new automation layer called Routines. An emerging autonomous loop built from Computer Use, Auto Mode, and Ultraplan. And a string of smaller but meaningful changes — prompt caching controls, effort sliders, push notifications, multi-agent code review — that add up to a fundamentally different developer experience.

This breakdown organizes everything by week, traces the logic behind each cluster of changes, and identifies the three platform-level shifts that matter most for developers building with Claude Code today.

## The Pace of Shipping: What 30+ Versions Actually Signals

Before diving into the weekly breakdown, it's worth contextualizing the rate.

Most developer tools ship a major version every quarter and patch releases on demand. Claude Code is operating on a different rhythm — closer to a continuous deployment model where features, fixes, and experiments land in rapid succession. Versions 2.1.69 through 2.1.112 over 30 days averages more than one release per day.

This has practical implications. Features marked "research preview" or "early preview" aren't marketing labels — they're genuinely experimental. Several shipped with known rough edges. Auto Mode, Computer Use CLI, and Ultraplan all fall into this category. The tradeoff Anthropic is making is explicit: get real-world usage data faster rather than shipping polished features slower.

For developers, this means two things. First, the tool is worth re-evaluating regularly — your mental model of what Claude Code can do is probably already outdated. Second, preview features carry real instability risk; treat them as opt-in experiments rather than production primitives.

---

## Week 12 (March 16–20): Memory, Loops, and the Groundwork

The month opened with infrastructure-level improvements that aren't flashy but underpin everything that followed.

### Auto-Memory Enhancements

Claude Code's auto-memory system — which builds a persistent file-based memory store across sessions — received custom directory support and timestamped memory entries. This matters more than it sounds: without timestamps, stale memories are indistinguishable from fresh ones. With them, both Claude and developers can reason about recency.

The `/context` suggestions were also improved, making Claude better at identifying when its working context is becoming unreliable and surfacing a prompt to refresh.

### /loop: Scheduled Task Execution

The `/loop` command arrived as a way to run a prompt or slash command on a recurring interval. At its most basic, you specify an interval and a task: `loop 5m /babysit-prs`. Claude fires the command every five minutes and reports back.

This was, in retrospect, a building block for the more sophisticated automation infrastructure that came in later weeks. On its own it's useful for active monitoring. What it signaled was a broader intent: Claude Code becoming a task scheduler, not just a task executor.

### Interactive Visualizations

Claude gained the ability to generate interactive charts, diagrams, and mobile-ready visualizations as output — rendered directly in the preview pane. For developers who previously had to context-switch to a separate tool for data visualization during a debugging or analysis session, this is a meaningful workflow improvement.

---

## Week 13 (March 23–27): Auto Mode, Computer Use, and Platform Expansion

Week 13 was the first major inflection point. Three distinct capability clusters landed simultaneously, each significant on its own.

### Auto Mode (Research Preview)

The most consequential new feature of the month started here.

Auto Mode introduces a classifier that evaluates every pending action before execution. The classifier distinguishes between safe operations (reading files, running tests, querying APIs) and risky ones (file deletion, system modifications, network writes). Safe actions proceed without a permission prompt. Risky ones are blocked and surfaced for human review.

The practical effect is a dramatic reduction in interruption for standard development workflows. A typical session involving file reads, searches, test runs, and incremental edits — the kind of work that makes up most of a coding day — can run with minimal intervention.

What Auto Mode is *not* is fully autonomous execution. The classifier is conservative by design, and the research preview designation means edge cases are expected. Developers using it as of April 2026 report occasional over-blocking on operations that are contextually safe, and the occasional under-blocking that the preview label implies is possible.

For Max plan subscribers on Opus 4.7, Auto Mode integrates with full autonomous execution — covered in Week 16.

### Computer Use in the Desktop App

Computer Use — Claude's ability to control a GUI — moved from pure API capability to an integrated feature in the Claude Code Desktop app.

The mechanics: Claude receives a screenshot, identifies UI elements, and issues click, type, and scroll commands. In the Desktop app, this means Claude can interact with other applications on your machine while you watch — opening a browser to verify a deployed change, navigating system settings, filling out forms.

The immediate developer use case is UI testing. Rather than writing Playwright or Selenium scripts for every interaction test, you can describe the test in natural language and let Claude execute it. The gap between "I want to verify this button works" and actually verifying it narrows significantly.

### PR Auto-Fix on Web

Claude Code Web gained automated PR fixing: Claude monitors CI pipelines on open pull requests, identifies failures, writes fixes, and pushes until the pipeline goes green. The loop is fully automated once triggered. For teams that spend meaningful time on CI red → fix → push cycles, this is a genuine time recovery.

### Transcript Search, PowerShell, and Conditional Hooks

Three smaller but practical additions:

**Transcript search with `/`** — Type `/` in any session to search across your full conversation history. Useful for developers who use Claude Code for extended sessions and need to reference earlier decisions or outputs.

**Native PowerShell tool for Windows** — Previous Windows support routed shell commands through WSL or cmd. A native PowerShell tool integration brings parity with the Unix shell experience, which matters for Windows-native development environments.

**Conditional `if` hooks** — Hooks (shell commands that fire in response to Claude Code events) gained conditional logic. You can now write hooks that execute only when specific conditions are met — a particular tool is used, a certain file is modified, a pattern matches in the output. This turns hooks from simple event listeners into a lightweight scripting layer.

---

## Week 14 (March 30 – April 3): Computer Use Comes to the CLI

The Desktop app got Computer Use in Week 13. Week 14 brought it to the terminal.

### Computer Use in the CLI (Research Preview)

This is the more significant of the two Computer Use deployments. Terminal-based Computer Use means Claude can launch native applications, interact with their UI, observe the result, and iterate — all from a `claude` session in your terminal, without requiring the Desktop app.

The canonical use case Anthropic describes: Claude writes code, opens the app it just built, clicks through the interface to verify behavior, identifies a bug visually, returns to the code, fixes it, and re-tests. The full edit-run-verify loop, autonomous.

As of research preview, stability is limited. Complex multi-step UI interactions have a meaningful failure rate, and the latency per action is noticeable. But the capability itself represents a meaningful architectural step: Claude Code is no longer a tool that only operates on files and terminal output. It can interact with the rendered, visual layer of software.

### /powerup: Interactive Onboarding Inside the Terminal

`/powerup` launches an in-terminal interactive lesson system — animated demos that walk through Claude Code features without leaving your session. The target is new users who need to learn the tool's capabilities, but the lesson content is dense enough to be useful for experienced users discovering features they've missed.

It's also a distribution mechanism. As Claude Code's surface area expands (and this month makes clear how fast that's happening), `/powerup` becomes a way to surface recently shipped features to users who aren't reading changelogs.

### Flicker-Free Alt-Screen Rendering

An opt-in alternative rendering mode arrived: `claude --alt-screen` switches to a virtual terminal buffer where the prompt input stays pinned to the bottom, scrollback is virtualized, and the flicker on redraw is eliminated.

This matters most in long sessions with large outputs. The default renderer redraws the full screen on every update; the alt-screen renderer only redraws changed regions. For developers running Claude Code alongside other terminal tabs, the visual noise reduction is immediate.

### MCP Result-Size Override and Plugin PATH

Two developer-facing improvements for extending Claude Code:

**Per-tool MCP result-size override up to 500K** — MCP tools previously had a fixed result-size ceiling that caused silent truncation on large responses. The new per-tool override lets you set limits up to 500KB per tool, giving control over the memory/completeness tradeoff.

**Plugin executables on Bash tool's PATH** — Plugin-bundled executables are now automatically added to the Bash tool's PATH during sessions. This closes a friction point in plugin development where custom binaries weren't accessible without manual PATH manipulation.

---

## Week 15 (April 6–10): Ultraplan, Monitor, and the Agent Infrastructure Layer

Week 15 was less about individual features and more about Anthropic shipping pieces of a larger infrastructure — one designed for long-running, observable, collaborative agent workflows.

### Ultraplan (Early Preview)

Ultraplan separates plan creation from plan execution across two environments.

From your CLI, you invoke `/ultraplan` with an objective. Claude drafts an execution plan in the cloud. You receive a link to a web editor where you can review the plan step by step, leave inline comments, modify individual actions, add constraints, or annotate expected outputs. Once you're satisfied, you either execute the plan remotely on Anthropic's infrastructure or pull it back to run locally.

The design reflects a lesson that's become clearer as agentic workflows mature: the failure mode of autonomous agents isn't usually capability gaps, it's misaligned plans. A 30-step plan with one wrong assumption on step 3 produces 27 steps of confident wrong work. Ultraplan inserts a human review checkpoint at the plan level before any code runs.

For developers managing complex multi-file refactors, migrations, or deployments, this is a more tractable model than pure "set and forget" autonomy.

### Monitor Tool: Streaming Background Events

The Monitor tool addresses a specific gap in long-running agentic tasks: observability.

When Claude Code runs a background task — a build, a test suite, a deploy — you previously had no way to stream its output back into the conversation in real time. Monitor changes that. It watches a background process and surfaces each stdout line as a conversation event, letting Claude react to output as it arrives.

The practical pattern: start a long-running process in the background, attach Monitor, and Claude can tail the logs, catch errors mid-run, and take corrective action before the process exits. No more waiting for a process to finish to discover it failed four minutes in.

### /loop Self-Pacing

The `/loop` command from Week 12 gained an important behavioral change: when you omit the interval, Claude decides its own polling cadence based on what it's watching.

Watching a fast-moving build? It polls frequently. Waiting for a deploy that takes 10 minutes? It sleeps longer between checks. The model calibrates to avoid burning API calls on idle polling while staying responsive to state changes. This is a small but meaningful step toward Claude Code managing its own resource consumption.

### /team-onboarding and /autofix-pr

Two commands worth noting:

**`/team-onboarding`** — Generates a teammate ramp-up guide from your local Claude Code usage patterns, hooks configuration, and project context. Designed for teams where one person has set up an optimized Claude Code workflow and needs to share it without writing documentation manually.

**`/autofix-pr`** — Enables PR auto-fix from the terminal, extending the Web feature from Week 13 to CLI users. Invoke it to have Claude monitor a PR's CI status and handle failures automatically.

---

## Week 16 (April 11–17): The Desktop Redesign and Routines

The final week of the month was the largest single release: a complete rebuild of the Claude Code Desktop app and the launch of Routines.

### Desktop App Redesign (April 14)

Anthropic described the redesign as rebuilding Claude Code Desktop "around parallel sessions." That framing is accurate — the new sidebar is the organizing principle.

**Persistent session sidebar** — Every active and recent session is visible in a persistent left sidebar. You can filter by status (running, paused, completed), project, or environment. Sessions can be grouped by project. The design acknowledges the reality of how developers use Claude Code: not in single sequential sessions, but in parallel across multiple repos and contexts.

**Drag-and-drop layout** — Every pane — terminal, chat, file editor, diff viewer, preview — is draggable. You can arrange and resize them into whatever grid matches your workflow. There's no fixed layout.

**Integrated terminal** — A terminal pane is now built into the app, removing the need to context-switch to a separate terminal window for running builds or tests during a Claude Code session.

**In-app file editor** — Files can be opened and edited directly in the Desktop app. Designed for spot edits and quick reviews, not as a full IDE replacement.

**Rebuilt diff viewer** — The previous diff viewer degraded on large changesets. The rebuilt version is architected for performance on exactly those cases — thousands of changed lines across dozens of files render without lag.

**Expanded preview pane** — The preview pane now handles HTML files and PDFs in addition to local app servers. Useful for reviewing generated reports, documentation, or static output without leaving the app.

**Side chat (⌘+; / Ctrl+;)** — Opens a parallel chat thread that can pull context from the main session without adding anything back to it. The design intention is: ask a clarifying question, get an answer, and return to the main task without polluting the main thread's context window.

### Routines (Research Preview)

Routines is the automation layer that makes Claude Code's capabilities persistent.

A Routine bundles three things: a prompt, a repository, and any connectors (GitHub, CI systems, external APIs). Once configured, it can run on a fixed schedule, fire in response to an API call, or trigger on a GitHub event — a new PR, a push to a branch, a tag creation.

The critical architectural detail: Routines run on Anthropic's cloud infrastructure. Your local machine doesn't need to be running. This separates Claude Code automations from the lifecycle of your laptop session, making them viable for overnight jobs, CI integration, and team-shared workflows.

Daily run caps scale by plan, which introduces practical constraints for high-volume automation. But the capability itself — a persistent, event-driven automation layer backed by the full Claude Code toolset — is a significant expansion of what "AI coding tool" means.

### Opus 4.7, xhigh Effort, and /effort

Claude Opus 4.7 introduced a new effort tier: **xhigh**, positioned between the existing `high` and `max` levels. In Claude Code, xhigh became the new default effort level across all plans.

The practical effect: more thorough reasoning on complex tasks without the full token expenditure of `max`. For multi-file refactors, architecture reviews, and complex bug investigations, xhigh hits a better cost-to-quality balance than either the previous default or `max`.

The **`/effort` command** now opens an interactive slider with arrow-key navigation, making effort adjustment a first-class in-session control rather than a configuration file setting.

For Max plan subscribers, Auto Mode combines with Opus 4.7 to enable fully autonomous execution — the classifier from Week 13 running at maximum model capability, with no interrupts on safe actions.

### Additional Week 16 Releases

Several smaller but useful additions landed alongside the major features:

**`/ultrareview`** — Runs a comprehensive code review using parallel multi-agent analysis. Multiple Claude instances review the same codebase simultaneously from different angles (security, performance, architecture, test coverage) and synthesize findings. Slower than a single-agent review but more thorough on large PRs.

**Push notifications** — Claude can send mobile push notifications when Remote Control is enabled and "Push when Claude decides" is configured. Useful for long-running background tasks where you want a phone alert on completion or failure.

**`/tui` and flicker-free rendering** — The `/tui fullscreen` command switches to an alternative terminal renderer in the current session, delivering the alt-screen experience without restarting Claude Code.

**`/less-permission-prompts` skill** — Scans your transcript history, identifies patterns in what you've approved, and generates a proposed allowlist for `.claude/settings.json`. Reduces future interruptions by codifying your approval patterns.

**Prompt caching controls** — Two new environment variables: `ENABLE_PROMPT_CACHING_1H` opts into a 1-hour prompt cache TTL (instead of the default 5-minute TTL), and `FORCE_PROMPT_CACHING_5M` forces the 5-minute TTL regardless of API-level settings. For developers running Claude Code on Bedrock, Vertex, or Foundry, this gives explicit control over the cost-vs-freshness tradeoff.

**`/recap`** — Generates a contextual summary when returning to an existing session. Configurable in `/config` and invocable manually. Useful after multi-hour breaks where the session context needs refreshing before continuing.

**"Auto (match terminal)" theme** — A new theme option that mirrors your terminal's current dark/light mode. Minor UX, but eliminates the visual context switch when Claude Code's theme diverges from your terminal's.

---

## Three Platform-Level Shifts Worth Tracking

Individual features aside, three structural patterns emerge from this month's releases that point to where Claude Code is heading.

### 1. From Tool to Runtime

The combination of Routines, cloud infrastructure, and event-driven triggers means Claude Code is evolving from a tool you invoke into a runtime that executes on your behalf. The distinction matters: tools operate in your session; runtimes operate independently of it.

Routines running on GitHub PR events, Auto Mode handling permissions autonomously, Monitor reacting to process output — these are runtime behaviors. Anthropic is building the infrastructure for Claude Code to be an always-on participant in a development workflow, not just an on-demand assistant.

### 2. The Autonomous Loop Is Nearly Closed

Computer Use (Desktop + CLI) + Auto Mode + Ultraplan + Monitor + Routines forms a nearly complete autonomous development loop:

- **Plan** a complex task (Ultraplan)
- **Execute** it with automated permissions (Auto Mode)
- **Interact** with the UI to verify output (Computer Use)
- **Observe** running processes in real time (Monitor)
- **Repeat** on schedule without manual re-triggering (Routines)

Each piece is still in preview. None of them is production-stable individually. But the architecture of the loop is now visible, and the pieces are all shipping in the same month. The gap between "Claude Code as assistant" and "Claude Code as autonomous developer" is closing faster than most developers' mental models of the tool suggest.

### 3. Human-in-the-Loop is a First-Class Design Pattern

Ultraplan, the session sidebar, side chats, and `/recap` all reflect a consistent design principle: autonomy is more useful when humans can inspect and intervene at structured points. Anthropic isn't shipping full autonomy — it's shipping autonomy with well-defined review surfaces.

This matters practically. The failure mode developers most fear with AI coding tools isn't that they'll do nothing; it's that they'll do a lot of wrong things confidently. The design pattern of Ultraplan (review before execute), side chats (branch without polluting context), and `/recap` (re-establish shared understanding) treats that failure mode as an architectural concern rather than an edge case.

---

## What's Still in Preview

As of April 17, 2026, the following features carry preview status:

- **Auto Mode** — research preview; classifier edge cases expected
- **Computer Use (CLI)** — research preview; multi-step UI interactions unreliable
- **Ultraplan** — early preview; web editor interface still evolving
- **Routines** — research preview; daily run caps apply, configuration surface limited

These features are worth experimenting with, but treating them as production-stable components of a team workflow carries real risk. The pace of iteration means they'll change significantly in the coming weeks — which is itself useful information for planning when to adopt them.

---

## Key Takeaways

- Anthropic shipped 30+ Claude Code versions in 30 days — the pace itself is a signal about prioritization and the competitive environment around AI coding tools.
- The desktop redesign is the most immediately usable change for most developers: parallel session management, an integrated terminal, and a rebuilt diff viewer address real friction in day-to-day usage.
- Routines is the most strategically significant new feature: cloud-native automation triggered by schedules, APIs, or GitHub events represents a new category of capability.
- The autonomous coding loop (Ultraplan → Auto Mode → Computer Use → Monitor → Routines) is architecturally complete in preview form. Stability will follow.
- Several small additions — prompt caching controls, `/less-permission-prompts`, `/recap`, conditional hooks — are immediately useful with no preview risk.

For developers who haven't updated Claude Code recently: run `npm update -g @anthropic-ai/claude-code` and spend 20 minutes with `/powerup`. The tool you've been using is meaningfully different from what's available today.

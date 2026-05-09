# Bugs & Problems Log

---

## [BUG-001] Remote Trigger не може публікувати статті
**Дата:** 2026-05-05  
**Статус:** ✅ Закрито (замінено GitHub Action)

**Проблема:**  
Remote Trigger (Daily Morning Trigger) генерує статтю але не може запушити в GitHub.

**Корінна причина:**  
Remote Trigger виконується на серверах Anthropic (Linux, `/home/user/`), а не на локальному Mac. Щоразу репо клонується заново на чистому сервері. Git операції йдуть через локальний проксі (`127.0.0.1:PORT`) який навмисно блокує push. Сервер не має доступу до локальних файлів Mac (`settings.local.json`, `.git/config`, MCP сервери).

**Що пробували:**
1. Токен хардкодом в промпті (`ghp_*`) → Claude security scanner блокує
2. `$GITHUB_TOKEN` через `settings.local.json` → файл локальний, на серверах Anthropic недоступний
3. curl до Vercel endpoint → заблокований проксі (зовнішні домени)
4. `git push` → 403, проксі блокує push навмисно
5. GitHub MCP Server через `settings.json` → MCP сервер локальний, на remote серверах недоступний
6. Токен в URL `.git/config` → `.git/config` локальний, на remote сервері не існує

**Що пробували (продовження):**
7. Toggle "Allow unrestricted git push" увімкнений в Permissions → все одно 403. Агент пушить в `claude/gifted-franklin-fmQWt` і проксі блокує.

**Нова гіпотеза:**  
Проксі не має GitHub credentials взагалі. Репозиторій доданий як текст в рутині, але GitHub акаунт не авторизований через OAuth або GitHub App.

**Що пробували (продовження 2):**
8. Connectors таб рутини → "No more connectors available" — неможливо підключити GitHub безпосередньо до рутини
9. Settings → Connectors → GitHub Integration показує "Connected", але в меню "..." тільки "Disconnect" — немає інформації про scope

**Поточний діагноз:**  
GitHub OAuth підключений з read-only scope (або неповним write scope). Proxy має credentials, але вони не дають права на push. Toggle "Allow unrestricted git push" увімкнений але 403 зберігається — це означає що проблема в OAuth scope, а не у відсутності credentials.

**Рішення:**  
Відмовились від рутини. GitHub Action (`.github/workflows/daily-blog.yml`) вже робить те саме — запускається щодня о 7:00 CEST, генерує статтю через Groq, пушить в main, Vercel деплоїть автоматично. Станом на 2026-05-05 workflow працює стабільно.

---

## [BUG-002] Неправильний site URL в конфігурації
**Дата:** 2026-05-05  
**Статус:** ✅ Вирішено

**Проблема:**  
`astro.config.mjs` і `robots.txt` містили `https://youragency.com` — sitemap і SEO теги генерувались з фейковим доменом.

**Рішення:**  
Замінено на `https://agency-website-omega-ten.vercel.app` в обох файлах. Запушено.

---

## [BUG-003] GitHub токен скомпрометований
**Дата:** 2026-05-05  
**Статус:** ✅ Вирішено

**Проблема:**  
Два токени потрапили у відкритий текст — один в промпті Remote Trigger, інший в скріншоті.

**Рішення:**  
Старі токени видалено на GitHub. Новий токен `github_pat_*` збережений тільки в `settings.local.json` (gitignored) і Vercel env vars.

---

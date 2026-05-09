# Blog Automation System — Spec & Decisions

## Задача
О 7:00 CEST щодня GitHub Action генерує одну статтю — саммарі IT/AI/Tech новин за попередній день — і публікує її на блог.

---

## Новини

- **Джерела:** TechCrunch, The Verge, Ars Technica, Hacker News, MIT Tech Review AI, OpenAI News
- **Фільтр:** тільки статті з `pubDate` від 00:00 до 23:59 попереднього дня (CEST)
- Статті без `pubDate` — відкидаються
- Якщо за вчора < 3 статей — розширити вікно до 36 годин
- Дедуплікація по заголовку

---

## Стаття

- `publishedAt` = дата виходу статті (день запуску Action)
- Новини в тілі = за попередній день
- Заголовок відображає конкретні новини дня, ніколи не generic
- Мова: тільки англійська
- Стиль: визначається автоматично Claude Haiku, не повторюється підряд

| Стиль | Коли застосовується |
|-------|---------------------|
| News Roundup | Багато рівнозначних новин |
| Deep Dive | Одна домінуюча подія |
| Rumor Report | Витоки, неперевірена інформація |
| Quick Hits | Мало новин, короткий формат |
| Trend Analysis | Кілька пов'язаних новин утворюють тренд |
| Breaking Down | Складне технічне оголошення яке треба пояснити |

---

## Frontmatter schema

Обов'язкові: `title`, `description`, `publishedAt`, `category`, `readingTime`

Генеруються Claude Haiku: `tags`, `metaTitle`, `metaDescription`, `keyTakeaways`, `faq`

Фіксовані в скрипті:
```
author: "Bohdan Shvchk"
authorRole: "Founder & Shopify Developer"
authorBio: "Shopify developer and web agency founder. Covering the tech and AI news that matters for modern businesses."
authorLinkedIn: "https://www.linkedin.com/in/bogdan-shevchuk-b3827414a/"
```

---

## Конфлікти тем

Перед генерацією Claude Haiku перевіряє нові теми проти останніх 30 записів у `scripts/topic-log.json`.

Вердикти:
- **NEW** → публікувати
- **CONTINUATION** → публікувати, органічно посилатись на попередню статтю в тексті
- **ALL_CONFLICT** → публікувати найменш схожу тему + Telegram сповіщення

Після публікації: запис в `topic-log.json`:
```json
{
  "date": "2026-05-09",
  "title": "...",
  "slug": "...",
  "style": "News Roundup",
  "forced": false,
  "topic_summary": "..."
}
```

Логіка тонкої грані:
- iOS 26.4 вчора + iOS 26.4 сьогодні = **CONFLICT**
- iOS 26.4 вчора + iOS 26.4.1 сьогодні = **CONTINUATION**
- iOS 26.4 вчора + знайдена вразливість в iOS 26.4 = **CONTINUATION**

---

## Помилки (Claude Haiku недоступний)

- Спроби 1-3: retry через 5с → 15с → 30с
- Спроби 4-6: retry через 1г → 1г → 1г
- Telegram з 3-ї спроби (з реальним часом до наступної спроби)
- Після 6 провалів: день пропускається, фінальне Telegram

---

## Telegram сповіщення

Канал: @shvchk_blog_poster_bot  
Формат: строгий технічний текст, без емодзі  
Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

Надсилається при:
1. Спроби 3, 4, 5 — назва кроку + текст помилки + час до наступної спроби
2. Спроба 6 провалилась — день пропущено
3. Немає новин за вчора — день пропущено
4. Невалідний frontmatter — яке поле відсутнє
5. ALL_CONFLICT — список конфліктних тем
6. Успіх — заголовок опублікованої статті

---

## Технічний стек

- **GitHub Action** — `.github/workflows/daily-blog.yml`, запуск о 7:00 CEST (5:00 UTC)
- **Python** — `scripts/generate_blog.py`
- **Claude Haiku 4.5** — `claude-haiku-4-5-20251001`
- **Astro** — статичний сайт
- **Vercel** — авто-деплой при push в main

Вартість: ~$0.80/1M вхідних токенів, менше $1 на місяць при щоденних запусках.

Secrets в GitHub Actions: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

---

## Повний флоу

```
GitHub Action (7:00 CEST)
  → Fetch 6 RSS джерел
  → Фільтр: pubDate = вчора (00:00–23:59 CEST), без pubDate — відкидати
  → Дедуплікація по заголовку
  → Claude Haiku: перевірка конфліктів (topic-log.json, останні 30)
  → Claude Haiku: вибір стилю (не повторювати останні 5)
  → Claude Haiku: генерація статті (publishedAt = сьогодні)
  → Валідація frontmatter
  → Збереження .md файлу
  → Оновлення topic-log.json
  → git commit + push → Vercel деплоїть
  → Telegram: успішна публікація з заголовком
```

**Роадмап (актуальный)**

**1. Миграция на ADK** — ✅ ЗАКРЫТО

* \~~Переписать `harness_orchestrator.py`: state machine → ADK session/state, все skills как tools одного `LlmAgent`~~
* \~~Внедрить `policy_gate` как `before_tool_callback` (решено)~~
* \~~Перевести остальные skills в tools (по одному, с проверкой)~~
* Все 7 skills на ADK: profile-intake, job-intake, match, post-match (все 3 опции: gap-closing, discussion, cv-generation)
* discussion и cv-generation реализованы впервые (раньше не существовали в коде, только SKILL.md)
* Прямых openai-client вызовов в активном пути не осталось, кроме scan\_for\_pii и semantic\_check\_is\_command (общие внутренние утилиты, не отдельные skills — оставлены как есть намеренно)

**2. Логи и тесты**

* Сверить `trajectory.log` с ADK-трассировкой (дублировать или нет)
* Переписать тесты под новый вызов (моки сейчас на `h.client.chat.completions.create`)

**3. Верификация**

* Сверить `specs/architecture.md` с новой архитектурой
* \~~Прогнать полный цикл вручную (profile → PII → job → PII → match → post-match меню все 3 опции → CV)~~ ✅ СДЕЛАНО, работает end-to-end: profile-intake → PII → job-intake → PII → match → post-match (gap-closing → re-match, discussion Q\&A, CV с Vibe Diff → cv.md → прощальный экран → выход)

**4. Документация**

* Обновить `README.md` под ADK-setup
* Собрать `docs/` (action\_plan, discussion\_skill\_design, match\_logic, Idea, системная инструкция) — без `git comment.md`
* README должен явно закрывать evaluation-таблицу капстоуна (ADK ✓, MCP Server — нет пока, Security features ✓, Deployability, Agent skills)

**5. Сборка папки для сдачи**

* Финальный прогон → сохранить в `data/` (profile.json, job.json, cv.md + copy trajectory.log)
* Проверить `.gitignore` (нет `.env`, нет сырых PII)

**6. Материалы для сабмита (вне кода)**

* Video (5 мин): проблема → почему агенты → архитектура → демо → как строили
* Kaggle Writeup


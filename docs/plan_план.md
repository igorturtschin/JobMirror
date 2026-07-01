**Роадмап (актуальный)**

**1. Миграция на ADK** (ядро, блокирует всё остальное)
- Переписать `harness_orchestrator.py`: state machine → ADK session/state, все skills как tools одного `LlmAgent`
- Внедрить `policy_gate` как `before_tool_callback` (решено)
- Перевести остальные skills в tools (по одному, с проверкой)

**2. Логи и тесты**
- Сверить `trajectory.log` с ADK-трассировкой (дублировать или нет)
- Переписать тесты под новый вызов (моки сейчас на `h.client.chat.completions.create`)

**3. Верификация**
- Сверить `specs/architecture.md` с новой архитектурой
- Прогнать полный цикл вручную (profile → PII → job → PII → match → post-match меню все 3 опции → CV)

**4. Документация**
- Обновить `README.md` под ADK-setup
- Собрать `docs/` (action_plan, discussion_skill_design, match_logic, Idea, системная инструкция) — без `git comment.md`
- README должен явно закрывать evaluation-таблицу капстоуна (ADK ✓, MCP Server — нет пока, Security features ✓, Deployability, Agent skills)

**5. Сборка папки для сдачи**
- Финальный прогон → сохранить в `data/` (profile.json, job.json, cv.md + copy trajectory.log)
- Проверить `.gitignore` (нет `.env`, нет сырых PII)

**6. Материалы для сабмита (вне кода)**
- Video (5 мин): проблема → почему агенты → архитектура → демо → как строили
- Kaggle Writeup

Открытый вопрос: **MCP Server** — в評alu-таблице это отдельный обязательный пункт ("Code"), в текущей архитектуре не упоминается. Нужно решить, добавляем ли MCP или это не обязательно (только 3 из концептов нужны — возможно уже закрыто ADK + Security + Skills).
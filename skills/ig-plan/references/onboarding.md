# First run / Первый запуск

Respond in the user's language. This plugin drafts content; it has no Instagram
connection, publishing API or external MCP server in V0. The 13 skills keep
their original names and can be selected in Codex; examples use $ig-human,
$ig-caption and $ig-reel. Use the actual loaded skill paths, including a plugin
cache path, rather than assuming .agents/skills or the repository cwd.

1. Ask one compact question only if missing: preferred language/style (en,
   ru, ru-social), intended output and existing facts/voice examples. Use the
   user's answers already provided. Russian social posts use the same
   ru-social engine for Instagram, VK, Telegram and Threads.
2. Resolve a user-selected local data folder, preferably inside their working
   project. INSTAGRAM_AGENT_HOME may point there; don't alter global environment
   variables. Existing runtime data defaults still work. Read a supplied
   voice.md when present. The blank template is ../ig-reel/assets/voice.md.
3. If the user requests saving a profile, copy the template to the selected
   data folder and fill only their supplied facts. Don't overwrite an existing
   profile or store real personal data inside the installed plugin/cache.
4. Verify Python using the available interpreter and the scripts in the loaded
   skill folders. Run one small requested content task, or a supplied-text
   style check. Read heuristic exit 1 as REVIEW; Russian exit 3 needs contextual
   rewriting. Don't fabricate a PASS or loop to erase legitimate humor/voice.
5. Explain which skill to use next for the requested output. Publishing,
   comments and DMs are performed manually by the user. Image export, browsing
   and transcription depend on tools actually present, and remain UNVERIFIED
   when unavailable. Never request Instagram passwords, tokens or API keys.

Для старта достаточно выбрать язык, дать задачу и свои факты. Ничего
подключать не нужно. Не добавляйте обязательный CTA/вопрос/хештеги к русскому
посту. Локальный Python не отправляет текст в сеть; сам Codex обрабатывает
запросы через настроенный пользователем сервис/модель.

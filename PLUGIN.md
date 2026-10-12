# Instagram Drafting for Codex · Черновики Instagram в Codex

Version 0.1.0. Thirteen skills for drafting, reviewing supplied evidence and
planning content, with Python's standard library and en/ru/ru-social editing.
Adapted from [Jake Schincariol's MIT original](https://github.com/Jakeschincariol/instagram-agent-skill).
This is an independent plugin, not an official OpenAI/Meta product.

## Install the complete plugin

With a Codex CLI that supports plugins:

```text
codex plugin marketplace add artem917/instagram-agent-codex
codex plugin add instagram-agent-codex@instagram-codex-local --json
codex plugin list --marketplace instagram-codex-local --json
```

These are commands users intentionally run for their own CLI profile. V0
testing used a separate CODEX_HOME; it did not alter the user's global profile.
To use a downloaded release ZIP, extract its single plugin folder, then use
that folder's absolute path instead of owner/repo in marketplace add. Keep
your test profile/cache outside that folder. No copying thirteen skill folders.

For a separate profile, from the GitHub source checkout:

```text
python scripts/install_plugin.py --codex-home /path/to/isolated-profile --dry-run
python scripts/install_plugin.py --codex-home /path/to/isolated-profile
```

The helper builds one clean source snapshot and runs native marketplace/add/list
commands using that explicitly chosen CODEX_HOME. It refuses the global home
and refuses source/cache overlap. It never copies authentication; use Codex's
normal sign-in flow in that profile when needed. Launch Codex with the same
CODEX_HOME. In PowerShell, for this process/session only:

```powershell
$env:CODEX_HOME = 'C:\path\to\isolated-profile'
codex -C 'C:\path\to\your-project'
```

A project marketplace alone is not claimed to activate the plugin automatically
in every client. Native installation is the verified path. The old standalone
scripts/install.py remains unchanged for project-local individual skills.

Installed plugin skills are namespaced. For example:

```text
$instagram-agent-codex:ig-plan help me set up this plugin
$instagram-agent-codex:ig-human edit this Russian post in ru-social
$instagram-agent-codex:ig-caption draft an English caption from these facts
$instagram-agent-codex:ig-reel make a Reel from this idea
```

The skill selector may insert the correct mention for you. Plugin setup uses
the existing ig-plan skill's onboarding branch, so the original 13 skills
remain exactly 13. Choose language/output, provide your facts/voice samples,
and choose a local data folder. No Instagram account or token is needed.
The original standalone `scripts/install.py` remains supported and unchanged.

## Первый запуск

Установите один плагин целиком указанными командами или установщиком отдельного профиля.
В Codex выберите навык ig-plan этого плагина и попросите помочь с первым
запуском. Достаточно языка, задачи, своих фактов и примеров речи. Профиль
voice.md сохраняйте в выбранной папке проекта, а не в установленном кэше.
Для русских публикаций любой соцсети есть единый ru-social; ru сохраняет
литературную типографику, en остаётся режимом Python CLI по умолчанию.

Скрипты запускаются из папки реально загруженного навыка. REVIEW — замечание
эвристики; NEEDS_REWRITE — просьба о контекстной правке, без готового текста.
Не добавляются обязательные CTA, вопросы, хештеги или выдуманные результаты.

## Boundaries and future MCP

V0 has no registered MCP servers, credentials, lifecycle hooks, account
connection or publishing tools. mcp.json is a valid empty portable component.
An official Instagram HTTPS API may later be wrapped by a separately reviewed
MCP adapter. No official Meta MCP endpoint is asserted or invented.
The future design requires per-account consent and fresh explicit approval
before any external write or publication. No OpenAI moderation/submission was
performed. Decide the real MCP component before an eventual first public
submission; today's skills-only public-update flow cannot later add MCP.

Local Python tools do not send drafts over the network. Codex itself uses
the model/service the user configured. Browser, image export and transcription
are optional session capabilities; unavailable operations remain UNVERIFIED.
Source research/constraints: docs/INSTAGRAM_MCP_PLAN.md in the GitHub repository.

MIT LICENSE and upstream credit ship in the plugin and every skill folder.
Canonical portable plugin.json is accompanied by a Codex compatibility overlay.
Official packaging references: [package format](https://developers.openai.com/plugins/build/plugins),
[submission rules](https://developers.openai.com/plugins/deploy/submission).

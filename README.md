# Instagram Agent for Codex

Самостоятельная адаптация 13 навыков
[Instagram Agent Skill](https://github.com/Jakeschincariol/instagram-agent-skill)
Jake Schincariol для **OpenAI Codex**. MIT, без API-ключей и подключений к
социальным аккаунтам. Исходные творческие методики принадлежат автору оригинала;
этот репозиторий добавляет совместимость с Codex и проверяемый локальный запуск.
Точная версия оригинала и изменения — в [UPSTREAM.md](UPSTREAM.md).

Навыки готовят сценарии, тексты, планы и анализ предоставленных данных.
Пользователь самостоятельно публикует и отправляет готовые материалы.
Публикация в Instagram, VK, API, интеграции и монетизация в эту версию не входят.

## Установка в выбранный проект

Требования: Codex с доступом к локальным файлам и shell; Python 3.10+ для
скриптов. Git нужен для клонирования, но можно скачать ZIP репозитория.
Python-инструменты и установщик используют только стандартную библиотеку.

Windows PowerShell:

```powershell
git clone https://github.com/artem917/instagram-agent-codex.git
Set-Location instagram-agent-codex
python scripts/install.py --project 'C:\path\to\your-project' --dry-run
python scripts/install.py --project 'C:\path\to\your-project'
```

Если Windows распознаёт только Python Launcher, замените `python` на `py -3`.
Папка проекта должна уже существовать. Для использования набора прямо в его
клоне достаточно `python scripts/install.py --project .`.

macOS/Linux:

```sh
git clone https://github.com/artem917/instagram-agent-codex.git
cd instagram-agent-codex
python3 scripts/install.py --project /path/to/your-project
```

Установщик копирует **весь набор** в `<проект>/.agents/skills/`, включая
вспомогательные файлы, лицензию и шаблон голоса. Он не меняет глобальную
конфигурацию Codex. Повторная установка идентичных файлов допустима; если
существующий навык отличается, установщик завершится до копирования любого
навыка. Для обновления сначала сохраните свои изменения и согласуйте различия.

Откройте выбранный проект в Codex и введите `$ig-reel` или найдите навык через
`/skills` в CLI. В графическом интерфейсе используйте доступный селектор
навыков. Если изменения не появились, перезапустите сессию Codex.
`/ig-reel` из оригинала заменён на `$ig-reel`; это упоминание навыка в запросе,
а не команда PowerShell. Официальные правила:
[Codex Skills](https://learn.chatgpt.com/docs/build-skills),
[Agent Skills specification](https://agentskills.io/specification).

Можно скопировать все папки `skills/ig-*` в `.agents/skills` вручную. Отдельная
установка только одного навыка не даёт полного набора: рабочие процессы
обращаются к `ig-human`, а `ig-viral` использует ресурсы `ig-reel`.

## Личные настройки и материалы

Каждый навык читает свой `references/codex.md`, где описано разрешение путей.
Каталог материалов определяется в таком порядке:

1. `INSTAGRAM_AGENT_HOME`, если задан;
2. `<CODEX_HOME>/instagram`, если задан `CODEX_HOME`;
3. `~/.codex/instagram` иначе.

Для отдельных аккаунтов задавайте отдельный каталог. Пример в текущей
PowerShell-сессии (установка навыков всё ещё остаётся локальной):

```powershell
$env:INSTAGRAM_AGENT_HOME = Join-Path (Get-Location) '.instagram-agent'
New-Item -ItemType Directory -Force $env:INSTAGRAM_AGENT_HOME | Out-Null
Copy-Item templates/voice.md (Join-Path $env:INSTAGRAM_AGENT_HOME 'voice.md')
```

Заполняйте `voice.md` своими фактами и примерами речи. Установщик не создаёт
и не перезаписывает личный профиль. Не копируйте заполненный профиль в
публичный репозиторий. При переносе данных из Claude используйте отдельную
ручную копию; автоматической миграции чужих настроек нет.
Навыки сохраняют `swipe.md`, `plan.md`, `log.md` только как локальные материалы.
Одобрение черновика фиксируется как `DRAFT_APPROVED`, а `POSTED`/`SENT` —
только после подтверждения фактической публикации/отправки пользователем.

## Все 13 навыков

| Навык | Возможность |
| --- | --- |
| `$ig-reel` | Три hook-варианта из 26 формул, скоринг, сценарий и расчёт beat sheet. |
| `$ig-viral` | Ранжирование вручную собранных Reels относительно baseline аккаунта, swipe-файл. |
| `$ig-caption` | Подпись, preview первых 125 символов и локальный lint. |
| `$ig-carousel` | Тексты слайдов и HTML-layout; экспорт изображений зависит от доступного renderer. |
| `$ig-story` | Последовательность Stories, тексты и рекомендации по stickers. |
| `$ig-profile` | Разбор предоставленного профиля по 12 пунктам, максимум 100 баллов. |
| `$ig-plan` | Недельный план, форматы, темы и предложения для ручного engagement. |
| `$ig-human` | Английский режим и общий RU-движок: `ru`, `ru-social`, словарь, стиль, типографика и проверка данных. |
| `$ig-comment` | Варианты комментариев к предоставленным постам. |
| `$ig-reply` | Сортировка предоставленных комментариев и черновики ответов. |
| `$ig-dm` | Черновики личных сообщений и максимум два follow-up. |
| `$ig-repurpose` | Идеи для Reels и каруселей из предоставленного длинного материала. |
| `$ig-audit` | Анализ предоставленных Insights и результатов публикаций. |

## Шесть локальных инструментов

Из корня репозитория; `examples/` содержит вымышленные тестовые данные:

```text
python skills/ig-reel/hookscore.py examples/hooks.txt --json
python skills/ig-reel/beats.py examples/script.txt --target 30 --json
python skills/ig-caption/caption.py examples/caption.txt --keywords "client proposals" --json
python skills/ig-human/humanize.py examples/draft.txt --out outputs/clean.txt --report
python skills/ig-human/detect.py examples/draft.txt outputs/clean.txt --json
python skills/ig-viral/swipe.py examples/captured.tsv --out outputs/swipe.md --json
```

Это проверка текстовых свойств, а не прогноз просмотров или доказательство
авторства текста. Оценки исходного автора на историческом корпусе не были
независимо воспроизведены этим портом. Исходные scoring-алгоритмы сохранены;
изменения CLI и обработки данных перечислены в [PORTING.md](PORTING.md).

Все скрипты принимают UTF-8, UTF-8 BOM и CRLF, включая пути с пробелами и
кириллицей. Вывод — UTF-8. PowerShell 5.1 может менять кодировку при `>` и
clipboard pipes: предпочтительны входные файлы `Set-Content -Encoding UTF8`
и встроенные `--out` у humanize/swipe. Для JSON без перекодирования используйте
захват stdout через Python. Не заключайте текст с `$` в двойные кавычки
PowerShell: используйте файл или одинарные кавычки.

Русские режимы:

```text
python skills/ig-human/humanize.py post.txt --mode ru-social --json
python skills/ig-human/detect.py original.txt edited.txt --mode ru-social --json
```

`ru` допускает литературную типографику; `ru-social` использует обычные
двойные кавычки, без длинного тире и пустых строк. Необязательные параметры
площадок отделены от языка (`--platform-settings settings.json`). Если
социальную пунктуацию или данные нельзя изменить безопасно, `text: null`,
`candidate` для проверки и exit 3; текстовый вызов не перезаписывает результат.
Никаких обязательных CTA, вопросов или хештегов.

Коды выхода английского режима:

| Инструмент | 0 | 1 | 2 |
| --- | --- | --- | --- |
| hookscore | Есть STRONG hook | Нет STRONG hook | Неверный ввод/ошибка файла |
| caption | READY | REVIEW/FIX | Неверный ввод/ошибка файла |
| detect | Последний текст PASS | REVIEW/FLAGGED | Неверный ввод/ошибка файла |
| beats, humanize, swipe | Отчёт/текст сформирован | — | Неверный ввод/ошибка файла |

`--json` использует те же коды выхода. REVIEW для короткого текста ожидаем:
часть detector-панели отвечает «too short to judge». Не дополняйте текст
выдуманными фактами ради PASS.

## Проверки

```text
python scripts/validate.py
python -m unittest discover -s tests -v
python -m compileall -q skills scripts tests
```

Валидатор проверяет используемое этим набором ограниченное подмножество YAML,
ресурсы, ссылки, Python-синтаксис, регулярные выражения, лицензии и hashes
сохранённых JSON. Он не является универсальным YAML parser. Результаты
проверок и реальные Codex smoke-запуски описаны в [TEST_REPORT.md](TEST_REPORT.md).

## Ограничения первой версии

- Браузерное исследование `ig-viral` требует реально доступного browser tool
  и открытых данных либо вставленных пользователем наблюдений. Нет crawler,
  автоматического логина или доступа к Instagram Insights.
- `yt-dlp` — только необязательный пример для YouTube. Не установлен и не
  требуется для набора. Транскрибация и монтаж нуждаются в доступных инструментах;
  без них `ig-repurpose` работает с предоставленным текстом.
- Для PNG/JPEG каруселей нужен доступный image renderer. Печать в PDF не даёт
  готовые изображения для Instagram. Полный image export отмечен UNVERIFIED.
- `ig-human` поддерживает `en` (по умолчанию), `ru` и единый `ru-social` для
  любых соцсетей. Остальные scoring-инструменты остаются английскими. См.
  [RU workflow](skills/ig-human/references/ru.md) и [RU test report](RU_TEST_REPORT.md).
  Сложные смысловые/грамматические правки делает Codex по рекомендациям;
  нормализатор не выдаёт небезопасную замену тире за готовый текст.
- `ig-human` сохраняет ZWJ/tag emoji; полный Unicode grapheme parser и
  общая гарантия смысловой эквивалентности не заявляются. Проверяйте результат.
- Числа 125/2200/5 и маркетинговые рекомендации сохранены как исходные
  настройки/ориентиры, а не обещание текущих правил Instagram. Проверяйте
  актуальные официальные ограничения перед реальным применением.
- Нет обещаний вирусности или результатов сторонних AI-detectors. Проверки
  автоматизации не доказывают качество всех будущих текстов.

## Авторство и лицензия

Оригинал: Jake Schincariol,
[instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill).
Адаптация для Codex: artem917, 2026.
[LICENSE](LICENSE) сохраняет исходный MIT-текст и copyright без изменений.
Каждая устанавливаемая папка также содержит LICENSE и NOTICE.md.
Проект не является официальным продуктом OpenAI или Meta.

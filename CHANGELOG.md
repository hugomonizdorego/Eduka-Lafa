# Changelog

## 0.1 Alpha (0.1.0a1) — 6 October 2026 · development restart

Version numbering restarts at **0.1 Alpha**. Every feature, test, screenshot and
document is being re-checked from the beginning; earlier prototype results are
history, not current guarantees.

### Redesign (LAFA Desktop, Virtual Assistant, Eduka-Settings)
- **LAFA Desktop redesigned**: new theme, icon navigation, Home dashboard
  (greeting, quick ask, Virtual Assistant toggle, feature cards, tip of the
  day, system check), chat suggestion chips. Settings left the sidebar list.
- **Edukasaun OS help** page and chat answers: 16 offline guides in EN/ID/PT/TET,
  allowlisted tool launcher without a shell, read-only system check, `/os`.
- **Virtual Assistant behaviour**: snaps onto the Eduka-Panel; idle cycle is
  walk to a random spot → activity → walk; activity duration configurable.
- **Hover questions**: touching LAFA with the cursor stops it and shows a
  changing "Can I help?" balloon that reacts to the current activity; clicking
  the balloon opens chat.
- **Personality**: innocent, curious, clever and funny. Each activity is an
  assistant duty; LAFA comments on activities, tells jokes (`/joke`, 😄 button,
  between cards). New preferences: hover questions, self-talk, jokes.
- **All settings in Eduka-Settings**: the native page now holds every
  non-secret preference, saves atomically and live-reloads LAFA with the new
  `--reload` role. LAFA's own settings window uses Eduka-Settings-style
  categories, including Personality & activities and About.
- Screenshot script rewritten: 23 captures including hover, panel walking and
  the Eduka-Settings page.
- Fixed: tool lookup now resolves `shutil.which` at call time; `&` in host
  group titles is no longer shown as a shortcut marker.

### Added
- **Open-source AI without a main server**: Ollama on this computer (free, no
  key, HTTP allowed only for loopback addresses) and any OpenAI-compatible
  open-source server over HTTPS (llama.cpp, vLLM, LocalAI, a school or
  community host). Key is optional for these servers.
- **Fetch available models** button in Settings for every provider except
  Perplexity, so users choose from real model IDs instead of guessing.
- `/calc` (also `/hitung`, `/kalkula`): bounded calculator parsed with `ast`,
  never `eval`; accepts `×`, `÷`, `^` and decimal commas.
- `/help` (also `/bantuan`, `/ajuda`): translated list of LAFA commands.
- LAFA Virtual Assistant greets by local time of day (morning, afternoon,
  evening) on first activation; can be turned off in Settings.
- LAFA Virtual and the Desktop character give a short hop when an answer arrives.

### Fixed
- Tetun, Indonesian and Portuguese Wikipedia searches with no result now fall
  back to English Wikipedia; the source URL shows which edition answered.
- Consecutive same-role messages are merged before provider calls, so
  providers requiring alternating roles accept the source-synthesis step.
- HTTP User-Agent now reports the real package version instead of a fixed value.
- Chat footer no longer warns about paid API credits when an open-source model
  is selected.

### Validation
- 131 automated tests passed in a headless Linux environment; 23 screenshots
  regenerated. See `docs/VALIDATION.md`.

## Prototype history (before the restart)

### Prototype 0.4

- Explicit Search public sources action and `/ask`; ordinary source-mode chat
  is no longer sent automatically to Wikipedia.
- Three settings tabs, complete common UI translations and translated service
  categories/lesson labels for English, Indonesian, Portuguese and Tetun.
- Provider/model edits use a draft; cancellation and failed preference writes
  preserve live preferences. Saving preserves coding output and chat drafts.
- Fixed 60-second activity rotation when culture and encouragement cards are
  both disabled; automatic popups respect pause, drafts and open chat.
- Native Eduka-Settings page factory, descriptor, integration test host,
  activation acknowledgement/timeout and strict single Qt binding checks.
- Safer source-hook auto-detection and launcher escaping for unusual paths.
- Bounded regular-file preference reads, field-by-field recovery, and a read-only
  system readiness checker with optional live public-source checks.
- 88 tests (87 passed, one environment skip) and 17 review screenshots.

### Prototype 0.3

- Separate Desktop, Settings and Virtual Assistant surfaces and launch roles.
- Virtual assistant off by default, translated activation and introduction.
- Traditional male Timor-Leste costume, Tebe-tebe and Bidu mascot poses.
- Seventeen activities; panel-edge walking configuration and idle source cards.
- Timor-Leste topic headlines from Tatoli, Timor Post and government feeds.
- Public extract mode without AI keys; bounded Python coding lessons and
  JavaScript/HTML/CSS read/export examples.
- English source/build documentation; system-language mode plus four UI locales.
- Native Eduka-Settings group and review-copy source integration generator.
- Hardened document access, special-file rejection, PDF limits, framed IPC,
  settings validation, lesson resource bounds and worker error recovery.
- Fourteen reproducible screenshots and expanded security/validation notes.

### Prototype 0.2

Desktop bubble input, fifteen activities, weather, world RSS headlines,
additional learning links, session reminders and same-user launcher activation.

### Prototype 0.1

Initial native assistant, official provider adapters, local file/document tools,
public encyclopedia, browser service links and nine character poses.

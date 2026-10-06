# Privacy and permissions

- API conversation sends the input and up to twelve prior messages to the
  selected provider after Send. Provider retention policies apply. Chat stays
  in memory unless the user exports it; switching provider clears context.
- Without a configured API, ordinary chat is never sent automatically to
  Wikipedia. Search public sources and `/ask` explicitly send the selected
  public topic; `/learn` explicitly searches public snippets. Search queries
  belong to the receiving site, so do not include private information. Prepared
  greetings and supportive replies are local; general AI conversation requires
  an optional configured provider.
- Local filename results stay on the computer. Document reading is local;
  Summarize confirms provider and character count before sending selected text.
  Explain with AI likewise confirms before sending lesson code.
- Listen confirms eight seconds of microphone capture and OpenAI transcription.
  The temporary audio is deleted and the transcript is reviewed in the input.
  There is no always-on microphone, camera, global keyboard hook or telemetry.
- Read aloud uses local espeak; Tetun uses Portuguese pronunciation as fallback.
- Website sign-in occurs in the default browser. LAFA does not read passwords,
  cookies, account sessions or browser storage. No universal account login exists.
- Secrets stay in session memory, external environment or an approved secure
  keyring. Settings files never contain API keys. Clear key does not delete
  externally managed environment variables.
- Weather sends an explicit city query or coordinates to Open-Meteo. Dili is
  the default; no device geolocation is used. World/local news retrieves RSS
  headline metadata. Full stories open only on the publisher website.
- When enabled, idle Timor-Leste news updates retrieve the three configured
  feeds at the selected interval. Curated culture cards are shipped locally;
  a source is contacted when the user opens its link. Browser searches contact
  that site when opened. Reachability probes run every 30 seconds.
- The mascot is disabled until enabled through Settings. It hides offline and
  stops animation/voice. Reminders wait offline and are lost when LAFA exits.
- Local IPC accepts five fixed same-user launch roles. It cannot submit a
  command, URL, message or filename. No network listener is included.
- `scripts/check-system.py` makes no public requests unless `--network` is
  selected. Reports include basic runtime and preference status, but no API
  keys, model IDs, chat text or selected folder paths. The network mode makes
  fixed public checks for Dili/Wikipedia/weather and configured Timor-Leste feeds.

The prepared supportive-chat messages and optional empathetic AI prompt support
conversation. They do not establish a human relationship, clinical expertise or
knowledge of everything on the internet. Source links identify where information
came from; users can compare independent references.

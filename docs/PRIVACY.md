# Privacy and permissions

- API conversation sends the input and up to twelve prior messages to the
  selected provider after Send. Provider retention policies apply. Chat stays
  in memory unless the user exports it; switching provider clears context.
- Without a configured API, a short topic typed in Husu LAFA (up to eight
  words, for example "buku" or "Ataúro") is first answered from LAFA's own
  lessons and atlas and, when online, looked up on Wikipedia in the interface
  language. Personal sentences (my/saya/ha'u, address, family, password,
  problem…), long text, code and anything that looks private are never sent.
  Search public sources and `/ask` explicitly send the selected public topic; `/learn` explicitly searches public snippets. Search queries
  belong to the receiving site, so do not include private information. Prepared
  greetings and supportive replies are local; general AI conversation requires
  an optional configured provider.
- LAFA's memory (`~/.cache/lafa/memory`, 0600) holds only public web pages
  of the listed learning and Timor-Leste sources, read when online about once
  an hour (robots.txt respected, HTTPS only, Facebook pages never read), and
  Wikipedia articles LAFA showed. Searching the memory never leaves the
  computer. With an AI signed in, the best public passages are sent with the
  question so the AI can cite them.
- AI Hub web tabs keep their sign-in cookies in a private LAFA profile
  (`~/.local/share/lafa/aihub`, 0700). Passwords are typed on the AI
  company's own page. LAFA never reads those cookies, tokens or the answers;
  "Ask the selected AIs" only types the question into the pages. Camera,
  microphone, location and notification requests are refused.
- OpenRouter sign-in uses OAuth PKCE: openrouter.ai sends a one-time code to
  a loopback address on this computer (localhost:3000) and LAFA exchanges it
  for a key, which is kept in the system keyring (or only for the session).
- Agent actions open installed programs from a fixed list (browser, files,
  settings, calculator…) without a shell; nothing typed is executed.
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
  stops animation/voice. Reminders also fire offline and are lost when LAFA exits.
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

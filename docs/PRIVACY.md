# Privacy and permissions

Lafa 0.2.0 has no account, no AI service, no Lafa server and no telemetry.
Everything below happens on this computer unless a line says that something
goes to a public website. That happens only when the learner presses a
button or types an internet command.

## Stays on this computer

- **Search** of lessons, the Timor-Leste atlas, Edukasaun OS guides, saved
  material and file names. Questions typed in the search box are never sent
  anywhere by themselves.
- **Files**: only the folders the learner chose are searched. The search uses
  file names; documents are read locally (bounded size; PDFs in a
  resource-limited worker). File contents are never sent to the internet.
  Symbolic links, FIFOs and files outside the chosen folders are refused.
- **Practice results, tasks, timetable, reminders, favourites and recent
  material**: JSON files in `~/.local/share/lafa` (written atomically, 0600).
  Practice results are personal progress, not an official report.
- **Settings**: `~/.config/lafa/settings.json` (0600). When upgrading from
  0.1.x, a one-time backup with the old AI fields is written next to it
  (`settings.json.0.1-backup`, 0600). Lafa never reads the system keyring.
  Keys stored there by 0.1.x stay until the user removes them.
- **Read aloud** uses local espeak-ng. There is no microphone, camera, global
  keyboard hook or always-on listening.
- **Actions** ("buka kalkulator", "loke kelas") open installed programs or
  Lafa pages from a fixed list, without a shell. Nothing typed is executed.

## Goes to a public website (only when asked)

- **Search internet sources** and `/ask`: the topic words (one line, at most
  300 characters) go to Wikipedia in the interface language. Personal
  sentences are not sent automatically, because nothing is.
- **Save for offline**: the chosen public page is fetched once and stored in
  `~/.cache/lafa/memory` (0600). Only front pages and feeds of the listed
  sources are read; robots.txt is respected. Logins, Facebook pages and whole
  sites are never read.
- **Source status** (Library → Internet sources): a HEAD request to the shown
  sources, at most once a day, or on *Check now*.
- **Weather** sends the chosen city or coordinates to Open-Meteo. Dili is the
  default, and device geolocation is not used.
- **News** (Timor-Leste and world) retrieves RSS headline metadata. Full
  stories open on the publisher's website.
- **Content catalogue** (when "update sources" is on, at most once per chosen
  interval, default daily): the validated data file `lafa/assets/catalog.json`
  is downloaded from the Lafa repository on GitHub. It is data only (links,
  tips, cards) and never code. Program updates come from APT / EUS.
- **Optional Timor-Leste news updates** for the Virtual Assistant are off by
  default.
- **Connection check**: a request to Wikipedia, Open-Meteo or
  timor-leste.gov.tl, only to know whether internet sources can be offered.
- **External sites and optional AI websites** (ChatGPT, Claude, Gemini) open
  in the user's own browser. Lafa does not sign in, read accounts, cookies,
  passwords or sessions, or send questions or documents there.

## Virtual Assistant

- It is off until it is switched on in Eduka-Settings → Lafa-Configuration.
  Lafa Desktop never switches it on.
- It observes only events inside Lafa's own windows. Fullscreen detection on
  X11 reads the active window's fullscreen state with `xprop`.
- Quiet mode, reduce motion and the hourly message limit are local preferences.

## Other

- Local IPC accepts five fixed same-user launch roles. It cannot submit a
  command, URL, message or file name. There is no network listener.
- `scripts/check-system.py` makes no public requests unless `--network` is
  given. Its report contains no folder paths or personal data.

Source links show where information came from. A reachable website does not
prove that its content is correct. Learners can compare independent
references.

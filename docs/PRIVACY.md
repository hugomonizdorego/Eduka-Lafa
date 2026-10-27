# Privacy (Lafa 0.3)

Lafa has no account, no login, no analytics and no AI. It sends no personal
data anywhere.

## What Lafa stores on this computer

| File | Content |
| --- | --- |
| `~/.config/lafa/settings.json` (0600) | Language, theme, text size, school level, learner name (optional), Virtual Assistant preferences |
| `~/.local/share/lafa/progress.json` (0600) | Items read, favourites, quiz results, word boxes (spaced repetition), XP, achievements, streak |
| `~/.local/share/lafa/lafa.db` and `media/` | Downloaded Wikipedia introductions and photos with their credits |
| `~/.local/share/lafa/updates/` | Content files downloaded from the update channel |

Settings → *Hamoos progresu* deletes the progress; *Offline no atualizasaun →
Hamoos dadus download* deletes the downloads.

## Network requests

Only HTTPS, only to these hosts, only when the learner asks (or when the
daily update check is allowed in settings), without cookies or personal data:

* `*.wikipedia.org/w/api.php` — introductions and lead-picture names;
* `commons.wikimedia.org/w/api.php` and `upload.wikimedia.org` — photo licence and file;
* `api.worldbank.org` — World Bank indicators for Timor-Leste;
* `raw.githubusercontent.com/hugomonizdorego/Eduka-Lafa/…` — the content manifest and files;
* a HEAD request to public sites to show *Online*/*Offline*.

Links to source pages (government sites, Britannica, Tripadvisor…) open in the
learner's own web browser.

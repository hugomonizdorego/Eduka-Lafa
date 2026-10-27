# Offline and online (Lafa 0.3)

Lafa is offline first: everything in Lafa Desktop and the Virtual Assistant
works without internet. The internet only adds downloads and updates.

| Works offline | Needs internet (on request or when allowed) |
| --- | --- |
| Encyclopedia (≈150 articles, municipalities, places, holidays), search, map, timeline, tourism, calendar and `.ics` export, millionaire quiz, words, flash cards, learning paths, progress, read aloud (espeak-ng), the Virtual Assistant | Offline pack (Wikipedia introductions + free-licence photos), content updates, World Bank data, opening a source page or Wikipedia in the web browser |

## Offline pack

*Offline no atualizasaun → Download hotu* downloads, for every item that names
a Wikipedia page, the introduction in Tetun, Portuguese, Indonesian and
English (Wikipedia, CC BY-SA 4.0) and one photo from Wikimedia Commons.
Photos are downloaded **only** when their licence is CC0, public domain,
CC BY or CC BY-SA and they are not marked non-free; the author, licence and
source page are saved with the photo and shown under it and on *Fonte no
lisensa*. Everything is stored in `~/.local/share/lafa/lafa.db` and
`~/.local/share/lafa/media/`, and can be cleared on the same page.

## Updates without a Lafa server

`lafa/assets/timor/manifest.json` (content version + SHA-256 and size of each
content, vocabulary and map file) is published in this public repository.
*Buka agora* (check now) — or the automatic check once a day when online and
allowed — downloads the manifest from `raw.githubusercontent.com`, then only
the files whose hash differs. A file is saved in `~/.local/share/lafa/updates`
only when its SHA-256 and size match, its path is a content/vocab/map JSON
file and its JSON has the expected shape. Newer files replace the packaged
ones when Lafa loads; a broken file is ignored. Lafa never downloads or runs
code.

## Online status

The top bar shows *Online* or *Offline*. A light HEAD request to a few public
hosts runs every 90 seconds in a worker; nothing waits for it.

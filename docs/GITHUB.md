# Upload source to GitHub

Create an empty GitHub repository, for example `lafa`, then run inside the
extracted `lafa/` folder. Replace YOUR-ACCOUNT with your actual account.

```bash
git init
git add .
git commit -m "LAFA 0.4.0 Desktop and Virtual Assistant"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/lafa.git
git push -u origin main
```

No GitHub repository was created or published by this deliverable. The ZIP is
source ready for your upload. Real keys, virtual environments, cache directories,
logs and build files are excluded by `.gitignore`.

Suggested repository description:

> LAFA: an animated AI desktop learning companion for Edukasaun OS, with local
> file search, public research, voice and official multi-provider APIs.

GitHub Actions runs core and offscreen Qt tests on push/pull request. Internet
accounts and provider credentials are not needed by the test suite.

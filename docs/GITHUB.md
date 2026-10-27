# Upload source to GitHub

Create an empty GitHub repository, for example `lafa`, then run inside the
extracted `lafa/` folder. Replace YOUR-ACCOUNT with your actual account.

```bash
git init
git add .
git commit -m "LAFA 0.1 Alpha Desktop and Virtual Assistant"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/lafa.git
git push -u origin main
```

No GitHub repository was created or published by this deliverable. The ZIP is
source ready for your upload. Real keys, virtual environments, cache directories,
logs and build files are excluded by `.gitignore`.

Suggested repository description:

> Lafa — Ensiklopédia Timór-Leste: an offline-first encyclopedia of
> Timor-Leste in Tetun, Portuguese, Indonesian and English (history, State,
> culture, economy, map, tourism, holidays, millionaire quiz, 1000+ Tetun
> words) with a virtual assistant for Edukasaun OS. No login, AI or server.

GitHub Actions runs core and offscreen Qt tests on push/pull request. The test
suite needs no internet, account or key.

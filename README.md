# Fahad Sabah — Academic Portfolio (GitHub Pages)

## Your portfolio URL (after deploy)

1. Create a GitHub account (or use yours).
2. Create a repository named **exactly**:
   - `YOUR_USERNAME.github.io`  
   OR  
   - `portfolio` (then enable Pages from `/` or `/docs`)
3. Push this folder’s contents to that repo’s `main` branch.
4. In GitHub: **Settings → Pages → Deploy from branch `main` / root**.

**URL forms:**
- User site: `https://YOUR_USERNAME.github.io/`
- Project site: `https://YOUR_USERNAME.github.io/portfolio/`

Suggested username if free: `fahadsabah` → **`https://fahadsabah.github.io/`**

Edit `index.html` and replace `YOUR_USERNAME` only if you change repo/links (Scholar/ORCID already set).

## Page contents
- `index.html` — photo, research, appointments, selected pubs, teaching, service
- `publications.html` — year-wise list (auto-synced from Semantic Scholar)
- `photo.jpg` — profile portrait
- `sync_publications_ss.py` — rebuild publications from Semantic Scholar author `152567681`
- `.github/workflows/sync-publications.yml` — weekly + manual sync

## Auto-update publications
1. Push this repo (already on `fswarisdar.github.io`).
2. GitHub → **Actions** → enable workflows if prompted.
3. Run **Sync publications (Semantic Scholar)** once (Actions → workflow → Run workflow), or wait for Monday 06:00 UTC.
4. Citations on the publications page are **Semantic Scholar** (often lower than Google Scholar). Keep the Scholar link for applications.

Manual local sync:
```powershell
cd e:\PythonProjects\JobApplications\github_portfolio
python sync_publications_ss.py
git add publications.html index.html ss_meta.json
git commit -m "chore: sync publications from Semantic Scholar"
git push
```

## Use on applications

Paste: **https://fswarisdar.github.io/**

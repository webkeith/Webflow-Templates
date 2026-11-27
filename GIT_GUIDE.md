# Git guide — block library

How to put the block library under version control, back it up on GitHub, and publish it as a live URL. Commands work in Terminal (macOS/Linux) and Git Bash or PowerShell (Windows).

## 1. One-time setup

```bash
git --version                      # install from git-scm.com if missing
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

## 2. Create the repository

From inside the unzipped `block-library` folder:

```bash
cd block-library
git init
git add .
git commit -m "Initial import: engine, 3 templates, dashboard UI, image registry"
```

`.gitignore` keeps generated files out of Git: `dist/` (rebuilt by `build.py`), Python caches and OS files. Commit sources, never build output.

**Your photos:** copy the eight `.jpg` files into `images/` before the first commit, so the repository is complete:

```bash
git add images/*.jpg
git commit -m "Add library photos"
```

They total a few MB, which is fine for plain Git. If you later add large videos or many high-res images, switch those to Git LFS: `git lfs install`, then `git lfs track "*.mp4"`.

## 3. Push to GitHub

1. Create an empty repository on github.com: no README, no .gitignore, private if the templates are client work.
2. Connect and push:

```bash
git remote add origin https://github.com/<you>/block-library.git
git push -u origin main
```

## 4. Daily workflow

```bash
git pull                                   # get the latest first
python templates/saas-b2b/generate.py      # only if you edited the SaaS generator
python build.py                            # rebuild dist/ and check it
git status                                 # see what changed
git add -A
git commit -m "Add pricing2 block"         # one change per commit, present tense
git push
```

Before each commit, open `dist/index.html` and check that the blocks you touched still preview correctly.

## 5. Branches for bigger changes

Use a branch per template or feature so `main` always builds:

```bash
git switch -c feature/clearance-template   # new branch
# ...work, commit as usual...
git push -u origin feature/clearance-template
```

Open a Pull Request on GitHub, review the diff, merge, then:

```bash
git switch main
git pull
git branch -d feature/clearance-template
```

**Naming:**
- `feature/<name>` for new templates or blocks
- `fix/<name>` for bug fixes
- `ui/<name>` for dashboard changes

## 6. Publish the library as a live URL (optional)

The included workflow `.github/workflows/pages.yml` rebuilds the library and publishes `dist/` on every push to `main`.

1. On GitHub, open the repository → **Settings → Pages**.
2. Under **Build and deployment**, choose **Source: GitHub Actions**.
3. Push to `main`. The site appears at `https://<you>.github.io/block-library/` after the workflow finishes (**Actions** tab).

A hosted library also gives every image a public URL. You can paste `https://<you>.github.io/block-library/images/hero-team.jpg` into the library's **Images** panel instead of uploading to Webflow first. Uploading to Webflow Assets is still better for production sites.

GitHub Pages sites are public even when the repository is private on paid plans. Don't publish client-confidential templates this way.

## 7. Releases

Tag a version when a set of blocks is ready to share:

```bash
git tag -a v1.1.0 -m "Add Small Business page blocks, combo-class and interaction fixes"
git push origin v1.1.0
```

On GitHub, **Releases → Draft a new release** turns the tag into a downloadable zip.

**Version numbers:**
- **Major** (2.0.0): changes that break pasted classes.
- **Minor** (1.1.0): new blocks or templates.
- **Patch** (1.0.1): fixes.

## 8. Undo and recovery

| Situation | Command |
|---|---|
| Discard uncommitted edits to a file | `git restore path/to/file` |
| Unstage a file | `git restore --staged path/to/file` |
| Fix the last commit message (not yet pushed) | `git commit --amend` |
| Undo a pushed commit safely | `git revert <commit-sha>` |
| See history | `git log --oneline --graph` |
| Compare with the last commit | `git diff` |

Avoid `git push --force` on `main`.

## 9. What lives where

| Path | Commit? | Notes |
|---|---|---|
| `engine/`, `build.py`, `ui/` | Yes | The converter and dashboard |
| `templates/*/` | Yes | `index.html`, `style.css`, `meta.json`, `nav.js`; for saas-b2b also `generate.py` |
| `images/`, `images.json` | Yes | Placeholder and library photos |
| `requirements.txt` | Yes | `pip install -r requirements.txt` |
| `.github/workflows/pages.yml` | Yes | Optional hosting |
| `dist/` | No | Rebuilt by `python build.py` |

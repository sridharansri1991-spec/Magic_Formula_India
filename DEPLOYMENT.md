# 🚀 Deploy to Streamlit Cloud — FREE Public URL

Follow these steps to deploy your Magic Formula Dashboard online for free.

## Prerequisites
- GitHub account (free): https://github.com/signup
- Streamlit account (free): https://share.streamlit.io

## Step 1 — Create GitHub Repository
1. Go to https://github.com/new
2. Name: `magic-formula-india` (or any name)
3. Visibility: **Public** (required for free Streamlit Cloud)
4. Click "Create repository"

## Step 2 — Upload Files (drag & drop)
1. Click "Add file" → "Upload files"
2. Drag ALL files from this folder EXCEPT `__pycache__/`
3. Commit changes

## Step 3 — Deploy
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Repository: `yourusername/magic-formula-india`
5. Main file: `magic_formula_app.py`
6. Click "Deploy!"

## Step 4 — Access
Your app is live at: `https://[your-app-name].streamlit.app`

## Troubleshooting
- If Screener.in blocks cloud IP: use Custom List with 10-20 stocks
- If deploy fails: check `requirements.txt` has exact versions
- App sleeps after 7 days idle — visit URL to wake up (30s)

## Auto-update
Any push to GitHub → app auto-redeploys. Edit files on GitHub web UI or use:
```
git clone https://github.com/yourusername/magic-formula-india
# make changes
git commit -am "update"
git push
```

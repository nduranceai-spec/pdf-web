# PDF Password Remover Web

A Git-ready web application for removing encryption from a PDF when the user knows the existing PDF password.

## Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python FastAPI
- PDF processing: pikepdf
- No database required

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000

## Deploy to Vercel

Import this repository into Vercel with the project root set to the repository root. The root `main.py` entrypoint imports the existing FastAPI app, and `vercel.json` routes requests to it. Python 3.12 is selected for the deployment runtime.

## Git

```bash
git init
git add .
git commit -m "Initial PDF password remover web app"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## Important
This app requires the correct existing PDF password. It does not crack or bypass unknown passwords. Uploaded and processed PDFs are stored temporarily in the system temporary directory and removed after processing or download.

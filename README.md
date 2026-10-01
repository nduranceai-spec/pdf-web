# PDF Password Remover Web

A Git-ready web application for removing encryption from a PDF when the user knows the existing PDF password.

## Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python FastAPI
- PDF processing: pikepdf
- No database required

## Run locally on Windows 11

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

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
This app requires the correct existing PDF password. It does not crack or bypass unknown passwords.

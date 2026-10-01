from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pikepdf
import tempfile
import os
import uuid

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(BASE, "static")
TMP = os.path.join(BASE, "tmp")
os.makedirs(TMP, exist_ok=True)

app = FastAPI(title="PDF Password Remover")

app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    with open(os.path.join(STATIC, "index.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/remove-password")
async def remove_password(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse({"error": "Please upload a PDF file."}, status_code=400)

    job_id = uuid.uuid4().hex
    input_path = os.path.join(TMP, f"{job_id}_input.pdf")
    output_path = os.path.join(TMP, f"{job_id}_unlocked.pdf")

    try:
        with open(input_path, "wb") as out:
            while chunk := await file.read(1024 * 1024):
                out.write(chunk)

        with pikepdf.open(input_path, password=password) as pdf:
            pdf.save(output_path)

        download_name = os.path.splitext(file.filename)[0] + "_unlocked.pdf"

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=download_name,
            background=None
        )

    except pikepdf.PasswordError:
        return JSONResponse(
            {"error": "Incorrect PDF password."},
            status_code=401
        )
    except pikepdf.PdfError:
        return JSONResponse(
            {"error": "The PDF could not be processed."},
            status_code=400
        )
    except Exception:
        return JSONResponse(
            {"error": "An unexpected error occurred."},
            status_code=500
        )
    finally:
        # Input is always deleted. The output is returned by FileResponse.
        # A production deployment should use a cleanup worker for output files.
        try:
            os.remove(input_path)
        except OSError:
            pass

import tempfile
from pathlib import Path

import pikepdf
from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
STATIC_DIR = PROJECT_ROOT / "static"
TEMP_DIR = Path(tempfile.gettempdir())

if not STATIC_DIR.is_dir():
    raise RuntimeError(f"Required static directory not found: {STATIC_DIR}")

app = FastAPI(title="PDF Password Remover")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def home():
    return FileResponse(STATIC_DIR / "index.html")


def _new_temp_pdf() -> Path:
    with tempfile.NamedTemporaryFile(dir=TEMP_DIR, suffix=".pdf", delete=False) as temp_file:
        return Path(temp_file.name)


@app.post("/api/remove-password")
async def remove_password(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    original_name = (file.filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    if not original_name.lower().endswith(".pdf"):
        return JSONResponse({"error": "Please upload a PDF file."}, status_code=400)

    input_path = None
    output_path = None

    try:
        input_path = _new_temp_pdf()
        output_path = _new_temp_pdf()
        header = bytearray()
        with input_path.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                if len(header) < 1024:
                    header.extend(chunk[:1024 - len(header)])
                out.write(chunk)

        if b"%PDF-" not in header:
            return JSONResponse({"error": "Please upload a valid PDF file."}, status_code=400)

        with pikepdf.open(input_path, password=password) as pdf:
            pdf.save(output_path)

        download_name = Path(original_name).stem + "_unlocked.pdf"
        background_tasks = BackgroundTasks()
        background_tasks.add_task(output_path.unlink, missing_ok=True)
        response = FileResponse(
            output_path,
            media_type="application/pdf",
            filename=download_name,
            background=background_tasks,
        )
        output_path = None
        return response

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
        await file.close()
        if input_path is not None:
            input_path.unlink(missing_ok=True)
        if output_path is not None:
            output_path.unlink(missing_ok=True)

import shutil
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.pipeline import executar_pipeline
from src.sheets_tracking import carregar_env, resolver_sheet_url

app = FastAPI(title="Analise A/B Cashback")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
def status():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Envie um arquivo CSV.")

    temp_id = uuid.uuid4().hex[:8]
    raiz = Path(__file__).resolve().parent.parent
    temp_path = raiz / "data" / f"upload_{temp_id}_{file.filename}"
    temp_path.parent.mkdir(parents=True, exist_ok=True)

    with temp_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        carregar_env(env_path=raiz / ".env")
        sheets_url = resolver_sheet_url()

        resultado = executar_pipeline(
            caminho_csv=temp_path,
            output_dir=raiz / "outputs",
            llm="openai",
            update_sheets=True,
            sheet_url=sheets_url,
        )

        parceiro = resultado["parceiro"]
        pdf_path = Path(resultado["pdf"])
        sheets_link = resultado["google_sheets"]["sheet_url"]

        output_dir = raiz / "outputs"
        pdf_relativo = pdf_path.relative_to(output_dir)

        return {
            "status": "success",
            "parceiro": parceiro,
            "pdf_url": f"/api/download/{pdf_relativo.as_posix()}",
            "pdf_name": pdf_relativo.name,
            "sheets_url": sheets_link,
        }

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if temp_path.exists():
            temp_path.unlink()


@app.get("/api/download/{pdf_name:path}")
def download_pdf(pdf_name: str):
    raiz = Path(__file__).resolve().parent.parent
    pdf_path = (raiz / "outputs" / pdf_name).resolve()
    if not str(pdf_path).startswith(str(raiz / "outputs")):
        raise HTTPException(400, "Caminho invalido.")
    if not pdf_path.exists():
        raise HTTPException(404, "PDF nao encontrado.")
    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )


FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{rest_of_path:path}")
    def serve_frontend(rest_of_path: str = ""):
        file_path = FRONTEND_DIST / rest_of_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        index = FRONTEND_DIST / "index.html"
        if index.exists():
            return HTMLResponse(index.read_text(encoding="utf-8"))
        raise HTTPException(404)

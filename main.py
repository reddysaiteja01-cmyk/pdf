from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

# Paths
FILE_DIR = Path("files")
PDF_FILE = FILE_DIR / "Occupancy_Certificate.pdf"
FAVICON_FILE = FILE_DIR / "favicon.ico"

@app.get("/download", response_class=FileResponse)
def download_pdf():
    """
    Download the Occupancy Certificate PDF.
    """
    if PDF_FILE.exists():
        return FileResponse(
            path=str(PDF_FILE),
            filename="Occupancy_Certificate.pdf",
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Occupancy_Certificate.pdf"}
        )
    return Response(content="File not found", status_code=404)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """
    Optional: Serve favicon to avoid 404 logs in browser.
    """
    if FAVICON_FILE.exists():
        return FileResponse(FAVICON_FILE)
    return Response(status_code=204)

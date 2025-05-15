from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from pathlib import Path
import qrcode

app = FastAPI()

# Paths
FILE_DIR = Path("files")
FILE_DIR.mkdir(exist_ok=True)
PDF_FILE = FILE_DIR / "Occupancy_Certificate.pdf"
QR_FILE = FILE_DIR / "download_qr.png"
FAVICON_FILE = FILE_DIR / "favicon.ico"

# Replace this with your actual Render URL once deployed
PUBLIC_DOWNLOAD_URL = "https://your-app.onrender.com/download"

@app.on_event("startup")
def generate_qr_code():
    """
    Generate a QR code pointing to the /download URL.
    Runs once at startup.
    """
    if not QR_FILE.exists():
        qr = qrcode.make(PUBLIC_DOWNLOAD_URL)
        qr.save(QR_FILE)

@app.get("/download", response_class=FileResponse)
def download_pdf():
    if PDF_FILE.exists():
        return FileResponse(
            path=str(PDF_FILE),
            filename="Occupancy_Certificate.pdf",
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Occupancy_Certificate.pdf"}
        )
    return Response(content="File not found", status_code=404)

@app.get("/qr", response_class=FileResponse)
def get_qr():
    if QR_FILE.exists():
        return FileResponse(QR_FILE, media_type="image/png")
    return Response(content="QR code not found", status_code=404)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    if FAVICON_FILE.exists():
        return FileResponse(FAVICON_FILE)
    return Response(status_code=204)

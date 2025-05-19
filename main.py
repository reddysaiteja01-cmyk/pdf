from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from pathlib import Path
from PIL import Image
import qrcode

app = FastAPI()

# Paths
FILE_DIR = Path("files")
FILE_DIR.mkdir(exist_ok=True)
PDF_FILE = FILE_DIR / "Occupancy_Certificate.pdf"
QR_FILE = FILE_DIR / "download_qr.png"
FAVICON_FILE = FILE_DIR / "favicon.ico"
LOGO_FILE = FILE_DIR / "logo.png"  # Add your logo as 'logo.png' in the files directory

# Replace this with your actual Render URL once deployed
PUBLIC_DOWNLOAD_URL = "https://pdfsacnit.onrender.com/download"

@app.on_event("startup")
def generate_qr_code():
    """
    Generate a QR code with a logo in the center pointing to the /download URL.
    Runs once at startup.
    """
    if not QR_FILE.exists():
        # Create the QR code with high error correction
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )
        qr.add_data(PUBLIC_DOWNLOAD_URL)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        if LOGO_FILE.exists():
            logo = Image.open(LOGO_FILE)

            # Resize logo
            qr_width, qr_height = qr_img.size
            logo_size = int(qr_width * 0.25)  # 25% of QR size
            logo = logo.resize((logo_size, logo_size), Image.ANTIALIAS)

            # Position logo at the center
            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            qr_img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)

        qr_img.save(QR_FILE)

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

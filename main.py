from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from pathlib import Path
from PIL import Image
import qrcode
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
FILE_DIR = Path("files")
FILE_DIR.mkdir(exist_ok=True)
PDF_FILE = FILE_DIR / "Occupancy_Certificate.pdf"
QR_FILE = FILE_DIR / "download_qr.png"
FAVICON_FILE = FILE_DIR / "favicon.ico"
LOGO_FILE = FILE_DIR / "logo.png"  # Your logo image file

# Public URL for the PDF
PUBLIC_DOWNLOAD_URL = "https://cdn-buildnow-telangana.onrender.com/download"

@app.on_event("startup")
def generate_qr_code():
    """
    Generate a high-density QR code with optional logo at the center.
    Runs once at startup.
    """
    try:
        if QR_FILE.exists():
            logger.info("QR code already exists. Skipping generation.")
            return

        logger.info("Generating high-density QR code...")
        qr = qrcode.QRCode(
            version=10,  # Higher version increases data capacity and complexity
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,  # Each "box" of the QR will be 10x10 pixels
            border=4      # Standard border size
        )
        qr.add_data(PUBLIC_DOWNLOAD_URL)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        if LOGO_FILE.exists():
            try:
                logo = Image.open(LOGO_FILE)
                qr_width, qr_height = qr_img.size
                logo_size = int(qr_width * 0.25)

                # Resize logo with high-quality resampling
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

                pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                qr_img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)
                logger.info("Logo added to QR code.")
            except Exception as e:
                logger.warning(f"Failed to add logo to QR: {e}")
        else:
            logger.info("Logo file not found. Generating QR without logo.")

        qr_img.save(QR_FILE)
        logger.info("High-density QR code generated and saved.")
    except Exception as e:
        logger.error(f"QR generation failed: {e}")

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

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance
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
LOGO_FILE = FILE_DIR / "logo.png"

# Public URL for the PDF
PUBLIC_DOWNLOAD_URL = "https://cdn-buildnow-telangana.onrender.com/download"

@app.on_event("startup")
def generate_qr_code():
    try:
        if QR_FILE.exists():
            logger.info("QR code already exists. Skipping generation.")
            return

        logger.info("Generating high-density QR code...")
        qr = qrcode.QRCode(
            version=10,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(PUBLIC_DOWNLOAD_URL)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        if LOGO_FILE.exists():
            try:
                logo = Image.open(LOGO_FILE).convert("RGBA")

                # Resize logo
                qr_width, qr_height = qr_img.size
                logo_size = int(qr_width * 0.25)
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

                # Create circular mask
                mask = Image.new("L", logo.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)

                # Enhance sharpness/brightness if needed
                logo = ImageEnhance.Sharpness(logo).enhance(2.0)
                logo = ImageEnhance.Brightness(logo).enhance(1.2)

                # Apply circular mask to logo
                logo.putalpha(mask)

                # Paste logo to center
                pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                qr_img.paste(logo, pos, logo)

                logger.info("Circular masked logo added to QR code.")
            except Exception as e:
                logger.warning(f"Failed to add logo: {e}")
        else:
            logger.info("Logo not found. Generating QR without it.")

        qr_img.convert("RGB").save(QR_FILE)
        logger.info("QR code saved.")
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

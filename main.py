from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance
import qrcode
import logging
import os

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
FILE_DIR = Path("files")
FILE_DIR.mkdir(exist_ok=True)

# Only one PDF and one route
PDF_FILES = {
    "occupancy_certificate": {
        "filename": "Occupancy Certificate.pdf",
        "qr_file": "occupancy.png",
        "route": "occupancy_certificate"
    }
}

LOGO_FILE = FILE_DIR / "logo.png"
FAVICON_FILE = FILE_DIR / "favicon.ico"


def generate_qr_code(pdf_key: str, public_url: str, qr_path: Path):
    try:
        logger.info(f"Generating QR code for {pdf_key}...")
        qr = qrcode.QRCode(
            version=10,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(public_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        # Add logo if available
        if LOGO_FILE.exists():
            try:
                logo = Image.open(LOGO_FILE).convert("RGBA")
                qr_width, qr_height = qr_img.size
                logo_size = int(qr_width * 0.25)
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

                # Circular mask
                mask = Image.new("L", logo.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)

                # Enhance logo
                logo = ImageEnhance.Sharpness(logo).enhance(2.0)
                logo = ImageEnhance.Brightness(logo).enhance(1.2)
                logo.putalpha(mask)

                pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                qr_img.paste(logo, pos, logo)
                logger.info("Logo added to QR code.")
            except Exception as e:
                logger.warning(f"Failed to add logo: {e}")

        qr_img.convert("RGB").save(qr_path)
        logger.info(f"QR code for {pdf_key} saved at {qr_path}")
    except Exception as e:
        logger.error(f"QR generation failed for {pdf_key}: {e}")


@app.on_event("startup")
def generate_all_qrs():
    for key, info in PDF_FILES.items():
        qr_path = FILE_DIR / info["qr_file"]
        public_url = f"https://cdn-buildnow-telangana.onrender.com/download/{info['route']}"
        if not qr_path.exists():
            generate_qr_code(key, public_url, qr_path)
        else:
            logger.info(f"QR for {key} already exists. Skipping.")


@app.get("/", response_class=HTMLResponse)
def home():
    """Simple homepage with links"""
    html = "<h2>Available Downloads & QR Codes</h2><ul>"
    for key, info in PDF_FILES.items():
        html += f"""
        <li>
            <b>{key}</b><br>
            <a href='/download/{info["route"]}'>Download PDF</a> |
            <a href='/qr/{info["route"]}'>View QR</a>
        </li>
        """
    html += "</ul>"
    return html


@app.get("/download/{pdf_name}", response_class=FileResponse)
def download_pdf(pdf_name: str):
    for info in PDF_FILES.values():
        if info["route"] == pdf_name:
            file_path = FILE_DIR / info["filename"]
            if file_path.exists():
                return FileResponse(
                    path=str(file_path),
                    filename=info["filename"],
                    media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={info['filename']}"}
                )
            return Response(content="File not found", status_code=404)
    return Response(content="Invalid PDF name", status_code=400)


@app.get("/qr/{pdf_name}", response_class=FileResponse)
def get_qr(pdf_name: str):
    for info in PDF_FILES.values():
        if info["route"] == pdf_name:
            qr_path = FILE_DIR / info["qr_file"]
            if qr_path.exists():
                return FileResponse(qr_path, media_type="image/png")
            return Response(content="QR code not found", status_code=404)
    return Response(content="Invalid QR name", status_code=400)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    if FAVICON_FILE.exists():
        return FileResponse(FAVICON_FILE)
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

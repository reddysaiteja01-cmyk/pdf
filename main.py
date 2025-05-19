from fastapi import FastAPI, Response from fastapi.responses import FileResponse from pathlib import Path from PIL import Image, ImageDraw, ImageEnhance import qrcode import logging

app = FastAPI()

Setup logging

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

Paths

FILE_DIR = Path("files") FILE_DIR.mkdir(exist_ok=True) FILES = { "occupancy": { "pdf": FILE_DIR / "Occupancy_Certificate.pdf", "qr": FILE_DIR / "occupancy_qr.png", "url": "https://cdn-buildnow-telangana.onrender.com/download/occupancy" }, "noc": { "pdf": FILE_DIR / "NOC_Certificate.pdf", "qr": FILE_DIR / "noc_qr.png", "url": "https://cdn-buildnow-telangana.onrender.com/download/noc" } } FAVICON_FILE = FILE_DIR / "favicon.ico" LOGO_FILE = FILE_DIR / "logo.png"

@app.on_event("startup") def generate_qr_codes(): for name, data in FILES.items(): qr_path = data["qr"] if qr_path.exists(): logger.info(f"QR code for {name} already exists. Skipping generation.") continue

logger.info(f"Generating QR code for {name}...")
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(data["url"])
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    if LOGO_FILE.exists():
        try:
            logo = Image.open(LOGO_FILE).convert("RGBA")
            qr_width, qr_height = qr_img.size
            logo_size = int(qr_width * 0.25)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            # Create circular mask
            mask = Image.new("L", logo.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)

            # Enhance logo
            logo = ImageEnhance.Sharpness(logo).enhance(2.0)
            logo = ImageEnhance.Brightness(logo).enhance(1.2)
            logo.putalpha(mask)

            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            qr_img.paste(logo, pos, logo)

            logger.info(f"Circular masked logo added to QR code for {name}.")
        except Exception as e:
            logger.warning(f"Failed to add logo to QR code for {name}: {e}")

    qr_img.convert("RGB").save(qr_path)
    logger.info(f"QR code for {name} saved.")

@app.get("/download/{doc_name}", response_class=FileResponse) def download_pdf(doc_name: str): if doc_name in FILES and FILES[doc_name]["pdf"].exists(): return FileResponse( path=str(FILES[doc_name]["pdf"]), filename=FILES[doc_name]["pdf"].name, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={FILES[doc_name]['pdf'].name}"} ) return Response(content="File not found", status_code=404)

@app.get("/qr/{doc_name}", response_class=FileResponse) def get_qr(doc_name: str): if doc_name in FILES and FILES[doc_name]["qr"].exists(): return FileResponse(FILES[doc_name]["qr"], media_type="image/png") return Response(content="QR code not found", status_code=404)

@app.get("/favicon.ico", include_in_schema=False) def favicon(): if FAVICON_FILE.exists(): return FileResponse(FAVICON_FILE) return Response(status_code=204)


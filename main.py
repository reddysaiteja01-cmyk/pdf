from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
import os

app = FastAPI()

@app.get("/download")
def download_pdf():
    file_path = "files/Occupancy_Certificate.pdf"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename="Occupancy_Certificate.pdf",
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Occupancy_Certificate.pdf"}
        )
    return Response(content="File not found", status_code=404)

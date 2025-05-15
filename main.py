from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
import os

app = FastAPI()

@app.get("/download")
def download_pdf():
    file_path = "files/your_file.pdf"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename="your_file.pdf",
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=your_file.pdf"}
        )
    return Response(content="File not found", status_code=404)
